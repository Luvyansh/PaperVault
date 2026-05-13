import os
import logging
from sqlalchemy import text

os.environ["DATABASE_URL"] = "postgresql://papervault:papervault@localhost:5433/papervault"
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Dropping partial app tables to reset Alembic...")

try:
    with engine.connect() as conn:
        # Dropping both singular and plural just to be absolutely safe
        conn.execute(text("DROP TABLE IF EXISTS topics CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS entities CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS entity CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS papers CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS paper CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        conn.commit()
    logger.info("✅ All tables cleared. The database is ready for Alembic.")
except Exception as e:
    logger.error(f"❌ Error during cleanup: {e}")