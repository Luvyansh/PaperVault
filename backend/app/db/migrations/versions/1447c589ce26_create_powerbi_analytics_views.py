"""create_powerbi_analytics_views

Revision ID: 1447c589ce26
Revises: d4177f8edc8f
Create Date: 2026-04-22 14:56:32.397666

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1447c589ce26'
down_revision: Union[str, None] = 'd4177f8edc8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Paper Intelligence View
    op.execute("""
        CREATE OR REPLACE VIEW vw_paper_intelligence AS
        SELECT 
            id AS paper_id,
            arxiv_id,
            category,
            DATE(published_at) AS publish_date,
            TO_CHAR(published_at, 'YYYY-MM') AS publish_month,
            authors,
            is_processed
        FROM papers
        WHERE is_processed = true;
    """)

    # 2. Entity Trend Analysis View
    op.execute("""
        CREATE OR REPLACE VIEW vw_entity_trends AS
        SELECT 
            e.id AS entity_id,
            p.arxiv_id,
            p.category,
            e.entity_type,
            LOWER(e.value) AS entity_value,
            DATE(p.published_at) AS publish_date
        FROM entities e
        JOIN papers p ON e.paper_id = p.id;
    """)

def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS vw_entity_trends;")
    op.execute("DROP VIEW IF EXISTS vw_paper_intelligence;")