# Financial Analyst Agent 🚀

**Table-Aware RAG Pipeline for Financial Document Analysis**

A sophisticated AI-powered financial analysis platform that processes SEC 10-K filings using advanced RAG (Retrieval Augmented Generation) technology. The system preserves table structures in financial documents and provides intelligent analysis using Google Gemini 2.5 Flash.

---

## 🎥 Demo Video

<div align="center">

[![Demo Video](Demo_Video/demo_video.mp4)](Demo_Video/demo_video.mp4)

*Click to watch the demo video showing the system in action!*

</div>

> **Note**: The demo video is located in `Demo_Video/demo_video.mp4`. GitHub may not display videos inline, so download and play locally if needed.

---

## 🎯 What This System Does

This platform transforms how financial documents are analyzed by:

1. **Processing SEC 10-K Filings**: Automatically extracts and converts HTML filings to structured Markdown
2. **Preserving Tables**: Maintains financial table integrity during conversion (critical for accurate analysis)
3. **Smart Retrieval**: Uses vector search to find only relevant sections instead of entire documents
4. **AI Analysis**: Leverages Gemini 2.5 Flash for comprehensive financial insights
5. **Interactive UI**: Clean, modern interface for querying and analyzing financial data

---

## ⚠️ Current Status & Known Limitations

### Token Usage (Experimental Phase)

**Current Behavior**: The system may send large amounts of tokens (90K-150K) to the LLM in a single request.

**Why This Happens**:
- This is an **experimental implementation** to test full document analysis capabilities
- The system is designed to work with Gemini 2.5 Flash's 1M token context window
- Some queries require full document context for accurate analysis

**This is NOT Production-Optimal** - We acknowledge this is inefficient and are actively working on improvements.

### How We're Resolving This

1. **✅ Smart Section Retrieval** (Implemented)
   - Chunks documents by sections (2,050 chunks indexed)
   - Retrieves only relevant sections based on query
   - **Status**: Partially working (needs ticker index for uploaded files)

2. **🔄 Token Budget System** (In Progress)
   - Limits retrieved content to 20K tokens max
   - Early stopping when budget reached
   - **Status**: Implemented but needs optimization

3. **⏳ Hybrid Search** (In Progress)
   - Combines semantic + keyword search
   - Better relevance = less tokens needed
   - **Status**: Code ready, needs testing

4. **📋 Future Improvements**:
   - Hierarchical chunking (multi-level)
   - Query understanding (intent classification)
   - Adaptive retrieval (query-specific strategies)
   - Caching layer for common queries

**Expected Timeline**: Full optimization in 2-3 weeks

---

## ✨ Key Features

- **📊 Table-Aware Processing**: Preserves financial table structures during conversion
- **🔍 Vector Database**: Qdrant integration for semantic search across 89+ companies
- **🧠 Smart Retrieval**: Section-level chunking for efficient query processing
- **💡 Long-Context Analysis**: Uses Gemini 2.5 Flash (1M token context) for comprehensive analysis
- **🎨 Interactive Frontend**: Clean, minimal React UI with query templates and visualizations
- **📤 File Upload**: Process new SEC filings through the frontend
- **⚡ Automatic Indexing**: Uploaded files are automatically indexed in Qdrant

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER QUERY                            │
│         "Show me Apple's revenue table"                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Ticker Extraction     │
        │   (Extract: AAPL)       │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Vector Search (Qdrant)│
        │   Find relevant sections│
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Smart Retrieval       │
        │   (Only relevant parts) │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Gemini 2.5 Flash      │
        │   (AI Analysis)         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Formatted Response    │
        │   (Tables + Insights)   │
        └─────────────────────────┘
```

### Data Flow

```
SEC full-submission.txt
    ↓
Extract HTML (from <TEXT> tag)
    ↓
Convert to Markdown (preserve tables)
    ↓
Chunk by Sections (2,050 chunks)
    ↓
Index in Qdrant (embeddings + metadata)
    ↓
