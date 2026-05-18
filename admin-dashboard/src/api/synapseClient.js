// Purpose: Axios client and admin endpoint helpers for Synapse admin APIs (FR-ADMIN-01, FR-RBAC-01)
import axios from "axios";

const synapseClient = axios.create({
  baseURL: import.meta.env.VITE_SYNAPSE_URL || "http://localhost:8008"
});

synapseClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

synapseClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.assign("/login");
    }
    return Promise.reject(error);
  }
);

export async function getUsers() {
  const { data } = await synapseClient.get("/_synapse/admin/v2/users", {
    params: { limit: 50 }
  });
  return data.users ?? [];
}

export async function suspendUser(userId) {
  const { data } = await synapseClient.post(`/_synapse/admin/v1/deactivate/${encodeURIComponent(userId)}`, {
    erase: false
  });
  return data;
}

export async function unsuspendUser(userId) {
  const { data } = await synapseClient.put(`/_synapse/admin/v2/users/${encodeURIComponent(userId)}`, {
    deactivated: false
  });
  return data;
}

export async function getServerVersion() {
  const { data } = await synapseClient.get("/_synapse/admin/v1/server_version");
  return data;
}

export async function getRoomList() {
  const { data } = await synapseClient.get("/_synapse/admin/v1/rooms", {
    params: { limit: 100 }
  });
  return data.rooms ?? [];
}

export async function getAuditLog() {
  const { data } = await synapseClient.get("/_synapse/admin/v1/audit", {
    params: { limit: 100 }
  });
  return data.audit_events ?? data.events ?? [];
}
