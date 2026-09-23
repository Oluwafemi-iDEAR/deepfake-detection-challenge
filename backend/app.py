"""
app.py
------
The web server. It exposes a small JSON API that the React frontend calls.

Route groups:
    Auth       /api/register, /api/login, /api/me
    Datasets   list, create (admin), download
    Submit     upload a prediction CSV and get it scored
    Leaderboard  ranked results for a dataset
    Admin      list users, release/unrelease datasets

Login uses JWT tokens: on login we hand the browser a signed token; the browser
sends it back on every request in the Authorization header.
"""

import os
import uuid

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Dataset, Submission
from scoring import score_submission


app = Flask(__name__)
app.config.from_object(Config)

# Allow the React dev server (a different port) to call this API.
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Make sure the upload folders exist.
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "datasets"), exist_ok=True)
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "submissions"), exist_ok=True)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def current_user():
    """Return the User row for whoever is logged in on this request."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def admin_required():
    """Return True if the logged-in user is an admin."""
    claims = get_jwt()
    return claims.get("role") == "admin"


def count_csv_rows(path):
    """Count data rows in a CSV (everything after the header)."""
    with open(path, encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    print(f"[register] payload: username={username} email={email}")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are all required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "That username is already taken."}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "That email is already registered."}), 409

    user = User(username=username, email=email, role="participant")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Account created. You can log in now."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    print(f"[login] attempt: username={username}")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401

    # The token carries the user id and role so we can check permissions later.
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": user.to_dict()})


@app.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    return jsonify(current_user().to_dict())


# --------------------------------------------------------------------------
# Datasets
# --------------------------------------------------------------------------
@app.route("/api/datasets", methods=["GET"])
@jwt_required()
def list_datasets():
    """Admins see every dataset; participants see only released ones."""
    if admin_required():
        datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    else:
        datasets = (
            Dataset.query.filter_by(released=True)
            .order_by(Dataset.created_at.desc())
            .all()
        )
    return jsonify([d.to_dict() for d in datasets])


@app.route("/api/datasets", methods=["POST"])
@jwt_required()
def create_dataset():
    """Admin only. Upload a media package + a ground-truth CSV to make a dataset."""
    if not admin_required():
        return jsonify({"error": "Admin access required."}), 403

    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    media_file = request.files.get("media")
    truth_file = request.files.get("ground_truth")

    print(f"[create_dataset] name={name} media={media_file} truth={truth_file}")

    if not name or media_file is None or truth_file is None:
        return jsonify({"error": "Name, a media file, and a ground-truth CSV are required."}), 400

    # Save both files with unique names so uploads never overwrite each other.
    dataset_folder = os.path.join(app.config["UPLOAD_FOLDER"], "datasets")
    tag = uuid.uuid4().hex[:8]
    media_name = f"{tag}_{secure_filename(media_file.filename)}"
    truth_name = f"{tag}_{secure_filename(truth_file.filename)}"
    media_path = os.path.join(dataset_folder, media_name)
    truth_path = os.path.join(dataset_folder, truth_name)
    media_file.save(media_path)
    truth_file.save(truth_path)

    dataset = Dataset(
        name=name,
        description=description,
        media_path=media_path,
        ground_truth_path=truth_path,
        num_files=count_csv_rows(truth_path),
        released=False,  # admin releases it explicitly later
    )
    db.session.add(dataset)
    db.session.commit()
    return jsonify(dataset.to_dict()), 201


@app.route("/api/datasets/<int:dataset_id>/download", methods=["GET"])
@jwt_required()
def download_dataset(dataset_id):
    """Controlled access: only released datasets can be downloaded by participants."""
    dataset = Dataset.query.get_or_404(dataset_id)
    if not dataset.released and not admin_required():
        return jsonify({"error": "This dataset has not been released yet."}), 403
    return send_file(dataset.media_path, as_attachment=True)


# --------------------------------------------------------------------------
# Submissions / scoring
# --------------------------------------------------------------------------
@app.route("/api/datasets/<int:dataset_id>/submit", methods=["POST"])
@jwt_required()
def submit(dataset_id):
    """Participant uploads a prediction CSV. We score it and save the result."""
    dataset = Dataset.query.get_or_404(dataset_id)
    if not dataset.released:
        return jsonify({"error": "This dataset is not open for submissions."}), 403

    csv_file = request.files.get("submission")
    if csv_file is None:
        return jsonify({"error": "Please attach your prediction CSV file."}), 400

    user = current_user()
    sub_folder = os.path.join(app.config["UPLOAD_FOLDER"], "submissions")
    filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(csv_file.filename)}"
    saved_path = os.path.join(sub_folder, filename)
    csv_file.save(saved_path)

    print(f"[submit] user={user.username} dataset={dataset.name} file={saved_path}")

    # Run the real scoring. If the CSV is malformed, tell the user what went wrong.
    try:
        result = score_submission(dataset.ground_truth_path, saved_path)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    submission = Submission(
        user_id=user.id,
        dataset_id=dataset.id,
        auc=result["auc"],
        accuracy=result["accuracy"],
        precision=result["precision"],
        recall=result["recall"],
        f1=result["f1"],
        num_scored=result["num_scored"],
    )
    db.session.add(submission)
    db.session.commit()

    # Send back the saved row plus the extra detail (confusion matrix + ROC points).
    response = submission.to_dict()
    response["confusion_matrix"] = result["confusion_matrix"]
    response["roc_points"] = result["roc_points"]
    return jsonify(response), 201


@app.route("/api/my-submissions", methods=["GET"])
@jwt_required()
def my_submissions():
    user = current_user()
    subs = (
        Submission.query.filter_by(user_id=user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in subs])


# --------------------------------------------------------------------------
# Leaderboard
# --------------------------------------------------------------------------
@app.route("/api/datasets/<int:dataset_id>/leaderboard", methods=["GET"])
@jwt_required()
def leaderboard(dataset_id):
    """Best (highest-AUC) submission per user for this dataset, ranked."""
    subs = (
        Submission.query.filter_by(dataset_id=dataset_id)
        .order_by(Submission.auc.desc())
        .all()
    )

    # Keep only each user's best score (the list is already sorted by AUC).
    best_per_user = {}
    for s in subs:
        if s.user_id not in best_per_user:
            best_per_user[s.user_id] = s

    ranked = sorted(best_per_user.values(), key=lambda s: s.auc, reverse=True)
    return jsonify([s.to_dict() for s in ranked])


# --------------------------------------------------------------------------
# Admin dashboard
# --------------------------------------------------------------------------
@app.route("/api/admin/users", methods=["GET"])
@jwt_required()
def admin_users():
    if not admin_required():
        return jsonify({"error": "Admin access required."}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/admin/datasets/<int:dataset_id>/release", methods=["POST"])
@jwt_required()
def toggle_release(dataset_id):
    if not admin_required():
        return jsonify({"error": "Admin access required."}), 403
    dataset = Dataset.query.get_or_404(dataset_id)
    dataset.released = not dataset.released  # flip released on/off
    db.session.commit()
    return jsonify(dataset.to_dict())


# --------------------------------------------------------------------------
# Startup
# --------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # create tables on first run
    app.run(debug=True, port=5001)
