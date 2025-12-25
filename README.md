# Trivia Web Application

A production-ready trivia game web application that generates custom quizzes based on TV shows or movies using OpenAI.

## Features

- Generate 10 trivia questions for any TV show or movie
- Deep knowledge questions covering plot, characters, actors, and iconic moments
- Multiple-choice format with 4 options per question
- Score tracking and persistence
- Modern dark mode UI, mobile responsive

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: Vanilla JavaScript
- **AI**: OpenAI API
- **Persistence**: In-memory (designed for easy database migration)

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trivia
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```bash
cp .env.example .env
# Then edit .env and add your OpenAI API key
```

Or create `.env` manually with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

5. Start the backend server (choose one method):

**Option A: Using the startup script:**
```bash
./start.sh
```

**Option B: Manual start:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

6. Open the frontend:

**Option A: Direct file open (may have CORS issues):**
Open `frontend/index.html` in your browser

**Option B: Using a simple HTTP server (recommended):**
```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080` in your browser.

**Note:** The frontend expects the backend to be running on `http://localhost:8000`. If you change the backend port, update `API_BASE_URL` in `frontend/app.js`.

## API Endpoints

### POST `/api/generate-quiz`
Generate a trivia quiz for a given show or movie.

**Request Body:**
```json
{
  "user_name": "John Doe",
  "topic": "The Office"
}
```

**Response:**
```json
{
  "quiz_id": "uuid",
  "questions": [
    {
      "question": "What is the name of...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A"
    }
  ]
}
```

### POST `/api/submit-quiz`
Submit quiz answers and get score.

**Request Body:**
```json
{
  "quiz_id": "uuid",
  "user_name": "John Doe",
  "answers": ["Option A", "Option B", ...]
}
```

**Response:**
```json
{
  "score": 8,
  "total": 10,
  "results": [
    {
      "question": "...",
      "selected": "Option A",
      "correct": "Option B",
      "is_correct": false
    }
  ]
}
```

### GET `/api/scores`
Get all quiz attempts for a user.

**Query Parameters:**
- `user_name`: The user's name

**Response:**
```json
{
  "attempts": [
    {
      "user_name": "John Doe",
      "quiz_topic": "The Office",
      "score": 8,
      "total": 10,
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

## Project Structure

```
trivia/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   ├── trivia_service.py    # OpenAI integration
│   │   ├── scoring_service.py   # Score calculation
│   │   └── persistence_service.py  # Data storage (JSON file)
│   └── models.py            # Pydantic models
├── frontend/
│   ├── index.html           # Main UI
│   ├── styles.css           # Dark mode styling
│   └── app.js               # Client-side logic
├── data/
│   └── quiz_history.json    # Quiz history storage (auto-created)
├── requirements.txt
├── .env                     # Environment variables (not in git)
└── README.md
```

## Data Persistence

Quiz history is automatically saved to `data/quiz_history.json`. The file is:
- Created automatically on first quiz submission
- Updated after every quiz attempt
- Loaded on application startup
- Stored in JSON format for easy inspection and migration

The data directory and file are automatically created if they don't exist.

## Development

The application is designed with clean service separation for easy maintenance and future scalability. The persistence layer can be easily swapped for a real database when needed.

## Deployment

The application is ready for deployment. Ensure:
- Environment variables are set in production
- CORS is configured appropriately
- Static files are served correctly

