"""
Qdrant client service
"""

from qdrant_client import QdrantClient
from app.config import QDRANT_URL, QDRANT_API_KEY

# Global client instance (lazy loading)
_qdrant_client = None


def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
    return _qdrant_client
