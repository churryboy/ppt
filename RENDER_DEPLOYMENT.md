# Deploy to Render

This guide explains how to deploy your "보고서 저장소" (Report Repository) application to Render.

## Option 1: Single Web Service (Recommended for Production)

This deploys both backend and frontend as a single service, with the backend serving the React frontend.

### Step 1: Update Backend to Serve Frontend

The backend is already configured to serve static files. Just build the frontend and deploy together.

### Step 2: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `https://github.com/churryboy/ppt`
4. Configure the service:

**Basic Settings:**
- **Name**: `ppt-report-repository` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave blank (uses repo root)
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**:
```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
```

- **Start Command**:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables** (Add these):
- `PYTHON_VERSION`: `3.11.0` (or your preferred version)
- `SECRET_KEY`: Generate a secure random string (e.g., use `openssl rand -hex 32`)

### Step 3: Update Backend to Serve Frontend (Required Update)

Add this to your `backend/main.py` to serve the React build:

```python
# Add this near the end of main.py, before if __name__ == "__main__":
from pathlib import Path
FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "build"

if FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD), html=True), name="frontend")
```

### Step 4: Update Frontend API URL

Update `frontend/src/App.js` to use relative URLs (it already does this, so no changes needed).

### Step 5: Deploy

Click "Create Web Service" and wait for deployment to complete (usually 3-5 minutes).

---

## Option 2: Separate Backend and Frontend (Alternative)

Deploy backend and frontend as two separate services.

### Backend Web Service

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `PYTHON_VERSION`: `3.11.0`
- `SECRET_KEY`: (random secure string)

### Frontend Static Site

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Publish Directory:**
```
frontend/build
```

**Environment Variables:**
- `REACT_APP_API_URL`: `https://your-backend-url.onrender.com`

Then update `frontend/src/App.js` to use `process.env.REACT_APP_API_URL` instead of `http://localhost:8000`.

---

## Important Notes

### 1. Database Persistence

By default, SQLite database files are NOT persistent on Render's free tier. For production:

**Option A: Use Render Disk (Paid add-on)**
- Add a persistent disk in Render dashboard
- Mount point: `/data`
- Update database path in code

**Option B: Use PostgreSQL (Recommended for Production)**
- Add PostgreSQL database in Render dashboard (free tier available)
- Install `psycopg2-binary` in requirements.txt
- Update `DATABASE_URL` in environment variables

### 2. File Storage

Uploaded files and generated images are also not persistent. For production:

**Option A: Use Render Disk**
- Mount persistent disk
- Store uploads/slides/archives in mounted directory

**Option B: Use Cloud Storage (Recommended)**
- Use AWS S3, Google Cloud Storage, or similar
- Update file upload/retrieval logic

### 3. Session Management

Current session storage is in-memory and will reset on deploy. For production:
- Use Redis for session storage
- Or use JWT tokens instead of sessions

### 4. Dependencies

Make sure these system dependencies are available (Render installs automatically):
- LibreOffice (for PPTX to PDF conversion)
- Poppler (for PDF to PNG conversion)

Add this to your `render.yaml` if needed:
```yaml
services:
  - type: web
    name: ppt-report
    env: python
    buildCommand: |
      apt-get update
      apt-get install -y libreoffice poppler-utils
      pip install -r requirements.txt
      cd frontend && npm install && npm run build
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

## Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Create Web Service on Render
- [ ] Set environment variables (SECRET_KEY)
- [ ] Configure build and start commands
- [ ] Wait for deployment
- [ ] Test login/registration
- [ ] Test file upload
- [ ] Test search functionality
- [ ] Test archive features

---

## Troubleshooting

**Build fails with "LibreOffice not found":**
- Add system dependencies to render.yaml

**Database resets after deploy:**
- Add persistent disk or use PostgreSQL

**CORS errors:**
- Update CORS settings in backend/main.py to include your Render domain

**Upload files disappear:**
- Add persistent disk or use cloud storage

**500 errors on upload:**
- Check Render logs for detailed error messages
- Verify LibreOffice and Poppler are installed

