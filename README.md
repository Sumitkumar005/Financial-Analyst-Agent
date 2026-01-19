# Financial Analyst Agent 🚀

**AI-Powered SEC 10-K Analysis with Table-Aware RAG**

An intelligent financial document analysis platform that processes SEC 10-K filings using advanced RAG (Retrieval Augmented Generation) technology. The system preserves complex financial table structures and provides comprehensive insights using Google Gemini 2.5 Flash.

---

## 🎥 Watch It In Action

<div align="center">

[![Financial Analyst Agent Demo](https://img.youtube.com/vi/B7q4Bxew5sw/maxresdefault.jpg)](https://www.youtube.com/watch?v=B7q4Bxew5sw)

**[▶️ Watch Full Demo Video](https://www.youtube.com/watch?v=B7q4Bxew5sw)**

*See the system analyze Apple's revenue tables, compare company financials, and extract insights in real-time*

</div>

---

## 🎯 Why This System Is Different

### The Problem
Traditional RAG systems break financial tables during document processing, losing critical numerical relationships and making analysis unreliable.

### Our Solution
Three key innovations that set this apart:

1. **🔧 Table-Aware Conversion**
   - Preserves financial statement structure during HTML → Markdown conversion
   - Maintains row/column relationships in complex tables
   - Ensures accurate numerical analysis

2. **📊 Section-Based Chunking**
   - Intelligent chunking by SEC 10-K sections (Item 1, Item 7, Financial Statements)
   - Context-aware retrieval (only relevant sections, not entire documents)
   - Token-efficient: 15-25K tokens for most queries vs 150K+ with naive approaches

3. **🎯 Smart Retrieval Pipeline**
   - Ticker extraction → Vector search → Section filtering → AI analysis
   - 2,050+ indexed sections across 89 companies
   - Sub-second response times for targeted queries

---

## ✨ Key Features

- **📈 Financial Table Preservation**: Maintains integrity of balance sheets, income statements, and cash flow tables
- **🔍 Semantic Search**: Qdrant vector database for intelligent document retrieval
- **🧠 Long-Context Analysis**: Gemini 2.5 Flash with 1M token context window
- **⚡ Token Efficient**: 20K token limit for cost-effective production use
- **🎨 Modern UI**: Clean React interface with real-time analysis
- **📤 File Upload**: Process new SEC filings instantly with auto-indexing
- **📊 Analytics Dashboard**: Track token usage, costs, and performance metrics

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER QUERY                           │
│         "Show me Apple's revenue for 2024"              │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │  Ticker Extraction      │  Extract: AAPL
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Vector Search (Qdrant) │  Semantic search across 2,050 sections
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Smart Section Filter   │  Filter by: ticker + relevance + token budget
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Context Assembly       │  Assemble sections (max 20K tokens)
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Gemini 2.5 Flash       │  AI analysis with financial expertise
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Formatted Response     │  Tables + Insights + Citations
      └─────────────────────────┘
```

### Data Processing Pipeline

```
SEC full-submission.txt (Raw filing)
    ↓
Extract HTML from <TEXT> tags
    ↓
Convert to Markdown (preserve tables)
    ↓
Chunk by Sections (2,050 chunks indexed)
    ↓
Generate Embeddings (sentence-transformers)
    ↓
Index in Qdrant (vector DB + metadata)
    ↓
Query → Retrieve → Analyze → Return Results
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Qdrant Cloud account (free tier works)
- Google Gemini API key (free tier: 1,500 requests/day)

### 1. Clone Repository

```bash
git clone https://github.com/Sumitkumar005/Financial-Analyst-Agent.git
cd Financial-Analyst-Agent
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Configure Environment

Create `.env` file in root directory:

```env
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Token limit (default: 20000)
MAX_RETRIEVAL_TOKENS=20000
```

**Getting API Keys:**
- Qdrant: Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
- Gemini: Get key at [aistudio.google.com](https://aistudio.google.com)

### 4. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 5. Index Data (First Time Only)

```bash
# Index companies in Qdrant
python -m backend.scripts.index

# Chunk files for smart retrieval
python -m backend.scripts.chunk_markdown_files
```

### 6. Run Application

**Terminal 1 - Backend:**
```bash
python -m backend.app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access Application:**
- 🌐 Frontend: http://localhost:5173
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health Check: http://localhost:8000/health

---

## 💡 Usage Examples

### Example Queries

```
✅ "Show me Apple's revenue breakdown for 2024"
✅ "Compare Microsoft and Google's operating expenses"
✅ "What are Amazon's top risk factors?"
✅ "Analyze Tesla's cash flow statement"
✅ "Find NVIDIA's R&D spending trends"
```

### API Usage

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me Apple revenue table for 2024",
    "max_companies": 5
  }'
```

---

## 🎨 Frontend Features

| Feature | Description |
|---------|-------------|
| **🔍 Query Templates** | Pre-built templates for common financial analyses |
| **💡 Smart Suggestions** | Auto-complete as you type |
| **📊 Visual Comparison** | Side-by-side charts for multi-company analysis |
| **⚡ Quick Insights** | AI-extracted key takeaways |
| **⌨️ Command Palette** | Press `Ctrl+K` for quick actions |
| **💾 Export Options** | Download as Markdown or JSON |
| **📈 Analytics** | Real-time token usage and cost tracking |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/companies` | GET | List all indexed companies (89 total) |
| `/analyze` | POST | Analyze financial query with AI |
| `/search` | POST | Semantic search across documents |
| `/upload` | POST | Upload and auto-index new SEC filing |
| `/files/{path}` | GET | Download processed Markdown files |

**Full API Documentation:** http://localhost:8000/docs

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Qdrant** - Vector database for semantic search
- **sentence-transformers** - Embedding model (all-MiniLM-L6-v2)
- **Google Gemini 2.5 Flash** - LLM for analysis
- **Pydantic** - Data validation and settings management

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-gen frontend build tool
- **Recharts** - Composable charting library
- **Framer Motion** - Production-ready animations

### Data Processing
- **BeautifulSoup4** - HTML parsing
- **markdownify** - HTML to Markdown conversion
- **NLTK** - Text processing and tokenization

---

## 📊 Performance Metrics

- **Indexed Companies**: 89 SEC 10-K filings
- **Total Sections**: 2,050+ indexed chunks
- **Average Query Time**: 2-4 seconds
- **Token Usage**: 15-25K tokens per query (optimized)
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Vector Search**: Sub-second retrieval

---

## 🏢 Production Considerations

### Token Efficiency
- **Token Budget**: 20K max per query (configurable)
- **Smart Filtering**: Only retrieve relevant sections
- **Cost Estimation**: ~$0.01-0.03 per query with Gemini Flash

### Scalability
- **Qdrant Cloud**: Handles millions of vectors
- **Async Processing**: FastAPI for concurrent requests
- **Caching**: Response caching for common queries

### Security
- **Environment Variables**: API keys never in code
- **CORS**: Configured for production
- **Rate Limiting**: Optional rate limit middleware

---

## 📁 Project Structure

```
Financial-Analyst-Agent/
├── backend/                    # Python Backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Configuration management
│   │   ├── models.py          # Pydantic models
│   │   ├── api/
│   │   │   └── routes.py      # API endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── qdrant_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   └── file_service.py
│   │   └── utils/             # Utilities
│   │       ├── html_extractor.py
│   │       ├── markdown_converter.py
│   │       └── ticker_extractor.py
│   ├── scripts/               # Data processing
│   │   ├── index.py
│   │   └── chunk_markdown_files.py
│   └── requirements.txt
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── styles/           # CSS modules
│   │   └── App.tsx
│   └── package.json
├── data/                      # Raw SEC 10-K files
├── processed_data/            # Markdown files
├── .env.example              # Environment template
└── README.md
```

---

## 🐛 Troubleshooting

### "No relevant sections found"

**Solution**: Ensure chunking script ran successfully
```bash
python -m backend.scripts.chunk_markdown_files
```

### "Qdrant connection failed"

**Solution**: Verify credentials in `.env`
```bash
# Check health endpoint
curl http://localhost:8000/health
```

### Frontend won't connect to backend

**Solution**: Ensure CORS is configured
```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Important**: Never commit API keys or secrets. Always use `.env` files.

---

## 🗺️ Roadmap

### Completed ✅
- [x] Table-aware RAG implementation
- [x] Section-based chunking
- [x] Vector search with Qdrant
- [x] Token budget optimization
- [x] React frontend with analytics

### In Progress 🚧
- [ ] Multi-company comparison dashboard
- [ ] Historical trend analysis
- [ ] Knowledge graph integration

### Planned 📋
- [ ] Real-time SEC filing updates
- [ ] Predictive financial modeling
- [ ] Multi-agent orchestration
- [ ] Export to Excel/PDF

---

## 📄 License

This project is for educational and research purposes.

---

## 🙏 Acknowledgments

- **SEC EDGAR** - Public company financial data
- **Qdrant** - Vector database infrastructure
- **Google** - Gemini API access
- **Anthropic** - Claude for development assistance
- **Open Source Community** - Amazing libraries and tools

---

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Sumitkumar005/Financial-Analyst-Agent/issues)
- **Documentation**: Check `docs/` folder for detailed guides
- **Demo Video**: [Watch on YouTube](https://www.youtube.com/watch?v=B7q4Bxew5sw)

---

## 🌟 Star This Project

If you find this useful, please ⭐ star the repository to help others discover it!

---

**Built with ❤️ for intelligent financial analysis**
