from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Converts text into a 768-dimensional vector representation for semantic search.
    """
    def __init__(self):
        # Upgraded to MPNet (768-d) based on superior SBERT BEIR benchmark performance
        print("Loading Embedding Model (all-mpnet-base-v2)...")
        self.model = SentenceTransformer("all-mpnet-base-v2")
        
    def generate_embedding(self, text: str) -> list[float]:
        if not text:
            return []
        
        vector = self.model.encode(text)
        return vector.tolist()

if __name__ == "__main__":
    embedder = Embedder()
    sample_text = "Machine learning models are improving rapidly."
    vector = embedder.generate_embedding(sample_text)
    
    print(f"\nText: '{sample_text}'")
    print(f"Generated Vector with {len(vector)} dimensions.") # Should print 768