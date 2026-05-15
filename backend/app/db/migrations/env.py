from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- DYNAMIC URL FETCH ---
# Grab the URL from Docker environment, fallback to host port for local testing
FORCE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://papervault:papervault@127.0.0.1:5433/papervault"
)

def include_object(object, name, type_, reflected, compare_to):
    # Ignore Airflow's tables - only process tables defined in our models.py
    if type_ == "table" and name not in target_metadata.tables:
        return False
    return True

def run_migrations_offline() -> None:
    context.configure(
        url=FORCE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="backend_alembic_version", # Isolated tracking table
        include_object=include_object            # Protects Airflow's tables
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    print(f"\n--- DEBUG: FORCING CONNECTION TO: {FORCE_URL} ---\n")
    
    connectable = create_engine(
        FORCE_URL, 
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table="backend_alembic_version", # Isolated tracking table
            include_object=include_object            # Protects Airflow's tables
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()