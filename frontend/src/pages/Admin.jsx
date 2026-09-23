// Admin.jsx
// The admin dashboard. Admins can create a new dataset, release/unrelease
// datasets, and view all registered users.

import { useEffect, useState } from "react";
import { listDatasets, createDataset, toggleRelease, getUsers } from "../api";

export default function Admin() {
  const [datasets, setDatasets] = useState([]);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Form fields for creating a dataset.
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [mediaFile, setMediaFile] = useState(null);
  const [truthFile, setTruthFile] = useState(null);

  // Load datasets and users together.
  function refresh() {
    listDatasets().then(setDatasets).catch((err) => setError(err.message));
    getUsers().then(setUsers).catch((err) => setError(err.message));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!mediaFile || !truthFile) {
      setError("Please choose both a media file and a ground-truth CSV.");
      return;
    }
    try {
      await createDataset(name, description, mediaFile, truthFile);
      setMessage(`Dataset "${name}" created. It is hidden until you release it.`);
      setName("");
      setDescription("");
      setMediaFile(null);
      setTruthFile(null);
      event.target.reset();
      refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleToggle(datasetId) {
    setError("");
    try {
      await toggleRelease(datasetId);
      refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h3 className="mb-3">Admin Dashboard</h3>
      {error && <div className="alert alert-danger">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}

      <div className="row">
        {/* Create a dataset */}
        <div className="col-md-5">
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h5>Create a dataset</h5>
              <form onSubmit={handleCreate}>
                <div className="mb-2">
                  <label className="form-label">Name</label>
                  <input className="form-control" value={name}
                         onChange={(e) => setName(e.target.value)} required />
                </div>
                <div className="mb-2">
                  <label className="form-label">Description</label>
                  <textarea className="form-control" rows="2" value={description}
                            onChange={(e) => setDescription(e.target.value)} />
                </div>
                <div className="mb-2">
                  <label className="form-label">Media file (what participants download)</label>
                  <input type="file" className="form-control"
                         onChange={(e) => setMediaFile(e.target.files[0])} required />
                </div>
                <div className="mb-3">
                  <label className="form-label">Ground-truth CSV (filename,label)</label>
                  <input type="file" accept=".csv" className="form-control"
                         onChange={(e) => setTruthFile(e.target.files[0])} required />
                </div>
                <button className="btn btn-primary" type="submit">Create dataset</button>
              </form>
            </div>
          </div>
        </div>

        {/* Manage datasets */}
        <div className="col-md-7">
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h5>Manage datasets</h5>
              <table className="table table-sm align-middle">
                <thead>
                  <tr><th>Name</th><th>Files</th><th>Status</th><th>Action</th></tr>
                </thead>
                <tbody>
                  {datasets.map((d) => (
                    <tr key={d.id}>
                      <td>{d.name}</td>
                      <td>{d.num_files}</td>
                      <td>
                        {d.released
                          ? <span className="badge bg-success">Released</span>
                          : <span className="badge bg-secondary">Hidden</span>}
                      </td>
                      <td>
                        <button className="btn btn-sm btn-outline-primary"
                                onClick={() => handleToggle(d.id)}>
                          {d.released ? "Unrelease" : "Release"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Registered users */}
      <div className="card shadow-sm">
        <div className="card-body">
          <h5>Registered users</h5>
          <table className="table table-sm">
            <thead>
              <tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Joined</th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>
                    <span className={"badge " + (u.role === "admin" ? "bg-danger" : "bg-info")}>
                      {u.role}
                    </span>
                  </td>
                  <td className="small text-muted">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
