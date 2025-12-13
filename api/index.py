"""
Vercel Serverless Function Entry Point
"""
from app.main import app

# Vercel expects 'app' or 'handler'
# FastAPI app is already named 'app' in app/main.py
