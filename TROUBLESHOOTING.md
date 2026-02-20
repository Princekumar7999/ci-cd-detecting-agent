# Railway Troubleshooting Guide

## 🚨 Crash Solution (Runtime)
If you see `ModuleNotFoundError: No module named 'langchain.prompts'`, I have already fixed this in the code. **Just redeploy.**

## 🏗️ Build Failure: "COPY requirements.txt . not found"
If you see this error, Railway is looking at the wrong Dockerfile.

### The Fix:
1.  Go to **Service Settings** -> **Build**.
2.  **Dockerfile Path**: Change this to `Dockerfile`.
    *   **INCORRECT**: `backend/Dockerfile`
    *   **CORRECT**: `Dockerfile` (or just leave it empty if it defaults to root)
3.  **Root Directory**: Should be `/` (or empty), NOT `backend`.

**Why?**
I created a special `Dockerfile` in the *root* of your repo that handles everything correctly. You must tell Railway to use *that* one, not the one inside the backend folder.

## 🔄 Infinite Restart Loop?
1.  **Clear Start Command**: Go to **Service Settings** -> **Deploy** -> **Start Command** and delete everything.
