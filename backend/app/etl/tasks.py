import logging
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

from app.etl.arxiv_client import ArxivClient
from app.services.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models import Paper, Entity
from app.nlp.ner import NERProcessor
from app.nlp.embedder import Embedder
from app.config.settings import get_settings

# --- NEW: Import the ML Service we just built ---
from app.services.ml_services import ml_classifier

logger = logging.getLogger(__name__)
settings = get_settings()

logger.info("Initializing NLP models for Celery worker...")
ner_processor = NERProcessor()
embedder = Embedder()

# Initialize ML Models in the Celery Worker memory
ml_classifier.load_models()

# Initialize Qdrant Vector DB
qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
try:
    qdrant.get_collection(settings.qdrant_collection)
except Exception:
    logger.info(f"Creating Qdrant collection: {settings.qdrant_collection}")
    qdrant.create_collection(
        collection_name=settings.qdrant_collection,
        # --- FIX: Upgraded to 768 dimensions for MPNet ---
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

@celery_app.task(
    name="app.etl.tasks.ingest_paper",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=60,
    queue="ingestion",
)
def ingest_paper(self, paper_dict: dict) -> dict:
    arxiv_id = paper_dict.get('arxiv_id')
    logger.info(f"Starting ingestion for paper: {arxiv_id}")
    
    db = SessionLocal()
    try:
        exists = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
        if exists:
            return {"status": "skipped", "arxiv_id": arxiv_id}

        pub_date = paper_dict.get("published_at")
        if isinstance(pub_date, str):
            pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))

        abstract = paper_dict.get("abstract", "")
        actual_category = paper_dict.get("category")
        
        # --- NEW: Run the paper through the Stacking Ensemble! ---
        ml_prediction = {"predicted_category": None, "confidence": None}
        if ml_classifier.is_ready:
            try:
                ml_prediction = ml_classifier.predict_category(abstract)
                logger.info(f"ML Prediction: {ml_prediction['predicted_category']} (Actual: {actual_category})")
            except Exception as e:
                logger.error(f"ML Classification failed for {arxiv_id}: {e}")

        # Vector embedding (768-d)
        entities_data = ner_processor.extract_entities(abstract)
        summary = abstract 
        vector = embedder.generate_embedding(summary)

        # 3. Load (Relational DB)
        new_paper = Paper(
            arxiv_id=arxiv_id,
            title=paper_dict.get("title"),
            abstract=abstract,
            summary=summary,
            authors=paper_dict.get("authors"),
            category=actual_category, # Store the actual ArXiv category
            pdf_url=paper_dict.get("pdf_url"),
            arxiv_url=paper_dict.get("arxiv_url"),
            published_at=pub_date,
            is_processed=True
        )
        db.add(new_paper)
        db.flush() 

        for e_data in entities_data:
            db.add(Entity(
                paper_id=new_paper.id, 
                entity_type=e_data["entity_type"], 
                value=e_data["value"]
            ))

        # 4. Load (Vector DB)
        qdrant.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=new_paper.id, 
                    vector=vector, 
                    payload={
                        "arxiv_id": new_paper.arxiv_id,
                        "title": new_paper.title,
                        "category": new_paper.category,
                        # --- NEW: Save ML predictions to Qdrant so the frontend/PowerBI can see them ---
                        "ml_predicted_category": ml_prediction.get("predicted_category"),
                        "ml_confidence": ml_prediction.get("confidence"),
                        "published_at": new_paper.published_at.isoformat(),
                        "abstract": new_paper.abstract,
                        "authors": new_paper.authors, 
                        "arxiv_url": new_paper.arxiv_url 
                    }
                )
            ]
        )

        db.commit()
        return {"status": "success", "arxiv_id": arxiv_id, "db_id": new_paper.id}

    except Exception as e:
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@celery_app.task(
    name="app.etl.tasks.refresh_topics",
    queue="analytics",
)
def refresh_topics() -> dict:
    logger.info("Topic refresh triggered. BERTopic implementation pending.")
    return {"status": "pending_bertopic_implementation"}

@celery_app.task(
    name="app.etl.tasks.fetch_daily_papers",
    queue="ingestion"
)
def fetch_daily_papers() -> dict:
    logger.info("Initializing ArxivClient for daily fetch...")
    client = ArxivClient()
    papers_list = client.fetch_papers()

    if not papers_list:
        logger.warning("No papers fetched today.")
        return {"status": "no_papers"}

    queued_count = 0
    for paper in papers_list:
        celery_app.send_task(
            name="app.etl.tasks.ingest_paper",
            kwargs={"paper_dict": paper},
            queue="ingestion"
        )
        queued_count += 1

    celery_app.send_task(name="app.etl.tasks.refresh_topics", queue="analytics")
    return {"status": "success", "queued": queued_count}