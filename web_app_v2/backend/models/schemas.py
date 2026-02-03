"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Mode(str, Enum):
    """Learning mode options."""
    LLM = "llm"
    SIMPLE = "simple"


class APIConfig(BaseModel):
    """API configuration from user."""
    api_key: str = Field(..., description="API key for LLM service")
    base_url: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="Base URL for API"
    )
    model: str = Field(default="gpt-3.5-turbo", description="Model name")


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    mode: Mode = Field(default=Mode.SIMPLE, description="Learning mode")
    config: Optional[APIConfig] = Field(None, description="API configuration for LLM mode")
    target_questions: int = Field(default=5, ge=1, le=50)


class SessionResponse(BaseModel):
    """Session data response."""
    session_id: str
    mode: Mode
    current_topic: Dict[str, Any]
    belief: Dict[str, float]
    total_answered: int = 0
    correct_count: int = 0
    accuracy: float = 0.0
    created_at: datetime
    updated_at: datetime


class TopicResponse(BaseModel):
    """Topic information."""
    id: str
    name: str
    level: int
    difficulty: float
    content: str
    prerequisites: List[str]


class AnswerRequest(BaseModel):
    """Submit an answer."""
    answer: str = Field(..., description="User's answer or 'true'/'false' for simple mode")
    use_llm: bool = Field(default=False, description="Whether to use LLM evaluation")


class AnswerResponse(BaseModel):
    """Response after submitting an answer."""
    correct: bool
    feedback: str
    llm_evaluation: Optional[Dict[str, Any]] = None
    updated_belief: Dict[str, float]
    next_topic: Optional[TopicResponse] = None
    total_answered: int
    correct_count: int
    accuracy: float


class BeliefState(BaseModel):
    """Bayesian belief state."""
    alpha: float
    beta: float
    expected_lambda: float
    variance: float
    confidence_interval: tuple[float, float]


class ProgressData(BaseModel):
    """Progress data for charts."""
    belief_history: List[Dict[str, Any]]
    topic_history: List[Dict[str, Any]]
    level_stats: Dict[str, Dict[str, int]]
    cumulative_accuracy: List[float]


class KnowledgeGraphNode(BaseModel):
    """Node in knowledge graph."""
    id: str
    name: str
    level: int
    difficulty: float
    x: float
    y: float


class KnowledgeGraphEdge(BaseModel):
    """Edge in knowledge graph."""
    source: str
    target: str


class KnowledgeGraphResponse(BaseModel):
    """Complete knowledge graph."""
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: Optional[str] = None
