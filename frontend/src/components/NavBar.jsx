// NavBar.jsx
// The top navigation bar. Shows the Morgan State logo and links that change
// depending on whether someone is logged in and whether they are an admin.

import { Link, useNavigate } from "react-router-dom";
import { isLoggedIn, isAdmin, getUser, logout } from "../auth";

export default function NavBar() {
  const navigate = useNavigate();
  const user = getUser();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: "#0a2240" }}>
      <div className="container">
        {/* Morgan State University logo (from frontend/public/morgan-logo.png). */}
        <Link className="navbar-brand d-flex align-items-center" to="/datasets">
          <img
            src="/morgan-logo.png"
            alt="Morgan State University"
            height="40"
            className="bg-white rounded px-2 py-1 me-2"
          />
          <span className="fw-semibold">Deepfake Detection Challenge</span>
        </Link>

        <div className="navbar-nav ms-auto align-items-lg-center">
          {isLoggedIn() ? (
            <>
              <Link className="nav-link" to="/datasets">Datasets</Link>
              {isAdmin() && <Link className="nav-link" to="/admin">Admin</Link>}
              <span className="navbar-text text-warning mx-2">
                {user.username} ({user.role})
              </span>
              <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link className="nav-link" to="/login">Login</Link>
              <Link className="nav-link" to="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
