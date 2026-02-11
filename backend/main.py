"""Main FastAPI application for PowerPoint search platform."""

import os
import shutil
import traceback
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import init_db, get_db, Presentation, Slide, User, ArchivedSlide, Quote, GeneratedQuote
from ppt_parser import parse_pptx, get_presentation_info
from quote_parser import parse_quote_file, generate_quote_from_requirements, learn_quote_with_llm
import json
import io


# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str


# Simple session storage (in production, use proper session management)
sessions = {}  # session_token -> user_id


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """Get current logged in user from session token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = sessions.get(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Initialize FastAPI app
app = FastAPI(title="PowerPoint Search Platform", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("./uploads")
SLIDES_DIR = Path("./slides")
ARCHIVES_DIR = Path("./archives")
QUOTES_DIR = Path("./quotes")
UPLOAD_DIR.mkdir(exist_ok=True)
SLIDES_DIR.mkdir(exist_ok=True)
ARCHIVES_DIR.mkdir(exist_ok=True)
QUOTES_DIR.mkdir(exist_ok=True)

# Mount static files for serving slide images
app.mount("/slides", StaticFiles(directory=str(SLIDES_DIR)), name="slides")
app.mount("/archives", StaticFiles(directory=str(ARCHIVES_DIR)), name="archives")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")


# Root endpoint removed - frontend React app is served at / instead
# API endpoints are available at /api/*


@app.post("/api/auth/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    user = User(username=user_data.username)
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create session
    import secrets
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = user.id
    
    return {
        "success": True,
        "user": user.to_dict(),
        "session_token": session_token
    }


@app.post("/api/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not user.check_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create session
    import secrets
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = user.id
    
    return {
        "success": True,
        "user": user.to_dict(),
        "session_token": session_token
    }


@app.post("/api/auth/logout")
async def logout(authorization: str = Header(None)):
    """Logout user."""
    if authorization and authorization in sessions:
        del sessions[authorization]
    
    return {"success": True}


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {"user": current_user.to_dict()}


def process_presentation_background(file_path: str, presentation_id: int, user_id: int):
    """Background task to process presentation and generate slides."""
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        print(f"🔄 Background processing started for presentation {presentation_id}")
        
        # Parse slides
        slides_output_dir = SLIDES_DIR / str(presentation_id)
        slides_data = parse_pptx(file_path, str(slides_output_dir))
        
        # Create slide records
        for slide_data in slides_data:
            slide = Slide(
                presentation_id=presentation_id,
                slide_number=slide_data["slide_number"],
                title=slide_data["title"],
                text_content=slide_data["text_content"],
                notes=slide_data["notes"],
                image_path=slide_data["image_path"],
                user_id=user_id
            )
            db.add(slide)
        
        db.commit()
        print(f"✅ Background processing completed for presentation {presentation_id}")
        
    except Exception as e:
        print(f"❌ Background processing failed for presentation {presentation_id}: {e}")
        traceback.print_exc()
        # Mark presentation as failed or delete it
        presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
        if presentation:
            db.delete(presentation)
            db.commit()
        # Clean up file
        if Path(file_path).exists():
            Path(file_path).unlink()
    finally:
        db.close()


@app.post("/api/upload")
async def upload_presentation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a PowerPoint presentation and parse it into slides (requires authentication).
    Processing happens in background for better performance.
    """
    # Validate file type
    if not file.filename.endswith(('.pptx', '.ppt')):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx and .ppt files are supported"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get basic presentation info (quick operation)
    try:
        ppt_info = get_presentation_info(str(file_path))
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to read presentation: {str(e)}")
    
    # Create presentation record immediately
    presentation = Presentation(
        user_id=current_user.id,
        filename=safe_filename,
        original_filename=file.filename,
        slide_count=ppt_info["slide_count"]
    )
    db.add(presentation)
    db.commit()
    db.refresh(presentation)
    
    # Process slides in background (slow operation with LibreOffice)
    background_tasks.add_task(
        process_presentation_background,
        str(file_path),
        presentation.id,
        current_user.id
    )
    
    # Return immediately
    return {
        "success": True,
        "presentation_id": presentation.id,
        "filename": file.filename,
        "slide_count": ppt_info["slide_count"],
        "message": f"Upload successful! Processing {ppt_info['slide_count']} slides in background...",
        "status": "processing"
    }


