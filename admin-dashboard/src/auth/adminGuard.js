// Purpose: Enforce admin token validation before protected routes render (FR-RBAC-01, NFR-SEC-01)
import { createElement, useEffect, useState } from "react";

const synapseUrl = import.meta.env.VITE_SYNAPSE_URL || "http://localhost:8008";

export default function AdminGuard({ children }) {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      window.location.assign("/login");
      return;
    }

    const verifyAdmin = async () => {
      try {
        const response = await fetch(`${synapseUrl}/_synapse/admin/v1/server_version`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (response.status === 200) {
          setStatus("ok");
          return;
        }

        if (response.status === 401 || response.status === 403) {
          localStorage.clear();
          window.location.assign("/login");
          return;
        }

        setStatus("error");
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error("Admin token validation failed", error);
        }
        setStatus("error");
      }
    };

    verifyAdmin();
  }, []);

  if (status === "checking") {
    return createElement(
      "p",
      { style: { fontFamily: "sans-serif", padding: "1rem" } },
      "Validating admin session…"
    );
  }

  if (status === "error") {
    return createElement(
      "p",
      { style: { fontFamily: "sans-serif", padding: "1rem" } },
      "Unable to validate admin token."
    );
  }

  return children;
}
