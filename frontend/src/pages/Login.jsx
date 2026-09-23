// Login.jsx
// The login form. On success it saves the token and goes to the datasets page.

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api";
import { saveLogin } from "../auth";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser from reloading the page
    setError("");
    try {
      const data = await login(username, password);
      saveLogin(data.token, data.user);
      navigate("/datasets");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-5">
        <div className="card shadow-sm">
          <div className="card-body">
            <div className="text-center mb-3">
              <img src="/morgan-logo.png" alt="Morgan State University" height="50" />
            </div>
            <h4 className="card-title text-center mb-3">Sign in</h4>

            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Username</label>
                <input
                  className="form-control"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <button className="btn btn-primary w-100" type="submit">
                Log in
              </button>
            </form>

            <p className="text-center mt-3 mb-0">
              No account? <Link to="/register">Register here</Link>
            </p>
          </div>
        </div>
        <p className="text-center text-muted mt-3 small">
          Demo accounts: admin / admin123 &nbsp;•&nbsp; student / student123
        </p>
      </div>
    </div>
  );
}