Query → Retrieve Sections → Analyze with Gemini
```

---

## 📁 Project Structure

```
Financial-Analyst-Agent/
├── backend/                    # Python backend
│   ├── app/                    # Main application
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Configuration
│   │   ├── models.py          # Pydantic models
│   │   ├── api/               # API routes
│   │   │   └── routes.py      # All endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── qdrant_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── file_service.py
│   │   │   ├── hybrid_retriever.py
│   │   │   ├── knowledge_graph.py
│   │   │   ├── time_series_extractor.py
│   │   │   └── multi_agent_orchestrator.py
│   │   └── utils/             # Utilities
│   │       ├── html_extractor.py
│   │       ├── markdown_converter.py
│   │       └── ticker_extractor.py
│   ├── scripts/               # Data processing
│   │   ├── index.py          # Index companies
│   │   ├── chunk_markdown_files.py  # Chunk for RAG
│   │   └── index_uploaded_files.py
│   ├── tests/                # Test files
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── styles/          # CSS files
│   │   └── App.tsx          # Main app
│   └── package.json
├── data/                     # Raw SEC 10-K files (in repo)
├── processed_data/           # Markdown files (in repo)
├── output/                   # Extracted HTML (in repo)
├── Demo_Video/              # Demo videos (in repo)
├── conversion_metadata.json  # Conversion tracking
├── .env.example             # Environment template
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Qdrant Cloud account** (or local Qdrant instance)
- **Google Gemini API key**

### Step 1: Clone Repository

```bash
git clone https://github.com/Sumitkumar005/Financial-Analyst-Agent.git
cd Financial-Analyst-Agent
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3: Environment Variables

Create `.env` file in root directory:

```env
# Qdrant Cloud Configuration
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Step 4: Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### Step 5: Index Data (First Time)

```bash
# Index companies in Qdrant
python -m backend.scripts.index

# Chunk files for smart retrieval (IMPORTANT!)
python -m backend.scripts.chunk_markdown_files
```

### Step 6: Run Application

**Terminal 1 - Backend:**
```bash
python -m backend.app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📊 How It Works

### 1. Document Processing

- **Input**: SEC `full-submission.txt` files
- **Extract**: HTML from `<TEXT>` tags
- **Convert**: HTML → Markdown (preserving tables)
- **Store**: Processed Markdown files in `processed_data/`

### 2. Indexing

- **Chunk**: Split documents by sections (Item 1, Item 7, Financial Statements, etc.)
- **Embed**: Create vector embeddings for each chunk
- **Index**: Store in Qdrant with metadata (ticker, section, year)

### 3. Query Processing

- **Extract Ticker**: Identify company from query
- **Retrieve**: Find relevant sections using vector search
- **Analyze**: Send to Gemini for AI analysis
- **Format**: Return structured response with tables

---

## 🎨 Frontend Features

- **📝 Query Templates**: Pre-built templates for common analyses
- **💡 Smart Suggestions**: Auto-suggestions as you type
- **📊 Visual Comparison**: Side-by-side company comparison with charts
- **⚡ Quick Insights**: Auto-extracted insights from analysis
- **⌨️ Command Palette**: Press `Ctrl+K` for quick actions
- **💾 Export**: Download analysis as Markdown
- **📈 Analytics**: Real-time token usage and cost tracking

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/companies` | GET | List all indexed companies |
| `/analyze` | POST | Analyze financial query |
| `/search` | POST | Semantic search |
| `/upload` | POST | Upload and process new file |
| `/files/{path}` | GET | Download processed files |

### Example API Call

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me Apple revenue table for 2024",
    "max_companies": 5
  }'
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Qdrant**: Vector database for semantic search
- **sentence-transformers**: Embedding model (all-MiniLM-L6-v2)
- **Google Gemini 2.5 Flash**: LLM for analysis
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Recharts**: Data visualization
- **Framer Motion**: Animations

---

## 📚 Documentation

Comprehensive documentation available in the repository:

- **Setup Guides**: Step-by-step setup instructions
- **Architecture**: System design and components
- **API Reference**: Complete API documentation
- **Features**: Detailed feature documentation
- **Testing**: How to test the system

---

## 🔧 Troubleshooting

### Issue: "No relevant sections found"

**Solution**: Run chunking script:
```bash
python -m backend.scripts.chunk_markdown_files
```

### Issue: "Ticker index not found"

**Solution**: Create index:
```bash
python -m backend.scripts.create_sections_ticker_index
```

### Issue: High token usage

**Status**: Known issue - see "Current Status" section above. Optimization in progress.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure no API keys in code
5. Submit a pull request

**Important**: Never commit API keys or secrets. Always use environment variables.

---

## 📄 License

This project is for educational and research purposes.

---

## 🙏 Acknowledgments

- **SEC EDGAR**: For providing financial filings
- **Qdrant**: For vector database infrastructure
- **Google**: For Gemini API
- **Open Source Community**: For amazing tools and libraries

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the code comments

---

## 🎯 Roadmap

- [x] Basic RAG implementation
- [x] Table preservation
- [x] Smart section retrieval
- [x] Hybrid search (dense + sparse)
- [ ] Token optimization (in progress)
- [ ] Knowledge graph integration
- [ ] Time-series analysis
- [ ] Multi-agent orchestration
- [ ] Predictive modeling
- [ ] Real-time updates

---

**Built with ❤️ for financial analysis**
