"""
Priority 1: Smart Section Retrieval - Chunk MD Files by Sections
Chunks markdown files into logical sections while preserving table integrity.
Creates embeddings for each chunk and stores in Qdrant.
"""

import json
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
import os

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("[ERROR] qdrant-client not installed. Run: pip install qdrant-client")
    exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("[ERROR] sentence-transformers not installed. Run: pip install sentence-transformers")
    exit(1)

# Configuration
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add project root to path
sys.path.insert(0, str(project_root))

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in environment variables or .env file")
    exit(1)

COLLECTION_NAME = "financial_sections"  # New collection for chunks
EMBEDDING_DIM = 384
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
PROCESSED_DATA_DIR = project_root / "processed_data"
# Note: We scan processed_data directly, no metadata file needed

# Standard 10-K section patterns
SECTION_PATTERNS = [
    (r"^Item\s+1\.?\s*[:\-]?\s*Business", "Business"),
    (r"^Item\s+1A\.?\s*[:\-]?\s*Risk\s+Factors", "Risk Factors"),
    (r"^Item\s+1B\.?\s*[:\-]?\s*Unresolved", "Unresolved Staff Comments"),
    (r"^Item\s+1C\.?\s*[:\-]?\s*Cybersecurity", "Cybersecurity"),
    (r"^Item\s+2\.?\s*[:\-]?\s*Properties", "Properties"),
    (r"^Item\s+3\.?\s*[:\-]?\s*Legal\s+Proceedings", "Legal Proceedings"),
    (r"^Item\s+4\.?\s*[:\-]?\s*Mine\s+Safety", "Mine Safety"),
    (r"^Item\s+5\.?\s*[:\-]?\s*Market", "Market Information"),
    (r"^Item\s+6\.?\s*[:\-]?\s*\[?Reserved\]?", "Reserved"),
    (r"^Item\s+7\.?\s*[:\-]?\s*Management", "MD&A"),
    (r"^Item\s+7A\.?\s*[:\-]?\s*Quantitative", "Market Risk"),
    (r"^Item\s+8\.?\s*[:\-]?\s*Financial\s+Statements", "Financial Statements"),
    (r"^Item\s+9\.?\s*[:\-]?\s*Changes", "Changes in Accountants"),
    (r"^Item\s+9A\.?\s*[:\-]?\s*Controls", "Controls and Procedures"),
    (r"^Item\s+9B\.?\s*[:\-]?\s*Other\s+Information", "Other Information"),
    (r"^Item\s+10\.?\s*[:\-]?\s*Directors", "Directors and Officers"),
    (r"^Item\s+11\.?\s*[:\-]?\s*Executive\s+Compensation", "Executive Compensation"),
    (r"^Item\s+12\.?\s*[:\-]?\s*Security\s+Ownership", "Security Ownership"),
    (r"^Item\s+13\.?\s*[:\-]?\s*Certain\s+Relationships", "Relationships and Transactions"),
    (r"^Item\s+14\.?\s*[:\-]?\s*Principal\s+Accountant", "Principal Accountant"),
    (r"^CONSOLIDATED\s+STATEMENTS?\s+OF\s+(INCOME|OPERATIONS|EARNINGS)", "Income Statement"),
    (r"^CONSOLIDATED\s+BALANCE\s+SHEETS?", "Balance Sheet"),
    (r"^CONSOLIDATED\s+STATEMENTS?\s+OF\s+CASH\s+FLOWS?", "Cash Flow Statement"),
    (r"^NOTES?\s+TO\s+(CONSOLIDATED\s+)?FINANCIAL\s+STATEMENTS?", "Notes to Financial Statements"),
    (r"^SEGMENT\s+INFORMATION", "Segment Information"),
    (r"^REVENUE", "Revenue"),
    (r"^NET\s+INCOME", "Net Income"),
]


def clean_xbrl_noise(content: str) -> str:
    """
    Priority 2: Remove XBRL metadata noise from start of file.
    """
    lines = content.split('\n')
    cleaned_lines = []
    skip_xbrl = True
    
    for line in lines:
        # Stop skipping when we hit actual content
        if skip_xbrl:
            # Skip XBRL metadata lines
            if (line.strip().startswith('xml') or 
                line.strip().startswith('aapl-') or
                line.strip().startswith('false') or
                'http://fasb.org' in line or
                'http://www.' in line and 'Member' in line or
                line.strip() == ''):
                continue
            # Stop skipping when we see actual content
            if line.strip() and not any(xbrl_indicator in line for xbrl_indicator in [
                'us-gaap:', 'xbrli:', 'iso4217:', 'aapl:', 'Member', 'http://'
            ]):
                skip_xbrl = False
        
        if not skip_xbrl:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def chunk_by_sections(content: str, ticker: str) -> List[Dict[str, Any]]:
    """
    Chunk markdown content by sections while preserving tables.
    Returns list of chunks with metadata.
    """
    chunks = []
    lines = content.split('\n')
    
    current_section = "Introduction"
    current_chunk_lines = []
    current_chunk_start = 0
    in_table = False
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect if we're in a table
        if line.strip().startswith('|') and '---' not in line:
            in_table = True
            table_lines.append(line)
        elif in_table:
            # Continue collecting table lines
            if line.strip().startswith('|') or line.strip() == '':
                table_lines.append(line)
            else:
                # Table ended, add to chunk
                if table_lines:
                    current_chunk_lines.extend(table_lines)
                    table_lines = []
                in_table = False
                current_chunk_lines.append(line)
        else:
            current_chunk_lines.append(line)
        
        # Check for section headers
        section_found = None
        for pattern, section_name in SECTION_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                section_found = section_name
                break
        
        # If we found a new section, save current chunk
        if section_found and section_found != current_section:
            if current_chunk_lines:
                chunk_text = '\n'.join(current_chunk_lines).strip()
                if len(chunk_text) > 100:  # Only save substantial chunks
                    chunks.append({
                        'text': chunk_text,
                        'section': current_section,
                        'start_line': current_chunk_start,
                        'end_line': i,
                        'ticker': ticker
                    })
            
            # Start new chunk
            current_section = section_found
            current_chunk_lines = [line]  # Include section header
            current_chunk_start = i
        
        i += 1
    
    # Add final chunk
    if current_chunk_lines:
        chunk_text = '\n'.join(current_chunk_lines).strip()
        if len(chunk_text) > 100:
            chunks.append({
                'text': chunk_text,
                'section': current_section,
                'start_line': current_chunk_start,
                'end_line': len(lines),
                'ticker': ticker
            })
    
    return chunks


