#!/bin/bash
# This script starts the FastAPI application using uvicorn.

echo "Starting the Symptom Checker Chatbot API server..."

# uvicorn app.main:app --reload
#
# Explanation:
# - app.main: tells uvicorn to look for a file named main.py in the 'app' directory.
# - :app: tells uvicorn to find an object named 'app' inside main.py.
# - --reload: enables auto-reload, so the server restarts when you change the code.
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload