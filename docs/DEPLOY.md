# Deploy KASLU LAB (public)

This app is **Streamlit** (long-running Python + WebSockets). **Vercel serverless cannot host the app itself** — only a landing page, redirect, or custom DNS.

## Recommended: public app URL

### Option A — Streamlit Community Cloud (free, public)

1. Push this repo to **GitHub** (public or private).
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. **Main file path:** `streamlit_app.py` (recommended on Cloud) or `app/Home.py` for local-style entry.
   - Cloud uses root `pages/*.py` shims → real code in `app/pages/`. After adding pages, run `python scripts/sync_root_pages.py`.
4. Add secrets from `.env.example` in the Cloud **Secrets** UI (optional AI keys).
5. You get a public URL like `https://your-app.streamlit.app`.

### Option B — Render (Docker, free tier)

1. Push to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → **New → Blueprint** (uses `render.yaml`) or **Web Service → Docker**.
3. Public URL like `https://kaslu-lab.onrender.com`.

**Note:** SQLite (`anammox.db`) on free tiers may reset on redeploy — fine for demos; use managed DB for production.

## Vercel (landing page — live)

Static landing (not the Streamlit app):

- **https://kaslu-lab.vercel.app** (project `kaslu-lab`)
- **https://vercel-site-six-rho.vercel.app** (project `vercel-site`)

Deploy updates from `vercel-site/`:

```bash
cd vercel-site && npx vercel deploy --prod
```

**Custom domain:** Vercel dashboard → project **vercel-site** → **Domains** → add/buy a domain. Point the app itself to Render/Streamlit, then link from the landing page (`?app=https://your-streamlit-url`).

Do **not** expect the root repo `vercel deploy` to run Streamlit — Vercel is serverless; use Render or Streamlit Cloud for the full app.

## GitHub

Repo (create/push if needed): `https://github.com/Huseynitsu/kaslu-lab` — push from your machine if the remote push failed:

```powershell
cd C:\Users\Huseyn\Desktop\my-first-project
git push -u origin main
```

## Local

```powershell
.\scripts\run-app.ps1
```
