import logging
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from app.nlp.embedder import Embedder
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

class PaperRetriever:
    """
    Handles semantic search queries against the Qdrant vector database.
    """
    def __init__(self):
        self.settings = get_settings()
        self.qdrant = QdrantClient(url=self.settings.qdrant_url, api_key=self.settings.qdrant_api_key)
        self.embedder = Embedder()
        self.similarity_threshold = 0.05 # Based on your Kaggle EDA findings

    def search(self, query: str, limit: int = 5) -> list[dict]:
        # 1. Convert the user's question into a vector (Ensure Embedder uses 768-d MPNet!)
        query_vector = self.embedder.generate_embedding(query)

        # 2. Search Qdrant with Error Handling
        try:
            search_results = self.qdrant.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=query_vector,
                limit=limit,
                with_payload=True 
            )
        except UnexpectedResponse as e:
            logger.error(f"Qdrant DB Error: {str(e)}")
            return [] # Return empty list gracefully if DB fails

        # 3. Format results AND apply the similarity threshold
        formatted_results = []
        for result in search_results:
            
            # Skip papers that are mathematically irrelevant to the query
            if result.score < self.similarity_threshold:
                logger.warning(f"Discarded paper '{result.payload.get('arxiv_id')}' (Score {result.score:.2f} below threshold)")
                continue
                
            fallback_url = f"https://arxiv.org/abs/{result.payload.get('arxiv_id')}"
            
            formatted_results.append({
                "score": result.score,
                "db_id": result.id,
                "arxiv_id": result.payload.get("arxiv_id"),
                "title": result.payload.get("title"),
                "category": result.payload.get("category"),
                "published_at": result.payload.get("published_at"),
                "abstract": result.payload.get("abstract", ""),
                "authors": result.payload.get("authors", "Unknown Author"), 
                "arxiv_url": result.payload.get("arxiv_url", fallback_url) 
            })

        return formatted_results

# Quick local test
if __name__ == "__main__":
    retriever = PaperRetriever()
    test_query = "What are the latest advancements in natural language processing and transformers?"
    print(f"\nSearching for: '{test_query}'...\n")
    
    results = retriever.search(test_query, limit=3)
    
    for r in results:
        print(f"[Score: {r['score']:.4f}] {r['title']} ({r['category']})")