"""
Database configuration and models for PostgreSQL (Supabase).
"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class QuizAttemptDB(Base):
    """Database model for quiz attempts."""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), nullable=False, index=True)
    quiz_topic = Column(String(200), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


def get_database_url():
    """
    Get database URL from environment variable.
    Falls back to SQLite for local development if DATABASE_URL is not set.
    For PostgreSQL, ensures psycopg3 driver is used.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Fallback to SQLite for local development
        logger.warning("DATABASE_URL not set, using SQLite for local development")
        database_url = "sqlite:///./data/trivia.db"
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
    elif database_url.startswith("postgresql://"):
        # Ensure psycopg3 driver is used for PostgreSQL connections
        # SQLAlchemy will auto-detect psycopg3, but explicit is better
        if "+psycopg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    return database_url


def create_engine_instance():
    """Create SQLAlchemy engine with appropriate connection args."""
    database_url = get_database_url()
    
    # SQLite needs special connection args
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )


# Create engine and session factory
engine = create_engine_instance()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables. Creates tables if they don't exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

