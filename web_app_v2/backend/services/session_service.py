"""
Session Service

Manages tutoring sessions with state persistence.
Uses in-memory storage (can be replaced with Redis).
"""

import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from teacher import AITeacher, LLMTeacher
from knowledge_graph import KnowledgeGraph


class SessionService:
    """Service for managing tutoring sessions."""
    
    def __init__(self):
        # In-memory session storage
        # For production, replace with Redis or database
        self._sessions: Dict[str, Dict] = {}
        self._knowledge_graph = KnowledgeGraph()
    
    def create_session(
        self, 
        mode: str = "simple", 
        config: Optional[Dict] = None,
        target_questions: int = 5
    ) -> Dict:
        """Create a new tutoring session."""
        session_id = str(uuid.uuid4())
        
        # Initialize teacher
        teacher = None
        use_llm = mode == "llm"
        
        if use_llm and config:
            try:
                teacher = LLMTeacher(
                    self._knowledge_graph,
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model", "gpt-3.5-turbo")
                )
            except Exception as e:
                print(f"Could not initialize LLM Teacher: {e}")
                teacher = None
        
        if teacher is None:
            teacher = AITeacher(self._knowledge_graph)
            use_llm = False
        
        # Get first topic
        current_topic = self._knowledge_graph.get_random_topic_at_level(0)
        
        # Create session
        session = {
            "session_id": session_id,
            "mode": mode,
            "use_llm": use_llm,
            "config": config,
            "target_questions": target_questions,
            "teacher": teacher,
            "current_topic": self._topic_to_dict(current_topic),
            "belief": teacher.get_current_belief(),
            "belief_history": [],
            "topic_history": [],
            "total_answered": 0,
            "correct_count": 0,
            "accuracy": 0.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self._sessions[session_id] = session
        
        # Return without teacher object (not serializable)
        return self._serialize_session(session)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID (serialized)."""
        session = self._sessions.get(session_id)
        if session:
            return self._serialize_session(session)
        return None
    
    def get_raw_session(self, session_id: str) -> Optional[Dict]:
        """Get raw session by ID (includes teacher object)."""
        return self._sessions.get(session_id)
    
    def submit_answer(
        self, 
        session_id: str, 
        answer: str, 
        use_llm: bool = False
    ) -> Dict:
        """Submit an answer and update session."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        teacher = session["teacher"]
        current_topic = teacher.knowledge_graph.get_topic_by_name(
            session["current_topic"]["name"]
        )
        
        # Process answer
        if use_llm:
            # LLM evaluation
            evaluation = teacher.evaluate_student_response(current_topic, answer)
            correct = evaluation.get("correct", False)
            feedback = evaluation.get("feedback", "")
            llm_evaluation = evaluation
        else:
            # Simple binary evaluation
            correct = answer.lower() in ["true", "correct", "yes", "1"]
            feedback = (
                "✓ Good work! You're mastering this topic." 
                if correct 
                else "✗ That's okay! Learning takes practice."
            )
            llm_evaluation = None
        
        # Update belief
        teacher.observe_student_performance(current_topic, correct)
        
        # Get updated belief
        belief = teacher.get_current_belief()
        estimated_level = int(belief["expected_lambda"])
        
        # Update history
        session["belief_history"].append({
            "topic": current_topic.name,
            "correct": correct,
            "belief": belief,
            "timestamp": datetime.now().isoformat()
        })
        
        session["topic_history"].append({
            "topic": current_topic.name,
            "level": current_topic.level,
            "correct": correct,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update stats
        session["total_answered"] += 1
        if correct:
            session["correct_count"] += 1
        session["accuracy"] = session["correct_count"] / session["total_answered"]
        
        # Get next topic
        next_topic = teacher.get_next_topic(estimated_level)
        if next_topic:
            session["current_topic"] = self._topic_to_dict(next_topic)
        
        session["belief"] = belief
        session["updated_at"] = datetime.now()
        
        return {
            "correct": correct,
            "feedback": feedback,
            "llm_evaluation": llm_evaluation,
            "updated_belief": belief,
            "next_topic": session["current_topic"] if next_topic else None,
            "total_answered": session["total_answered"],
            "correct_count": session["correct_count"],
            "accuracy": session["accuracy"]
        }
    
    def get_level_stats(self, session_id: str) -> Dict[str, Dict[str, int]]:
        """Get statistics grouped by level."""
        session = self._sessions.get(session_id)
        if not session:
            return {}
        
        stats = {}
        for record in session["topic_history"]:
            level = str(record["level"])
            if level not in stats:
                stats[level] = {"total": 0, "correct": 0}
            stats[level]["total"] += 1
            if record["correct"]:
                stats[level]["correct"] += 1
        
        return stats
    
    def get_cumulative_accuracy(self, session_id: str) -> List[float]:
        """Get cumulative accuracy over time."""
        session = self._sessions.get(session_id)
        if not session:
            return []
        
        cumulative = []
        correct_so_far = 0
        
        for i, record in enumerate(session["topic_history"], 1):
            if record["correct"]:
                correct_so_far += 1
            cumulative.append((correct_so_far / i) * 100)
        
        return cumulative
    
    def reset_session(self, session_id: str) -> bool:
        """Reset a session to initial state."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        # Reinitialize teacher
        config = session.get("config")
        mode = session.get("mode", "simple")
        
        teacher = None
        if mode == "llm" and config:
            try:
                teacher = LLMTeacher(
                    self._knowledge_graph,
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model", "gpt-3.5-turbo")
                )
            except Exception:
                teacher = None
        
        if teacher is None:
            teacher = AITeacher(self._knowledge_graph)
        
        current_topic = self._knowledge_graph.get_random_topic_at_level(0)
        
        # Reset session data
        session.update({
            "teacher": teacher,
            "current_topic": self._topic_to_dict(current_topic),
            "belief": teacher.get_current_belief(),
            "belief_history": [],
            "topic_history": [],
            "total_answered": 0,
            "correct_count": 0,
            "accuracy": 0.0,
            "updated_at": datetime.now()
        })
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def _topic_to_dict(self, topic) -> Dict:
        """Convert Topic object to dictionary."""
        return {
            "id": topic.name.lower().replace(" ", "_"),
            "name": topic.name,
            "level": topic.level,
            "difficulty": topic.difficulty,
            "content": topic.content,
            "prerequisites": topic.prerequisites
        }
    
    def _serialize_session(self, session: Dict) -> Dict:
        """Serialize session for API response (remove non-serializable objects)."""
        return {
            k: v for k, v in session.items() 
            if k not in ["teacher", "config"]
        }
