"""
Vector Indexer for Table-Aware RAG Pipeline
Indexes all 89 company Markdown files in Qdrant for semantic search.
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
    SentenceTransformer = None

# Configuration
# Qdrant Cloud Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in environment variables or .env file")
    print("Please create a .env file with your Qdrant credentials")
    exit(1)
COLLECTION_NAME = "financial_reports"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, free, good quality
# Paths relative to project root
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

METADATA_FILE = project_root / "conversion_metadata.json"
PROCESSED_DATA_DIR = project_root / "processed_data"


def get_embedding_model():
    """Initialize sentence-transformers embedding model."""
    if SentenceTransformer is None:
        print("[ERROR] sentence-transformers not available!")
        return None
    
    print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL}...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[SUCCESS] Model loaded! Dimension: {EMBEDDING_DIM}")
        return lambda text: model.encode(text, convert_to_numpy=True).tolist()
    except Exception as e:
        print(f"[ERROR] Error loading model: {e}")
        return None


def extract_summary(markdown_path: Path, max_chars: int = 2000) -> str:
    """
    Extract a summary from the Markdown file.
    Strategy: First section + key financial terms.
    """
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


def load_metadata() -> List[Dict[str, Any]]:
    """Load conversion metadata."""
    if not Path(METADATA_FILE).exists():
        print(f"[ERROR] {METADATA_FILE} not found!")
        return []
    
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def initialize_qdrant(client: QdrantClient) -> bool:
    """Initialize Qdrant collection if it doesn't exist."""
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"[INFO] Collection '{COLLECTION_NAME}' already exists.")
            # Optionally delete and recreate
            response = input(f"   Delete and recreate? (y/N): ").strip().lower()
            if response == 'y':
                client.delete_collection(COLLECTION_NAME)
                print(f"   Deleted existing collection.")
            else:
                return True
        
        # Create collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"[SUCCESS] Created collection '{COLLECTION_NAME}' with dimension {EMBEDDING_DIM}")
        return True
    except Exception as e:
        print(f"[ERROR] Error initializing Qdrant: {e}")
        return False


def index_companies(client: QdrantClient, embedding_fn) -> int:
    """Index all companies in Qdrant."""
    metadata = load_metadata()
    
    if not metadata:
        print("[ERROR] No metadata found. Run conversion first.")
        return 0
    
    print(f"\n[INFO] Indexing {len(metadata)} companies...")
    
    points = []
    failed = []
    
    for i, company_data in enumerate(metadata, 1):
        ticker = company_data.get('ticker', 'UNKNOWN')
        markdown_file = company_data.get('markdown_file', '')
        
        # Convert Windows path to forward slashes if needed
        markdown_path = Path(markdown_file.replace('\\', '/'))
        
        if not markdown_path.exists():
            # Try relative path
            markdown_path = PROCESSED_DATA_DIR / markdown_path.name
        
        if not markdown_path.exists():
            print(f"[WARNING] [{i}/{len(metadata)}] {ticker}: File not found: {markdown_file}")
            failed.append(ticker)
            continue
        
        # Extract summary
        summary = extract_summary(markdown_path)
        
        # Generate embedding
        try:
            embedding = embedding_fn(summary)
        except Exception as e:
            print(f"[WARNING] [{i}/{len(metadata)}] {ticker}: Embedding error: {e}")
            failed.append(ticker)
            continue
        
        # Create point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "ticker": ticker,
                "year": company_data.get('year', '2024'),
                "file_path": str(markdown_path),
                "summary": summary[:1000],  # Store truncated summary
                "tables_count": company_data.get('estimated_tables', 0),
                "size_mb": company_data.get('markdown_size_mb', 0),
                "lines": company_data.get('markdown_lines', 0)
            }
        )
        points.append(point)
        
        if i % 10 == 0:
            print(f"   Processed {i}/{len(metadata)} companies...")
    
    # Upload to Qdrant
    if points:
        print(f"\n[INFO] Uploading {len(points)} points to Qdrant...")
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"[SUCCESS] Successfully indexed {len(points)} companies!")
            if failed:
                print(f"[WARNING] Failed to index {len(failed)} companies: {', '.join(failed)}")
            return len(points)
        except Exception as e:
            print(f"[ERROR] Error uploading to Qdrant: {e}")
            return 0
    
    return 0


def verify_index(client: QdrantClient) -> None:
    """Verify the index was created correctly."""
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"\n[INFO] Collection Info:")
        print(f"   Name: {COLLECTION_NAME}")
        print(f"   Points: {collection_info.points_count}")
        print(f"   Vector Size: {EMBEDDING_DIM}")
        
        # Sample a few points
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=3
        )
        if result[0]:
            print(f"\n[INFO] Sample Points:")
            for point in result[0]:
                print(f"   - {point.payload.get('ticker')} ({point.payload.get('year')})")
    except Exception as e:
        print(f"[WARNING] Error verifying index: {e}")


def main():
    """Main indexing function."""
    print("=" * 60)
    print("Financial Reports Vector Indexer")
    print("=" * 60)
    
    # Check Qdrant connection (Cloud)
    print(f"\n[INFO] Connecting to Qdrant Cloud...")
    print(f"   URL: {QDRANT_URL}")
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        
        # Test connection
        client.get_collections()
        print("[SUCCESS] Connected to Qdrant Cloud!")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Qdrant: {e}")
        print("\n💡 Check your QDRANT_URL and QDRANT_API_KEY in .env file")
        print(f"   Current URL: {QDRANT_URL}")
        if not QDRANT_API_KEY:
            print("   ⚠️  QDRANT_API_KEY not set (may be required for your cluster)")
        return
    
    # Initialize collection
    if not initialize_qdrant(client):
        return
    
    # Get embedding model
    embedding_fn = get_embedding_model()
    if embedding_fn is None:
        print("[ERROR] Cannot proceed without embedding model!")
        return
    
    # Index companies
    indexed_count = index_companies(client, embedding_fn)
    
    if indexed_count > 0:
        verify_index(client)
        print(f"\n[SUCCESS] Indexing complete! {indexed_count} companies indexed.")
        print(f"\n[INFO] Next step: Build the FastAPI agent (server.py)")
    else:
        print("\n[ERROR] No companies were indexed. Check errors above.")


if __name__ == "__main__":
    main()
