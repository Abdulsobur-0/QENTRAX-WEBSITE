# Qentrax Africa — Dynamic Website

## Project Structure
```
qentrax/
├── app.py              ← Flask backend (API + database)
├── index.html          ← Frontend (served by Flask)
├── requirements.txt    ← Python packages
├── start.py            ← Easy start script
├── Procfile            ← For Railway/Render deployment
├── qentrax.db          ← SQLite database (auto-created)
└── static/
    └── uploads/        ← Uploaded photos stored here
        └── logo.jpg    ← Put your logo here
```

## Quick Start (Local)

1. Put your logo file as `static/logo.jpg`
2. Run:
```bash
pip install -r requirements.txt
python app.py
```
3. Open http://localhost:5000
4. Admin: go to Admin Panel, password = `qentrax2025`

---

## Deploy to Railway (FREE — recommended)

Railway gives you a live URL like `qentrax.up.railway.app` that works on any device.

1. Go to https://railway.app → Sign up free
2. Click "New Project" → "Deploy from GitHub repo"
3. Push this folder to a GitHub repo first:
   ```bash
   git init
   git add .
   git commit -m "Qentrax Africa website"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/qentrax.git
   git push -u origin main
   ```
4. Railway auto-detects Python and deploys
5. Set environment variable: `SECRET_KEY` = any random string
6. Your site is live! Upload a photo from your phone → it instantly shows on laptop too.

---

## Deploy to Render (FREE)

1. Go to https://render.com → New Web Service
2. Connect your GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Done

---

## How Photo Upload Works

When you upload a photo in Admin Panel:
1. Photo is cropped in browser
2. Sent via POST to `/api/about/photo`
3. Saved as a file in `static/uploads/` on the server
4. URL stored in the database as `/static/uploads/filename.jpg`
5. Every device loads the photo from that URL → works everywhere instantly

## Admin Password
Default: `qentrax2025`
To change: edit `ADMIN_PASS` in `app.py` line 13

## API Endpoints
- GET  /api/ads          → list all ad slides
- POST /api/ads          → create ad (admin)
- PUT  /api/ads/:id      → update ad (admin)
- DELETE /api/ads/:id    → delete ad (admin)
- GET  /api/news         → list all news
- GET  /api/sectors      → list all sectors
- GET  /api/about        → get about info
- PUT  /api/about        → update about text (admin)
- POST /api/about/photo  → upload profile photo (admin)
- GET  /api/stats        → get stats + insights
- PUT  /api/stats        → update stats (admin)
