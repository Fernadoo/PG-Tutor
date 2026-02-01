"""
Student simulation for the AI tutoring system.

This module simulates student behavior based on their true knowledge level
and the difficulty of topics being presented.
"""

import random
import numpy as np
from typing import Dict, Any, Optional
from knowledge_graph import Topic


class Student:
    """
    Simulated student with a true knowledge level.

    The student has a true knowledge level (unknown to the teacher) and
    responds to topics based on how well their knowledge matches the topic difficulty.
    """

    def __init__(self, true_level: float, performance_variance: float = 0.5):
        """
        Initialize the student.

        Args:
            true_level: The student's true knowledge level (unknown to teacher)
            performance_variance: Controls how much student performance varies
        """
        self.true_level = true_level
        self.performance_variance = performance_variance
        self.total_questions = 0
        self.correct_answers = 0
        self.topic_history = []

    def answer_question(self, topic: Topic) -> bool:
        """
        Simulate the student answering a question about a topic.

        The probability of answering correctly decreases as the topic difficulty
        increases relative to the student's true knowledge level.

        Args:
            topic: The topic being tested

        Returns:
            True if student answers correctly, False otherwise
        """
        # Calculate probability of correct answer based on difficulty vs knowledge
        difficulty_diff = abs(topic.level - self.true_level)

        # Base probability decreases with difficulty difference
        base_prob = max(0.1, 1.0 - difficulty_diff * 0.2)

        # Add some randomness based on variance
        prob_correct = max(0.0, min(1.0, base_prob + random.gauss(0, self.performance_variance)))

        # Generate random outcome
        answer_correct = random.random() < prob_correct

        # Track statistics
        self.total_questions += 1
        if answer_correct:
            self.correct_answers += 1

        self.topic_history.append({
            'topic': topic.name,
            'level': topic.level,
            'difficulty': topic.difficulty,
            'correct': answer_correct,
            'probability': prob_correct
        })

        return answer_correct

    def get_accuracy(self) -> float:
        """
        Get the student's overall accuracy.

        Returns:
            Accuracy as a fraction (0.0 to 1.0)
        """
        if self.total_questions == 0:
            return 0.0
        return self.correct_answers / self.total_questions

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of student performance.

        Returns:
            Dictionary with performance metrics
        """
        return {
            'true_level': self.true_level,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy': self.get_accuracy(),
            'topic_history': self.topic_history[-5:]  # Last 5 topics
        }

    def reset(self):
        """
        Reset student statistics.
        """
        self.total_questions = 0
        self.correct_answers = 0
        self.topic_history = []