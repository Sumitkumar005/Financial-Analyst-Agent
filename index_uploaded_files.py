"""
Index Uploaded Files in Qdrant
Indexes all uploaded Markdown files (those with _uploaded.md suffix) in Qdrant.
This keeps uploaded files separate from the original 89 companies.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
import os

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("❌ qdrant-client not installed. Run: pip install qdrant-client")
    exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
    exit(1)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in environment variables or .env file")
    exit(1)
COLLECTION_NAME = "financial_reports"
EMBEDDING_DIM = 384
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
PROCESSED_DATA_DIR = Path("processed_data")


def extract_summary(markdown_path: Path, max_chars: int = 2000) -> str:
    """Extract a summary from the Markdown file."""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get first max_chars
        summary = content[:max_chars]
        
        # Try to find key sections
        key_sections = [
            "Item 1. Business",
            "Item 7. Management",
            "Item 8. Financial",
            "CONSOLIDATED STATEMENTS",
            "REVENUE",
            "NET INCOME"
        ]
        
        found_sections = []
        for section in key_sections:
            idx = content.find(section)
            if idx != -1:
                snippet = content[idx:idx+500]
                found_sections.append(snippet)
        
        if found_sections:
            summary += "\n\nKey Sections:\n" + "\n".join(found_sections[:3])
        
        return summary.strip()
    except Exception as e:
        print(f"[WARNING] Error reading {markdown_path}: {e}")
        return f"Financial report for {markdown_path.stem}"


def find_uploaded_files() -> List[Path]:
    """Find all uploaded Markdown files (those ending with _uploaded.md)."""
    uploaded_files = []
    
    if not PROCESSED_DATA_DIR.exists():
        return uploaded_files
    
    for md_file in PROCESSED_DATA_DIR.glob("*_uploaded.md"):
        uploaded_files.append(md_file)
    
    return uploaded_files


def extract_ticker_from_filename(filename: str) -> str:
    """Extract ticker from filename like 'AAPL_uploaded.md'."""
    parts = filename.replace('_uploaded.md', '').split('_')
    return parts[0].upper() if parts else "UNKNOWN"


def main():
    """Index all uploaded files in Qdrant."""
    print("="*80)
    print("INDEXING UPLOADED FILES IN QDRANT")
    print("="*80)
    print()
    
    # Find uploaded files
    uploaded_files = find_uploaded_files()
    
    if not uploaded_files:
        print("[INFO] No uploaded files found. Upload files through the frontend first.")
        return
    
    print(f"[INFO] Found {len(uploaded_files)} uploaded file(s)")
    print()
    
    # Initialize embedding model
    print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL}...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print("[SUCCESS] Model loaded!")
    
    # Initialize Qdrant
    print(f"\n[INFO] Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    # Check if collection exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    
    if COLLECTION_NAME not in collection_names:
        print(f"[ERROR] Collection '{COLLECTION_NAME}' does not exist!")
        print(f"[INFO] Run 'python index.py' first to create the collection.")
        return
    
    print(f"[INFO] Using collection: {COLLECTION_NAME}")
    print()
    
    # Index each uploaded file
    indexed_count = 0
    failed_count = 0
    
    for i, md_file in enumerate(uploaded_files, 1):
        ticker = extract_ticker_from_filename(md_file.name)
        print(f"[{i}/{len(uploaded_files)}] Processing {ticker}...")
        
        try:
            # Extract summary
            summary = extract_summary(md_file)
            
            # Generate embedding
            embedding = embedding_model.encode(summary, convert_to_numpy=True).tolist()
            
            # Get file stats
            content = md_file.read_text(encoding='utf-8')
            file_size = len(content)
            file_size_mb = file_size / (1024 * 1024)
            lines_count = len(content.splitlines())
            tables_count = content.count('|') // 3
            
            # Create point with "uploaded" tag
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "ticker": ticker,
                    "year": "2024",  # Could extract from content
                    "file_path": str(md_file),
                    "summary": summary[:1000],
                    "tables_count": tables_count,
                    "size_mb": file_size_mb,
                    "lines": lines_count,
                    "source": "uploaded",  # Tag to separate from original 89
                    "uploaded_at": str(uuid.uuid4())
                }
            )
            
            # Upsert to Qdrant
            client.upsert(collection_name=COLLECTION_NAME, points=[point])
            
            print(f"  ✅ Indexed: {ticker} ({file_size_mb:.2f} MB, {lines_count:,} lines)")
            indexed_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            failed_count += 1
    
    print()
    print("="*80)
    print(f"[COMPLETE] Indexed {indexed_count} uploaded file(s)")
    if failed_count > 0:
        print(f"[WARNING] {failed_count} file(s) failed to index")
    print(f"[INFO] Uploaded files are now ready for QnA and agentic analysis!")
    print("="*80)


if __name__ == "__main__":
    main()
