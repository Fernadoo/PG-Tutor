"""
Streamlit Web Interface for AI Tutoring System

Main application entry point for the web-based tutoring interface.
"""

import streamlit as st
import sys
import os
import json
import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.lesson_view import render_lesson_view, render_lesson_content_llm
from components.progress_chart import render_progress_chart
from components.knowledge_graph_viz import render_knowledge_graph
from components.session_history import render_session_history
from components.settings_panel import render_settings_panel
from components.entrance_setup import render_entrance_setup, check_api_configured
from utils.session_manager import (
    initialize_session,
    get_current_topic,
    submit_answer,
    get_session_summary,
    reset_session
)
from teacher import LLMTeacher

# Page configuration
st.set_page_config(
    page_title="AI Tutoring System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .topic-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .correct-answer {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .stat-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with session info and controls."""
    with st.sidebar:
        st.markdown("## 🎓 AI Tutor")
        
        # Session stats (only show if session is initialized)
        if 'session_initialized' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Session Stats")
            
            summary = get_session_summary()
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['total_sessions']}</div>
                    <div class="stat-label">Questions</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                accuracy = summary.get('accuracy', 0) * 100
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{accuracy:.0f}%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Current level
            if 'last_estimated_lambda' in summary:
                level = summary['last_estimated_lambda']
                st.markdown(f"**Estimated Level:** {level:.2f}")
                
                # Progress bar for level
                level_progress = min(level / 5.0, 1.0)
                st.progress(level_progress)
            
            st.markdown("---")
            
            # Reset button
            if st.button("🔄 Reset Session", type="secondary"):
                reset_session()
                st.rerun()
        
        # Settings (only show if API is configured)
        if check_api_configured():
            st.markdown("---")
            st.markdown("### ⚙️ Settings")
            render_settings_panel()


def render_main_content():
    """Render the main content area."""
    # Check if API/Mode is configured - if not, show entrance setup
    if not check_api_configured():
        render_entrance_setup()
        return
    
    # Header
    st.markdown('<div class="main-header">🤖 AI Tutoring System</div>', unsafe_allow_html=True)
    
    # Initialize session if not already done
    if 'session_initialized' not in st.session_state:
        st.info("👋 Welcome! Click 'Start Learning' below to begin your personalized tutoring session.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Learning", type="primary", use_container_width=True):
                initialize_session()
                st.rerun()
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📖 Lesson", "🕸️ Knowledge Graph", "📜 History"])
    
    with tab1:
        render_lesson_tab()
    
    with tab2:
        render_knowledge_graph()
    
    with tab3:
        render_session_history()


def render_lesson_tab():
    """Render the lesson tab with current topic and question."""
    current_topic = get_current_topic()
    
    if current_topic is None:
        st.error("No topic available. Please reset the session.")
        return
    
    # Topic info card
    st.markdown(f"""
    <div class="topic-card">
        <h3>📚 {current_topic.name}</h3>
        <p><strong>Level:</strong> {current_topic.level} | <strong>Difficulty:</strong> {current_topic.difficulty:.2f}/1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lesson content
    st.markdown("---")
    st.markdown("### 📝 Lesson Content")
    
    # Check if we should use LLM to generate content
    use_llm = st.session_state.get('use_llm', False)
    teacher = st.session_state.get('teacher')
    
    if use_llm and isinstance(teacher, LLMTeacher):
        # Generate lesson content using LLM
        # Use a key to track if we've already generated content for this topic
        content_key = f'llm_content_{current_topic.name}'
        
        if content_key not in st.session_state:
            with st.spinner("🤖 Generating personalized lesson..."):
                try:
                    lesson_content = teacher.get_lesson_content(current_topic)
                    st.session_state[content_key] = lesson_content
                    # Update topic content so evaluation has context
                    current_topic.content = lesson_content
                except Exception as e:
                    st.error(f"Error generating lesson: {str(e)}")
                    st.session_state[content_key] = current_topic.content
        
        # Display the generated content
        lesson_content = st.session_state.get(content_key, current_topic.content)
        render_lesson_content_llm(lesson_content)
    else:
        # Use static content for non-LLM mode
        render_lesson_view(current_topic)
    
    # Answer section
    st.markdown("---")
    st.markdown("### ✏️ Your Answer")
    
    # Check if we're waiting for an answer
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = True
    
    if st.session_state.waiting_for_answer:
        # Use LLM mode or simple mode based on configuration
        use_llm = st.session_state.get('use_llm', False)
        
        if use_llm:
            # LLM mode: text input for natural language answers
            answer = st.text_area(
                "Type your answer here:",
                height=150,
                placeholder="Enter your answer or explanation...",
                key="llm_answer"
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("📤 Submit Answer", type="primary"):
                    if answer.strip():
                        submit_answer(answer, use_llm=True)
                        st.session_state.waiting_for_answer = False
                        st.rerun()
                    else:
                        st.warning("Please enter an answer before submitting.")
        else:
            # Simple mode: binary choice
            st.markdown("Did you answer correctly?")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✓ Correct", type="primary"):
                    submit_answer(True, use_llm=False)
                    st.session_state.waiting_for_answer = False
                    st.rerun()
            
            with col2:
                if st.button("✗ Incorrect", type="secondary"):
                    submit_answer(False, use_llm=False)
                    st.session_state.waiting_for_answer = False
                    st.rerun()
            
            with col3:
                if st.button("📖 Show Content"):
                    st.markdown("---")
                    st.markdown("#### Topic Details")
                    st.write(current_topic.content)
                    if current_topic.prerequisites:
                        st.markdown("**Prerequisites:**")
                        for prereq in current_topic.prerequisites:
                            st.markdown(f"- {prereq}")
    else:
        # Show feedback
        if 'last_feedback' in st.session_state:
            feedback = st.session_state.last_feedback
            is_correct = feedback.get('correct', False)
            
            feedback_class = "correct-answer" if is_correct else "incorrect-answer"
            feedback_emoji = "✅" if is_correct else "❌"
            
            st.markdown(f"""
            <div class="topic-card {feedback_class}">
                <h4>{feedback_emoji} Feedback</h4>
                <p>{feedback.get('feedback', 'No feedback provided.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if feedback.get('llm_evaluation'):
                with st.expander("View LLM Evaluation Details"):
                    st.json(feedback['llm_evaluation'])
        
        # Progress visualization
        st.markdown("---")
        st.markdown("### 📊 Learning Progress")
        render_progress_chart()
        
        # Next question button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next Question", type="primary", use_container_width=True):
                st.session_state.waiting_for_answer = True
                if 'last_feedback' in st.session_state:
                    del st.session_state.last_feedback
                st.rerun()


def main():
    """Main application entry point."""
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()
