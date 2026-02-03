# Usage Guide - PowerPoint Search Platform

## Quick Start

### 1. Installation

First, install all dependencies:

```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Manual installation
# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### 2. Running the Application

You need to run both the backend and frontend:

**Terminal 1 - Backend:**
```bash
cd /Users/meteorresearch/vibe-coding/ppt
source venv/bin/activate  # If using venv
python backend/main.py
```

The backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd /Users/meteorresearch/vibe-coding/ppt/frontend
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Features Overview

### 📤 Upload PowerPoint Files

1. Click on the **Upload** tab
2. Click the upload area or drag and drop a `.pptx` or `.ppt` file
3. Wait for the file to be processed
4. The system will:
   - Extract all slides
   - Parse text content from each slide
   - Extract speaker notes
   - Store metadata in the database

### 📁 Browse Presentations

1. Click on the **Presentations** tab
2. View all uploaded presentations
3. Each card shows:
   - Filename
   - Number of slides
   - Upload date
4. Click **View Slides** to see details
5. Click the 🗑️ icon to delete a presentation

### 👁️ View Slide Details

1. Click **View Slides** on any presentation
2. See all slides with:
   - Slide number
   - Title
   - Full text content
   - Speaker notes (if available)
3. Scroll through all slides in sequence

### 🔍 Search Slides

1. Click on the **Search** tab
2. Enter your search query
3. Results will show:
   - Matching slides
   - Presentation name
   - Slide number
   - Highlighted content
   - Speaker notes

The search looks for matches in:
- Slide titles
- Body text
- Speaker notes

## API Documentation

### Endpoints

#### Upload Presentation
```
POST /api/upload
Content-Type: multipart/form-data

Request:
- file: PowerPoint file (.pptx or .ppt)

Response:
{
  "success": true,
  "presentation_id": 1,
  "filename": "presentation.pptx",
  "slide_count": 10,
  "message": "Successfully uploaded and parsed 10 slides"
}
```

#### List Presentations
```
GET /api/presentations?skip=0&limit=100

Response:
{
  "presentations": [
    {
      "id": 1,
      "filename": "20240203_120000_presentation.pptx",
      "original_filename": "presentation.pptx",
      "upload_date": "2024-02-03T12:00:00",
      "slide_count": 10
    }
  ],
  "total": 1
}
```

#### Get Presentation Details
```
GET /api/presentations/{presentation_id}

Response:
{
  "presentation": {...},
  "slides": [
    {
      "id": 1,
      "presentation_id": 1,
      "slide_number": 1,
      "title": "Introduction",
      "text_content": "Welcome to...",
      "notes": "Remember to...",
      "image_path": null
    }
  ]
}
```

#### Search Slides
```
GET /api/search?q=keyword

Response:
{
  "query": "keyword",
  "results": [
    {
      "slide": {...},
      "presentation": {...}
    }
  ],
  "count": 5
}
```

#### Delete Presentation
```
DELETE /api/presentations/{presentation_id}

Response:
{
  "success": true,
  "message": "Presentation 1 deleted"
}
```

## Data Storage

### File Storage
- **Uploaded Files**: `./uploads/` directory
- **Slide Images**: `./slides/` directory (organized by presentation ID)

### Database
- **Database File**: `ppt_search.db` (SQLite)
- **Tables**:
  - `presentations`: Stores presentation metadata
  - `slides`: Stores individual slide data

## Advanced Usage

### Accessing the API Directly

You can use tools like `curl` or `Postman`:

```bash
# Upload a file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/presentation.pptx"

# Search slides
curl "http://localhost:8000/api/search?q=introduction"

# List presentations
curl http://localhost:8000/api/presentations
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Change the port in backend/main.py
# Line: uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Database errors:**
```bash
# Delete and recreate the database
rm ppt_search.db
python backend/main.py
```

### Frontend Issues

**Port 3000 already in use:**
- The frontend will automatically prompt to use a different port

**CORS errors:**
- Ensure the backend is running
- Check that the proxy is configured in `frontend/package.json`

**Build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Performance Tips

1. **Large Files**: Files with 100+ slides may take 10-30 seconds to process
2. **Search**: Search is performed on the server for better performance
3. **Storage**: Each presentation creates a database entry and stores the original file

## Security Notes

For production use, consider:
- Adding authentication
- Limiting file sizes
- Restricting CORS origins
- Using environment variables for configuration
- Implementing rate limiting
- Adding input validation and sanitization

## Development

### Adding New Features

**Backend:**
- Add new endpoints in `backend/main.py`
- Modify database models in `backend/database.py`
- Extend parsing logic in `backend/ppt_parser.py`

**Frontend:**
- Modify UI in `frontend/src/App.js`
- Add styles in `frontend/src/App.css`

### Running Tests

```bash
# Backend (if tests are added)
pytest backend/

# Frontend
cd frontend
npm test
```

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in the browser console and terminal
3. Ensure all dependencies are correctly installed

