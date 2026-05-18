// Purpose: User administration table with suspend/unsuspend controls and guardrails (FR-ADMIN-02, FR-RBAC-01)
import { useEffect, useState } from "react";
import { getUsers, suspendUser, unsuspendUser } from "../api/synapseClient";

function Badge({ value, truthyLabel, falsyLabel }) {
  const isTruthy = Boolean(value);
  return (
    <span
      style={{
        padding: "0.2rem 0.5rem",
        borderRadius: "999px",
        background: isTruthy ? "#dcfce7" : "#fee2e2",
        color: isTruthy ? "#166534" : "#991b1b",
        fontSize: "0.8rem"
      }}
    >
      {isTruthy ? truthyLabel : falsyLabel}
    </span>
  );
}

export default function UserTable() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyUser, setBusyUser] = useState("");

  const loadUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (fetchError) {
      setError(fetchError?.response?.data?.error || fetchError.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const mutateUser = async (userId, deactivate) => {
    const action = deactivate ? "suspend" : "unsuspend";
    const confirmed = window.confirm(`Are you sure you want to ${action} ${userId}?`);
    if (!confirmed) {
      return;
    }

    setBusyUser(userId);
    try {
      if (deactivate) {
        await suspendUser(userId);
      } else {
        await unsuspendUser(userId);
      }
      await loadUsers();
    } catch (mutationError) {
      setError(mutationError?.response?.data?.error || mutationError.message || `Unable to ${action} user`);
    } finally {
      setBusyUser("");
    }
  };

  if (loading) {
    return <p>Loading users…</p>;
  }

  if (error) {
    return (
      <div>
        <p style={{ color: "#991b1b" }}>{error}</p>
        <button type="button" onClick={loadUsers}>Retry</button>
      </div>
    );
  }

  return (
    <section>
      <h3>User administration</h3>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th align="left">user_id</th>
              <th align="left">display_name</th>
              <th align="left">admin</th>
              <th align="left">creation_ts</th>
              <th align="left">last_seen_ip</th>
              <th align="left">deactivated</th>
              <th align="left">actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const userId = user.name || user.user_id;
              return (
                <tr key={userId}>
                  <td>{userId}</td>
                  <td>{user.displayname || "-"}</td>
                  <td><Badge value={user.admin} truthyLabel="admin" falsyLabel="user" /></td>
                  <td>{user.creation_ts ? new Date(user.creation_ts).toLocaleString() : "-"}</td>
                  <td>{user.last_seen_ip || "-"}</td>
                  <td><Badge value={user.deactivated} truthyLabel="deactivated" falsyLabel="active" /></td>
                  <td>
                    {user.deactivated ? (
                      <button type="button" disabled={busyUser === userId} onClick={() => mutateUser(userId, false)}>
                        Unsuspend
                      </button>
                    ) : (
                      <button type="button" disabled={busyUser === userId} onClick={() => mutateUser(userId, true)}>
                        Suspend
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
