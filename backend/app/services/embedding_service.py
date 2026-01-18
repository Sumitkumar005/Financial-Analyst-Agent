"""
Embedding model service
"""

from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

# Global model instance (lazy loading)
_embedding_model = None


def get_embedding_model():
    """Get or create embedding model."""
    global _embedding_model
    if _embedding_model is None:
        print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL}...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[SUCCESS] Model loaded!")
    return _embedding_model
