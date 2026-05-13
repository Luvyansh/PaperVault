from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config.settings import get_settings

settings = get_settings()
client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

print(f"Recreating '{settings.qdrant_collection}' with 768 dimensions...")

# recreate_collection forcefully deletes the old one and makes a new one
client.recreate_collection(
    collection_name=settings.qdrant_collection,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)
print("✅ Success! Qdrant is ready for 768-d MPNet embeddings.")