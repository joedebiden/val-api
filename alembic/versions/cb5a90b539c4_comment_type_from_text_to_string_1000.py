"""comment type from Text to String(1000)

Revision ID: cb5a90b539c4
Revises: afcba9a20121
Create Date: 2025-08-06 18:11:52.714830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb5a90b539c4'
down_revision: Union[str, Sequence[str], None] = 'afcba9a20121'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
