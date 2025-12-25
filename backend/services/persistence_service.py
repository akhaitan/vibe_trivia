from typing import List, Dict, Optional
from datetime import datetime
from backend.models import QuizAttempt
import uuid
import json
import os
import logging

logger = logging.getLogger(__name__)


class PersistenceService:
    """
    Persistence service for quiz attempts using JSON file storage.
    Designed to be easily replaceable with a real database.
    """
    
    def __init__(self, data_file: str = "data/quiz_history.json"):
        """
        Initialize persistence service.
        
        Args:
            data_file: Path to JSON file for storing quiz history
        """
        self.data_file = data_file
        # Store quiz data: quiz_id -> (questions, topic)
        self._quizzes: Dict[str, tuple] = {}
        
        # Store quiz attempts: user_name -> List[QuizAttempt]
        self._attempts: Dict[str, List[QuizAttempt]] = {}
        
        # Load existing data from file
        self._load_from_file()
    
    def store_quiz(self, quiz_id: str, questions: List, topic: str) -> None:
        """Store a generated quiz for later retrieval."""
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
        """Save a quiz attempt for a user and persist to file."""
        attempt = QuizAttempt(
            user_name=user_name,
            quiz_topic=quiz_topic,
            score=score,
            total=total,
            timestamp=datetime.now()
        )
        
        if user_name not in self._attempts:
            self._attempts[user_name] = []
        
        self._attempts[user_name].append(attempt)
        
        # Persist to file after saving
        self._save_to_file()
    
    def get_user_attempts(self, user_name: str) -> List[QuizAttempt]:
        """Get all quiz attempts for a user."""
        return self._attempts.get(user_name, [])
    
    def get_all_attempts(self) -> List[QuizAttempt]:
        """
        Get all quiz attempts across all users.
        Returns attempts sorted by timestamp (newest first).
        Designed to be easily replaced with a database query.
        """
        all_attempts = []
        for user_attempts in self._attempts.values():
            all_attempts.extend(user_attempts)
        
        # Sort by timestamp, newest first
        all_attempts.sort(key=lambda x: x.timestamp, reverse=True)
        return all_attempts
    
    def generate_quiz_id(self) -> str:
        """Generate a unique quiz ID."""
        return str(uuid.uuid4())
    
    def _load_from_file(self) -> None:
        """Load quiz attempts from JSON file."""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.dirname(self.data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                logger.info(f"Created data directory: {data_dir}")
            
            # Load file if it exists
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Restore attempts from JSON
                self._attempts = {}
                for item in data.get('attempts', []):
                    user_name = item['user_name']
                    if user_name not in self._attempts:
                        self._attempts[user_name] = []
                    
                    # Convert timestamp string back to datetime
                    attempt = QuizAttempt(
                        user_name=item['user_name'],
                        quiz_topic=item['quiz_topic'],
                        score=item['score'],
                        total=item['total'],
                        timestamp=datetime.fromisoformat(item['timestamp'])
                    )
                    self._attempts[user_name].append(attempt)
                
                logger.info(f"Loaded {len(self.get_all_attempts())} quiz attempts from {self.data_file}")
            else:
                logger.info(f"History file not found, starting with empty history: {self.data_file}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {self.data_file}: {e}")
            logger.warning("Starting with empty history due to file parse error")
            self._attempts = {}
        except Exception as e:
            logger.error(f"Error loading history file {self.data_file}: {e}")
            logger.warning("Starting with empty history due to load error")
            self._attempts = {}
    
    def _save_to_file(self) -> None:
        """Save quiz attempts to JSON file."""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.dirname(self.data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            # Convert attempts to JSON-serializable format
            attempts_data = []
            for user_attempts in self._attempts.values():
                for attempt in user_attempts:
                    attempts_data.append({
                        'user_name': attempt.user_name,
                        'quiz_topic': attempt.quiz_topic,
                        'score': attempt.score,
                        'total': attempt.total,
                        'timestamp': attempt.timestamp.isoformat()
                    })
            
            # Write to file atomically (write to temp file, then rename)
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({'attempts': attempts_data}, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.replace(temp_file, self.data_file)
            logger.debug(f"Saved {len(attempts_data)} quiz attempts to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Error saving history file {self.data_file}: {e}")
            # Don't raise - we don't want to fail the quiz submission if file write fails
            # The data is still in memory, so the API will work

