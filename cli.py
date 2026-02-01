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
import json
import datetime
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


def run_interactive_session(num_sessions: int = 5, no_prompt: bool = False):
    """
    Run an interactive tutoring session with the user as the student.

    Args:
        num_sessions: Number of topics to cover
        no_prompt: Skip "Press Enter" prompts for automated testing
    """
    # Create timestamp for log files
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = os.path.join("record", f"{timestamp}.log")
    json_file_path = os.path.join("record", f"{timestamp}.json")

    # Ensure record directory exists
    os.makedirs("record", exist_ok=True)

    # Data structure for JSON storage
    session_data = {
        'timestamp': timestamp,
        'num_sessions': num_sessions,
        'no_prompt': no_prompt,
        'sessions': [],
        'final_summary': None,
        'teacher_belief_history': []
    }

    def log_message(message: str):
        """Helper to log messages to both console and file."""
        print(message)
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(message + "\n")

    log_message("\n" + "="*60)
    log_message("              AI TUTORING SYSTEM")
    log_message("="*60)
    log_message("\nWelcome! I'll be your AI tutor today.")
    log_message("I'll ask you questions and adapt to your learning progress.")
    log_message("Based on your answers, I'll adjust the difficulty level.")
    log_message("\nLet's get started!")

    # Initialize components
    knowledge_graph = KnowledgeGraph()
    teacher = AITeacher(knowledge_graph)

    # Start with level 0 topics
    current_level = 0
    current_topic = knowledge_graph.get_random_topic_at_level(current_level)

    if not current_topic:
        log_message("No topics available. Something went wrong with the knowledge graph.")
        return

    session_counter = 0

    while session_counter < num_sessions:
        session_counter += 1
        log_message("\n" + "-"*60)
        log_message(f"SESSION {session_counter}/{num_sessions}")
        log_message("-"*60)

        # Show topic and get feedback
        while True:
            feedback = get_user_feedback(current_topic.name, current_topic.difficulty)

            if feedback == "show_content":
                show_topic_content(current_topic)
                # Log content view
                log_message(f"User viewed content for: {current_topic.name}")
                continue
            else:
                correct = feedback
                break

        # Teacher observes and updates belief
        teacher.observe_student_performance(current_topic, correct)

        # Get teacher's belief update
        belief = teacher.get_current_belief()
        estimated_level = int(belief['expected_lambda'])

        # Record session data for JSON
        session_record = {
            'session_number': session_counter,
            'topic': current_topic.name,
            'topic_level': current_topic.level,
            'topic_difficulty': current_topic.difficulty,
            'user_correct': correct,
            'teacher_belief': belief.copy()
        }
        session_data['sessions'].append(session_record)
        session_data['teacher_belief_history'].append(belief.copy())

        # Provide feedback to user
        log_message("\n" + "-"*30)
        log_message("FEEDBACK")
        log_message("-"*30)
        if correct:
            log_message("✓ Good work! You're mastering this topic.")
        else:
            log_message("✗ That's okay! Learning takes practice.")
            log_message("   Consider reviewing the topic content again.")

        # Show teacher's assessment
        log_message(f"\nTeacher's assessment:")
        log_message(f"  Estimated knowledge level: {belief['expected_lambda']:.2f}")

        # Get and show recommendation
        recommendation = teacher.get_recommendation()
        log_message(f"  Recommendation: {recommendation}")

        # Select next topic based on assessment
        next_topic = teacher.get_next_topic(estimated_level)

        if next_topic:
            # Brief introduction to next topic
            log_message(f"\nNext topic: {next_topic.name}")
            log_message(f"  Level: {next_topic.level}")
            log_message(f"  Difficulty: {next_topic.difficulty:.2f}/1.0")

            current_topic = next_topic
        else:
            log_message("\nNo more topics available at appropriate level.")
            log_message("Let's review a topic from current level.")
            current_topic = knowledge_graph.get_random_topic_at_level(estimated_level)
            if current_topic:
                log_message(f"Review topic: {current_topic.name}")

        # Show progress
        if session_counter < num_sessions and not no_prompt:
            log_message("\nPress Enter to continue to next session...")
            try:
                input()
            except KeyboardInterrupt:
                log_message("\n\nSession interrupted.")
                break

    # Final summary
    log_message("\n" + "="*60)
    log_message("SESSION COMPLETE")
    log_message("="*60)

    teacher_summary = teacher.get_session_summary()
    if teacher_summary.get('message'):
        log_message(teacher_summary['message'])
    else:
        log_message(f"Total sessions: {teacher_summary['total_sessions']}")
        log_message(f"Your accuracy: {teacher_summary['accuracy']:.2%}")
        log_message(f"Final estimated level: {teacher_summary['last_estimated_lambda']:.2f}")

        # Add summary to session data
        session_data['final_summary'] = teacher_summary
        session_data['final_estimated_level'] = teacher_summary['last_estimated_lambda']
        session_data['user_accuracy'] = teacher_summary['accuracy']

        # Personalized feedback
        final_level = teacher_summary['last_estimated_lambda']
        if final_level < 1.0:
            log_message("\nKeep practicing! You're building a strong foundation.")
        elif final_level < 2.5:
            log_message("\nGood progress! You're developing solid intermediate skills.")
        elif final_level < 4.0:
            log_message("\nExcellent work! You've reached an advanced level.")
        else:
            log_message("\nOutstanding! You're demonstrating expert-level knowledge.")

    log_message("\nThank you for learning with the AI Tutoring System!")
    log_message("="*60)

    # Save JSON data
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)
        log_message(f"\nSession data saved to: {json_file_path}")
    except Exception as e:
        log_message(f"\nWarning: Could not save JSON data: {e}")

    log_message(f"Session log saved to: {log_file_path}")


def main():
    """Main entry point for the interactive CLI."""
    parser = argparse.ArgumentParser(description='Interactive AI Tutoring System')
    parser.add_argument('--sessions', type=int, default=5,
                       help='Number of tutoring sessions (default: 5)')
    parser.add_argument('--level', type=int, default=None,
                       help='Starting level (optional, system will adapt automatically)')
    parser.add_argument('--no-prompt', action='store_true',
                       help='Skip "Press Enter" prompts for automated testing')

    args = parser.parse_args()

    try:
        run_interactive_session(args.sessions, args.no_prompt)
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during session: {e}")
        print("Please report this issue.")
        sys.exit(1)


if __name__ == "__main__":
    main()