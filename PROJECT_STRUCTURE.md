# Project Structure

Clean, organized, and developer-friendly project structure.

```
Financial-Analyst-Agent/
│
├── 📁 backend/                    # Python Backend
│   ├── 📁 app/                    # Main Application
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Configuration
│   │   ├── models.py          # Pydantic models
│   │   ├── 📁 api/               # API Routes
│   │   │   └── routes.py         # All endpoints
│   │   ├── 📁 services/          # Business Logic
│   │   │   ├── qdrant_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   └── file_service.py
│   │   └── 📁 utils/             # Utilities
│   │       ├── html_extractor.py
│   │       ├── markdown_converter.py
│   │       └── ticker_extractor.py
│   ├── 📁 scripts/               # Data Processing
│   │   ├── index.py
│   │   ├── chunk_markdown_files.py
│   │   ├── create_ticker_index.py
│   │   └── ...
│   └── 📁 tests/                 # Tests
│       ├── test_api.py
│       └── test_qdrant_connection.py
│
├── 📁 frontend/                   # React Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/        # React Components
│   │   ├── 📁 styles/            # CSS Files
│   │   └── App.tsx, main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── 📁 docs/                       # Documentation
│   ├── README.md                 # Docs index
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── SETUP_QDRANT.md
│   ├── FRONTEND_SETUP.md
│   └── 📁 reference/             # Reference Materials
│       ├── COPY_PASTE_QUERIES.txt
│       └── ...
│
├── 📄 README.md                   # Main README
├── 📄 CONTRIBUTING.md             # Contributing guide
├── 📄 requirements.txt            # Python dependencies
├── 📄 start_server.bat           # Windows server starter
└── 📄 .env.example               # Environment template
```

## Directory Purposes

### `backend/`
- **app/**: Core application code with clean separation of concerns
- **scripts/**: One-time data processing and setup scripts
- **tests/**: Test files for backend functionality

### `frontend/`
- Complete React application with components, styles, and configuration
- Self-contained with its own `package.json` and build setup

### `docs/`
- All project documentation in one place
- Reference materials for research and testing

### Root Directory
- Only essential files: README, requirements, config templates
- Clean and minimal for easy navigation

## Benefits

✅ **Clear separation** between backend, frontend, and docs  
✅ **Easy navigation** - everything in its logical place  
✅ **Developer-friendly** - standard structure patterns  
✅ **Scalable** - easy to add new features  
✅ **Professional** - follows best practices  
