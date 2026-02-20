# Deployment Guide

Follow these steps to deploy your application to **Railway (Backend)** and **Vercel (Frontend)**.

---

## 1. Push Changes to GitHub

Ensure your latest changes are pushed to GitHub:

```bash
git add .
git commit -m "Prepared for deployment"
git push origin main
```

---

## 2. Deploy Backend (Railway)

1.  **Login to Railway**: Go to [railway.app](https://railway.app/) and login with GitHub.
2.  **New Project**: Click **New Project** -> **Deploy from GitHub repo**.
3.  **Select Repository**: Choose your repository (`ci-cd-detecting-agent`).
4.  **Configure Service**:
    *   Click on the newly created service card.
    *   Go to **Settings**.
    *   **Root Directory**: Set this to `backend` (Important!).
    *   **Build Command**: Railway should auto-detect from `requirements.txt`.
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (Auto-detected from `Procfile` if correct, else verify).
5.  **Environment Variables**:
    *   Go to **Variables**.
    *   Add `GOOGLE_API_KEY` with your API key.
6.  **Generate Domain**:
    *   Go to **Settings** -> **Networking**.
    *   Click **Generate Domain**.
    *   **Copy this URL** (e.g., `https://backend-production.up.railway.app`). You will need it for the frontend.

---

## 3. Deploy Frontend (Vercel)

1.  **Login to Vercel**: Go to [vercel.com](https://vercel.com/) and login with GitHub.
2.  **Add New Project**: Click **Add New...** -> **Project**.
3.  **Import Repository**: Find `ci-cd-detecting-agent` and click **Import**.
4.  **Configure Project**:
    *   **Root Directory**: Click `Edit` and select `frontend`.
    *   **Framework Preset**: Select **Vite**.
    *   **Build Command**: `npm run build` (Default).
    *   **Output Directory**: `dist` (Default).
5.  **Environment Variables**:
    *   Expand **Environment Variables**.
    *   Key: `VITE_API_URL`
    *   Value: Your Railway Backend URL (e.g., `https://backend-production.up.railway.app`). **Do not add a trailing slash.**
6.  **Deploy**: Click **Deploy**.

---

## 4. Verification

1.  Open your Vercel URL (e.g., `https://ci-cd-detecting-agent.vercel.app`).
2.  The app should load.
3.  Enter a repo URL and click **Run Agent**.
4.  If it works, the frontend is successfully talking to the backend!

---

## Troubleshooting

-   **Backend 404/Connection Refused**: Check Railway logs. Ensure the Root Directory is `backend`.
-   **Frontend "Failed to fetch"**: Check the `VITE_API_URL` in Vercel settings. It must match your Railway URL exactly (missing `https://` is a common error).
