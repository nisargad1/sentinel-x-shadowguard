# SENTINEL-X ShadowGuard — Cloud Deployment & Demo Persistence Guide

This guide ensures your hackathon demo **never expires** and can be accessed 24/7 by judges.

---

## Option 1: Free 24/7 Permanent Cloud Deployment (Recommended)

To give judges a permanent URL that stays online even when your laptop is turned off:

### Deploy to Render.com (100% Free)
1. Sign up or log into [https://render.com](https://render.com) using your GitHub account (`nisargad1`).
2. Click **New +** -> **Web Service**.
3. Select your repository: `nisargad1/sentinel-x-shadowguard`.
4. Render will automatically detect the **Dockerfile** or `render.yaml`.
5. Set:
   - **Environment:** Docker
   - **Plan:** Free
   - **Region:** Any (e.g. Oregon or Frankfurt)
6. Click **Deploy Web Service**.
7. In ~3 minutes, Render builds the React frontend + Python FastAPI backend and gives you a permanent URL:
   `https://sentinel-x-shadowguard.onrender.com`

---

## Option 2: 1-Click Hackathon Day Demo Launcher (`START_DEMO.bat`)

If you are presenting from your laptop tomorrow:

1. Open the project folder: `sentinel-x-shadowguard`.
2. Double-click **`START_DEMO.bat`**.
3. It will automatically:
   - Start the FastAPI backend on `http://localhost:8000`.
   - Start a Cloudflare tunnel and output the fresh public HTTPS link.
   - Automatically open your browser to the live dashboard.

---

## Option 3: Localhost (100% Fail-Proof for Screen-Sharing)

When presenting your screen on Google Meet, Zoom, or on the stage projector:
- **Always open `http://localhost:8000`** in your browser.
- **Why?**
  - Instant response times (< 1.5ms per scenario).
  - Works even if the venue Wi-Fi drops completely.
  - Zero risk of DNS expiration or tunnel drops.
