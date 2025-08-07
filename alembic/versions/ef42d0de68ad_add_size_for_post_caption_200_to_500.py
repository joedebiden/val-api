"""add size for post caption 200 to 500

Revision ID: ef42d0de68ad
Revises: 440ab7426422
Create Date: 2025-08-07 12:51:53.856876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef42d0de68ad'
down_revision: Union[str, Sequence[str], None] = '440ab7426422'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
