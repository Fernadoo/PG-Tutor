"""
FastAPI Backend for AI Tutoring System

A production-ready API for the AI tutoring system with:
- REST endpoints for session management
- WebSocket support for real-time updates
- Stateless architecture with optional Redis
- Multi-user support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add src to path for importing existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api import sessions, topics, config
from core.connection_manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("🚀 AI Tutor API starting up...")
    yield
    # Shutdown
    print("👋 AI Tutor API shutting down...")


app = FastAPI(
    title="AI Tutoring System API",
    description="Production API for personalized Bayesian tutoring",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include routers
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(config.router, prefix="/api/config", tags=["config"])


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages (e.g., answer submissions)
            await manager.broadcast_to_session(session_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)


@app.get("/")
async def root():
    return {
        "message": "AI Tutoring System API v2.0",
        "docs": "/docs",
        "endpoints": {
            "sessions": "/api/sessions",
            "topics": "/api/topics",
            "config": "/api/config"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
