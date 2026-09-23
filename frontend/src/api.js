// api.js
// One small place that talks to the backend. Every function returns the parsed
// JSON, or throws an Error whose message is the backend's error text so pages
// can show it to the user.

import { getToken } from "./auth";

// Where the backend lives. In local development this is empty, so calls go to
// "/api/..." and Vite's proxy forwards them to http://localhost:5001.
// In production we set VITE_API_URL (in Vercel) to the deployed backend URL.
export const API_BASE = import.meta.env.VITE_API_URL || "";

// Build the headers, adding the login token when we have one.
function authHeaders(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  return headers;
}

// Handle the response: return JSON on success, throw the error message on failure.
async function handle(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }
  return data;
}

// ---- JSON requests ----
export async function postJson(url, body) {
  const response = await fetch(API_BASE + url, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  return handle(response);
}

export async function getJson(url) {
  const response = await fetch(API_BASE + url, { headers: authHeaders() });
  return handle(response);
}

// ---- File upload (multipart form) ----
export async function postForm(url, formData) {
  const response = await fetch(API_BASE + url, {
    method: "POST",
    headers: authHeaders(), // no Content-Type: the browser sets it for form data
    body: formData,
  });
  return handle(response);
}

// ---- Named calls used across the app ----
export const register = (username, email, password) =>
  postJson("/api/register", { username, email, password });

export const login = (username, password) =>
  postJson("/api/login", { username, password });

export const listDatasets = () => getJson("/api/datasets");
export const getLeaderboard = (id) => getJson(`/api/datasets/${id}/leaderboard`);
export const getMySubmissions = () => getJson("/api/my-submissions");
export const getUsers = () => getJson("/api/admin/users");

export const submitPredictions = (datasetId, file) => {
  const form = new FormData();
  form.append("submission", file);
  return postForm(`/api/datasets/${datasetId}/submit`, form);
};

export const createDataset = (name, description, mediaFile, truthFile) => {
  const form = new FormData();
  form.append("name", name);
  form.append("description", description);
  form.append("media", mediaFile);
  form.append("ground_truth", truthFile);
  return postForm("/api/datasets", form);
};

export const toggleRelease = (datasetId) =>
  postForm(`/api/admin/datasets/${datasetId}/release`, new FormData());
