"""
Session Manager for Streamlit Web App

Handles initialization, state management, and session logic.
"""

import streamlit as st
import sys
import os
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from teacher import AITeacher, LLMTeacher
from knowledge_graph import KnowledgeGraph


def initialize_session():
    """Initialize the tutoring session."""
    # Create knowledge graph
    knowledge_graph = KnowledgeGraph()
    
    # Check for user-provided API config from session state (from entrance setup)
    llm_config = st.session_state.get('llm_config')
    use_llm = st.session_state.get('use_llm', False)
    
    # If no user config, try to load from config.yaml (for backwards compatibility)
    if not llm_config:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'llm' in config and config['llm'].get('api_key'):
                        llm_config = config['llm']
                        use_llm = True
            except Exception:
                pass
    
    # Fallback to environment variables
    if not llm_config and os.environ.get('OPENAI_API_KEY'):
        llm_config = {
            'api_key': os.environ.get('OPENAI_API_KEY'),
            'base_url': os.environ.get('OPENAI_BASE_URL'),
            'model': 'gpt-3.5-turbo'
        }
        use_llm = True
    
    # Initialize teacher
    teacher = None
    if use_llm and llm_config:
        try:
            teacher = LLMTeacher(knowledge_graph, **llm_config)
        except Exception as e:
            st.warning(f"Could not initialize LLM Teacher: {e}. Using standard teacher.")
    
    if teacher is None:
        teacher = AITeacher(knowledge_graph)
    
    # Get first topic
    current_topic = knowledge_graph.get_random_topic_at_level(0)
    
    # Store in session state
    st.session_state.teacher = teacher
    st.session_state.knowledge_graph = knowledge_graph
    st.session_state.current_topic = current_topic
    st.session_state.session_initialized = True
    st.session_state.use_llm = use_llm
    st.session_state.waiting_for_answer = True
    st.session_state.belief_history = []
    st.session_state.topic_history = []
    st.session_state.session_data = {
        'timestamp': __import__('datetime').datetime.now().strftime("%Y%m%d%H%M%S"),
        'sessions': []
    }


def get_current_topic():
    """Get the current topic being taught."""
    return st.session_state.get('current_topic')


def submit_answer(answer, use_llm=False):
    """
    Submit an answer and update the model.
    
    Args:
        answer: Either bool (simple mode) or str (LLM mode)
        use_llm: Whether to use LLM evaluation
    """
    teacher = st.session_state.teacher
    topic = st.session_state.current_topic
    
    feedback = {
        'correct': False,
        'feedback': '',
        'llm_evaluation': None
    }
    
    if use_llm and isinstance(answer, str):
        # LLM evaluation
        try:
            evaluation = teacher.evaluate_student_response(topic, answer)
            feedback['correct'] = evaluation.get('correct', False)
            feedback['feedback'] = evaluation.get('feedback', 'No feedback provided.')
            feedback['llm_evaluation'] = evaluation
            correct = feedback['correct']
        except Exception as e:
            feedback['feedback'] = f"Error during evaluation: {str(e)}"
            correct = False
    else:
        # Simple binary evaluation
        correct = bool(answer)
        if correct:
            feedback['correct'] = True
            feedback['feedback'] = "✓ Good work! You're mastering this topic."
        else:
            feedback['correct'] = False
            feedback['feedback'] = "✗ That's okay! Learning takes practice. Consider reviewing the topic content."
    
    # Update teacher's belief
    teacher.observe_student_performance(topic, correct)
    
    # Get current belief
    belief = teacher.get_current_belief()
    estimated_level = int(belief['expected_lambda'])
    
    # Store history
    st.session_state.belief_history.append({
        'topic': topic.name,
        'correct': correct,
        'belief': belief.copy()
    })
    
    st.session_state.topic_history.append({
        'topic': topic.name,
        'level': topic.level,
        'correct': correct
    })
    
    # Record session data
    session_record = {
        'topic': topic.name,
        'topic_level': topic.level,
        'user_correct': correct,
        'teacher_belief': belief.copy()
    }
    st.session_state.session_data['sessions'].append(session_record)
    
    # Store feedback for display
    st.session_state.last_feedback = feedback
    
    # Select next topic
    next_topic = teacher.get_next_topic(estimated_level)
    if next_topic:
        st.session_state.current_topic = next_topic
    else:
        # Fallback to current level
        st.session_state.current_topic = st.session_state.knowledge_graph.get_random_topic_at_level(estimated_level)


def get_session_summary():
    """Get summary of the current session."""
    teacher = st.session_state.get('teacher')
    if teacher:
        summary = teacher.get_session_summary()
        # Ensure all expected keys are present
        if 'message' in summary:
            # Teacher returned a message, we need to provide default values
            return {
                'total_sessions': 0,
                'correct_answers': 0,
                'accuracy': 0,
                'last_estimated_lambda': 0.0,
                'message': summary.get('message', 'No session data yet')
            }
        return summary
    return {
        'total_sessions': 0,
        'correct_answers': 0,
        'accuracy': 0,
        'last_estimated_lambda': 0.0,
        'message': 'No session data yet'
    }


def reset_session():
    """Reset the current session."""
    keys_to_clear = [
        'teacher', 'knowledge_graph', 'current_topic', 'session_initialized',
        'use_llm', 'waiting_for_answer', 'belief_history', 'topic_history',
        'session_data', 'last_feedback', 'llm_config', 'api_configured'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Also clear any cached LLM content
    llm_content_keys = [key for key in st.session_state.keys() if key.startswith('llm_content_')]
    for key in llm_content_keys:
        del st.session_state[key]


def save_session_to_file():
    """Save the current session data to a JSON file."""
    import json
    import os
    from datetime import datetime
    
    if 'session_data' not in st.session_state:
        return None
    
    # Ensure record directory exists
    record_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'record')
    os.makedirs(record_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"web_session_{timestamp}.json"
    filepath = os.path.join(record_dir, filename)
    
    # Prepare data
    data = st.session_state.session_data.copy()
    data['total_sessions'] = len(data['sessions'])
    data['final_summary'] = get_session_summary()
    
    # Save
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return filepath
    except Exception:
        return None
