"""
AI Teacher implementation for the tutoring system.

This module contains the core logic for the AI teacher that makes decisions
based on Bayesian updates of student knowledge levels.
"""

import random
import numpy as np
import json
import re
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from typing import List, Dict, Any, Optional
from bayesian_model import BayesianKnowledgeModel
from knowledge_graph import KnowledgeGraph, Topic


class AITeacher:
    """
    AI Teacher that adapts instruction based on student performance.

    Uses Bayesian inference to model student knowledge and selects
    appropriate topics based on the student's estimated knowledge level.
    """

    def __init__(self, knowledge_graph: KnowledgeGraph,
                 initial_alpha: float = 1.0, initial_beta: float = 1.0):
        """
        Initialize the AI teacher.

        Args:
            knowledge_graph: Knowledge graph containing topics
            initial_alpha: Initial shape parameter for Gamma prior
            initial_beta: Initial rate parameter for Gamma prior
        """
        self.knowledge_graph = knowledge_graph
        self.bayesian_model = BayesianKnowledgeModel(initial_alpha, initial_beta)
        self.current_student_level = 0
        self.session_history = []

    def observe_student_performance(self, topic: Topic, correct: bool) -> None:
        """
        Observe a student's performance on a topic.

        This simulates the teacher observing whether the student answered
        correctly or incorrectly on a given topic.

        Args:
            topic: The topic that was tested
            correct: Whether the student answered correctly
        """
        # For simplicity, we'll map correctness to a level observation
        # In a more sophisticated model, we'd have a more nuanced mapping
        if correct:
            # Student demonstrated mastery of the topic
            # Successful answer suggests student can handle this level
            observation = topic.level + 1
        else:
            # Student struggled with the topic
            # Failed answer suggests student might be below this level
            observation = max(0, topic.level - 1)

        # Update the Bayesian model with this observation
        self.bayesian_model.update_belief(np.array([observation]))

        # Record session
        self.session_history.append({
            'topic': topic.name,
            'level': topic.level,
            'correct': correct,
            'observed_level': observation,
            'estimated_lambda': self.bayesian_model.get_expected_lambda()
        })

    def get_next_topic(self, current_level: int) -> Optional[Topic]:
        """
        Select the next appropriate topic for the student.

        Based on the current student level and Bayesian belief about their
        knowledge, select a topic that is slightly more challenging.

        Args:
            current_level: Current estimated student level

        Returns:
            Next topic to present, or None if no suitable topic found
        """
        # Determine how much to advance based on current level
        # If current_level is very low (beginner), we should be more conservative
        if current_level <= 1:
            # For beginners, only advance 1 level at most
            levels_ahead = 1
        else:
            # For more advanced students, can advance 1-2 levels
            levels_ahead = random.randint(1, 2)

        # Get potential topics from the next few levels
        next_level_topics = self.knowledge_graph.get_next_level_topics(
            current_level, max_levels_ahead=levels_ahead
        )

        # Filter topics that are accessible based on student level
        accessible_topics = [
            topic for topic in next_level_topics
            if self.knowledge_graph.is_valid_prerequisite(topic.name, current_level)
        ]

        # Return a random accessible topic
        if accessible_topics:
            return random.choice(accessible_topics)
        else:
            # If no topics are available at next level, try topics at current level
            current_level_topics = self.knowledge_graph.get_topics_at_level(current_level)
            if current_level_topics:
                return random.choice(current_level_topics)
            else:
                # If no topics at current level, try any available topics
                all_levels = self.knowledge_graph.get_all_levels()
                for level in all_levels:
                    topics = self.knowledge_graph.get_topics_at_level(level)
                    if topics:
                        return random.choice(topics)
                return None

    def get_current_belief(self) -> Dict[str, Any]:
        """
        Get the current Bayesian belief about the student's knowledge.

        Returns:
            Dictionary with current belief information
        """
        belief = self.bayesian_model.get_posterior_distribution()
        belief['current_level_estimate'] = self.bayesian_model.get_expected_lambda()
        belief['session_history'] = len(self.session_history)
        return belief

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current teaching session.

        Returns:
            Summary of the session including statistics
        """
        if not self.session_history:
            return {'message': 'No session data yet'}

        total_sessions = len(self.session_history)
        correct_answers = sum(1 for s in self.session_history if s['correct'])
        accuracy = correct_answers / total_sessions if total_sessions > 0 else 0

        return {
            'total_sessions': total_sessions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'last_estimated_lambda': self.bayesian_model.get_expected_lambda(),
            'session_history': self.session_history[-5:]  # Last 5 sessions
        }

    def reset_session(self):
        """
        Reset the teacher's session state.
        """
        self.bayesian_model = BayesianKnowledgeModel()
        self.current_student_level = 0
        self.session_history = []

    def get_recommendation(self) -> str:
        """
        Get a recommendation based on current belief.

        Returns:
            Text recommendation for the teacher
        """
        lambda_estimate = self.bayesian_model.get_expected_lambda()
        if lambda_estimate < 0.5:
            return "Student is at a beginner level. Focus on foundational concepts."
        elif lambda_estimate < 1.5:
            return "Student is progressing well with basic topics."
        elif lambda_estimate < 2.5:
            return "Student is developing intermediate skills. Progress to more complex concepts."
        elif lambda_estimate < 3.5:
            return "Student has solid knowledge. Challenge with advanced topics."
        else:
            return "Student is demonstrating expert-level understanding. Consider specialized topics."


class LLMTeacher(AITeacher):
    """
    LLM-based Teacher that uses a Large Language Model to interact with students.
    """

    def __init__(self, knowledge_graph: KnowledgeGraph, api_key: str, base_url: str = None,
                 model: str = "gpt-3.5-turbo", initial_alpha: float = 1.0, initial_beta: float = 1.0):
        """
        Initialize the LLM teacher.

        Args:
            knowledge_graph: Knowledge graph containing topics
            api_key: OpenAI API key
            base_url: Optional base URL for API
            model: Model name to use
            initial_alpha: Initial shape parameter for Gamma prior
            initial_beta: Initial rate parameter for Gamma prior
        """
        super().__init__(knowledge_graph, initial_alpha, initial_beta)
        if OpenAI is None:
            raise ImportError("The 'openai' library is required for LLMTeacher.")

        print(api_key, base_url)

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def get_lesson_content(self, topic: Topic) -> str:
        """
        Generate lesson content for a topic using LLM, adapted to student level.

        Args:
            topic: The topic to teach

        Returns:
            Generated lesson content string
        """
        student_level = self.bayesian_model.get_expected_lambda()
        system_prompt = f"""
        You are an AI Tutor teaching {topic.name} (Level {topic.level}).
        The student's estimated skill level is {student_level:.2f} (on a scale of 0-5).
        
        Topic Description: {topic.content}
        
        总是用中文回复
        """
        
        user_prompt = """
        Please provide a concise lesson explanation and a practice question suitable for this student's level.
        The explanation should be clear and engaging.
        The question should test their understanding of the concept.
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model, # 替换模型 id
                messages=[
                    {
                    "role": "system",
                    "content": system_prompt
                    },    
                    {
                    "role": "user",
                    "content": user_prompt
                    }
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating lesson content: {str(e)}\n\nDefault Content: {topic.content}"

    def evaluate_student_response(self, topic: Topic, student_response: str) -> Dict[str, Any]:
        """
        Evaluate student's natural language response using LLM.

        Args:
            topic: The topic being tested
            student_response: The student's answer

        Returns:
            Dictionary with 'correct' (bool) and 'feedback' (str)
        """
        system_prompt = f"""
        Topic: {topic.name}
        Topic Content: {topic.content}
        Student Answer: {student_response}
        
        总是用中文回复
        
        Evaluate if the student's answer is correct based on the topic.
        Return a JSON object with:
        - "correct": boolean (true if the answer demonstrates understanding, false otherwise)
        - "feedback": string (brief, constructive feedback explaining why it's correct or incorrect)
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict but helpful tutor. Output valid JSON only."},
                    {"role": "user", "content": system_prompt}
                ],
            )
            content = completion.choices[0].message.content
            print(content)
            
            # Extract JSON using regex
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # If no JSON found, try to parse the whole content
                return json.loads(content)
        except Exception as e:
            # Fallback for error or non-JSON response
            return {
                "correct": False,
                "feedback": f"Could not evaluate response automatically. Error: {str(e)}"
            }
