// Purpose: Admin audit event viewer with text filtering for review workflows (FR-ADMIN-03, NFR-TRACE-01)
import { useEffect, useMemo, useState } from "react";
import { getAuditLog } from "../api/synapseClient";

export default function AuditLog() {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const payload = await getAuditLog();
        setEvents(payload);
      } catch (fetchError) {
        setError(fetchError?.response?.data?.error || fetchError.message || "Failed to load audit log");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const filteredEvents = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) {
      return events;
    }
    return events.filter((event) => JSON.stringify(event).toLowerCase().includes(query));
  }, [events, filter]);

  if (loading) {
    return <p>Loading audit log…</p>;
  }

  if (error) {
    return <p style={{ color: "#991b1b" }}>{error}</p>;
  }

  return (
    <section>
      <h3>Audit log</h3>
      <input
        value={filter}
        onChange={(event) => setFilter(event.target.value)}
        placeholder="Filter by actor, action, or room"
        style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
      />
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "0.5rem" }}>
        {filteredEvents.map((event, index) => (
          <li key={`${event.id || event.event_id || index}`} style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "0.75rem" }}>
            <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(event, null, 2)}</pre>
          </li>
        ))}
      </ul>
      {!filteredEvents.length && <p>No audit records matched the current filter.</p>}
    </section>
  );
}
