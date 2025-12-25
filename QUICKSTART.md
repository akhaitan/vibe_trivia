# Quick Start Guide

## Prerequisites
- Python 3.9+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Setup (5 minutes)

1. **Clone and navigate:**
   ```bash
   cd trivia
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_key_here" > .env
   # Or manually create .env and add: OPENAI_API_KEY=your_key_here
   ```

5. **Start backend:**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start frontend (in a new terminal):**
   ```bash
   cd frontend
   python -m http.server 8080
   ```

7. **Open browser:**
   Navigate to `http://localhost:8080`

## Testing

1. Enter your name
2. Enter a TV show or movie (e.g., "The Office", "Inception")
3. Click "Generate Quiz"
4. Answer all 10 questions
5. Submit and see your results!

## Troubleshooting

**Backend won't start:**
- Check that `.env` file exists and has `OPENAI_API_KEY` set
- Verify Python version: `python3 --version` (should be 3.9+)
- Make sure you're in the project root directory

**Frontend can't connect to backend:**
- Verify backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Update `API_BASE_URL` in `frontend/app.js` if backend is on different port

**Quiz generation fails:**
- Verify OpenAI API key is valid
- Check you have API credits/quota
- Review backend logs for detailed error messages

