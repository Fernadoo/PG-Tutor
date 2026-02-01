"""
Knowledge graph structure for AI tutoring system.

This module implements a hierarchical representation of topics organized by difficulty levels.
Topics are arranged in levels where each level builds upon the previous one.
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Topic:
    """Represents a learning topic with difficulty and prerequisites."""

    name: str
    level: int
    difficulty: float  # Normalized difficulty score (0.0 to 1.0)
    prerequisites: List[str]  # Names of prerequisite topics
    content: str  # Brief description or content outline


class KnowledgeGraph:
    """
    Hierarchical knowledge graph for organizing learning topics.

    Topics are organized by difficulty levels, with each level containing
    multiple topics that build upon each other.
    """

    def __init__(self):
        """Initialize empty knowledge graph."""
        self.topics_by_level: Dict[int, List[Topic]] = defaultdict(list)
        self.topics_by_name: Dict[str, Topic] = {}
        self._build_sample_graph()

    def _build_sample_graph(self):
        """Build a sample knowledge graph for demonstration."""

        # Define sample topics organized by levels
        sample_topics = [
            # Level 0: Basic Concepts
            Topic("Introduction to Algebra", 0, 0.2, [], "Basic algebraic expressions and equations"),
            Topic("Variables and Expressions", 0, 0.3, [], "Understanding variables and evaluating expressions"),

            # Level 1: Elementary Operations
            Topic("Linear Equations", 1, 0.4, ["Introduction to Algebra"], "Solving linear equations with one variable"),
            Topic("Basic Inequalities", 1, 0.5, ["Variables and Expressions"], "Understanding and solving basic inequalities"),

            # Level 2: Intermediate Concepts
            Topic("Quadratic Equations", 2, 0.6, ["Linear Equations"], "Solving quadratic equations by factoring"),
            Topic("Systems of Equations", 2, 0.7, ["Linear Equations"], "Solving systems of linear equations"),

            # Level 3: Advanced Topics
            Topic("Polynomial Functions", 3, 0.8, ["Quadratic Equations"], "Understanding and working with polynomial functions"),
            Topic("Trigonometric Basics", 3, 0.9, ["Linear Equations", "Quadratic Equations"], "Introduction to sine, cosine, tangent"),

            # Level 4: Expert Level
            Topic("Calculus Fundamentals", 4, 0.95, ["Polynomial Functions", "Trigonometric Basics"], "Introduction to derivatives and integrals"),
        ]

        # Add topics to the graph
        for topic in sample_topics:
            self.add_topic(topic)

    def add_topic(self, topic: Topic):
        """
        Add a topic to the knowledge graph.

        Args:
            topic: Topic object to add
        """
        self.topics_by_level[topic.level].append(topic)
        self.topics_by_name[topic.name] = topic

    def get_topics_at_level(self, level: int) -> List[Topic]:
        """
        Get all topics at a specific difficulty level.

        Args:
            level: Difficulty level

        Returns:
            List of topics at that level
        """
        return self.topics_by_level.get(level, [])

    def get_all_levels(self) -> List[int]:
        """
        Get all difficulty levels in the knowledge graph.

        Returns:
            Sorted list of difficulty levels
        """
        return sorted(self.topics_by_level.keys())

    def get_random_topic_at_level(self, level: int) -> Optional[Topic]:
        """
        Get a random topic from a specific level.

        Args:
            level: Difficulty level

        Returns:
            Random topic at that level, or None if level is empty
        """
        topics = self.get_topics_at_level(level)
        return random.choice(topics) if topics else None

    def get_next_level_topics(self, current_level: int, max_levels_ahead: int = 2) -> List[Topic]:
        """
        Get topics from levels that are a few levels deeper than current.

        Args:
            current_level: Current student level
            max_levels_ahead: Maximum number of levels to advance

        Returns:
            List of appropriate next-level topics
        """
        next_levels = range(current_level + 1, min(current_level + max_levels_ahead + 1,
                                                  max(self.get_all_levels()) + 1))
        topics = []
        for level in next_levels:
            level_topics = self.get_topics_at_level(level)
            topics.extend(level_topics)
        return topics

    def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """
        Get a topic by its name.

        Args:
            name: Name of the topic

        Returns:
            Topic object or None if not found
        """
        return self.topics_by_name.get(name)

    def get_prerequisites(self, topic_name: str) -> List[str]:
        """
        Get prerequisite topics for a given topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List of prerequisite topic names
        """
        topic = self.get_topic_by_name(topic_name)
        return topic.prerequisites if topic else []

    def is_valid_prerequisite(self, topic_name: str, student_level: int) -> bool:
        """
        Check if a student has sufficient knowledge to tackle a topic.

        Args:
            topic_name: Name of the topic
            student_level: Current student level

        Returns:
            True if student can attempt the topic, False otherwise
        """
        topic = self.get_topic_by_name(topic_name)
        if not topic:
            return False

        # For simplicity, we'll assume the student can handle any topic at or below their level
        # In a more sophisticated model, we'd check specific prerequisites
        return topic.level <= student_level

    def get_topic_difficulty(self, topic_name: str) -> float:
        """
        Get the difficulty rating of a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            Difficulty rating (0.0 to 1.0)
        """
        topic = self.get_topic_by_name(topic_name)
        return topic.difficulty if topic else 0.0

    def get_hierarchical_structure(self) -> Dict[str, Any]:
        """
        Get the complete hierarchical structure of the knowledge graph.

        Returns:
            Dictionary representing the knowledge hierarchy
        """
        structure = {
            'levels': {},
            'total_topics': len(self.topics_by_name)
        }

        for level, topics in self.topics_by_level.items():
            structure['levels'][level] = [
                {
                    'name': topic.name,
                    'difficulty': topic.difficulty,
                    'prerequisites': topic.prerequisites,
                    'content': topic.content
                } for topic in topics
            ]

        return structure