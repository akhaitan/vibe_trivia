#!/bin/bash

# Trivia App Startup Script

echo "Starting Trivia Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "You can copy .env.example to .env and update it"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Start the backend server
echo "Starting backend server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

