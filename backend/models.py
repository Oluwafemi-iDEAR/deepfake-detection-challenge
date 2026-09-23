"""
models.py
---------
The database tables, described as Python classes using SQLAlchemy.

Three tables:
    User        - people who log in (role is 'admin' or 'participant')
    Dataset     - a challenge dataset an admin releases
    Submission  - one scored prediction file a participant uploaded
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# One shared database object the app imports and initialises.
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="participant")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user can have many submissions.
    submissions = db.relationship("Submission", backref="user", lazy=True)

    def set_password(self, password):
        """Store a salted hash, never the raw password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Dataset(db.Model):
    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")

    # Path to the downloadable media package participants receive.
    media_path = db.Column(db.String(255), nullable=False)
    # Path to the hidden ground-truth CSV. Never sent to participants.
    ground_truth_path = db.Column(db.String(255), nullable=False)

    # How many files the ground truth contains (shown in the portal).
    num_files = db.Column(db.Integer, default=0)
    # Only released datasets are visible to participants.
    released = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", backref="dataset", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "num_files": self.num_files,
            "released": self.released,
            "created_at": self.created_at.isoformat(),
        }


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)

    # The metrics we computed and saved.
    auc = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1 = db.Column(db.Float, nullable=False)
    num_scored = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username,
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset.name,
            "auc": self.auc,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "num_scored": self.num_scored,
            "created_at": self.created_at.isoformat(),
        }
