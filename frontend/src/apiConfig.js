/**
 * Centralized API configuration for MedSafe frontend
 */

// In Vite, environment variables starting with VITE_ are available via import.meta.env
// These are injected at BUILD TIME.
const envUrl = import.meta.env.VITE_API_BASE_URL;
const isProduction = window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1";

// Hardcoded production URL as a final fallback for your Render backend
const PRODUCTION_URL = "https://medsafe-vmwu.onrender.com";

export const API_BASE = envUrl || (isProduction ? PRODUCTION_URL : "http://localhost:8000");

console.log("MedSafe API Base URL Configuration:");
console.log("- Value from Environment:", import.meta.env.VITE_API_BASE_URL);
console.log("- Resolved API_BASE:", API_BASE);
console.log("- Current Hostname:", window.location.hostname);

if (API_BASE.includes("localhost") && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
  console.warn(
    "🚨 CRITICAL DEPLOYMENT ISSUE: Your frontend is calling LOCALHOST instead of your Render backend! " +
    "Check your Vercel/Render Environment Variables Settings for 'VITE_API_BASE_URL'."
  );
}

export const API_ROUTES = {
  UPLOAD: `${API_BASE}/api/upload/reports`,
  SUMMARIZE: (id) => `${API_BASE}/api/summarize/report/${id}/all`,
  SUMMARIZE_TYPE: (id, type) => `${API_BASE}/api/summarize/report/${id}?summary_type=${type}`,
  CHAT: `${API_BASE}/api/chat/qa`,
};
