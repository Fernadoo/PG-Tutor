"""
Teacher Service

Wrapper service for teacher operations.
"""

import sys
import os
from typing import Dict, Optional, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from teacher import AITeacher, LLMTeacher
from knowledge_graph import KnowledgeGraph


class TeacherService:
    """Service for teacher operations."""
    
    def __init__(self):
        self._kg = KnowledgeGraph()
    
    def create_teacher(
        self, 
        mode: str = "simple",
        config: Optional[Dict] = None
    ) -> object:
        """Create a teacher instance."""
        if mode == "llm" and config:
            try:
                return LLMTeacher(
                    self._kg,
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model", "gpt-3.5-turbo")
                )
            except Exception as e:
                print(f"Failed to create LLM teacher: {e}")
                return AITeacher(self._kg)
        
        return AITeacher(self._kg)
    
    def get_lesson_content(
        self, 
        teacher: object, 
        topic_name: str
    ) -> str:
        """Get lesson content for a topic."""
        topic = self._kg.get_topic_by_name(topic_name)
        if not topic:
            return "Topic not found"
        
        if isinstance(teacher, LLMTeacher):
            try:
                return teacher.get_lesson_content(topic)
            except Exception as e:
                return f"Error generating lesson: {str(e)}"
        
        return topic.content
    
    def evaluate_answer(
        self,
        teacher: object,
        topic_name: str,
        answer: str
    ) -> Dict[str, Any]:
        """Evaluate a student answer."""
        topic = self._kg.get_topic_by_name(topic_name)
        if not topic:
            return {
                "correct": False,
                "feedback": "Topic not found"
            }
        
        if isinstance(teacher, LLMTeacher):
            try:
                return teacher.evaluate_student_response(topic, answer)
            except Exception as e:
                return {
                    "correct": False,
                    "feedback": f"Error evaluating: {str(e)}"
                }
        
        # Simple evaluation
        is_correct = answer.lower() in ["true", "correct", "yes", "1"]
        return {
            "correct": is_correct,
            "feedback": (
                "✓ Correct!" if is_correct 
                else "✗ Incorrect. Try again!"
            )
        }
