// Datasets.jsx
// The dataset release portal. Lists the datasets the logged-in user can see.
// Participants only see released datasets; admins see all of them.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listDatasets } from "../api";

export default function Datasets() {
  const [datasets, setDatasets] = useState([]);
  const [error, setError] = useState("");

  // Load the datasets once, when the page first shows.
  useEffect(() => {
    listDatasets()
      .then(setDatasets)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <h3 className="mb-3">Available Challenge Datasets</h3>
      {error && <div className="alert alert-danger">{error}</div>}

      {datasets.length === 0 ? (
        <p className="text-muted">No datasets available yet.</p>
      ) : (
        <div className="row">
          {datasets.map((d) => (
            <div className="col-md-6 mb-3" key={d.id}>
              <div className="card h-100 shadow-sm">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <h5 className="card-title">{d.name}</h5>
                    {d.released ? (
                      <span className="badge bg-success">Released</span>
                    ) : (
                      <span className="badge bg-secondary">Not released</span>
                    )}
                  </div>
                  <p className="card-text text-muted">{d.description}</p>
                  <p className="small mb-3">{d.num_files} files in this dataset</p>
                  <Link className="btn btn-primary btn-sm me-2" to={`/datasets/${d.id}`}>
                    Open
                  </Link>
                  <Link
                    className="btn btn-outline-secondary btn-sm"
                    to={`/datasets/${d.id}/leaderboard`}
                  >
                    Leaderboard
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
