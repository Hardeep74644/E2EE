// Purpose: Main admin dashboard layout with sidebar navigation and content panes (FR-ADMIN-01, NFR-UI-01)
import { useMemo, useState } from "react";
import AuditLog from "./AuditLog";
import ServerHealth from "./ServerHealth";
import UserTable from "./UserTable";

const tabs = [
  { id: "health", label: "Server Health" },
  { id: "users", label: "Users" },
  { id: "audit", label: "Audit Log" }
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("health");

  const content = useMemo(() => {
    if (activeTab === "users") {
      return <UserTable />;
    }
    if (activeTab === "audit") {
      return <AuditLog />;
    }
    return <ServerHealth />;
  }, [activeTab]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", minHeight: "100vh", fontFamily: "sans-serif" }}>
      <aside style={{ background: "#0f172a", color: "#fff", padding: "1rem" }}>
        <h2 style={{ marginTop: 0 }}>Admin Panel</h2>
        <nav>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                marginBottom: "0.5rem",
                padding: "0.5rem",
                borderRadius: "6px",
                border: 0,
                background: activeTab === tab.id ? "#1d4ed8" : "#334155",
                color: "#fff"
              }}
            >
              {tab.label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => {
              localStorage.clear();
              window.location.assign("/login");
            }}
            style={{ marginTop: "1rem", width: "100%", padding: "0.5rem" }}
          >
            Logout
          </button>
        </nav>
      </aside>
      <main style={{ padding: "1rem" }}>
        {content}
      </main>
    </div>
  );
}
