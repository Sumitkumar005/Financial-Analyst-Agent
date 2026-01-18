"""
FastAPI Server for Table-Aware Financial Analysis Agent
"""

import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import markdownify

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("[ERROR] Required packages not installed. Run: pip install qdrant-client sentence-transformers")
    exit(1)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARNING] Google Generative AI not installed. Gemini features will be disabled.")
    print("   Install with: pip install google-generativeai")

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION_NAME = "financial_reports"  # Original collection (company-level)
SECTIONS_COLLECTION = "financial_sections"  # New collection (section-level chunks)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
PROCESSED_DATA_DIR = Path("processed_data")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"  # Corrected model name

# Validate required environment variables
if not QDRANT_URL:
    raise ValueError("QDRANT_URL environment variable is required. Please set it in .env file")
if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY environment variable is required. Please set it in .env file")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in .env file")
MAX_TOKENS_PER_FILE = 800000  # Leave room in 1M token window
USE_SMART_RETRIEVAL = True  # Toggle: True = smart retrieval, False = full file

# Initialize FastAPI
app = FastAPI(
    title="Financial Analyst Agent API",
    description="Table-Aware RAG pipeline for financial document analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients (lazy loading)
_qdrant_client = None
_embedding_model = None
_gemini_model = None


def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
    return _qdrant_client


def get_embedding_model():
    """Get or create embedding model."""
    global _embedding_model
    if _embedding_model is None:
        print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL}...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[SUCCESS] Model loaded!")
    return _embedding_model


def get_gemini_model():
    """Get or create Gemini model."""
    global _gemini_model
    if not GEMINI_AVAILABLE:
        return None
    if _gemini_model is None:
        if not GEMINI_API_KEY:
            print("[WARNING] GOOGLE_API_KEY not set. Gemini features disabled.")
            return None
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            print(f"[SUCCESS] Gemini model '{GEMINI_MODEL}' loaded!")
            print(f"[INFO] API Key configured: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-4:]}")
        except Exception as e:
            print(f"[ERROR] Failed to load Gemini: {e}")
            return None
    return _gemini_model


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)."""
    return len(text) // 4


def extract_10k_html_from_txt(content: str) -> Optional[str]:
    """Extract FULL 10-K HTML from full-submission.txt using <TEXT> tag method"""
    try:
        # Find the first DOCUMENT section with TYPE=10-K and extract from <TEXT> tag
        pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"[ERROR] HTML extraction failed: {e}")
        return None


def convert_html_to_markdown(html_content: str) -> str:
    """Convert HTML to Markdown using markdownify, then fix table formatting"""
    md = markdownify.markdownify(html_content, heading_style="ATX")
    
    # Post-process: Fix tab-separated tables to markdown format
    # This ensures all tables are properly formatted
    lines = md.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line looks like a tab-separated table row
        if '\t' in line and line.count('\t') >= 2 and bool(re.search(r'[\d$%]', line)):
            # Collect consecutive table lines
            table_lines = [line]
            i += 1
            
            while i < len(lines):
                next_line = lines[i]
                if '\t' in next_line and next_line.count('\t') >= 2 and bool(re.search(r'[\d$%]', next_line)):
                    table_lines.append(next_line)
                    i += 1
                elif not next_line.strip():  # Empty line might be separator
                    i += 1
                    break
                else:
                    break
            
            # Convert to markdown table
            if len(table_lines) >= 2:
                rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.split('\t') if c.strip() or len(c) > 0]
                    if len(cells) >= 2:
                        rows.append(cells)
                
                if rows:
                    max_cols = max(len(r) for r in rows)
                    for r in rows:
                        while len(r) < max_cols:
                            r.append('')
                    
                    # Build markdown table
                    fixed_lines.append('| ' + ' | '.join(rows[0]) + ' |')
                    fixed_lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
                    for row in rows[1:]:
                        fixed_lines.append('| ' + ' | '.join(row) + ' |')
                    continue
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)


def extract_ticker_from_content(content: str) -> Optional[str]:
    """Extract ticker symbol from content (look for common patterns)"""
    # Try to find ticker in various patterns
    patterns = [
        r'<ticker>(\w+)</ticker>',
        r'CIK.*?(\d{10})',  # CIK number
        r'CENTRAL INDEX KEY:\s*(\d{10})',
        r'\(([A-Z]{1,5})\)',  # Ticker in parentheses
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # If it's a CIK, we can't convert to ticker easily, so skip
            if pattern.startswith('CIK') or 'INDEX' in pattern:
                continue
            return match.group(1).upper()
    
    return None


def retrieve_relevant_sections(query: str, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Priority 1: Smart Section Retrieval
    Retrieve only relevant sections from Qdrant instead of loading full file.
    """
    try:
        client = get_qdrant_client()
        embedding_model = get_embedding_model()
        
        if embedding_model is None:
            print(f"[WARNING] Embedding model not available. Using full file.")
            return []
        
        # Check if sections collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if SECTIONS_COLLECTION not in collection_names:
            print(f"[WARNING] Sections collection '{SECTIONS_COLLECTION}' not found. Using full file.")
            print(f"[INFO] Run 'python chunk_markdown_files.py' to create the sections collection.")
            return []
        
        # Generate query embedding
        import numpy as np
        query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()
        
        # Search for relevant sections
        results = client.search(
            collection_name=SECTIONS_COLLECTION,
            query_vector=query_embedding,
            query_filter={
                "must": [
                    {"key": "ticker", "match": {"value": ticker}}
                ]
            },
            limit=limit
        )
        
        sections = []
        for result in results:
            sections.append({
                'text': result.payload.get('text', ''),
                'section': result.payload.get('section', 'Unknown'),
                'score': result.score,
                'metadata': result.payload
            })
        
        print(f"[INFO] Retrieved {len(sections)} relevant sections for {ticker}")
        return sections
        
    except Exception as e:
        print(f"[WARNING] Smart retrieval failed: {e}. Falling back to full file.")
        return []


