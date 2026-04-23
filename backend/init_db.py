import os
import logging

# 1. Force the script to use the externally mapped port (5433) BEFORE loading the engine
os.environ["DATABASE_URL"] = "postgresql://papervault:papervault@localhost:5433/papervault"

from app.db.session import engine
from app.db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Connecting to PostgreSQL on localhost:5433 to create tables...")

# 2. Look at your models and create the missing tables in Postgres
Base.metadata.create_all(bind=engine)

logger.info("Tables created successfully! The database is ready.")