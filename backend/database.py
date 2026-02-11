"""Database models and setup for the PowerPoint search platform."""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import hashlib

Base = declarative_base()


class User(Base):
    """Model for storing user accounts."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to presentations
    presentations = relationship("Presentation", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if password matches."""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat()
        }


class Presentation(Base):
    """Model for storing presentation metadata."""
    
    __tablename__ = "presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    slide_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="presentations")
    slides = relationship("Slide", back_populates="presentation", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "upload_date": self.upload_date.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else self.upload_date.isoformat(),
            "slide_count": self.slide_count
        }


class Slide(Base):
    """Model for storing individual slide data."""
    
    __tablename__ = "slides"
    
    id = Column(Integer, primary_key=True, index=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"), nullable=False)
    slide_number = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    text_content = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to presentation
    presentation = relationship("Presentation", back_populates="slides")
    
    def to_dict(self):
        return {
            "id": self.id,
            "presentation_id": self.presentation_id,
            "slide_number": self.slide_number,
            "title": self.title,
            "text_content": self.text_content,
            "notes": self.notes,
            "image_path": self.image_path,
            "download_count": self.download_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ArchivedSlide(Base):
    """Model for storing archived slides (persists independently of original presentation)."""
    
    __tablename__ = "archived_slides"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_slide_id = Column(Integer, nullable=True)  # Reference to original, but nullable
    original_presentation_name = Column(String, nullable=False)
    slide_number = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    text_content = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)  # Copied to archives directory
    archived_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_presentation_name": self.original_presentation_name,
            "slide_number": self.slide_number,
            "title": self.title,
            "text_content": self.text_content,
            "notes": self.notes,
            "image_path": self.image_path,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None
        }


# Database setup - Use PostgreSQL if DATABASE_URL is set, otherwise SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ppt_search.db")

# PostgreSQL URL fix for Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL settings for better concurrency
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Quote(Base):
    """Model for storing uploaded quote files."""
    
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    items = Column(Text)  # JSON string of quote items
    total_amount = Column(Integer)  # Total amount in KRW
    
    user = relationship("User", back_populates="quotes")


class GeneratedQuote(Base):
    """Model for storing generated quotes."""
    
    __tablename__ = "generated_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requirements = Column(Text, nullable=False)
    items = Column(Text)  # JSON string of quote items
    total_amount = Column(Integer)  # Total amount in KRW
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


# Update User model to include quotes relationship
User.quotes = relationship("Quote", back_populates="user")


def init_db():
    """Initialize the database."""
    # Use checkfirst=True to avoid race conditions with multiple workers
    Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

