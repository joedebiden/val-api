"""add updated_at column to Message table

Revision ID: 1ba93ff69fd5
Revises: aa7e6970d17e
Create Date: 2025-08-21 23:16:43.460122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ba93ff69fd5'
down_revision: Union[str, Sequence[str], None] = 'aa7e6970d17e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'message',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.func.now(),
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('message', 'updated_at')
