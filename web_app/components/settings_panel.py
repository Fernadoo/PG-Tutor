"""
Settings Panel Component

Configuration options for the tutoring session.
"""

import streamlit as st
import os


def render_settings_panel():
    """Render the settings panel in the sidebar."""
    # Check current mode
    use_llm = st.session_state.get('use_llm', False)
    
    # Show current mode status
    if use_llm:
        st.success("✓ AI Tutor Mode (LLM)")
        
        # Show API configuration info (masked)
        llm_config = st.session_state.get('llm_config', {})
        if llm_config:
            api_key = llm_config.get('api_key', '')
            if api_key:
                masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                st.markdown(f"**API Key:** `{masked_key}`")
            
            base_url = llm_config.get('base_url', '')
            if base_url:
                st.markdown(f"**Base URL:** `{base_url}`")
            
            model = llm_config.get('model', 'gpt-3.5-turbo')
            st.markdown(f"**Model:** `{model}`")
    else:
        st.info("✓ Simple Mode (Binary answers)")
    
    st.markdown("---")
    
    # Reconfigure button
    if st.button("🔧 Reconfigure API / Mode", type="secondary", use_container_width=True):
        # Clear API configuration to go back to entrance screen
        if 'api_configured' in st.session_state:
            del st.session_state.api_configured
        if 'llm_config' in st.session_state:
            del st.session_state.llm_config
        if 'session_initialized' in st.session_state:
            del st.session_state.session_initialized
        st.rerun()
    
    st.markdown("---")
    
    # Session settings
    st.markdown("#### Session Settings")
    
    # Number of sessions
    num_sessions = st.number_input(
        "Target Questions",
        min_value=3,
        max_value=20,
        value=5,
        help="Number of questions per session"
    )
    st.session_state.target_questions = num_sessions
    
    # Difficulty preference
    difficulty_mode = st.selectbox(
        "Difficulty Mode",
        options=["Adaptive (Recommended)", "Easy", "Medium", "Hard"],
        index=0,
        help="How the system selects topics"
    )
    st.session_state.difficulty_mode = difficulty_mode
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **AI Tutoring System v1.0**
        
        This system uses Bayesian inference to:
        - Estimate your knowledge level
        - Adaptively select topics
        - Optimize your learning path
        
        Powered by:
        - Poisson-Gamma conjugate priors
        - Hierarchical knowledge graphs
        - LLM-generated content (optional)
        
        **Security Note:** Your API key is stored only in memory for this session and is never saved to disk.
        """)
