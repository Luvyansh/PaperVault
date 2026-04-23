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

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------
# GLOBAL ML INITIALIZATION
# Removed the heavy DistilBART summarizer to prevent CPU lockup
# ---------------------------------------------------------
logger.info("Initializing NLP models for Celery worker...")
ner_processor = NERProcessor()
embedder = Embedder()

# Initialize Qdrant Vector DB
qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
try:
    qdrant.get_collection(settings.qdrant_collection)
except Exception:
    logger.info(f"Creating Qdrant collection: {settings.qdrant_collection}")
    qdrant.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
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
            logger.info(f"Paper {arxiv_id} already exists. Skipping.")
            return {"status": "skipped", "arxiv_id": arxiv_id}

        pub_date = paper_dict.get("published_at")
        if isinstance(pub_date, str):
            pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))

        abstract = paper_dict.get("abstract", "")
        
        # 2. Transform (NLP Pipeline - Streamlined)
        entities_data = ner_processor.extract_entities(abstract)
        
        # BYPASS: We use the abstract itself as the summary for embedding
        summary = abstract 
        vector = embedder.generate_embedding(summary)

        # 3. Load (Relational DB)
        new_paper = Paper(
            arxiv_id=arxiv_id,
            title=paper_dict.get("title"),
            abstract=abstract,
            summary=summary,
            authors=paper_dict.get("authors"),
            category=paper_dict.get("category"),
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
                        "published_at": new_paper.published_at.isoformat(),
                        "abstract": new_paper.abstract,
                        "authors": new_paper.authors,       # <-- Added Author extraction
                        "arxiv_url": new_paper.arxiv_url    # <-- Added URL extraction
                    }
                )
            ]
        )

        db.commit()
        logger.info(f"Successfully ingested {arxiv_id}")
        return {"status": "success", "arxiv_id": arxiv_id, "db_id": new_paper.id}

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to ingest {arxiv_id}: {str(e)}")
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