def extract_relevant_sections(content: str, query: str) -> str:
    """
    Smart section extraction based on query.
    Keeps tables intact, extracts relevant sections.
    """
    query_lower = query.lower()
    
    # Key sections to look for
    section_keywords = {
        "revenue": ["revenue", "net sales", "segment", "aws", "azure"],
        "income": ["income", "earnings", "profit", "loss"],
        "balance": ["balance sheet", "assets", "liabilities"],
        "cash": ["cash flow", "operating activities"],
        "segment": ["segment", "business segment", "geographic"]
    }
    
    # Find relevant keywords
    relevant_sections = []
    for section, keywords in section_keywords.items():
        if any(kw in query_lower for kw in keywords):
            relevant_sections.append(section)
    
    # If no specific sections, return full content
    if not relevant_sections:
        return content
    
    lines = content.split('\n')
    extracted = []
    in_relevant_section = False
    table_mode = False
    
    for i, line in enumerate(lines):
        # Check if line starts a relevant section
        for section in relevant_sections:
            if section.lower() in line.lower() and len(line) < 200:
                in_relevant_section = True
                extracted.append(line)
                continue
        
        # Always include tables (they might be relevant)
        if '|' in line and '---' in line:
            table_mode = True
            extracted.append(line)
            continue
        
        if table_mode:
            if '|' in line:
                extracted.append(line)
            else:
                # End of table
                table_mode = False
                if in_relevant_section:
                    extracted.append(line)
                in_relevant_section = False
            continue
        
        if in_relevant_section:
            extracted.append(line)
            # Stop after section ends (empty line + new heading)
            if line.strip() == '' and i < len(lines) - 1:
                next_line = lines[i+1].strip()
                if next_line and next_line[0].isupper() and len(next_line) < 100:
                    # Likely a new section
                    if not any(sec in next_line.lower() for sec in relevant_sections):
                        in_relevant_section = False
    
    result = '\n'.join(extracted)
    
    # If extraction is too small, return full content
    if len(result) < len(content) * 0.1:  # Less than 10% extracted
        return content
    
    return result


# Request/Response Models
class AnalyzeRequest(BaseModel):
    query: str
    max_companies: Optional[int] = 5


