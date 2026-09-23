// Leaderboard.jsx
// Shows each participant's best submission for a dataset, ranked by AUC.

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getLeaderboard } from "../api";

export default function Leaderboard() {
  const { id } = useParams();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getLeaderboard(id)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [id]);

  return (
    <div>
      <Link to="/datasets" className="btn btn-link px-0">&larr; Back to datasets</Link>
      <h3 className="mb-3">Leaderboard</h3>
      {error && <div className="alert alert-danger">{error}</div>}

      {rows.length === 0 ? (
        <p className="text-muted">No submissions yet. Be the first!</p>
      ) : (
        <table className="table table-striped shadow-sm bg-white">
          <thead className="table-dark">
            <tr>
              <th>Rank</th>
              <th>Participant</th>
              <th>AUC</th>
              <th>Accuracy</th>
              <th>F1</th>
              <th>Submitted</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={row.id}>
                <td>
                  {index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : index + 1}
                </td>
                <td>{row.username}</td>
                <td className="fw-bold">{row.auc}</td>
                <td>{row.accuracy}</td>
                <td>{row.f1}</td>
                <td className="small text-muted">
                  {new Date(row.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
