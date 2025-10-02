#!/usr/bin/env python3
"""
Startup script for the Gemini RAG Agent server
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Gemini RAG Agent Server...")
    print("Server will be available at: http://localhost:2024")
    print("Health check: http://localhost:2024/")
    print("Chat UI should connect to: http://localhost:2024")
    
    uvicorn.run(
        "app.server:app",
        host="0.0.0.0",
        port=2024,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )