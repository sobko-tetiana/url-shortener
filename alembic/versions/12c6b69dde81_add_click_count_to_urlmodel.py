"""Add click_count to UrlModel

Revision ID: 12c6b69dde81
Revises: 3563889f1529
Create Date: 2026-09-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12c6b69dde81'
down_revision: Union[str, Sequence[str], None] = '3563889f1529'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'urls',
        sa.Column(
            'click_count',
            sa.Integer(),
            nullable=False,
            server_default='0',
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('urls', 'click_count')
