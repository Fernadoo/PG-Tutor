# AI Tutoring System - React + FastAPI Edition (v2.0)

A production-ready, scalable web application for the AI Tutoring System built with **React + TypeScript** frontend and **FastAPI** backend.

## 🏗️ Architecture

```
┌─────────────────┐      HTTP/REST      ┌─────────────────┐
│   React Frontend│ ←────────────────→ │  FastAPI Backend│
│  (TypeScript)   │    WebSocket      │   (Python)      │
│   Port: 5173    │ ←──────────────→  │   Port: 8000    │
└─────────────────┘                    └─────────────────┘
       │                                       │
       │  Zustand State                        │  Session
       │  Management                           │  Management
       │                                       │
       ▼                                       ▼
   Interactive UI                        Bayesian Model
   - Real-time Charts                    - LLM Integration
   - Knowledge Graph                    - Multi-user Support
   - Responsive Design                  - Stateless API
```

## 📁 Project Structure

```
web_app_v2/
├── backend/                      # FastAPI Backend
│   ├── api/
│   │   ├── sessions.py           # Session management endpoints
│   │   ├── topics.py              # Topic and graph endpoints
│   │   └── config.py              # Configuration endpoints
│   ├── core/
│   │   └── connection_manager.py  # WebSocket connection manager
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── session_service.py     # Business logic
│   │   ├── knowledge_graph_service.py
│   │   └── teacher_service.py
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile
│
├── frontend/                      # React Frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts         # Axios API client
│   │   ├── components/
│   │   │   ├── Layout.tsx        # App layout with sidebar
│   │   │   ├── TopicCard.tsx     # Topic display
│   │   │   ├── AnswerInput.tsx   # Answer input component
│   │   │   └── ProgressCharts.tsx # Recharts visualizations
│   │   ├── hooks/
│   │   │   └── useSession.ts     # Custom session hook
│   │   ├── pages/
│   │   │   ├── Setup.tsx         # API configuration page
│   │   │   ├── Lesson.tsx        # Lesson and questions
│   │   │   ├── Progress.tsx      # Progress dashboard
│   │   │   ├── KnowledgeGraph.tsx # Interactive graph
│   │   │   └── History.tsx       # Session history
│   │   ├── store/
│   │   │   └── index.ts          # Zustand state management
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript interfaces
│   │   ├── App.tsx               # Main app with routing
│   │   └── main.tsx              # Entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml            # Docker orchestration
└── README.md
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
cd web_app_v2

# Start all services
docker-compose up --build

# Access the app:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Development

**Backend:**
```bash
cd web_app_v2/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd web_app_v2/frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

## ✨ Features

### 🔐 Secure API Configuration
- API key entered through web interface (not stored in config files)
- Credentials stored only in backend memory
- Support for custom base URLs and models
- Two modes: AI Tutor (LLM) or Simple Mode

### 📖 Interactive Learning
- LLM-generated personalized lessons (AI Tutor mode)
- Binary correct/incorrect tracking (Simple mode)
- Adaptive topic selection based on Bayesian belief
- Natural language answer evaluation

### 📊 Real-time Analytics
- Bayesian belief visualization with confidence intervals
- Knowledge level estimation (λ) tracking
- Interactive charts with Recharts
- Accuracy statistics by topic level
- Cumulative progress tracking

### 🕸️ Knowledge Graph
- Interactive graph visualization with React Flow
- Color-coded difficulty levels
- Prerequisite relationships
- Dynamic node positioning

### 📜 Session Management
- Complete question history
- Performance analytics dashboard
- Session export (JSON)
- Multi-user support (stateless backend)

### 🔄 Real-time Updates
- WebSocket connection for live updates
- Progress synchronization across tabs
- Collaborative features ready

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type hints
- **Uvicorn** - Lightning-fast ASGI server
- **WebSockets** - Real-time bidirectional communication
- **Existing src/** - Reuses Bayesian model, teacher, knowledge graph

### Frontend
- **React 18** - UI library with concurrent features
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **React Query** - Server state management
- **Recharts** - Composable charting library
- **React Flow** - Interactive node-based graphs
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 📡 API Endpoints

### Sessions
- `POST /api/sessions/create` - Create new session
- `GET /api/sessions/{id}` - Get session info
- `POST /api/sessions/{id}/answer` - Submit answer
- `GET /api/sessions/{id}/progress` - Get progress data
- `GET /api/sessions/{id}/belief` - Get belief state
- `POST /api/sessions/{id}/reset` - Reset session
- `DELETE /api/sessions/{id}` - Delete session

### Topics
- `GET /api/topics/list` - List all topics
- `GET /api/topics/{id}` - Get topic details
- `GET /api/topics/graph/visualization` - Get graph structure

### Config
- `GET /api/config/defaults` - Get default configuration
- `GET /api/config/models` - Get available models

### WebSocket
- `ws://localhost:8000/ws/{session_id}` - Real-time updates

## 🏛️ Architecture Decisions

### Why FastAPI + React?

1. **Scalability**: Stateless backend supports multiple concurrent users
2. **Performance**: FastAPI is one of the fastest Python frameworks
3. **Type Safety**: Full TypeScript frontend + Pydantic backend
4. **Real-time**: WebSocket support for live updates
5. **Developer Experience**: Auto-generated API docs, hot reload
6. **Production Ready**: Built-in validation, error handling, CORS

### Key Differences from Streamlit Version

| Feature | Streamlit (v1) | React + FastAPI (v2) |
|---------|----------------|---------------------|
| **State** | In-memory (single user) | Stateless API (multi-user) |
| **Real-time** | Page rerun | WebSocket/SSE |
| **Customization** | Limited | Full control |
| **Scalability** | Single instance | Horizontal scaling ready |
| **Mobile** | Responsive | PWA-ready |
| **Charts** | Plotly | Recharts (more customizable) |
| **Graph Viz** | NetworkX static | React Flow interactive |

## 🔒 Security

- API keys stored only in backend memory (never persisted)
- CORS protection enabled
- Input validation with Pydantic
- No sensitive data in logs
- Session isolation between users

## 📝 Configuration

### Frontend Environment Variables
Create `.env` file in `frontend/`:
```env
VITE_API_URL=http://localhost:8000
```

### Default Values (config.yaml)
```yaml
llm:
  base_url: "https://api.openai.com/v1"  # Default base URL
  model: "gpt-3.5-turbo"                 # Default model
```

## 🧪 Development

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Code Quality
```bash
# Backend linting
cd backend
black .
flake8

# Frontend linting
cd frontend
npm run lint
```

## 🚀 Deployment

### Production Build
```bash
# Backend
cd backend
docker build -t ai-tutor-backend .

# Frontend
cd frontend
docker build -t ai-tutor-frontend .
```

### Environment Variables
```bash
# Backend
OPENAI_API_KEY=sk-...  # Optional: for fallback

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

## 🆚 Comparison with Streamlit Version

**Choose Streamlit (web_app/) if:**
- Quick prototype or MVP
- Single user/internal tool
- Python-first team
- Less than 1 hour to deploy

**Choose React + FastAPI (web_app_v2/) if:**
- Production application
- Multiple concurrent users
- Need authentication system
- Real-time collaboration
- Custom branding/design
- Mobile app experience
- Horizontal scaling needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit a pull request

## 📄 License

Same as the main project.

## 🙏 Acknowledgments

- Built on the original AI Tutoring System core
- FastAPI for the excellent web framework
- React team for the amazing UI library
- All contributors to the dependencies

---

**Happy Learning! 🎓**
