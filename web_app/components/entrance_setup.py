"""
Entrance/Setup Component

Initial setup screen for users to configure API credentials before starting.
"""

import streamlit as st
import os
import yaml


def get_default_config():
    """Get default configuration values from config.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    defaults = {
        'base_url': 'https://api.openai.com/v1',
        'model': 'gpt-3.5-turbo'
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'llm' in config:
                    llm_config = config['llm']
                    if llm_config.get('base_url'):
                        defaults['base_url'] = llm_config['base_url']
                    if llm_config.get('model'):
                        defaults['model'] = llm_config['model']
        except Exception:
            pass
    
    return defaults


def render_entrance_setup():
    """Render the entrance setup screen for API configuration."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🎓 Welcome to AI Tutoring System</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Personalized learning powered by Bayesian AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get default values from config
    defaults = get_default_config()
    
    # Create columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Configure Your API Access")
        st.info("""
        To use the AI tutor with LLM-generated content, please provide your API credentials.
        Your API key will only be stored in memory for this session and will not be saved to disk.
        """)
        
        # API Key input
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="Enter your OpenAI API key (sk-...)",
            help="Your API key is kept secure and only used for this session"
        )
        
        # Base URL input with default
        base_url = st.text_input(
            "Base URL (optional)",
            value=defaults.get('base_url', 'https://api.openai.com/v1'),
            placeholder="https://api.openai.com/v1",
            help="The API endpoint URL. Change this if using a custom or proxy server."
        )
        
        # Model selection
        model = st.selectbox(
            "Model",
            options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "DeepSeek-V3"],
            index=0,
            help="Select the AI model to use for generating lessons"
        )
        
        # Mode selection
        st.markdown("### 📚 Select Learning Mode")
        
        mode_col1, mode_col2 = st.columns(2)
        
        with mode_col1:
            st.markdown("""
            **🤖 AI Tutor Mode**
            - LLM-generated personalized lessons
            - Natural language answers
            - Adaptive explanations
            """)
            llm_mode = st.button("🚀 Start with AI Tutor", type="primary", use_container_width=True)
        
        with mode_col2:
            st.markdown("""
            **✏️ Simple Mode**
            - Binary correct/incorrect
            - Static topic content
            - No API key required
            """)
            simple_mode = st.button("📖 Start Simple Mode", type="secondary", use_container_width=True)
        
        # Handle mode selection
        if llm_mode:
            if not api_key or not api_key.strip():
                st.error("⚠️ Please enter an API key to use AI Tutor mode.")
                return None
            
            # Store configuration in session state
            st.session_state.llm_config = {
                'api_key': api_key.strip(),
                'base_url': base_url.strip() if base_url else defaults.get('base_url'),
                'model': model
            }
            st.session_state.use_llm = True
            st.session_state.api_configured = True
            st.rerun()
        
        if simple_mode:
            # Simple mode doesn't need API key
            st.session_state.llm_config = None
            st.session_state.use_llm = False
            st.session_state.api_configured = True
            st.rerun()
        
        # Divider
        st.markdown("---")
        
        # Help section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **How to get an API Key:**
            1. Visit [OpenAI Platform](https://platform.openai.com/) or your AI provider
            2. Sign up or log in to your account
            3. Navigate to API Keys section
            4. Create a new API key
            5. Copy and paste it here
            
            **Custom Base URL:**
            - Use this if you're accessing the API through a proxy
            - Or if you're using a different AI provider (e.g., Azure, DeepSeek)
            - Default works for standard OpenAI API
            
            **Security Note:**
            Your API key is stored only in memory for this session and is never saved to disk.
            """)
    
    return None


def check_api_configured():
    """Check if API is configured or if we're in simple mode."""
    return st.session_state.get('api_configured', False)
