"""id column UUID to Int

Revision ID: 440ab7426422
Revises: cb5a90b539c4
Create Date: 2025-08-07 12:02:08.982179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '440ab7426422'
down_revision: Union[str, Sequence[str], None] = 'cb5a90b539c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
