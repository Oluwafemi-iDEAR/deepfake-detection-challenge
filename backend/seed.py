"""
seed.py
-------
Prepares the platform for a demo with REAL, reproducible data:

  1. Generates a ground-truth CSV (200 files, half real / half deepfake) and a
     small "media" placeholder file, saved under ../sample_data/.
  2. Generates two sample participant submissions: one strong detector and one
     weak detector, so the leaderboard has real, different scores.
  3. Creates the database tables.
  4. Creates an admin account, a demo participant account, and one released
     dataset that points at the generated ground-truth file.

Run it with:   python seed.py
The random seed is fixed, so everyone who runs this gets identical numbers.
"""

import csv
import os
import numpy as np

from app import app
from models import db, User, Dataset

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data"))
NUM_FILES = 200


def generate_sample_files():
    """Write ground truth + two example submissions as real CSV files."""
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    rng = np.random.default_rng(42)  # fixed seed -> reproducible numbers

    # Half the files are real (label 0), half are deepfake (label 1).
    filenames = [f"clip_{i:04d}.mp4" for i in range(NUM_FILES)]
    labels = [0] * (NUM_FILES // 2) + [1] * (NUM_FILES // 2)

    # Ground truth CSV.
    truth_path = os.path.join(SAMPLE_DIR, "ground_truth.csv")
    with open(truth_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "label"])
        for name, label in zip(filenames, labels):
            writer.writerow([name, label])

    # A strong detector: fakes get high scores, reals get low scores (with noise).
    strong_path = os.path.join(SAMPLE_DIR, "sample_submission_strong.csv")
    with open(strong_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "score"])
        for name, label in zip(filenames, labels):
            center = 0.75 if label == 1 else 0.25
            score = float(np.clip(rng.normal(center, 0.15), 0, 1))
            writer.writerow([name, round(score, 4)])

    # A weak detector: scores barely separate the two classes.
    weak_path = os.path.join(SAMPLE_DIR, "sample_submission_weak.csv")
    with open(weak_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "score"])
        for name, label in zip(filenames, labels):
            center = 0.55 if label == 1 else 0.45
            score = float(np.clip(rng.normal(center, 0.25), 0, 1))
            writer.writerow([name, round(score, 4)])

    # A stand-in for the downloadable media package (a real, small text file).
    media_path = os.path.join(SAMPLE_DIR, "dataset_media_README.txt")
    with open(media_path, "w", encoding="utf-8") as f:
        f.write(
            "Deepfake Challenge - Demo Dataset\n"
            "In a real challenge this download would be a ZIP of 200 video clips.\n"
            "Score your predictions against them and upload a CSV of filename,score.\n"
        )

    print(f"[seed] wrote sample files to {SAMPLE_DIR}")
    return media_path, truth_path


def seed_database(media_path, truth_path):
    with app.app_context():
        db.create_all()

        # Admin account.
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@morgan.edu", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("[seed] created admin  (username: admin  / password: admin123)")

        # Demo participant account.
        if not User.query.filter_by(username="student").first():
            student = User(username="student", email="student@morgan.edu", role="participant")
            student.set_password("student123")
            db.session.add(student)
            print("[seed] created participant (username: student / password: student123)")

        # One released dataset pointing at the generated ground truth.
        if not Dataset.query.filter_by(name="Deepfake Video Challenge 2026").first():
            row_count = max(0, sum(1 for _ in open(truth_path, encoding="utf-8")) - 1)
            dataset = Dataset(
                name="Deepfake Video Challenge 2026",
                description="200 short clips, half real and half AI-generated. "
                            "Predict the probability each clip is a deepfake.",
                media_path=media_path,
                ground_truth_path=truth_path,
                num_files=row_count,
                released=True,
            )
            db.session.add(dataset)
            print("[seed] created released dataset: Deepfake Video Challenge 2026")

        db.session.commit()
        print("[seed] done.")


if __name__ == "__main__":
    media_path, truth_path = generate_sample_files()
    seed_database(media_path, truth_path)
