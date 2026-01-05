# 🕉️ Gita Counsellor - AI-Powered Bhagavad Gita Guidance

> Your AI counsellor for life's challenges. Get personalized spiritual guidance from the Bhagavad Gita - ask modern questions and receive comprehensive answers with relevant verses, practical advice, and spiritual exercises.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)

## ✨ Features

- 🔍 **AI-Powered Research**: Ask any question about modern life problems and get comprehensive guidance
- 📚 **700+ Verses**: Semantic search through all Bhagavad Gita verses using vector embeddings
- 🎯 **Contextual Answers**: Receive detailed analysis, practical steps, and spiritual exercises
- 💾 **Dual Database**: SQLite for verse reference + Qdrant for semantic vector search
- 📱 **Progressive Web App**: Works offline with PWA support
- 🚀 **Production Ready**: One-click deployment on Railway
- 🎨 **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS

## 🎯 One-Line Description

**AI-powered Bhagavad Gita counsellor - Get personalized spiritual guidance for modern life problems with relevant verses and practical advice.**

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   Qdrant    │
│  (React)    │      │  (FastAPI)   │      │  (Vector DB)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   SQLite     │
                     │  (Verses DB) │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   OpenAI     │
                     │ (LLM + Embed)│
                     └──────────────┘
```

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for SQLite database
- Qdrant - Vector database for semantic search
- LangChain + LangGraph - AI agent orchestration
- OpenAI - GPT-4 embeddings and LLM

**Frontend:**
- React 18 - UI framework
- Vite - Build tool and dev server
- Tailwind CSS - Utility-first styling
- PWA - Progressive Web App capabilities

**Infrastructure:**
- Docker - Containerization
- Railway - Cloud deployment platform

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Docker (optional, for containerized development)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gita-counsellor.git
   cd gita-counsellor
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

4. **Configuration:**
   ```bash
   # Copy example config
   cp config.example.yaml config.yaml
   
   # Add your OpenAI API key
   # Edit config.yaml or set environment variable:
   export OPENAI_API_KEY=your-api-key-here
   ```

5. **Run Services:**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

6. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

7. **Ingest Data (First Time):**
   - Open http://localhost:3000
   - Navigate to "Ingestion" tab
   - Click "Start Ingestion"
   - Wait ~2-3 minutes for completion

### Docker Development

```bash
# Start all services
docker compose up --build

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Qdrant: http://localhost:6333
```

## 📦 Deployment

### Railway (Recommended)

See **[RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)** for detailed deployment instructions.

**Quick Steps:**
1. Create Railway project
2. Deploy Qdrant service (Docker Hub: `qdrant/qdrant:latest`)
3. Deploy Backend service (Root: empty, Dockerfile: `backend/Dockerfile`)
4. Deploy Frontend service (Root: `frontend`, Dockerfile: `frontend/Dockerfile`)
5. Set environment variables
6. Ingest data

**Estimated Time:** ~15-20 minutes

## 📖 API Documentation

### Research Endpoint

Get comprehensive guidance for a question:

```bash
POST /api/research
Content-Type: application/json

{
  "query": "How to deal with stress and anxiety?",
  "context": "I'm a software developer facing work pressure" // optional
}
```

**Response:**
```json
{
  "analysis": "Detailed analysis of the problem...",
  "guidance": "Practical actionable steps...",
  "exercises": "Spiritual exercises and practices...",
  "verses": [
    {
      "verse_id": "2.47",
      "chapter": 2,
      "verse_number": 47,
      "text": "You have a right to perform your prescribed duty...",
      "relevance_score": 0.95
    }
  ]
}
```

### Other Endpoints

- `GET /api/verses` - List verses (supports filters: `chapter`, `verse_number`, `verse_id`)
- `GET /api/verses/{verse_id}` - Get specific verse
- `POST /api/ingest` - Ingest EPUB file
- `GET /api/ingestion/status` - Check ingestion status
- `GET /api/stats` - Database statistics
- `GET /health` - Health check

**Interactive API Docs:** Visit `/docs` when backend is running

## 🎓 How It Works

1. **User Query**: Ask a question about a modern problem
2. **AI Analysis**: LangGraph agent analyzes the problem and identifies relevant Gita principles
3. **Vector Search**: Qdrant finds semantically similar verses using embeddings
4. **Synthesis**: GPT-4 synthesizes comprehensive guidance with:
   - Problem analysis from Gita perspective
   - Practical actionable steps
   - Spiritual exercises and practices
5. **Response**: Returns formatted answer with referenced verses

## 📁 Project Structure

```
gita-counsellor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── research_agent.py    # AI research agent (LangGraph)
│   ├── ingestion.py         # EPUB ingestion service
│   ├── vector_store.py      # Qdrant wrapper
│   ├── models.py            # SQLAlchemy models
│   ├── config.py            # Configuration loader
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── railway.json         # Railway config
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── api.js           # API client
│   │   └── ...
│   ├── package.json         # Node dependencies
│   ├── Dockerfile           # Frontend container
│   ├── nginx.conf.template  # Nginx config template
│   └── railway.json         # Railway config
├── epubs/
│   └── BhagavadGitaAsItIs.epub
├── docker-compose.yml       # Local development
├── RAILWAY_QUICK_START.md   # Deployment guide
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is for **educational and spiritual purposes**. 

The Bhagavad Gita text is from "Bhagavad Gita As It Is" by A.C. Bhaktivedanta Swami Prabhupada.

## 🙏 Credits

- **Bhagavad Gita As It Is** by A.C. Bhaktivedanta Swami Prabhupada
- Built with modern AI and web technologies
- Inspired by the timeless wisdom of the Bhagavad Gita

## 📞 Support

- 🚀 [Railway Deployment Guide](RAILWAY_QUICK_START.md)
- 🐛 [Report Issues](https://github.com/yourusername/gita-counsellor/issues)

## ⭐ Star History

If you find this project helpful, please consider giving it a star! ⭐

---

**Made with ❤️ for spiritual seekers and modern problem solvers**
#   g i t a - c o u n s e l l o r  
 