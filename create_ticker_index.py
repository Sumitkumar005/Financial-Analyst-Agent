"""
Create index for ticker field in Qdrant to enable filtering.
This is optional - the server will work without it, but filtering will be slower.
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in environment variables or .env file")
    exit(1)
COLLECTION_NAME = "financial_reports"

def create_index():
    """Create index for ticker field."""
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    try:
        # Create payload index for ticker field
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="ticker",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"[SUCCESS] Created index for 'ticker' field in collection '{COLLECTION_NAME}'")
        return True
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"[INFO] Index for 'ticker' already exists")
            return True
        else:
            print(f"[ERROR] Failed to create index: {e}")
            return False

if __name__ == "__main__":
    print("Creating index for 'ticker' field...")
    create_index()
