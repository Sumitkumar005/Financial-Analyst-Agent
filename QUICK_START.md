# Quick Start (5 Minutes)

Fastest way to get the application running.

## 1. Install Dependencies

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

## 2. Create `.env` File

Create `.env` in project root:

```env
QDRANT_URL=your_url
QDRANT_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

## 3. Run

```bash
# Terminal 1: Backend
python -m backend.app.main

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 4. Open

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

Done! 🚀
