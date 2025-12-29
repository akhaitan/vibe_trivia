from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import logging

from backend.models import (
    QuizRequest,
    QuizResponse,
    SubmitQuizRequest,
    SubmitQuizResponse,
    ScoresResponse
)
from backend.services.trivia_service import TriviaService
from backend.services.scoring_service import ScoringService
from backend.services.persistence_service import PersistenceService
from backend.database import init_db

# Load environment variables
load_dotenv()

# Initialize database on startup
init_db()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trivia API", version="1.0.0")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the path to frontend directory
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_exists = os.path.exists(frontend_path)

# Serve static files (CSS, JS) if frontend directory exists
if frontend_exists:
    logger.info(f"Serving frontend from: {frontend_path}")

# Initialize services
trivia_service = TriviaService()
scoring_service = ScoringService()
persistence_service = PersistenceService()


@app.get("/")
def root():
    """Serve frontend index.html or health check."""
    if frontend_exists:
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"status": "ok", "message": "Trivia API is running"}


@app.post("/api/generate-quiz", response_model=QuizResponse)
def generate_quiz(request: QuizRequest):
    """
    Generate a trivia quiz for the given topic.
    
    Args:
        request: QuizRequest with user_name and topic
        
    Returns:
        QuizResponse with quiz_id and questions
    """
    try:
        # Generate quiz using OpenAI
        questions = trivia_service.generate_quiz(request.topic)
        
        # Generate unique quiz ID and store quiz
        quiz_id = persistence_service.generate_quiz_id()
        persistence_service.store_quiz(quiz_id, questions, request.topic)
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=questions
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/submit-quiz", response_model=SubmitQuizResponse)
def submit_quiz(request: SubmitQuizRequest):
    """
    Submit quiz answers and get score.
    
    Args:
        request: SubmitQuizRequest with quiz_id, user_name, and answers
        
    Returns:
        SubmitQuizResponse with score, total, and detailed results
    """
    try:
        # Retrieve stored quiz
        quiz_data = persistence_service.get_quiz(request.quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        questions, topic = quiz_data
        
        # Validate answer count
        if len(request.answers) != len(questions):
            raise HTTPException(
                status_code=400,
                detail=f"Expected {len(questions)} answers, got {len(request.answers)}"
            )
        
        # Calculate score
        score, results = scoring_service.calculate_score(questions, request.answers)
        
        # Generate performance phrase
        performance_phrase = trivia_service.generate_performance_phrase(
            topic=topic,
            score=score,
            total=len(questions)
        )
        
        # Save attempt
        persistence_service.save_attempt(
            user_name=request.user_name,
            quiz_topic=topic,
            score=score,
            total=len(questions)
        )
        
        return SubmitQuizResponse(
            score=score,
            total=len(questions),
            results=results,
            performance_phrase=performance_phrase
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/scores", response_model=ScoresResponse)
def get_scores(user_name: str):
    """
    Get all quiz attempts for a user.
    
    Args:
        user_name: The user's name
        
    Returns:
        ScoresResponse with list of attempts
    """
    attempts = persistence_service.get_user_attempts(user_name)
    return ScoresResponse(attempts=attempts)


@app.get("/api/history", response_model=ScoresResponse)
def get_history():
    """
    Get all quiz attempts across all users (quiz history).
    Returns attempts sorted by timestamp (newest first).
    
    Returns:
        ScoresResponse with list of all attempts
    """
    attempts = persistence_service.get_all_attempts()
    return ScoresResponse(attempts=attempts)


# Serve frontend files (CSS, JS, and other assets)
# These routes must come before the catch-all route but after API routes
if frontend_exists:
    @app.get("/styles.css")
    def serve_css():
        """Serve CSS file."""
        return FileResponse(os.path.join(frontend_path, "styles.css"))
    
    @app.get("/app.js")
    def serve_js():
        """Serve JavaScript file."""
        return FileResponse(os.path.join(frontend_path, "app.js"))


# Serve frontend files (for SPA routing) - MUST be last to not interfere with API routes
@app.get("/{path:path}")
def serve_frontend(path: str):
    """
    Serve frontend files. For API routes, let them pass through.
    For other paths, serve frontend files or index.html for SPA routing.
    """
    # Don't interfere with API routes
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    if frontend_exists:
        file_path = os.path.join(frontend_path, path)
        # If it's a file that exists, serve it
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # For SPA routing (e.g., /quiz, /results), return index.html
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

