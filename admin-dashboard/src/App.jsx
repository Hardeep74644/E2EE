// Purpose: Route-level composition of login flow and protected admin dashboard (FR-ADMIN-01, FR-RBAC-01)
import { useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import AdminGuard from "./auth/adminGuard";
import Dashboard from "./components/Dashboard";

function LoginPage() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("admin_token") ?? "");

  const submit = (event) => {
    event.preventDefault();
    if (!token.trim()) {
      return;
    }
    localStorage.setItem("admin_token", token.trim());
    navigate("/");
  };

  return (
    <main style={{ maxWidth: 480, margin: "3rem auto", fontFamily: "sans-serif" }}>
      <h1>Admin Login</h1>
      <p>Paste a Synapse admin access token to access protected routes.</p>
      <form onSubmit={submit}>
        <label htmlFor="token">Admin token</label>
        <textarea
          id="token"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          rows={4}
          style={{ width: "100%", marginTop: "0.5rem" }}
        />
        <button type="submit" style={{ marginTop: "1rem" }}>
          Continue
        </button>
      </form>
    </main>
  );
}

function RequireLogin({ children }) {
  const location = useLocation();
  const token = localStorage.getItem("admin_token");
  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireLogin>
            <AdminGuard>
              <Dashboard />
            </AdminGuard>
          </RequireLogin>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
