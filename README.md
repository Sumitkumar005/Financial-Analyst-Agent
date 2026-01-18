# Financial-Analyst-Agent

Table-Aware RAG Pipeline for Financial Document Analysis

## 🎯 Overview

A sophisticated financial analysis platform that processes SEC 10-K filings using a Table-Aware RAG (Retrieval Augmented Generation) pipeline. The system preserves table structures in financial documents and provides AI-powered analysis using Gemini 2.5 Flash.

## ✨ Features

- **Table-Aware Processing**: Preserves financial table structures during HTML to Markdown conversion
- **Vector Database**: Qdrant integration for semantic search across 89+ companies
- **Smart Retrieval**: Section-level chunking for efficient query processing
- **Long-Context Analysis**: Uses Gemini 2.5 Flash (1M token context) for comprehensive analysis
- **Interactive Frontend**: Clean, minimal React UI with query templates and visualizations
- **File Upload**: Process new SEC filings through the frontend
- **Automatic Indexing**: Uploaded files are automatically indexed in Qdrant

## 🏗️ Architecture

```
SEC full-submission.txt
    ↓
Extract HTML (from <TEXT> tag)
    ↓
Convert to Markdown (preserve tables)
    ↓
Index in Qdrant (summaries + embeddings)
    ↓
Query → Retrieve → Load Full Document → Analyze with Gemini
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Qdrant Cloud account (or local Qdrant instance)
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sumitkumar005/Financial-Analyst-Agent.git
   cd Financial-Analyst-Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python server.py
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
.
├── data/                    # Raw SEC 10-K files (not in repo)
├── output/                  # Extracted HTML files (not in repo)
├── processed_data/          # Markdown files (not in repo)
├── uploads/                 # Uploaded files (not in repo)
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── styles/         # CSS files
│   └── package.json
├── server.py                # FastAPI backend
├── index.py                  # Vector indexing script
├── chunk_markdown_files.py   # Section chunking script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md
```

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# Qdrant Cloud Configuration
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 📊 Data Processing

### Index Existing Files

```bash
python index.py
```

### Chunk Files for Smart Retrieval

```bash
python chunk_markdown_files.py
```

### Index Uploaded Files

```bash
python index_uploaded_files.py
```

## 🎨 Frontend Features

- **Query Templates**: Pre-built query templates for common analyses
- **Smart Suggestions**: Auto-suggestions as you type
- **Visual Comparison**: Side-by-side company comparison with charts
- **Quick Insights**: Auto-extracted insights from analysis
- **Command Palette**: Press `Ctrl+K` for quick actions
- **Export**: Download analysis as Markdown

## 🔒 Security

- **No API keys in code**: All keys must be set via environment variables
- **`.env` file ignored**: Never commit your `.env` file
- **Secure defaults**: Application fails safely if keys are missing

## 📝 API Endpoints

- `GET /health` - Health check
- `GET /companies` - List all indexed companies
- `POST /analyze` - Analyze financial query
- `POST /search` - Semantic search
- `POST /upload` - Upload and process new file
- `GET /files/{file_path}` - Download processed files

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python
- **Vector DB**: Qdrant Cloud
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Google Gemini 2.5 Flash
- **Frontend**: React, TypeScript, Vite
- **Charts**: Recharts
- **Animations**: Framer Motion

## 📚 Documentation

- `SYSTEM_ARCHITECTURE.md` - Complete system architecture
- `HONEST_ANALYSIS_AND_IMPROVEMENTS.md` - System analysis and improvements
- `UPLOADED_FILES_RAG_PIPELINE.md` - Upload feature documentation
- `TEST_QUERIES.md` - Test queries for verification

## 🤝 Contributing

Contributions are welcome! Please ensure:
- No API keys in code
- All secrets use environment variables
- Code follows existing patterns

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- SEC EDGAR for providing financial filings
- Qdrant for vector database infrastructure
- Google for Gemini API
