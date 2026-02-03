# PowerPoint Search Platform

A modern, full-stack web application for uploading PowerPoint presentations, automatically extracting slides, and making them fully searchable with a beautiful UI.

![Status](https://img.shields.io/badge/status-ready-brightgreen) ![Python](https://img.shields.io/badge/python-3.8+-blue) ![React](https://img.shields.io/badge/react-18.2-blue)

## 🌟 Features

### Core Functionality
- 📤 **Upload PowerPoint Files** - Drag & drop or click to upload .pptx files
- 📊 **Automatic Parsing** - Extracts all slides, text, and speaker notes automatically
- 🔍 **Full-Text Search** - Search across all slides by title, content, or notes
- 👁️ **Slide Viewer** - Browse all slides with formatted text display
- 💾 **Persistent Storage** - SQLite database for metadata, files stored locally
- 🗑️ **Easy Management** - Delete presentations and all associated data with one click

### User Experience
- 🎨 Beautiful, modern gradient UI
- 📱 Fully responsive design (works on mobile, tablet, desktop)
- ⚡ Fast, real-time search results
- 🎯 Intuitive tab-based navigation
- ✨ Smooth animations and transitions
- 📝 Clear feedback messages

## 🚀 Quick Start

**Fastest way to get started:**

```bash
cd /Users/meteorresearch/vibe-coding/ppt
./start.sh          # Install all dependencies
./run_backend.sh    # Terminal 1: Start backend
./run_frontend.sh   # Terminal 2: Start frontend
```

Then open `http://localhost:3000` in your browser!

📖 **See [QUICKSTART.md](QUICKSTART.md) for detailed instructions**

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Modern Python web framework)
- python-pptx (PowerPoint file parsing)
- SQLAlchemy (Database ORM)
- SQLite (Lightweight database)
- Uvicorn (ASGI server)

**Frontend:**
- React 18 (UI library)
- Axios (HTTP client)
- Modern CSS with gradients and animations
- Responsive design principles

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- pip (Python package manager)
- npm (Node package manager)

### Automated Setup
```bash
./start.sh
```

### Manual Setup
```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 🎯 Running the Application

### Simple Method

**Terminal 1 - Backend:**
```bash
./run_backend.sh
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
# Frontend opens at http://localhost:3000
```

### Manual Method

**Terminal 1 - Backend:**
```bash
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in minutes
- **[USAGE.md](USAGE.md)** - Detailed usage guide and API documentation
- **README.md** (this file) - Project overview and architecture

## 🔌 API Endpoints

The backend provides a RESTful API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload a PowerPoint file |
| GET | `/api/presentations` | List all presentations |
| GET | `/api/presentations/{id}` | Get presentation with all slides |
| GET | `/api/search?q=query` | Search slides by text |
| DELETE | `/api/presentations/{id}` | Delete a presentation |
| GET | `/docs` | Interactive API documentation |

📚 **See [USAGE.md](USAGE.md) for detailed API documentation with examples**

## 📁 Project Structure

```
ppt/
├── backend/                      # Python backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI app & routes
│   ├── database.py               # SQLAlchemy models
│   └── ppt_parser.py             # PowerPoint parsing
│
├── frontend/                     # React frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js                # Main application
│   │   ├── App.css               # Styles
│   │   ├── index.js              # Entry point
│   │   └── index.css             # Global styles
│   └── package.json
│
├── uploads/                      # Uploaded PPT files (created at runtime)
├── slides/                       # Extracted slide data (created at runtime)
├── ppt_search.db                 # SQLite database (created at runtime)
│
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── QUICKSTART.md                 # Quick start guide
├── USAGE.md                      # Detailed usage & API docs
├── start.sh                      # Setup script
├── run_backend.sh                # Backend launcher
├── run_frontend.sh               # Frontend launcher
└── test_setup.py                 # Setup verification script
```

## 🧪 Testing Your Setup

