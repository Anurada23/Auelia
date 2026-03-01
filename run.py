#!/usr/bin/env python3
"""
Finder AI v2 - Main Entry Point
Run this file to start the application
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now we can import
import uvicorn
from config import settings
from utils import logger

def main():
    """Start the Finder AI application"""
    
    print("=" * 60)
    print("🤖 Starting Finder AI v2...")
    print("=" * 60)
    print()
    print(f"📡 API Server: http://{settings.api_host}:{settings.api_port}")
    print(f"📄 API Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"🌐 Frontend: Open frontend/index.html in your browser")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        # Start the server
        uvicorn.run(
            "api.app:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("👋 Shutting down Finder AI v2...")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if .env file exists and has GROQ_API_KEY")
        print("2. Make sure port 8000 is available")
        print("3. Verify all dependencies are installed: pip install -r requirements-minimal.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()