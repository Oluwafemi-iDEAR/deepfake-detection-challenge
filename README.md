# Deepfake Detection Challenge Platform

A secure web platform for benchmarking deepfake-detection models, built for the
**Guardians of Forensic Evidence Initiative**. Participants download a dataset,
run their detector, and upload a prediction CSV; the platform scores it against a
hidden ground truth using real metrics (AUC, accuracy, confusion matrix, ROC) and
ranks everyone on a leaderboard.

Stack: **Flask** (Python API) · **React + Bootstrap** (frontend) · **PostgreSQL**
(with a SQLite fallback) · **scikit-learn** (scoring).

## Project layout

```
backend/    Flask JSON API, database models, and the real scoring engine
frontend/   React + Bootstrap single-page app (Vite)
sample_data/ real ground-truth + example submission CSVs
```

## Run it (two terminals)

**1. Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py          # creates tables, demo accounts, and one dataset
python app.py           # serves the API on http://localhost:5001
```

**2. Frontend**

```bash
cd frontend
npm install
npm run dev             # serves the app on http://localhost:5173
```

Open http://localhost:5173.

## Demo accounts

| Role        | Username | Password    |
|-------------|----------|-------------|
| Admin       | admin    | admin123    |
| Participant | student  | student123  |

## Using PostgreSQL instead of SQLite

```bash
createdb deepfake_challenge
cd backend
cp .env.example .env
# in .env set:
# DATABASE_URL=postgresql://localhost:5432/deepfake_challenge
python seed.py
```

## Try the sample submissions

Log in as `student`, open the dataset, and upload one of:

- `sample_data/sample_submission_strong.csv` → AUC ≈ 0.999
- `sample_data/sample_submission_weak.csv`   → AUC ≈ 0.668

## CSV formats

```
ground_truth.csv   filename,label     label = 1 (deepfake) or 0 (real)
submission.csv     filename,score     score = probability the clip is a deepfake
```
