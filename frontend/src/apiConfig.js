/**
 * Centralized API configuration for MedSafe frontend
 */

// In Vite, environment variables starting with VITE_ are available via import.meta.env
// These are injected at BUILD TIME.
export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

console.log("MedSafe API Base URL:", API_BASE);

if (API_BASE.includes("localhost") && window.location.hostname !== "localhost") {
  console.warn(
    "⚠️ WARNING: Frontend is deployed but calling LOCALHOST! " +
    "Make sure to set VITE_API_BASE_URL in your deployment environment variables (Vercel/Render)."
  );
}

export const API_ROUTES = {
  UPLOAD: `${API_BASE}/api/upload/reports`,
  SUMMARIZE: (id) => `${API_BASE}/api/summarize/report/${id}/all`,
  SUMMARIZE_TYPE: (id, type) => `${API_BASE}/api/summarize/report/${id}?summary_type=${type}`,
  CHAT: `${API_BASE}/api/chat/qa`,
};