@app.get("/api/presentations")
async def list_presentations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of uploaded presentations for the current user.
    """
    presentations = db.query(Presentation).filter(
        Presentation.user_id == current_user.id
    ).order_by(
        Presentation.upload_date.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "presentations": [p.to_dict() for p in presentations],
        "total": db.query(Presentation).count()
    }


@app.get("/api/presentations/{presentation_id}")
async def get_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific presentation including all slides (user's own only).
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    slides = db.query(Slide).filter(
        Slide.presentation_id == presentation_id
    ).order_by(Slide.slide_number).all()
    
    return {
        "presentation": presentation.to_dict(),
        "slides": [s.to_dict() for s in slides]
    }


@app.get("/api/search")
async def search_slides(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for slides by meta-text (multi-layered search) and presentation filename (user's own presentations only).
    
    Search priority:
    1. Presentation filename (original file name) - highest priority
    2. Slide title (primary meta-text layer) - high priority
    3. Body text content (secondary layer) - medium priority
    4. Speaker notes (tertiary layer) - low priority
    
    Results are ordered by relevance, with filename and title matches first.
    """
    search_term = f"%{q}%"
    
    # Search in all meta-text layers AND presentation filename (user's presentations only)
    slides = db.query(Slide).join(Presentation).filter(
        Presentation.user_id == current_user.id,
        (Presentation.original_filename.like(search_term)) |
        (Slide.title.like(search_term)) |
        (Slide.text_content.like(search_term)) |
        (Slide.notes.like(search_term))
    ).all()
    
    # Sort results by relevance (filename and title matches first)
    def get_relevance_score(slide):
        """Calculate relevance score based on where the match was found."""
        query_lower = q.lower()
        score = 0
        presentation = slide.presentation
        
        # Highest priority: Presentation filename match
        if presentation.original_filename and query_lower in presentation.original_filename.lower():
            score += 200
            # Extra bonus if match is at the start of filename
            if presentation.original_filename.lower().startswith(query_lower):
                score += 100
        
        # Primary layer: Slide title match (high priority)
        if slide.title and query_lower in slide.title.lower():
            score += 100
            # Bonus if match is at the start
            if slide.title.lower().startswith(query_lower):
                score += 50
        
        # Secondary layer: Body text match
        if slide.text_content and query_lower in slide.text_content.lower():
            score += 10
        
        # Tertiary layer: Notes match
        if slide.notes and query_lower in slide.notes.lower():
            score += 1
        
        return score
    
    # Sort slides by relevance
    slides_sorted = sorted(slides, key=get_relevance_score, reverse=True)
    
    # Build results with metadata
    results = []
    for slide in slides_sorted:
        presentation = slide.presentation
        
        # Determine which layer(s) matched
        matched_layers = []
        if presentation.original_filename and q.lower() in presentation.original_filename.lower():
            matched_layers.append("filename")
        if slide.title and q.lower() in slide.title.lower():
            matched_layers.append("title")
        if slide.text_content and q.lower() in slide.text_content.lower():
            matched_layers.append("content")
        if slide.notes and q.lower() in slide.notes.lower():
            matched_layers.append("notes")
        
        # Determine relevance level
        if "filename" in matched_layers:
            relevance = "highest"
        elif "title" in matched_layers:
            relevance = "high"
        elif "content" in matched_layers:
            relevance = "medium"
        else:
            relevance = "low"
        
        results.append({
            "slide": slide.to_dict(),
            "presentation": {
                "id": presentation.id,
                "filename": presentation.original_filename,
                "upload_date": presentation.upload_date.isoformat()
            },
            "matched_layers": matched_layers,  # Show which layers matched
            "relevance": relevance
        })
    
    return {
        "query": q,
        "results": results,
        "count": len(results),
        "info": "Results sorted by relevance: filename matches first, then title, content, and notes"
    }


