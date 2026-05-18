// Purpose: Live health metrics panel exposing Synapse version, rooms, and MAU estimate (FR-ADMIN-04, NFR-MON-01)
import { useEffect, useState } from "react";
import { getRoomList, getServerVersion, getUsers } from "../api/synapseClient";

export default function ServerHealth() {
  const [state, setState] = useState({
    loading: true,
    error: "",
    version: "-",
    roomCount: 0,
    mau: 0
  });

  useEffect(() => {
    const refresh = async () => {
      try {
        const [versionData, rooms, users] = await Promise.all([
          getServerVersion(),
          getRoomList(),
          getUsers()
        ]);

        setState({
          loading: false,
          error: "",
          version: versionData.server_version || versionData.version || "unknown",
          roomCount: Array.isArray(rooms) ? rooms.length : 0,
          mau: Array.isArray(users) ? users.filter((user) => !user.deactivated).length : 0
        });
      } catch (fetchError) {
        setState((previous) => ({
          ...previous,
          loading: false,
          error: fetchError?.response?.data?.error || fetchError.message || "Failed to load health data"
        }));
      }
    };

    refresh();
  }, []);

  if (state.loading) {
    return <p>Loading server metrics…</p>;
  }

  if (state.error) {
    return <p style={{ color: "#991b1b" }}>{state.error}</p>;
  }

  return (
    <section>
      <h3>Server health</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(140px, 1fr))", gap: "1rem" }}>
        <article style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem" }}>
          <strong>Version</strong>
          <p>{state.version}</p>
        </article>
        <article style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem" }}>
          <strong>Room count</strong>
          <p>{state.roomCount}</p>
        </article>
        <article style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem" }}>
          <strong>MAU (estimated)</strong>
          <p>{state.mau}</p>
        </article>
      </div>
    </section>
  );
}
