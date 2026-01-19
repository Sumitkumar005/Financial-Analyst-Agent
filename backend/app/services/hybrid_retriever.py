"""
Hybrid Retriever: Combines dense vector search + sparse keyword search (BM25)
for better retrieval accuracy.
"""

from typing import List, Dict, Any
from backend.app.services.qdrant_service import get_qdrant_client
from backend.app.services.embedding_service import get_embedding_model
from backend.app.config import SECTIONS_COLLECTION
from qdrant_client.models import Filter, FieldCondition, MatchValue

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print("[WARNING] rank-bm25 not installed. Install with: pip install rank-bm25")


class HybridRetriever:
    """
    Hybrid retrieval combining:
    1. Dense vector search (semantic similarity)
    2. Sparse keyword search (BM25)
    """
    
    def __init__(self):
        self.client = get_qdrant_client()
        self.embedding_model = get_embedding_model()
        self.bm25_indexes = {}  # Per-ticker BM25 indexes
    
    def retrieve(self, query: str, ticker: str, limit: int = 5, use_hybrid: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve relevant sections using hybrid search.
        
        Args:
            query: User query
            ticker: Company ticker
            limit: Number of results
            use_hybrid: Whether to use hybrid search (True) or dense only (False)
        """
        if not use_hybrid or not BM25_AVAILABLE:
            # Fallback to dense-only search
            return self._dense_search(query, ticker, limit)
        
        # Hybrid search: combine dense + sparse
        dense_results = self._dense_search(query, ticker, limit * 2)  # Get more candidates
        sparse_results = self._sparse_search(query, ticker, limit * 2)
        
        # Combine and rerank
        combined = self._combine_results(dense_results, sparse_results, limit)
        
        return combined
    
    def _dense_search(self, query: str, ticker: str, limit: int) -> List[Dict[str, Any]]:
        """Dense vector search using embeddings."""
        if self.embedding_model is None:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True).tolist()
        
        # Search in Qdrant
        try:
            results = self.client.query_points(
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
                    'dense_score': result.score,
                    'sparse_score': 0.0,
                    'metadata': result.payload
                })
            
            return sections
        except Exception as e:
            print(f"[WARNING] Dense search failed: {e}")
            return []
    
    def _sparse_search(self, query: str, ticker: str, limit: int) -> List[Dict[str, Any]]:
        """Sparse keyword search using BM25."""
        # Build BM25 index if not exists
        if ticker not in self.bm25_indexes:
            self._build_bm25_index(ticker)
        
        if ticker not in self.bm25_indexes:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        bm25 = self.bm25_indexes[ticker]['bm25']
        scores = bm25.get_scores(query_tokens)
        
        # Get chunks with scores
        chunks = self.bm25_indexes[ticker]['chunks']
        results = [
            {
                'text': chunk['text'],
                'section': chunk['section'],
                'score': float(score),
                'dense_score': 0.0,
                'sparse_score': float(score),
                'metadata': chunk
            }
            for chunk, score in zip(chunks, scores)
        ]
        
        # Sort by score
        results.sort(key=lambda x: x['sparse_score'], reverse=True)
        return results[:limit]
    
    def _build_bm25_index(self, ticker: str):
        """Build BM25 index for a ticker by fetching all chunks."""
        try:
            # Fetch all chunks for this ticker
            results = self.client.scroll(
                collection_name=SECTIONS_COLLECTION,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="ticker",
                            match=MatchValue(value=ticker)
                        )
                    ]
                ),
                limit=1000  # Adjust if needed
            )
            
            chunks = []
            corpus = []
            
            for point in results[0]:
                chunk_text = point.payload.get('text', '')
                if chunk_text:
                    chunks.append({
                        'text': chunk_text,
                        'section': point.payload.get('section', 'Unknown'),
                        'metadata': point.payload
                    })
                    # Tokenize for BM25
                    tokens = chunk_text.lower().split()
                    corpus.append(tokens)
            
            if corpus:
                # Create BM25 index
                bm25 = BM25Okapi(corpus)
                self.bm25_indexes[ticker] = {
                    'bm25': bm25,
                    'chunks': chunks
                }
                print(f"[INFO] Built BM25 index for {ticker} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"[WARNING] Failed to build BM25 index for {ticker}: {e}")
    
    def _combine_results(self, dense_results: List[Dict], sparse_results: List[Dict], limit: int) -> List[Dict]:
        """Combine dense and sparse results with weighted fusion."""
        # Create a map of chunks by text (simple deduplication)
        combined_map = {}
        
        # Add dense results
        for result in dense_results:
            chunk_key = result['text'][:100]  # Use first 100 chars as key
            combined_map[chunk_key] = result
        
        # Add/update with sparse results
        for result in sparse_results:
            chunk_key = result['text'][:100]
            if chunk_key in combined_map:
                # Update sparse score
                combined_map[chunk_key]['sparse_score'] = result['sparse_score']
            else:
                combined_map[chunk_key] = result
        
        # Normalize scores and combine
        final_results = []
        for chunk_key, result in combined_map.items():
            # Normalize scores (both should be 0-1)
            dense_norm = result.get('dense_score', 0.0)
            sparse_norm = min(result.get('sparse_score', 0.0) / 10.0, 1.0)  # Normalize BM25 score
            
            # Weighted fusion: 70% semantic, 30% keyword
            final_score = 0.7 * dense_norm + 0.3 * sparse_norm
            
            result['final_score'] = final_score
            final_results.append(result)
        
        # Sort by final score
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        return final_results[:limit]


# Global instance
_hybrid_retriever = None

def get_hybrid_retriever() -> HybridRetriever:
    """Get or create hybrid retriever instance."""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever
