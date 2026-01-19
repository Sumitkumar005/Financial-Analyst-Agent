"""
Create keyword index on 'ticker' field for financial_sections collection
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in .env file")
    exit(1)

COLLECTION_NAME = "financial_sections"

def main():
    print("="*80)
    print("Creating ticker index for financial_sections collection")
    print("="*80)
    
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    try:
        # Create keyword index on ticker field
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="ticker",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"[SUCCESS] Index created on 'ticker' field for '{COLLECTION_NAME}' collection!")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"[INFO] Index on 'ticker' already exists for '{COLLECTION_NAME}'")
        else:
            print(f"[ERROR] Failed to create index: {e}")
            return False
    
    print("="*80)
    return True

if __name__ == "__main__":
    main()
