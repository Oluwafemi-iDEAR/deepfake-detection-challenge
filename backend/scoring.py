"""
scoring.py
----------
The scientific core of the platform.

A participant uploads a prediction CSV. We compare those predictions against
the hidden ground-truth CSV for the dataset and compute REAL evaluation metrics:
AUC, accuracy, a confusion matrix, precision/recall/F1, and the ROC curve points.

CSV formats
    ground truth : filename,label     (label = 1 for deepfake/fake, 0 for real)
    submission   : filename,score      (score = predicted probability it is fake)

Nothing here is faked. Every number comes from scikit-learn run on the two files.
"""

import csv
from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


def read_two_column_csv(path, value_name):
    """Read a 'filename,value' CSV into a dict {filename: value}.

    Raises ValueError with a clear message if the file is malformed so the
    participant knows exactly what to fix.
    """
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip the header row
        if header is None:
            raise ValueError("The CSV file is empty.")
        line_number = 1
        for row in reader:
            line_number += 1
            if len(row) < 2:
                raise ValueError(
                    f"Line {line_number}: expected 'filename,{value_name}' but got '{row}'."
                )
            filename = row[0].strip()
            try:
                value = float(row[1])
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: the {value_name} '{row[1]}' is not a number."
                )
            rows[filename] = value
    if not rows:
        raise ValueError("No data rows found in the CSV file.")
    return rows


def score_submission(ground_truth_path, submission_path):
    """Compare a submission to the ground truth and return a metrics dictionary.

    We log the aligned payload so problems are easy to troubleshoot later.
    """
    truth = read_two_column_csv(ground_truth_path, "label")
    predictions = read_two_column_csv(submission_path, "score")

    # Align the two files by filename. Every ground-truth file must have a prediction.
    missing = [name for name in truth if name not in predictions]
    if missing:
        raise ValueError(
            f"Your submission is missing predictions for {len(missing)} file(s), "
            f"for example: {missing[:5]}"
        )

    # Build matched lists in a stable order.
    filenames = sorted(truth.keys())
    y_true = [int(truth[name]) for name in filenames]
    y_score = [float(predictions[name]) for name in filenames]

    # Turn out how many rows we scored so it shows up in the logs for troubleshooting.
    print(f"[scoring] scored {len(filenames)} files "
          f"| positives={sum(y_true)} | truth={ground_truth_path} | sub={submission_path}")

    # Predicted labels use the standard 0.5 probability threshold.
    y_pred = [1 if score >= 0.5 else 0 for score in y_score]

    # AUC needs both classes present; guard against a degenerate ground truth.
    if len(set(y_true)) < 2:
        raise ValueError("Ground truth must contain both real (0) and fake (1) labels.")

    auc = roc_auc_score(y_true, y_score)
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # Confusion matrix laid out as [[TN, FP], [FN, TP]].
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    # ROC curve points so the frontend can draw the curve.
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_points = [{"fpr": float(x), "tpr": float(y)} for x, y in zip(fpr, tpr)]

    result = {
        "num_scored": len(filenames),
        "auc": round(float(auc), 4),
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "roc_points": roc_points,
    }
    print(f"[scoring] result payload: {result}")
    return result
