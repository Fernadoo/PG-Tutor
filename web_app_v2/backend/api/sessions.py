"""
API Router for Session Management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Optional
import uuid
from datetime import datetime

from models.schemas import (
    CreateSessionRequest, SessionResponse, AnswerRequest, 
    AnswerResponse, ProgressData, BeliefState
)
from services.session_service import SessionService
from services.teacher_service import TeacherService

router = APIRouter()
session_service = SessionService()
teacher_service = TeacherService()


@router.post("/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new tutoring session."""
    try:
        session = session_service.create_session(
            mode=request.mode,
            config=request.config.dict() if request.config else None,
            target_questions=request.target_questions
        )
        return SessionResponse(**session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session)


@router.get("/{session_id}/lesson")
async def get_lesson(session_id: str):
    """Get personalized lesson content for the current topic."""
    session = session_service.get_raw_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        teacher = session.get("teacher")
        current_topic = session.get("current_topic")
        
        if not teacher or not current_topic:
            raise HTTPException(status_code=400, detail="No active topic")
        
        # Generate lesson content
        lesson_content = teacher_service.get_lesson_content(
            teacher, 
            current_topic["name"]
        )
        
        return {
            "topic": current_topic,
            "lesson_content": lesson_content,
            "mode": session.get("mode", "simple")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(session_id: str, request: AnswerRequest):
    """Submit an answer and get feedback."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        result = session_service.submit_answer(
            session_id=session_id,
            answer=request.answer,
            use_llm=request.use_llm
        )
        return AnswerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/progress", response_model=ProgressData)
async def get_progress(session_id: str):
    """Get detailed progress data for charts."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ProgressData(
        belief_history=session.get("belief_history", []),
        topic_history=session.get("topic_history", []),
        level_stats=session_service.get_level_stats(session_id),
        cumulative_accuracy=session_service.get_cumulative_accuracy(session_id)
    )


@router.get("/{session_id}/belief", response_model=BeliefState)
async def get_belief(session_id: str):
    """Get current Bayesian belief state."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    belief = session.get("belief", {})
    return BeliefState(**belief)


@router.post("/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset a session."""
    success = session_service.reset_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session reset successfully"}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