@app.get("/api/slides/{slide_id}")
async def get_slide(
    slide_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific slide.
    """
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    return {
        "slide": slide.to_dict(),
        "presentation": slide.presentation.to_dict()
    }


@app.delete("/api/presentations/{presentation_id}")
async def delete_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a presentation and all its slides (user's own only).
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Delete associated files
    file_path = UPLOAD_DIR / presentation.filename
    if file_path.exists():
        file_path.unlink()
    
    slides_dir = SLIDES_DIR / str(presentation_id)
    if slides_dir.exists():
        shutil.rmtree(slides_dir)
    
    # Delete from database (slides will be deleted by cascade)
    db.delete(presentation)
    db.commit()
    
    return {
        "success": True,
        "message": f"Presentation {presentation_id} deleted"
    }


@app.post("/api/slides/{slide_id}/download")
async def track_download(
    slide_id: int,
    db: Session = Depends(get_db)
):
    """
    Track when a slide image is downloaded.
    """
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Increment download count
    slide.download_count = (slide.download_count or 0) + 1
    db.commit()
    
    return {
        "success": True,
        "slide_id": slide_id,
        "download_count": slide.download_count
    }


@app.post("/api/slides/{slide_id}/archive")
async def archive_slide(
    slide_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive a slide (persists independently of original presentation).
    """
    slide = db.query(Slide).join(Presentation).filter(
        Slide.id == slide_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Check if already archived
    existing = db.query(ArchivedSlide).filter(
        ArchivedSlide.original_slide_id == slide_id,
        ArchivedSlide.user_id == current_user.id
    ).first()
    
    if existing:
        return {
            "success": True,
            "message": "Slide already archived",
            "archived_slide": existing.to_dict()
        }
    
    # Copy image to archives directory
    archived_image_path = None
    if slide.image_path:
        source_image = SLIDES_DIR / str(slide.presentation_id) / slide.image_path
        if source_image.exists():
            # Create user-specific archive directory
            user_archive_dir = ARCHIVES_DIR / str(current_user.id)
            user_archive_dir.mkdir(exist_ok=True)
            
            # Generate unique filename for archive
            archive_filename = f"archived_{slide_id}_{slide.image_path}"
            dest_image = user_archive_dir / archive_filename
            
            # Copy image
            shutil.copy2(source_image, dest_image)
            archived_image_path = f"{current_user.id}/{archive_filename}"
    
    # Create archived slide record
    archived_slide = ArchivedSlide(
        user_id=current_user.id,
        original_slide_id=slide_id,
        original_presentation_name=slide.presentation.original_filename,
        slide_number=slide.slide_number,
        title=slide.title,
        text_content=slide.text_content,
        notes=slide.notes,
        image_path=archived_image_path
    )
    
    db.add(archived_slide)
    db.commit()
    db.refresh(archived_slide)
    
    return {
        "success": True,
        "archived_slide": archived_slide.to_dict()
    }


@app.get("/api/archives")
async def get_archived_slides(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all archived slides for the current user.
    """
    archived_slides = db.query(ArchivedSlide).filter(
        ArchivedSlide.user_id == current_user.id
    ).order_by(
        ArchivedSlide.archived_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "archived_slides": [slide.to_dict() for slide in archived_slides],
        "count": len(archived_slides)
    }


@app.delete("/api/archives/{archive_id}")
async def delete_archived_slide(
    archive_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an archived slide.
    """
    archived_slide = db.query(ArchivedSlide).filter(
        ArchivedSlide.id == archive_id,
        ArchivedSlide.user_id == current_user.id
    ).first()
    
    if not archived_slide:
        raise HTTPException(status_code=404, detail="Archived slide not found")
    
    # Delete image file
    if archived_slide.image_path:
        image_file = ARCHIVES_DIR / archived_slide.image_path
        if image_file.exists():
            image_file.unlink()
    
    # Delete database record
    db.delete(archived_slide)
    db.commit()
    
    return {
        "success": True,
        "message": f"Archived slide {archive_id} deleted"
    }


# ==================== Quote Calculator API ====================

class QuoteGenerateRequest(BaseModel):
    requirements: str


@app.post("/api/quotes/upload")
async def upload_quote(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a quote file (Excel or CSV) for learning."""
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx, .xls, and .csv files are supported"
        )
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = QUOTES_DIR / safe_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Parse quote file
    try:
        quote_data = parse_quote_file(str(file_path))
        
        # Learn from quote using LLM
        learning_summary = learn_quote_with_llm(quote_data)
        print(f"LLM Learning Summary: {learning_summary}")
        
        # Save to database
        quote = Quote(
            user_id=current_user.id,
            filename=safe_filename,
            original_filename=file.filename,
            items=json.dumps(quote_data['items'], ensure_ascii=False),
            total_amount=quote_data['total_amount']
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)
        
        return {
            "success": True,
            "quote_id": quote.id,
            "filename": file.filename,
            "item_count": quote_data['item_count'],
            "total_amount": quote_data['total_amount'],
            "message": f"Quote uploaded and learned successfully",
            "learning_summary": learning_summary if learning_summary else None
        }
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to parse quote: {str(e)}")


@app.get("/api/quotes/uploaded")
async def get_uploaded_quotes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all uploaded quotes for the current user."""
    quotes = db.query(Quote).filter(
        Quote.user_id == current_user.id
    ).order_by(Quote.uploaded_at.desc()).all()
    
    return {
        "quotes": [{
            "id": q.id,
            "filename": q.original_filename,
            "uploaded_at": q.uploaded_at.isoformat(),
            "total_amount": q.total_amount
        } for q in quotes]
    }


@app.post("/api/quotes/generate")
async def generate_quote(
    request: QuoteGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new quote based on requirements."""
    # Get historical quotes
    historical_quotes = db.query(Quote).filter(
        Quote.user_id == current_user.id
    ).all()
    
    # Convert to dict format
    historical_data = []
    for q in historical_quotes:
        historical_data.append({
            'items': q.items,
            'total_amount': q.total_amount
        })
    
    # Generate quote
    try:
        generated_data = generate_quote_from_requirements(
            request.requirements,
            historical_data
        )
        
        # Save generated quote
        generated_quote = GeneratedQuote(
            user_id=current_user.id,
            requirements=request.requirements,
            items=json.dumps(generated_data['items'], ensure_ascii=False),
            total_amount=generated_data['total_amount']
        )
        db.add(generated_quote)
        db.commit()
        db.refresh(generated_quote)
        
        return {
            "success": True,
            "quote": {
                "id": generated_quote.id,
                "requirements": generated_quote.requirements,
                "items": generated_data['items'],
                "total_amount": generated_data['total_amount'],
                "created_at": generated_quote.created_at.isoformat()
            }
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate quote: {str(e)}")


@app.get("/api/quotes/history")
async def get_quote_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quote generation history."""
    quotes = db.query(GeneratedQuote).filter(
        GeneratedQuote.user_id == current_user.id
    ).order_by(GeneratedQuote.created_at.desc()).limit(20).all()
    
    return {
        "quotes": [{
            "id": q.id,
            "requirements": q.requirements[:100] + "..." if len(q.requirements) > 100 else q.requirements,
            "total_amount": q.total_amount,
            "created_at": q.created_at.isoformat()
        } for q in quotes]
    }


@app.post("/api/quotes/{quote_id}/export")
async def export_quote(
    quote_id: int,
    format: str = Query("excel", regex="^(excel|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export quote as Excel or CSV."""
    quote = db.query(GeneratedQuote).filter(
        GeneratedQuote.id == quote_id,
        GeneratedQuote.user_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Parse items
    items = json.loads(quote.items) if isinstance(quote.items, str) else quote.items
    
    if format == "excel":
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        
        # Create DataFrame
        df = pd.DataFrame(items)
        df.columns = ['항목', '단가', '수량', '금액']
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='견적서')
        
        output.seek(0)
        
        from fastapi.responses import Response
        return Response(
            content=output.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=quote_{quote_id}.xlsx"}
        )
    
    else:  # CSV
        import csv
        import pandas as pd
        
        df = pd.DataFrame(items)
        df.columns = ['항목', '단가', '수량', '금액']
        
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue().encode('utf-8-sig'),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=quote_{quote_id}.csv"}
        )


# Serve React frontend in production (after all API routes are defined)
FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "build"
if FRONTEND_BUILD.exists():
    print(f"✅ Serving frontend from {FRONTEND_BUILD}")
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD), html=True), name="frontend")
else:
    print(f"⚠️  Frontend build not found at {FRONTEND_BUILD}")
    print("   Run 'cd frontend && npm run build' to create production build")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

