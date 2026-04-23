from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Converts text into a 384-dimensional vector representation for semantic search.
    """
    def __init__(self):
        # all-MiniLM-L6-v2 is the standard for local, fast, accurate embeddings.
        # It's small (~80MB) and extremely fast on CPUs.
        print("Loading Embedding Model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
    def generate_embedding(self, text: str) -> list[float]:
        """
        Takes a string and returns a list of floats (the vector).
        """
        if not text:
            return []
        
        # .encode() returns a NumPy array. We convert it to a standard Python list
        # because our Qdrant vector database expects a standard JSON-serializable list.
        vector = self.model.encode(text)
        return vector.tolist()

if __name__ == "__main__":
    embedder = Embedder()
    sample_text = "Machine learning models are improving rapidly."
    vector = embedder.generate_embedding(sample_text)
    
    print(f"\nText: '{sample_text}'")
    print(f"Generated Vector with {len(vector)} dimensions.")
    print(f"First 5 numbers in the vector: {vector[:5]}")