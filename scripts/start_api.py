#!/usr/bin/env python3
"""
Script to start the Smart Home Assistant API server.
"""

import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables from .env file before importing any modules
load_dotenv(os.path.join(project_root, '.env'))

if __name__ == "__main__":
    import uvicorn
    from app.api.main import app
    
    print("🚀 Starting Smart Home Assistant API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation will be available at: http://localhost:8000/docs")
    print("🔄 Use Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )