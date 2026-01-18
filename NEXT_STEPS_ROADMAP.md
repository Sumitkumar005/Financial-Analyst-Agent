# Next Steps Roadmap: Table-Aware RAG Pipeline

## ✅ Completed: Phase 1 - Ingestion
- [x] Extract HTML from 89 companies' full-submission.txt files
- [x] Convert HTML to Markdown preserving table structures
- [x] Generate metadata files (JSON/CSV) with conversion statistics
- [x] All 89 Markdown files ready in `processed_data/` folder

## 🚀 Current Phase: Phase 2 - Vector Indexing

### Goal
Make the 89 Markdown files searchable using Qdrant vector database.

### Implementation Steps

#### Step 1: Set up Qdrant
- **Option A**: Docker (recommended)
  ```bash
  docker run -p 6333:6333 qdrant/qdrant
  ```
- **Option B**: Local installation
  ```bash
  pip install qdrant-client
  ```

#### Step 2: Create `index.py`
**Purpose**: Index all 89 companies in Qdrant for semantic search

**Logic**:
1. Load `conversion_metadata.json` to get all file paths
2. For each Markdown file:
   - Extract a summary (first 2000 chars + key sections)
   - Generate embedding using `text-embedding-3-small` or `jina-embeddings-v3`
   - Create Qdrant point with:
     - `id`: UUID
     - `vector`: Embedding
     - `payload`: 
       - `ticker`: "AAPL"
       - `year`: "2024"
       - `file_path`: "./processed_data/AAPL_2024.md"
       - `summary`: First 2000 chars
       - `tables_count`: From metadata
       - `size_mb`: From metadata
3. Upload all points to Qdrant collection

**Key Design Decision**:
- We store **summaries** in Qdrant, not full documents
- Full documents are loaded from disk when needed (long-context approach)
- This allows fast semantic search to find relevant companies

## 📋 Next Phase: Phase 3 - Agent API

### Goal
Build FastAPI server with agent endpoints for financial analysis.

### Implementation Steps

#### Step 1: Create `server.py` (FastAPI)
**Endpoints**:
- `POST /analyze` - Main analysis endpoint
- `GET /health` - Health check
- `GET /companies` - List all indexed companies

#### Step 2: Implement Agent Workflow (LangGraph)
**Router Node**:
- Extract company tickers from user query
- Example: "Compare AWS and Azure revenue" → ['AMZN', 'MSFT']

**Retriever Node**:
- Query Qdrant for matching companies
- Filter by ticker and get latest year
- Return file paths

**Loader Node**:
- Read full Markdown content from file paths
- No chunking - load entire documents

**Generator Node**:
- Send to Gemini 2.5 Flash:
  - User query
  - Full document content (both companies)
  - System prompt for table-aware analysis
- Return structured JSON response

## 🎯 Key Insights from RLM Paper

The **Recursive Language Models (RLM)** paper is highly relevant:

1. **Long Context Handling**: RLMs treat long prompts as external environment
   - Similar to our approach: store full docs on disk, load when needed
   - Avoids context rot by selective loading

2. **Programmatic Access**: RLMs use REPL to interact with context
   - Our approach: Use Qdrant for semantic search, then load full docs
   - More efficient than loading everything into context

3. **Recursive Sub-calls**: RLMs make sub-LM calls for complex tasks
   - Our approach: Could use Gemini for summary generation, then full analysis
   - Future enhancement: Multi-step reasoning for complex comparisons

## 📦 Required Dependencies

```bash
pip install qdrant-client fastapi uvicorn langchain langchain-google-genai langchain-community openai
```

## 🔄 Workflow Diagram

```
User Query: "Compare AWS vs Azure revenue"
    ↓
Router Node (LLM): Extract ['AMZN', 'MSFT']
    ↓
Retriever Node: Query Qdrant → Get file paths
    ↓
Loader Node: Read full AMZN_2024.md + MSFT_2024.md
    ↓
Generator Node: Send to Gemini 2.5 Flash (1M+ tokens)
    ↓
Response: Structured JSON with analysis
```

## ⚠️ Important Notes

1. **No Chunking**: We load full documents to preserve table integrity
2. **Hybrid Search**: Qdrant for finding companies, full-text for analysis
3. **Long Context**: Gemini 2.5 Flash handles 1M+ tokens, perfect for our use case
4. **Table Preservation**: Markdown format ensures tables remain intact

## 🎯 Success Criteria

- [ ] All 89 companies indexed in Qdrant
- [ ] Can query by company name/ticker semantically
- [ ] FastAPI server running
- [ ] Agent can extract tickers from natural language queries
- [ ] Agent can load and analyze full documents
- [ ] Response includes accurate table data (no hallucinations)
