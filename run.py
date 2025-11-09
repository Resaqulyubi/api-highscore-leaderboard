"""
Simple script to run the HighScore API locally
"""
import sys
import os
import uvicorn
from app.config import settings

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    print("Starting HighScore API...")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"Docs: http://{settings.host}:{settings.port}/docs")
    print(f"ReDoc: http://{settings.host}:{settings.port}/redoc")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
