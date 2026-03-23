# Deployment Guide for MedSafe

To ensure your frontend correctly communicates with your backend in a deployed environment, follow these steps:

## 1. Frontend Configuration (Vercel/Netlify)

When deploying your React/Vite frontend, you MUST set the following Environment Variable in your deployment settings:

- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://your-backend-api-url.com` (No trailing slash)

### Why?
Vite uses `import.meta.env.VITE_API_BASE_URL` at build time. If not set, it defaults to `http://localhost:8000`.

---

## 2. Backend Configuration (Render/Railway/Heroku)

In your backend deployment settings, set these Environment Variables:

- **Key**: `FRONTEND_URL`
- **Value**: `https://your-frontend-domain.vercel.app` (The URL where your React app is hosted)
- **Key**: `GEMINI_API_KEY`
- **Value**: `your_api_key_here`

### Why?
The backend needs to know your frontend URL to allow cross-origin requests (CORS). Without this, the browser will block requests even if the URL is correct.

---

## 3. Database Note
Since the project uses SQLite (`medsummarize.db`), any data uploaded to a service like Render will be lost whenever the server restarts (ephemeral storage). 
- **Tip**: For persistent data, consider switching to PostgreSQL or using a persistent disk volume if your provider supports it.