Verify everything is installed correctly:

```bash
python test_setup.py
```

This will check:
- ✅ Python package installations
- ✅ Directory structure
- ✅ Database configuration

## 💡 Usage Examples

### Upload a Presentation
1. Click **Upload** tab
2. Select or drag-drop a .pptx file
3. Wait for processing (5-30 seconds depending on file size)
4. See confirmation with slide count

### Search Across All Slides
1. Click **Search** tab
2. Type keywords (e.g., "introduction", "sales", "Q4 results")
3. View matching slides with context
4. See which presentation and slide number

### View Presentation Details
1. Click **Presentations** tab
2. Click **View Slides** on any presentation
3. Scroll through all slides
4. See titles, content, and speaker notes

## 🎨 Screenshots & Features

### What Gets Extracted:
- ✅ Slide titles
- ✅ All text content from slides
- ✅ Speaker notes
- ✅ Slide numbers and metadata
- ✅ Presentation information

### Search Capabilities:
- Search by slide title
- Search by slide content
- Search by speaker notes
- Case-insensitive matching
- Instant results

## 🔧 Configuration

### Backend Configuration
Edit `backend/main.py` to customize:
- Port (default: 8000)
- CORS settings
- File upload limits
- Database location

### Frontend Configuration
Edit `frontend/package.json` to customize:
- Proxy settings
- Port (default: 3000)

## 🚨 Troubleshooting

### Common Issues

**"Port 8000 already in use"**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**Frontend won't connect to backend**
- Ensure backend is running first
- Check `http://localhost:8000` is accessible
- Clear browser cache

**File upload fails**
- Check file is .pptx format (not .ppt)
- Ensure file is not corrupted
- Check backend logs for errors

### Getting Help

1. Check [USAGE.md](USAGE.md) for detailed documentation
2. Run `python test_setup.py` to verify setup
3. Check terminal output for error messages
4. Visit `http://localhost:8000/docs` for API testing

## 🔐 Security Considerations

**For Production Deployment:**
- ✅ Add authentication and authorization
- ✅ Implement rate limiting
- ✅ Add file size restrictions
- ✅ Validate and sanitize inputs
- ✅ Use environment variables for config
- ✅ Restrict CORS to specific origins
- ✅ Add HTTPS/SSL
- ✅ Implement proper error handling
- ✅ Add logging and monitoring

## 🚀 Deployment

### Local Development
Already configured! Just run the scripts.

### Deploy to Render (Recommended)
The easiest way to deploy this application to production:

```bash
# See detailed deployment guide
cat RENDER_DEPLOYMENT.md
```

**Quick Deploy:**
- **Build Command**: `pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..`
- **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

📖 **See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete instructions**

### Other Production Deployment Options
- **Docker**: Container-based deployment (see Dockerfile and docker-compose.yml)
- **Heroku**: Easy cloud deployment
- **AWS/GCP/Azure**: Cloud infrastructure
- **VPS**: Self-hosted option

## 🛣️ Roadmap & Future Features

Potential enhancements:
- [ ] PDF export of slides
- [ ] Slide thumbnail generation
- [ ] Advanced search filters
- [ ] User authentication
- [ ] Multi-user support
- [ ] Slide annotations
- [ ] Presentation merging
- [ ] Export search results
- [ ] Cloud storage integration
- [ ] Mobile app

## 🤝 Contributing

This is an open-source project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available for personal and commercial use.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - JavaScript UI library
- [python-pptx](https://python-pptx.readthedocs.io/) - PowerPoint parsing
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit

## 📞 Support

Need help? Check these resources:
1. [QUICKSTART.md](QUICKSTART.md) - Getting started
2. [USAGE.md](USAGE.md) - Detailed usage guide
3. `python test_setup.py` - Verify your setup
4. API docs at `http://localhost:8000/docs`

---

**Made with ❤️ for better presentation management**

