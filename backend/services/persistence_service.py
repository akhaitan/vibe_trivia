from typing import List, Dict, Optional
from datetime import datetime
from backend.models import QuizAttempt
from backend.database import SessionLocal, QuizAttemptDB, init_db
import uuid
import logging

logger = logging.getLogger(__name__)


class PersistenceService:
    """
    Persistence service for quiz attempts using PostgreSQL (Supabase).
    Falls back to SQLite for local development if DATABASE_URL is not set.
    """
    
    def __init__(self):
        """Initialize persistence service with database."""
        # Initialize database tables
        init_db()
        
        # Store quiz data in-memory: quiz_id -> (questions, topic)
        # Quizzes are temporary and don't need to be persisted
        self._quizzes: Dict[str, tuple] = {}
        
        logger.info("PersistenceService initialized with database")
    
    def store_quiz(self, quiz_id: str, questions: List, topic: str) -> None:
        """Store a generated quiz for later retrieval (in-memory only)."""
        self._quizzes[quiz_id] = (questions, topic)
    
    def get_quiz(self, quiz_id: str) -> Optional[tuple]:
        """Retrieve a stored quiz by ID."""
        return self._quizzes.get(quiz_id)
    
    def save_attempt(
        self,
        user_name: str,
        quiz_topic: str,
        score: int,
        total: int
    ) -> None:
        """Save a quiz attempt to the database."""
        db = SessionLocal()
        try:
            attempt = QuizAttemptDB(
                user_name=user_name,
                quiz_topic=quiz_topic,
                score=score,
                total=total,
                timestamp=datetime.utcnow()
            )
            db.add(attempt)
            db.commit()
            logger.info(f"Saved quiz attempt: {user_name} - {quiz_topic} - {score}/{total}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving quiz attempt: {e}")
            raise
        finally:
            db.close()
    
    def get_user_attempts(self, user_name: str) -> List[QuizAttempt]:
        """Get all quiz attempts for a user."""
        db = SessionLocal()
        try:
            db_attempts = db.query(QuizAttemptDB)\
                .filter(QuizAttemptDB.user_name == user_name)\
                .order_by(QuizAttemptDB.timestamp.desc())\
                .all()
            
            return [
                QuizAttempt(
                    user_name=a.user_name,
                    quiz_topic=a.quiz_topic,
                    score=a.score,
                    total=a.total,
                    timestamp=a.timestamp
                )
                for a in db_attempts
            ]
        except Exception as e:
            logger.error(f"Error retrieving user attempts: {e}")
            return []
        finally:
            db.close()
    
    def get_all_attempts(self) -> List[QuizAttempt]:
        """
        Get all quiz attempts across all users.
        Returns attempts sorted by timestamp (newest first).
        """
        db = SessionLocal()
        try:
            db_attempts = db.query(QuizAttemptDB)\
                .order_by(QuizAttemptDB.timestamp.desc())\
                .all()
            
            return [
                QuizAttempt(
                    user_name=a.user_name,
                    quiz_topic=a.quiz_topic,
                    score=a.score,
                    total=a.total,
                    timestamp=a.timestamp
                )
                for a in db_attempts
            ]
        except Exception as e:
            logger.error(f"Error retrieving all attempts: {e}")
            return []
        finally:
            db.close()
    
    def generate_quiz_id(self) -> str:
        """Generate a unique quiz ID."""
        return str(uuid.uuid4())

