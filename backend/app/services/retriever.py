from qdrant_client import QdrantClient
from app.nlp.embedder import Embedder
from app.config.settings import get_settings

class PaperRetriever:
    """
    Handles semantic search queries against the Qdrant vector database.
    """
    def __init__(self):
        self.settings = get_settings()
        self.qdrant = QdrantClient(url=self.settings.qdrant_url, api_key=self.settings.qdrant_api_key)
        self.embedder = Embedder()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        # 1. Convert the user's question into a 384-dimensional vector
        query_vector = self.embedder.generate_embedding(query)

        # 2. Search Qdrant for the closest matching vectors
        search_results = self.qdrant.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=query_vector,
            limit=limit,
            with_payload=True 
        )

        # 3. Format the results into a clean list of dictionaries
        formatted_results = []
        for result in search_results: # <-- Here is your loop!
            
            # Fallback URL generator in case it isn't in the database
            fallback_url = f"https://arxiv.org/abs/{result.payload.get('arxiv_id')}"
            
            formatted_results.append({
                "score": result.score,
                "db_id": result.id,
                "arxiv_id": result.payload.get("arxiv_id"),
                "title": result.payload.get("title"),
                "category": result.payload.get("category"),
                "published_at": result.payload.get("published_at"),
                "abstract": result.payload.get("abstract", ""),
                # --- NEW FIELDS FOR THE FRONTEND MODAL ---
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