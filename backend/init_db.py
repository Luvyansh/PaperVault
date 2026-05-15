import os
import logging
import time
from sqlalchemy.sql import text

# Check if we are inside Docker, fallback to localhost for manual host execution
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://papervault:papervault@localhost:5433/papervault"

from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_connection(max_retries=5, delay=2):
    """Pings the database to ensure it is ready to accept connections."""
    logger.info("Initializing database connection check...")
    
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful! Ready for Alembic.")
            return
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed: Database not ready yet. Retrying in {delay} seconds...")
            time.sleep(delay)
            
    logger.error("❌ Could not connect to the database after multiple attempts.")
    raise Exception("Database connection timeout.")

if __name__ == "__main__":
    check_db_connection()