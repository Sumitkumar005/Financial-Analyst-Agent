"""
File retrieval and section extraction service
"""

from typing import List, Dict, Any
from backend.app.services.qdrant_service import get_qdrant_client
from backend.app.services.embedding_service import get_embedding_model
from backend.app.config import SECTIONS_COLLECTION

# Try to use hybrid retriever if available
try:
    from backend.app.services.hybrid_retriever import get_hybrid_retriever
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False
    print("[INFO] Hybrid retriever not available, using dense-only search")


def retrieve_relevant_sections(query: str, ticker: str, limit: int = 5, use_hybrid: bool = True) -> List[Dict[str, Any]]:
    """
    Priority 1: Smart Section Retrieval
    Retrieve only relevant sections from Qdrant instead of loading full file.
    Uses hybrid search (dense + sparse/BM25) if available, otherwise falls back to dense-only.
    """
    # Try hybrid retriever first (if available and enabled)
    if use_hybrid and HYBRID_AVAILABLE:
        try:
            hybrid_retriever = get_hybrid_retriever()
            results = hybrid_retriever.retrieve(query, ticker, limit, use_hybrid=True)
            
            # Convert to expected format
            sections = []
            for result in results:
                sections.append({
                    'text': result.get('text', ''),
                    'section': result.get('section', 'Unknown'),
                    'score': result.get('final_score', result.get('score', 0.0)),
                    'metadata': result.get('metadata', {})
                })
            
            print(f"[INFO] ✅ Hybrid retrieval: {len(sections)} relevant sections for {ticker} (dense + BM25)")
            return sections
        except Exception as e:
            print(f"[WARNING] Hybrid retrieval failed: {e}. Falling back to dense-only search.")
            # Fall through to dense-only search
    
    # Fallback: Dense-only search (original implementation)
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
            print(f"[INFO] Run 'python -m backend.scripts.chunk_markdown_files' to create the sections collection.")
            return []
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()
        
        # Import Filter for query
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Search for relevant sections using query_points
        results = client.query_points(
            collection_name=SECTIONS_COLLECTION,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="ticker",
                        match=MatchValue(value=ticker)
                    )
                ]
            ),
            limit=limit
            # Note: SearchParams(ef=...) not supported in this Qdrant version
            # Qdrant uses optimized HNSW by default
        )
        
        sections = []
        for result in results.points:
            sections.append({
                'text': result.payload.get('text', ''),
                'section': result.payload.get('section', 'Unknown'),
                'score': result.score,
                'metadata': result.payload
            })
        
        print(f"[INFO] Retrieved {len(sections)} relevant sections for {ticker} (dense-only)")
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
