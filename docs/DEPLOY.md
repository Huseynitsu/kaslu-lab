# Deploy KASLU LAB (public)

This app is **Streamlit** (long-running Python + WebSockets). **Vercel serverless cannot host the app itself** — only a landing page, redirect, or custom DNS.

## Recommended: public app URL

### Option A — Streamlit Community Cloud (free, public)

1. Push this repo to **GitHub** (public or private).
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. **Main file path:** `app/Home.py`
4. Add secrets from `.env.example` in the Cloud **Secrets** UI (optional AI keys).
5. You get a public URL like `https://your-app.streamlit.app`.

### Option B — Render (Docker, free tier)

1. Push to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → **New → Blueprint** (uses `render.yaml`) or **Web Service → Docker**.
3. Public URL like `https://kaslu-lab.onrender.com`.

**Note:** SQLite (`anammox.db`) on free tiers may reset on redeploy — fine for demos; use managed DB for production.

## Vercel (domain / landing only)

Use Vercel when you want:

- A **`*.vercel.app`** landing that links to Streamlit/Render, or
- **DNS** for a domain you bought on Vercel, pointing to Streamlit/Render (see Streamlit custom domain docs).

Do **not** expect `vercel deploy` to run Streamlit without a separate container host.

## Local

```powershell
.\scripts\run-app.ps1
```
