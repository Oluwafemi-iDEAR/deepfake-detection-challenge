// App.jsx
// Sets up the pages (routes) and protects the ones that need a login.

import { Routes, Route, Navigate } from "react-router-dom";
import { isLoggedIn, isAdmin } from "./auth";
import NavBar from "./components/NavBar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Datasets from "./pages/Datasets";
import DatasetDetail from "./pages/DatasetDetail";
import Leaderboard from "./pages/Leaderboard";
import Admin from "./pages/Admin";

// Wrap a page so it redirects to /login when nobody is logged in.
function Protected({ children }) {
  return isLoggedIn() ? children : <Navigate to="/login" replace />;
}

// Wrap a page so only admins can open it.
function AdminOnly({ children }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return isAdmin() ? children : <Navigate to="/datasets" replace />;
}

export default function App() {
  return (
    <>
      <NavBar />
      <div className="container my-4">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/datasets" element={<Protected><Datasets /></Protected>} />
          <Route path="/datasets/:id" element={<Protected><DatasetDetail /></Protected>} />
          <Route path="/datasets/:id/leaderboard" element={<Protected><Leaderboard /></Protected>} />
          <Route path="/admin" element={<AdminOnly><Admin /></AdminOnly>} />
          {/* Anything else goes to the datasets page (or login if needed). */}
          <Route path="*" element={<Navigate to="/datasets" replace />} />
        </Routes>
      </div>
    </>
  );
}
