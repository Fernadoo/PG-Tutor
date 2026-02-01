#!/usr/bin/env python3
"""
Command-line interface for the AI Tutoring System.

This script provides an interactive interface for running tutoring sessions
between a simulated student and the AI teacher.
"""

import argparse
import sys
import os
from typing import Optional

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teacher import AITeacher
from student import Student
from knowledge_graph import KnowledgeGraph


def run_tutoring_session(student_level: float, num_sessions: int = 5):
    """
    Run a complete tutoring session.

    Args:
        student_level: The student's true knowledge level
        num_sessions: Number of topics to teach
    """
    print("=== AI Tutoring System Demo ===")
    print(f"Student true knowledge level: {student_level}")
    print()

    # Initialize components
    knowledge_graph = KnowledgeGraph()
    teacher = AITeacher(knowledge_graph)
    student = Student(student_level)

    print("Starting tutoring session...")
    print("-" * 50)

    # Start with a topic at the student's level
    current_level = int(student_level)
    current_topic = knowledge_graph.get_random_topic_at_level(current_level)

    if not current_topic:
        # If no topic at current level, pick the lowest level topic
        levels = knowledge_graph.get_all_levels()
        if levels:
            current_topic = knowledge_graph.get_random_topic_at_level(levels[0])
        else:
            print("No topics available in knowledge graph!")
            return

    print(f"Initial topic: {current_topic.name}")
    print(f"Topic difficulty: {current_topic.difficulty:.2f}")
    print()

    # Run the specified number of sessions
    for i in range(num_sessions):
        print(f"--- Session {i+1} ---")

        # Student answers the question
        correct = student.answer_question(current_topic)
        print(f"Student answered {'correctly' if correct else 'incorrectly'}")

        # Teacher observes and updates belief
        teacher.observe_student_performance(current_topic, correct)

        # Get teacher's belief update
        belief = teacher.get_current_belief()
        print(f"Teacher's belief - Estimated λ: {belief['expected_lambda']:.2f}")

        # Get recommendation
        recommendation = teacher.get_recommendation()
        print(f"Recommendation: {recommendation}")

        # Get session summary
        summary = teacher.get_session_summary()
        print(f"Session accuracy: {summary['accuracy']:.2f}")

        # Select next topic
        next_topic = teacher.get_next_topic(int(belief['expected_lambda']))
        print(f"Next topic: {next_topic.name}")
        print()

        # Move to next topic
        current_topic = next_topic

    # Final summary
    print("=" * 50)
    print("SESSION SUMMARY")
    print("=" * 50)

    student_summary = student.get_performance_summary()
    print(f"Student true level: {student.true_level}")
    print(f"Student accuracy: {student_summary['accuracy']:.2f}")

    teacher_summary = teacher.get_session_summary()
    print(f"Teacher's final λ estimate: {teacher_summary['last_estimated_lambda']:.2f}")
    print(f"Total sessions: {teacher_summary['total_sessions']}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='AI Tutoring System')
    parser.add_argument('--level', type=float, default=1.0,
                       help='Student\'s true knowledge level (default: 1.0)')
    parser.add_argument('--sessions', type=int, default=5,
                       help='Number of tutoring sessions (default: 5)')

    args = parser.parse_args()

    try:
        run_tutoring_session(args.level, args.sessions)
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during session: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()