def initialize_collection(client: QdrantClient) -> bool:
    """Initialize Qdrant collection for sections."""
    try:
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"[INFO] Collection '{COLLECTION_NAME}' already exists. Deleting to recreate...")
            client.delete_collection(COLLECTION_NAME)
        
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
                # Note: Qdrant uses HNSW by default for efficient vector search
                # HNSW parameters are optimized automatically
            )
        )
        print(f"[SUCCESS] Collection '{COLLECTION_NAME}' created!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create collection: {e}")
        return False


def extract_ticker_from_filename(filename: str) -> str:
    """Extract ticker from filename like AAPL_2024.md -> AAPL"""
    # Remove extension and split by underscore
    name = Path(filename).stem
    parts = name.split('_')
    if parts:
        return parts[0].upper()
    return "UNKNOWN"


def main():
    """Main function to chunk and index all MD files."""
    print("="*80)
    print("PRIORITY 1: Smart Section Retrieval - Chunking & Indexing")
    print("="*80)
    
    # Find all MD files in processed_data directory
    if not PROCESSED_DATA_DIR.exists():
        print(f"[ERROR] Directory not found: {PROCESSED_DATA_DIR}")
        return
    
    md_files = list(PROCESSED_DATA_DIR.glob("*.md"))
    
    if not md_files:
        print(f"[ERROR] No MD files found in {PROCESSED_DATA_DIR}")
        return
    
    print(f"\n[INFO] Found {len(md_files)} MD files to process")
    
    # Initialize embedding model
    print(f"\n[INFO] Loading embedding model: {EMBEDDING_MODEL}...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print("[SUCCESS] Model loaded!")
    
    # Initialize Qdrant
    print(f"\n[INFO] Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    if not initialize_collection(client):
        return
    
    # Process each MD file
    all_points = []
    total_chunks = 0
    processed_count = 0
    
    for md_file in md_files:
        # Extract ticker from filename
        ticker = extract_ticker_from_filename(md_file.name)
        
        # Extract year from filename if available (e.g., AAPL_2024.md)
        year = "2024"  # Default
        name_parts = md_file.stem.split('_')
        for part in name_parts:
            if part.isdigit() and len(part) == 4:
                year = part
                break
        
        print(f"\n[PROCESSING] {ticker} ({year}) - {md_file.name}...")
        
        try:
            # Read and clean file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean XBRL noise
            content = clean_xbrl_noise(content)
            
            # Chunk by sections
            chunks = chunk_by_sections(content, ticker)
            
            print(f"  -> Found {len(chunks)} sections")
            
            # Create embeddings and prepare points
            for chunk in chunks:
                # Generate embedding
                embedding = embedding_model.encode(chunk['text'], convert_to_numpy=True).tolist()
                
                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        'ticker': ticker,
                        'section': chunk['section'],
                        'text': chunk['text'],
                        'start_line': chunk['start_line'],
                        'end_line': chunk['end_line'],
                        'year': year,
                        'file_path': str(md_file),
                        'chunk_length': len(chunk['text']),
                        'tables_count': chunk['text'].count('| --- |')  # Rough estimate
                    }
                )
                all_points.append(point)
                total_chunks += 1
            
            processed_count += 1
            
            # Batch upload every 100 chunks
            if len(all_points) >= 100:
                client.upsert(collection_name=COLLECTION_NAME, points=all_points)
                print(f"  -> Uploaded {len(all_points)} chunks to Qdrant")
                all_points = []
        
        except Exception as e:
            print(f"  [ERROR] Failed to process {md_file.name}: {e}")
            continue
    
    # Upload remaining points
    if all_points:
        client.upsert(collection_name=COLLECTION_NAME, points=all_points)
        print(f"\n[SUCCESS] Uploaded final {len(all_points)} chunks")
    
    print(f"\n{'='*80}")
    print(f"[COMPLETE] Indexed {total_chunks} chunks from {processed_count} companies")
    print(f"[INFO] Collection: {COLLECTION_NAME}")
    print(f"[INFO] Use this collection for smart section retrieval!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
