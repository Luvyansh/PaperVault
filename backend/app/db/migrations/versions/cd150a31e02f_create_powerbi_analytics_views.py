"""create_powerbi_analytics_views

Revision ID: cd150a31e02f
Revises: 1447c589ce26
Create Date: 2026-04-22 22:19:36.137162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd150a31e02f'
down_revision: Union[str, None] = '1447c589ce26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
