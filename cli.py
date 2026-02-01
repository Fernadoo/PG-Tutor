#!/usr/bin/env python3
"""
Interactive command-line interface for the AI Tutoring System.

This script provides an interactive interface where users (students)
interact directly with the AI teacher.
"""

import argparse
import sys
import os
import random
import time
from typing import Optional, Dict, Any

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teacher import AITeacher
from knowledge_graph import KnowledgeGraph


def get_user_feedback(topic_name: str, difficulty: float) -> bool:
    """
    Ask the user if they answered correctly.

    Args:
        topic_name: Name of the topic
        difficulty: Difficulty rating of the topic

    Returns:
        True if user answered correctly, False otherwise
    """
    print(f"\nTopic: {topic_name}")
    print(f"Difficulty: {difficulty:.2f}/1.0")
    print("Did you answer correctly?")
    print("1. Yes")
    print("2. No")
    print("3. Partially (some correct)")
    print("4. Show topic content")

    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice == "1":
                return True
            elif choice == "2":
                return False
            elif choice == "3":
                # For partially correct, we'll treat it as incorrect for now
                print("Treating partial correctness as needs more practice.")
                return False
            elif choice == "4":
                return "show_content"
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n\nSession interrupted.")
            sys.exit(0)


def show_topic_content(topic) -> None:
    """
    Display detailed content about a topic.

    Args:
        topic: Topic object to display
    """
    print("\n" + "="*50)
    print(f"TOPIC: {topic.name}")
    print(f"LEVEL: {topic.level}")
    print(f"DIFFICULTY: {topic.difficulty:.2f}/1.0")
    print("\nCONTENT:")
    print(topic.content)
    print("\nPREREQUISITES:")
    if topic.prerequisites:
        for prereq in topic.prerequisites:
            print(f"  - {prereq}")
    else:
        print("  None (introductory topic)")
    print("="*50 + "\n")


def run_interactive_session(num_sessions: int = 5):
    """
    Run an interactive tutoring session with the user as the student.

    Args:
        num_sessions: Number of topics to cover
    """
    print("\n" + "="*60)
    print("              AI TUTORING SYSTEM")
    print("="*60)
    print("\nWelcome! I'll be your AI tutor today.")
    print("I'll ask you questions and adapt to your learning progress.")
    print("Based on your answers, I'll adjust the difficulty level.")
    print("\nLet's get started!")

    # Initialize components
    knowledge_graph = KnowledgeGraph()
    teacher = AITeacher(knowledge_graph)

    # Start with level 0 topics
    current_level = 0
    current_topic = knowledge_graph.get_random_topic_at_level(current_level)

    if not current_topic:
        print("No topics available. Something went wrong with the knowledge graph.")
        return

    session_counter = 0

    while session_counter < num_sessions:
        session_counter += 1
        print("\n" + "-"*60)
        print(f"SESSION {session_counter}/{num_sessions}")
        print("-"*60)

        # Show topic and get feedback
        while True:
            feedback = get_user_feedback(current_topic.name, current_topic.difficulty)

            if feedback == "show_content":
                show_topic_content(current_topic)
                continue
            else:
                correct = feedback
                break

        # Teacher observes and updates belief
        teacher.observe_student_performance(current_topic, correct)

        # Get teacher's belief update
        belief = teacher.get_current_belief()
        estimated_level = int(belief['expected_lambda'])

        # Provide feedback to user
        print("\n" + "-"*30)
        print("FEEDBACK")
        print("-"*30)
        if correct:
            print("✓ Good work! You're mastering this topic.")
        else:
            print("✗ That's okay! Learning takes practice.")
            print("   Consider reviewing the topic content again.")

        # Show teacher's assessment
        print(f"\nTeacher's assessment:")
        print(f"  Estimated knowledge level: {belief['expected_lambda']:.2f}")

        # Get and show recommendation
        recommendation = teacher.get_recommendation()
        print(f"  Recommendation: {recommendation}")

        # Select next topic based on assessment
        next_topic = teacher.get_next_topic(estimated_level)

        if next_topic:
            # Brief introduction to next topic
            print(f"\nNext topic: {next_topic.name}")
            print(f"  Level: {next_topic.level}")
            print(f"  Difficulty: {next_topic.difficulty:.2f}/1.0")

            current_topic = next_topic
        else:
            print("\nNo more topics available at appropriate level.")
            print("Let's review a topic from current level.")
            current_topic = knowledge_graph.get_random_topic_at_level(estimated_level)
            if current_topic:
                print(f"Review topic: {current_topic.name}")

        # Show progress
        if session_counter < num_sessions:
            print("\nPress Enter to continue to next session...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n\nSession interrupted.")
                break

    # Final summary
    print("\n" + "="*60)
    print("SESSION COMPLETE")
    print("="*60)

    teacher_summary = teacher.get_session_summary()
    if teacher_summary.get('message'):
        print(teacher_summary['message'])
    else:
        print(f"Total sessions: {teacher_summary['total_sessions']}")
        print(f"Your accuracy: {teacher_summary['accuracy']:.2%}")
        print(f"Final estimated level: {teacher_summary['last_estimated_lambda']:.2f}")

        # Personalized feedback
        final_level = teacher_summary['last_estimated_lambda']
        if final_level < 1.0:
            print("\nKeep practicing! You're building a strong foundation.")
        elif final_level < 2.5:
            print("\nGood progress! You're developing solid intermediate skills.")
        elif final_level < 4.0:
            print("\nExcellent work! You've reached an advanced level.")
        else:
            print("\nOutstanding! You're demonstrating expert-level knowledge.")

    print("\nThank you for learning with the AI Tutoring System!")
    print("="*60)


def main():
    """Main entry point for the interactive CLI."""
    parser = argparse.ArgumentParser(description='Interactive AI Tutoring System')
    parser.add_argument('--sessions', type=int, default=5,
                       help='Number of tutoring sessions (default: 5)')
    parser.add_argument('--level', type=int, default=None,
                       help='Starting level (optional, system will adapt automatically)')

    args = parser.parse_args()

    try:
        run_interactive_session(args.sessions)
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during session: {e}")
        print("Please report this issue.")
        sys.exit(1)


if __name__ == "__main__":
    main()