"""add unique constraint to phone_number

Revision ID: 6e7ad61d7e05
Revises: fd6c64576b2c
Create Date: 2025-08-22 18:43:58.428809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e7ad61d7e05'
down_revision: Union[str, Sequence[str], None] = 'fd6c64576b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_members_phone_number'), ['phone_number'], unique=True)

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_members_phone_number'))