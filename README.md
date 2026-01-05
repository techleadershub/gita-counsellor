# 🕉️ Gita Counsellor

> AI-powered Bhagavad Gita counsellor - Get personalized spiritual guidance for modern life problems with relevant verses and practical advice.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)

## ✨ Features

- 🔍 AI-powered research and guidance from Bhagavad Gita
- 📚 Semantic search through 700+ verses
- 🎯 Contextual answers with practical advice
- 📱 Progressive Web App (PWA)
- 🚀 Production-ready deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+, Node.js 18+
- OpenAI API Key

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/gita-counsellor.git
cd gita-counsellor

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../config.example.yaml ../config.yaml
# Add OPENAI_API_KEY to config.yaml or export it
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access: Frontend at http://localhost:3000, Backend at http://localhost:8000

### Docker

```bash
docker compose up --build
```

## 📦 Deployment

See [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md) for Railway deployment guide.

## 📖 API

- `POST /api/research` - Get guidance for a question
- `GET /api/verses` - List/search verses
- `GET /api/verses/{verse_id}` - Get specific verse
- `GET /health` - Health check

Interactive API docs: http://localhost:8000/docs

## 🏗️ Tech Stack

**Backend:** FastAPI, SQLAlchemy, Qdrant, LangChain, LangGraph, OpenAI  
**Frontend:** React, Vite, Tailwind CSS, PWA  
**Infrastructure:** Docker, Railway

## 📁 Project Structure

```
gita-counsellor/
├── backend/          # FastAPI backend
├── frontend/          # React frontend
├── epubs/            # Source data
└── docker-compose.yml
```

## 🤝 Contributing

Contributions welcome! Fork, create a feature branch, and submit a PR.

## 📝 License

Educational and spiritual purposes. Bhagavad Gita text from "Bhagavad Gita As It Is" by A.C. Bhaktivedanta Swami Prabhupada.

## 🙏 Credits

- Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada
- Built with modern AI and web technologies

---

**Made with ❤️ for spiritual seekers and modern problem solvers**
