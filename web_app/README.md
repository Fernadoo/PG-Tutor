# AI Tutoring System - Web Interface

This directory contains the Streamlit-based web interface for the AI Tutoring System.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

Or install just the web-specific dependencies:
```bash
pip install streamlit plotly networkx pandas
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will start and open in your default browser at `http://localhost:8501`

## Features

### 🔐 Secure API Configuration
- API key entered through web interface (not stored in config files)
- Credentials stored only in memory for the session
- Support for custom base URLs (proxies, Azure, DeepSeek, etc.)
- Two learning modes: AI Tutor (LLM) or Simple Mode

### 📖 Interactive Lessons
- LLM-generated personalized lessons with AI Tutor mode
- Adaptive content based on your knowledge level
- Support for both natural language and binary answers

### 📊 Real-time Analytics
- Bayesian belief visualization
- Knowledge level estimation (λ)
- Progress tracking with beautiful charts
- Accuracy statistics by topic and level

### 🕸️ Knowledge Graph
- Interactive visualization of topic hierarchy
- Prerequisite relationships
- Difficulty levels color-coded

### 📜 Session History
- Complete question history
- Performance analytics
- Export session data as JSON

### ⚙️ Settings
- View and reconfigure API settings
- Configure target number of questions
- Difficulty mode selection

## Architecture

```
web_app/
├── app.py                      # Main application entry point
├── components/                 # UI components
│   ├── __init__.py
│   ├── entrance_setup.py      # API configuration entrance screen
│   ├── lesson_view.py         # Lesson display
│   ├── progress_chart.py      # Bayesian visualization
│   ├── knowledge_graph_viz.py # Graph visualization
│   ├── session_history.py     # History dashboard
│   └── settings_panel.py      # Settings UI
├── utils/                      # Utilities
│   ├── __init__.py
│   └── session_manager.py     # Session state management
└── README.md
```

## Configuration

### Web Interface Setup (Recommended)

1. Start the app: `streamlit run app.py`
2. On the entrance screen, enter your API credentials:
   - **API Key**: Your OpenAI or provider API key
   - **Base URL**: Optional (defaults from config.yaml)
   - **Model**: Select your preferred model
3. Choose your learning mode:
   - **AI Tutor Mode**: LLM-generated lessons with natural language answers
   - **Simple Mode**: Binary correct/incorrect without API calls

### Default Values (config.yaml)

The `config.yaml` file provides default values for base URL and model:

```yaml
llm:
  # DO NOT store API key here - enter it in the web interface instead
  base_url: "https://api.openai.com/v1"  # default base URL
  model: "gpt-3.5-turbo"                 # default model
```

### Environment Variable (Alternative)

You can also set the API key via environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

1. **Setup**: Enter your API credentials on the entrance screen
2. **Start**: Click "Start Learning" to begin a session
3. **Answer**: Type your answer (AI mode) or select correct/incorrect (Simple mode)
4. **Feedback**: Review AI-generated feedback and see your progress
5. **Continue**: Click "Next Question" to proceed
6. **Explore**: View Knowledge Graph and History tabs

## Security

🔒 **Your API key is secure:**
- Entered through the web interface, not stored in files
- Kept only in memory for your session
- Never saved to disk or logged
- Cleared when you close the browser or reset the session

## Session Data

Sessions are automatically saved to the `../record/` directory with timestamps, just like the CLI version. Session data includes your progress and performance metrics, but **never** includes your API key.

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari

## Troubleshooting

**Import errors**: Make sure you're running from the `web_app` directory or have installed the package.

**LLM not working**: 
- Check that you entered a valid API key on the entrance screen
- Verify your API key has sufficient credits/quota
- Check the base URL if using a custom provider

**Want to switch modes?**: Click "Reconfigure API / Mode" in the settings panel to go back to the entrance screen.

**Charts not showing**: Try refreshing the page - sometimes Plotly charts need a reload.
