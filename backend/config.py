"""
config.py
---------
All settings in one place. Values come from environment variables (a .env file
in development) so we never hard-code secrets or database passwords.

The database URL defaults to a local SQLite file. That means the app runs even
if PostgreSQL is not installed. To use PostgreSQL, set DATABASE_URL in .env, for
example:

    DATABASE_URL=postgresql://localhost:5432/deepfake_challenge
"""

import os
from dotenv import load_dotenv

load_dotenv()  # read the .env file if it exists

# Absolute path to this backend folder, used to build safe file paths.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Where uploaded datasets and submissions are stored on disk.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # Database: use PostgreSQL if DATABASE_URL is set, otherwise a local SQLite file.
    _database_url = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    )
    # Some hosts (like Render) hand out URLs starting with "postgres://", but
    # SQLAlchemy needs "postgresql://". Fix it so the app connects either way.
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret used to sign login tokens (JWT). Override in production via .env.
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "dev-only-secret-change-me-in-production-0123456789"
    )

    # Largest file we accept for an upload: 50 MB.
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
