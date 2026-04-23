from celery import Celery
from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "papervault",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.etl.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.etl.tasks.ingest_paper": {"queue": "ingestion"},
        "app.etl.tasks.refresh_topics": {"queue": "analytics"},
    }
)