class AnalyzeResponse(BaseModel):
    query: str
    companies_found: List[str]
    file_paths: List[str]
    analysis: str
    metadata: Dict[str, Any]


class CompanyInfo(BaseModel):
    ticker: str
    year: str
    file_path: str
    tables_count: int
    size_mb: float
    lines: int


class ProcessFileResponse(BaseModel):
    success: bool
    steps: Dict[str, Any]
    ticker: Optional[str]
    html_size: int
    markdown_size: int
    markdown_preview: str
    file_path: Optional[str]
    html_file_path: Optional[str] = None
    indexed: bool = False
    ready_for_qa: bool = False
    error: Optional[str] = None


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Analyst Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/companies": "List all indexed companies",
            "/analyze": "Analyze financial query (POST)",
            "/search": "Semantic search companies (POST)",
            "/upload": "Upload and process TXT file (POST)",
            "/files/{file_path}": "Download processed Markdown files (GET)"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collections": collection_names,
            "embedding_model": EMBEDDING_MODEL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    """
    Serve processed files (Markdown or HTML) for download.
    Handles URL-encoded paths (e.g., processed_data%5CD_uploaded.md)
    """
    try:
        # Decode URL-encoded path
        import urllib.parse
        decoded_path = urllib.parse.unquote(file_path)
        
        # Handle Windows backslashes - convert to forward slashes
        decoded_path = decoded_path.replace('\\', '/')
        
        # Determine file type
        is_html = decoded_path.endswith('.html')
        media_type = 'text/html' if is_html else 'text/markdown'
        
        # Try multiple path variations
        path_variations = [
            Path(decoded_path),  # Direct path
            PROCESSED_DATA_DIR / Path(decoded_path).name,  # Just filename
            Path(decoded_path).resolve(),  # Absolute path
        ]
        
        # Also try extracting filename from path
        if 'processed_data' in decoded_path:
            filename = decoded_path.split('processed_data')[-1].lstrip('/\\')
            path_variations.append(PROCESSED_DATA_DIR / filename)
        
        file_path_obj = None
        for path_var in path_variations:
            if path_var.exists() and path_var.is_file():
                file_path_obj = path_var
                break
        
        if not file_path_obj:
            # Last resort: try to find by filename only
            filename = Path(decoded_path).name
            potential_file = PROCESSED_DATA_DIR / filename
            if potential_file.exists():
                file_path_obj = potential_file
        
        if not file_path_obj or not file_path_obj.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {decoded_path}"
            )
        
        return FileResponse(
            path=str(file_path_obj),
            filename=file_path_obj.name,
            media_type=media_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")


@app.get("/companies")
async def list_companies():
    """List all indexed companies."""
    try:
        client = get_qdrant_client()
        
        # Scroll all points
        result = client.scroll(collection_name=COLLECTION_NAME, limit=1000)
        
        companies = []
        seen_tickers = set()
        
        for point in result[0]:
            payload = point.payload
            ticker = payload.get("ticker")
            
            if ticker and ticker not in seen_tickers:
                seen_tickers.add(ticker)
                companies.append({
                    "ticker": ticker,
                    "year": payload.get("year", "2024"),
                    "file_path": payload.get("file_path", ""),
                    "tables_count": payload.get("tables_count", 0),
                    "size_mb": payload.get("size_mb", 0),
                    "lines": payload.get("lines", 0)
                })
        
        return {
            "total": len(companies),
            "companies": sorted(companies, key=lambda x: x["ticker"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing companies: {str(e)}")


@app.post("/upload", response_model=ProcessFileResponse)
async def upload_and_process(file: UploadFile = File(...)):
    """
    Upload full-submission.txt file and process it through the pipeline:
    1. Upload → 2. Extract HTML → 3. Convert to Markdown → 4. Extract Ticker → 5. Save
    """
    steps = {
        "upload": {"status": "processing", "message": "Uploading file..."},
        "extract_html": {"status": "pending", "message": "Waiting..."},
        "convert_markdown": {"status": "pending", "message": "Waiting..."},
        "extract_ticker": {"status": "pending", "message": "Waiting..."},
        "save": {"status": "pending", "message": "Waiting..."}
    }
    
    try:
        # Step 1: Upload
        file_id = str(uuid.uuid4())
        upload_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        steps["upload"] = {
            "status": "completed",
            "message": f"File uploaded: {len(content):,} bytes",
            "size": len(content)
        }
        
        # Step 2: Extract HTML
        steps["extract_html"]["status"] = "processing"
        steps["extract_html"]["message"] = "Extracting HTML from TXT..."
        
        txt_content = content.decode('utf-8', errors='ignore')
        html_content = extract_10k_html_from_txt(txt_content)
        
        if not html_content:
            return ProcessFileResponse(
                success=False,
                steps=steps,
                ticker=None,
                html_size=0,
                markdown_size=0,
                markdown_preview="",
                file_path=None,
                error="Could not extract HTML from file. Make sure it's a valid SEC full-submission.txt file."
            )
        
        html_size = len(html_content)
        steps["extract_html"] = {
            "status": "completed",
            "message": f"HTML extracted: {html_size:,} characters",
            "size": html_size
        }
        
        # Step 3: Convert to Markdown
        steps["convert_markdown"]["status"] = "processing"
        steps["convert_markdown"]["message"] = "Converting HTML to Markdown..."
        
        markdown_content = convert_html_to_markdown(html_content)
        markdown_size = len(markdown_content)
        
        steps["convert_markdown"] = {
            "status": "completed",
            "message": f"Markdown converted: {markdown_size:,} characters",
            "size": markdown_size,
            "lines": len(markdown_content.splitlines()),
            "tables_estimate": markdown_content.count('|') // 3
        }
        
        # Step 4: Extract Ticker
        steps["extract_ticker"]["status"] = "processing"
        steps["extract_ticker"]["message"] = "Extracting ticker symbol..."
        
        ticker = extract_ticker_from_content(txt_content)
        if not ticker:
            # Try to extract from filename
            filename_upper = file.filename.upper()
            ticker_match = re.search(r'([A-Z]{1,5})', filename_upper)
            if ticker_match:
                ticker = ticker_match.group(1)
            else:
                ticker = "UNKNOWN"
        
        steps["extract_ticker"] = {
            "status": "completed",
            "message": f"Ticker extracted: {ticker}",
            "ticker": ticker
        }
        
        # Step 5: Save files (HTML + Markdown)
        steps["save"]["status"] = "processing"
        steps["save"]["message"] = "Saving files..."
        
        PROCESSED_DATA_DIR.mkdir(exist_ok=True)
        
        # Save HTML file
        html_filename = f"{ticker}_uploaded.html"
        html_path = PROCESSED_DATA_DIR / html_filename
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save Markdown file
        md_filename = f"{ticker}_uploaded.md"
        md_path = PROCESSED_DATA_DIR / md_filename
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        steps["save"] = {
            "status": "completed",
            "message": f"Files saved: {md_filename}, {html_filename}",
            "file_path": str(md_path),
            "html_file_path": str(html_path)
        }
        
        # Step 6: Index in Qdrant (for RAG pipeline)
        indexed = False
        try:
            client = get_qdrant_client()
            embedding_model = get_embedding_model()
            
            if embedding_model:
                # Extract summary
                summary = markdown_content[:2000]
                key_sections = ["Item 1. Business", "Item 7. Management", "Item 8. Financial"]
                for section in key_sections:
                    idx = markdown_content.find(section)
                    if idx != -1:
                        summary += "\n\n" + markdown_content[idx:idx+500]
                
                # Generate embedding
                embedding = embedding_model.encode(summary, convert_to_numpy=True).tolist()
                
                # Create point with "uploaded" tag to separate from original 89
                from qdrant_client.models import PointStruct
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "ticker": ticker,
                        "year": "2024",  # Could extract from content
                        "file_path": str(md_path),
                        "summary": summary[:1000],
                        "tables_count": markdown_content.count('|') // 3,
                        "size_mb": markdown_size / (1024 * 1024),
                        "lines": len(markdown_content.splitlines()),
                        "source": "uploaded",  # Tag to separate from original 89
                        "uploaded_at": str(uuid.uuid4())  # Timestamp-like identifier
                    }
                )
                
                # Upsert to Qdrant
                client.upsert(collection_name=COLLECTION_NAME, points=[point])
                indexed = True
                print(f"[SUCCESS] Indexed uploaded file for {ticker} in Qdrant")
        except Exception as e:
            print(f"[WARNING] Failed to index uploaded file: {e}")
        
        # Generate preview (first 2000 chars)
        preview = markdown_content[:2000] + "..." if len(markdown_content) > 2000 else markdown_content
        
        return ProcessFileResponse(
            success=True,
            steps=steps,
            ticker=ticker,
            html_size=html_size,
            markdown_size=markdown_size,
            markdown_preview=preview,
            file_path=str(md_path),
            html_file_path=str(html_path),
            indexed=indexed,
            ready_for_qa=indexed  # Ready for QnA if indexed
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] File processing failed: {error_msg}")
        return ProcessFileResponse(
            success=False,
            steps=steps,
            ticker=None,
            html_size=0,
            markdown_size=0,
            markdown_preview="",
            file_path=None,
            error=error_msg
        )


@app.post("/search")
async def search_companies(query: str, limit: int = 10):
    """Semantic search for companies."""
    try:
        client = get_qdrant_client()
        embedding_model = get_embedding_model()
        
        if embedding_model is None:
            raise HTTPException(status_code=500, detail="Embedding model not available")
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()
        
        # Search
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        
        companies = []
        for result in results:
            companies.append({
                "ticker": result.payload.get("ticker", ""),
                "year": result.payload.get("year", "2024"),
                "score": result.score,
                "summary": result.payload.get("summary", "")[:500]
            })
        
        return {
            "query": query,
            "results": companies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze financial query using RAG pipeline.
    """
    try:
        # Step 1: Router - Extract tickers from query
        tickers = extract_tickers_simple(request.query)
        
        if not tickers:
            raise HTTPException(
                status_code=400,
                detail="No companies found in query. Please mention company names or tickers."
            )
        
        # Limit companies
        tickers = tickers[:request.max_companies]
        
        print(f"[INFO] Analyzing query: '{request.query}'")
        print(f"[INFO] Companies found: {tickers}")
        
        # Step 2: Retriever - Find companies in Qdrant
        client = get_qdrant_client()
        file_paths = []
        companies_data = []
        
        for ticker in tickers:
            # Find company in Qdrant using filter (index now exists)
            try:
                result = client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter={
                        "must": [
                            {"key": "ticker", "match": {"value": ticker}}
                        ]
                    },
                    limit=10  # Get multiple in case there are uploaded versions
                )
                
                # Prefer uploaded files if available, otherwise use original
                matching_point = None
                uploaded_point = None
                
                for point in result[0]:
                    payload = point.payload
                    if payload.get("source") == "uploaded":
                        uploaded_point = point
                    elif not matching_point:
                        matching_point = point
                
                # Use uploaded file if available, otherwise use original
                if uploaded_point:
                    payload = uploaded_point.payload
                    file_path = payload.get("file_path")
                    print(f"[INFO] Using uploaded file for {ticker}")
                elif matching_point:
                    payload = matching_point.payload
                    file_path = payload.get("file_path")
                    print(f"[INFO] Using original file for {ticker}")
                else:
                    print(f"[WARNING] Ticker {ticker} not found in Qdrant")
                    continue
            except Exception as e:
                # Fallback: scroll all and filter in Python
                print(f"[WARNING] Filter failed, using fallback: {e}")
                result = client.scroll(collection_name=COLLECTION_NAME, limit=1000)
                matching_point = None
                for point in result[0]:
                    if point.payload.get("ticker") == ticker:
                        matching_point = point
                        break
                if not matching_point:
                    print(f"[WARNING] Ticker {ticker} not found in Qdrant")
                    continue
                payload = matching_point.payload
                file_path = payload.get("file_path")
            
            # Normalize path (handle Windows/Unix paths)
            if file_path:
                # Convert backslashes to forward slashes
                file_path = file_path.replace('\\', '/')
                # Try multiple path variations
                path_variations = [
                    Path(file_path),  # Original path
                    PROCESSED_DATA_DIR / Path(file_path).name,  # Just filename in processed_data
                    PROCESSED_DATA_DIR / f"{ticker}_2024.md", # Fallback: construct from ticker
                    Path(file_path).resolve(),  # Absolute path
                ]
                
                found_path = None
                for path_var in path_variations:
                    if path_var.exists():
                        found_path = path_var
                        break
                
                if found_path:
                    # Load full file
                    with open(found_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_paths.append(str(found_path))
                    companies_data.append({
                        "ticker": ticker,
                        "file_path": str(found_path),
                        "content_length": len(content),
                        "metadata": payload
                    })
                    print(f"[INFO] Loaded file for {ticker}: {found_path}")
                else:
                    print(f"[WARNING] File not found for {ticker}. Tried: {file_path}")
                    print(f"[WARNING] Variations tried: {path_variations}")
            else:
                print(f"[WARNING] No file_path in payload for {ticker}")
        
        # Step 4: Generator - Analyze with Gemini
        gemini = get_gemini_model()
        
        if gemini is None:
            # Fallback: Return file info without analysis
            analysis = f"""
[INFO] Analysis for query: "{request.query}"

Companies analyzed: {', '.join(tickers)}
Files loaded: {len(file_paths)}
Total content size: {sum(c['content_length'] for c in companies_data)} characters.

[NOTE] Gemini API not configured. Set GOOGLE_API_KEY environment variable to enable analysis.
"""
        else:
            # Prepare content for Gemini
            all_content = []
            total_tokens = 0
            
            for company_data in companies_data:
                ticker = company_data['ticker']
                file_path = company_data['file_path']
                
                # Priority 1: Try smart section retrieval first
                if USE_SMART_RETRIEVAL:
                    sections = retrieve_relevant_sections(request.query, ticker, limit=5)
                    
                    if sections:
                        # Use retrieved sections
                        section_texts = []
                        for section in sections:
                            section_texts.append(f"### {section['section']}\n{section['text']}")
                        
                        content = "\n\n".join(section_texts)
                        tokens = estimate_tokens(content)
                        total_tokens += tokens
                        print(f"[INFO] Using smart retrieval for {ticker}: {tokens} tokens from {len(sections)} sections")
                    else:
                        # Fallback to full file
                        print(f"[INFO] Smart retrieval unavailable for {ticker}, using full file")
                        content = Path(file_path).read_text(encoding='utf-8')
                        tokens = estimate_tokens(content)
                        total_tokens += tokens
                else:
                    # Load full file (original behavior)
                    content = Path(file_path).read_text(encoding='utf-8')
                    tokens = estimate_tokens(content)
                    total_tokens += tokens
                
                # If total is too large, use smart extraction (fallback)
                if total_tokens > MAX_TOKENS_PER_FILE * len(companies_data):
                    print(f"[INFO] Content too large ({total_tokens} tokens), extracting relevant sections...")
                    content = extract_relevant_sections(content, request.query)
                    tokens = estimate_tokens(content)
                    print(f"[INFO] Extracted content: {tokens} tokens")
                
                all_content.append(f"=== {ticker} ({company_data['metadata'].get('year', '2024')}) ===\n{content}\n")
            
            # Combine all content
            combined_content = "\n\n".join(all_content)
            final_tokens = estimate_tokens(combined_content)
            
            print(f"[INFO] Sending to Gemini: {final_tokens} tokens")
            
            # Create prompt
            system_prompt = """You are a financial analyst expert. Analyze the provided financial documents and answer the user's query.

CRITICAL INSTRUCTIONS FOR TABLES:
- Pay EXTREMELY close attention to TABLES - they contain critical financial data
- Preserve EXACT numbers, dates, and percentages from tables - do not round or approximate
- When showing tables in your response, you MUST use proper markdown table format with pipe separators (|)
- DO NOT use tabs, spaces, or any other format - ONLY use markdown table format
- Markdown table format example:
  | Column 1 | Column 2 | Column 3 |
  |----------|----------|----------|
  | Data 1   | Data 2   | Data 3   |
- Extract data directly from tables - do not make up numbers
- If the query asks for a table, reconstruct it completely with all rows and columns in markdown format
- Preserve table structure: row headers (security types, categories), column headers (years, periods), and all data cells
- For calculations (percentages, differences), show your work or cite the exact values used
- Cite specific sections and table names when referencing data (e.g., "Interest Rate Risk table", "Item 7A")
- If data is not found, clearly state that rather than guessing

Format your response as a clear, structured analysis with properly formatted markdown tables when relevant. ALWAYS use | separators for tables, never tabs or spaces."""
            
            full_prompt = f"{system_prompt}\n\nUser Query: {request.query}\n\nDocuments:\n{combined_content}"
            
            try:
                # Generate response
                response = gemini.generate_content(full_prompt)
                analysis = response.text
                
                # Post-process to fix table formatting if needed
                # Check if response contains tab-separated tables
                if '\t' in analysis and analysis.count('\t') > 10:
                    print("[INFO] Detected tab-separated tables, attempting to fix format...")
                    try:
                        # Simple fix: replace tabs with | separators for table-like lines
                        lines = analysis.split('\n')
                        fixed_lines = []
                        for line in lines:
                            if '\t' in line and len(line.split('\t')) >= 3:
                                # Convert tab-separated to markdown table row
                                cells = [cell.strip() for cell in line.split('\t')]
                                fixed_lines.append('| ' + ' | '.join(cells) + ' |')
                            else:
                                fixed_lines.append(line)
                        analysis = '\n'.join(fixed_lines)
                        print("[INFO] Table formatting fixed!")
                    except Exception as e:
                        print(f"[WARNING] Could not fix table formatting: {e}")
                
                print(f"[SUCCESS] Gemini analysis complete!")
                
            except Exception as e:
                print(f"[ERROR] Gemini analysis failed: {e}")
                analysis = f"""
[ERROR] Analysis failed: {str(e)}

Companies analyzed: {', '.join(tickers)}
Files loaded: {len(file_paths)}
Total tokens: {final_tokens}

Please check your GEMINI_API_KEY and try again.
"""
        
        return AnalyzeResponse(
            query=request.query,
            companies_found=tickers,
            file_paths=file_paths,
            analysis=analysis,
            metadata={
                "total_files": len(file_paths),
                "total_content_size": sum(c['content_length'] for c in companies_data),
                "companies": companies_data
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing: {str(e)}")


def extract_tickers_simple(query: str) -> List[str]:
    """
    Simple ticker extraction using keyword matching.
    TODO: Replace with LLM-based extraction for better accuracy.
    """
    # Common company name to ticker mapping
    company_map = {
        "apple": "AAPL", "microsoft": "MSFT", "amazon": "AMZN", "google": "GOOGL",
        "alphabet": "GOOGL", "meta": "META", "facebook": "META", "tesla": "TSLA",
        "nvidia": "NVDA", "netflix": "NFLX", "disney": "DIS", "jpmorgan": "JPM",
        "jpm": "JPM", "bank of america": "BAC", "goldman sachs": "GS",
        "morgan stanley": "MS", "citigroup": "C", "wells fargo": "WFC",
        "aws": "AMZN", "azure": "MSFT", "gcp": "GOOGL"
    }
    
    query_lower = query.lower()
    found_tickers = []
    
    # Check for direct ticker mentions (uppercase 2-5 letter codes)
    ticker_pattern = r'\b([A-Z]{2,5})\b'
    direct_tickers = re.findall(ticker_pattern, query)
    found_tickers.extend(direct_tickers)
    
    # Check for company names
    for company, ticker in company_map.items():
        if company in query_lower and ticker not in found_tickers:
            found_tickers.append(ticker)
    
    return list(set(found_tickers))  # Remove duplicates


# Server startup
if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("🚀 Starting Financial Analyst Agent API Server")
    print("="*80)
    print(f"[INFO] Server will start at: http://localhost:8000")
    print(f"[INFO] API docs available at: http://localhost:8000/docs")
    print(f"[INFO] Health check: http://localhost:8000/health")
    print("="*80)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
