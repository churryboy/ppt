# 🚀 Quick Start Guide

Get your PowerPoint Search Platform running in 3 simple steps!

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- PowerPoint files (.pptx format)

## Installation & Setup

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/meteorresearch/vibe-coding/ppt
./start.sh
```

### Option 2: Manual Setup

```bash
# 1. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend
npm install
cd ..
```

## Running the Application

### Easy Way - Two Separate Terminals:

**Terminal 1 - Backend:**
```bash
./run_backend.sh
# Or: python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
# Or: cd frontend && npm start
```

### What to Expect:

1. **Backend** starts on `http://localhost:8000`
   - You'll see: "✅ Database initialized"
   - API docs available at: `http://localhost:8000/docs`

2. **Frontend** opens automatically at `http://localhost:3000`
   - Your browser should open automatically
   - If not, manually navigate to `http://localhost:3000`

## First Steps

1. **Upload a PowerPoint file**
   - Click the "📤 Upload" tab
   - Select or drag & drop a .pptx file
   - Wait a few seconds for processing

2. **View your presentations**
   - Click "📁 Presentations" to see all uploaded files
   - Click "View Slides" to see slide details

3. **Search your slides**
   - Click "🔍 Search"
   - Type any keyword
   - See all matching slides instantly

## Project Structure

```
ppt/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # API endpoints
│   ├── database.py         # SQLAlchemy models
│   └── ppt_parser.py       # PowerPoint parsing logic
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js          # Main application
│   │   └── App.css         # Styling
│   └── package.json
│
├── requirements.txt        # Python dependencies
├── README.md              # Full documentation
├── USAGE.md               # Detailed usage guide
├── run_backend.sh         # Backend startup script
└── run_frontend.sh        # Frontend startup script
```

## Features at a Glance

✅ Upload PowerPoint files (.pptx)  
✅ Automatic slide extraction  
✅ Text parsing from slides  
✅ Speaker notes extraction  
✅ Full-text search across all slides  
✅ Beautiful, responsive UI  
✅ RESTful API for integrations  
✅ SQLite database for metadata  

## Troubleshooting

### Backend won't start?
- Ensure Python 3.8+ is installed: `python3 --version`
- Check if port 8000 is available: `lsof -i :8000`
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start?
- Ensure Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Clear cache: `rm -rf node_modules && npm install`

### Can't upload files?
- Make sure both backend AND frontend are running
- Check browser console for errors (F12)
- Ensure file is .pptx format (not .ppt)

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Check [USAGE.md](USAGE.md) for API documentation
- Visit `http://localhost:8000/docs` for interactive API docs

## Support

Having issues? Here's what to check:

1. ✅ Both backend and frontend are running
2. ✅ No error messages in terminal
3. ✅ Browser console is clear (press F12)
4. ✅ File is valid .pptx format

---

**Happy Searching! 🔍✨**

