// DatasetDetail.jsx
// One dataset: download the media, upload a prediction CSV, and see the real
// scoring results (metrics, confusion matrix, and ROC curve).

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { listDatasets, submitPredictions, API_BASE } from "../api";
import { getToken } from "../auth";
import RocCurve from "../components/RocCurve";

export default function DatasetDetail() {
  const { id } = useParams();
  const [dataset, setDataset] = useState(null);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // Find this dataset in the list the user is allowed to see.
  useEffect(() => {
    listDatasets()
      .then((all) => setDataset(all.find((d) => String(d.id) === id)))
      .catch((err) => setError(err.message));
  }, [id]);

  // Download the dataset media. We fetch with the login token, then save the blob.
  async function handleDownload() {
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/datasets/${id}/download`, {
        headers: { Authorization: "Bearer " + getToken() },
      });
      if (!response.ok) throw new Error("Download failed. Is the dataset released?");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `dataset_${id}.bin`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  }

  // Upload the prediction CSV and show the scored result.
  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    if (!file) {
      setError("Please choose a CSV file first.");
      return;
    }
    setBusy(true);
    try {
      const data = await submitPredictions(id, file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!dataset) {
    return <p className="text-muted">Loading dataset…</p>;
  }

  const cm = result && result.confusion_matrix;

  return (
    <div>
      <Link to="/datasets" className="btn btn-link px-0">&larr; Back to datasets</Link>
      <h3>{dataset.name}</h3>
      <p className="text-muted">{dataset.description}</p>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row">
        {/* Left: download + submit */}
        <div className="col-md-6">
          <div className="card shadow-sm mb-3">
            <div className="card-body">
              <h5>1. Download the dataset</h5>
              <p className="small text-muted">
                Get the {dataset.num_files} media files to run your detector on.
              </p>
              <button className="btn btn-outline-primary" onClick={handleDownload}>
                Download dataset
              </button>
            </div>
          </div>

          <div className="card shadow-sm">
            <div className="card-body">
              <h5>2. Submit your predictions</h5>
              <p className="small text-muted">
                Upload a CSV with columns <code>filename,score</code> (score = the
                probability the clip is a deepfake, between 0 and 1).
              </p>
              <form onSubmit={handleSubmit}>
                <input
                  type="file"
                  accept=".csv"
                  className="form-control mb-3"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <button className="btn btn-primary" type="submit" disabled={busy}>
                  {busy ? "Scoring…" : "Submit and score"}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right: results */}
        <div className="col-md-6">
          {result ? (
            <div className="card shadow-sm">
              <div className="card-body">
                <h5>Your results</h5>
                <table className="table table-sm">
                  <tbody>
                    <tr><th>AUC</th><td>{result.auc}</td></tr>
                    <tr><th>Accuracy</th><td>{result.accuracy}</td></tr>
                    <tr><th>Precision</th><td>{result.precision}</td></tr>
                    <tr><th>Recall</th><td>{result.recall}</td></tr>
                    <tr><th>F1 score</th><td>{result.f1}</td></tr>
                    <tr><th>Files scored</th><td>{result.num_scored}</td></tr>
                  </tbody>
                </table>

                <h6 className="mt-3">Confusion matrix</h6>
                <table className="table table-bordered text-center small">
                  <thead>
                    <tr>
                      <th></th><th>Predicted real</th><th>Predicted fake</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th>Actually real</th>
                      <td className="table-success">{cm.true_negative}</td>
                      <td className="table-danger">{cm.false_positive}</td>
                    </tr>
                    <tr>
                      <th>Actually fake</th>
                      <td className="table-danger">{cm.false_negative}</td>
                      <td className="table-success">{cm.true_positive}</td>
                    </tr>
                  </tbody>
                </table>

                <h6 className="mt-3">ROC curve</h6>
                <RocCurve points={result.roc_points} />

                <Link
                  className="btn btn-outline-secondary btn-sm mt-3"
                  to={`/datasets/${id}/leaderboard`}
                >
                  See the leaderboard
                </Link>
              </div>
            </div>
          ) : (
            <div className="alert alert-info">
              Your scoring results will appear here after you submit.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
