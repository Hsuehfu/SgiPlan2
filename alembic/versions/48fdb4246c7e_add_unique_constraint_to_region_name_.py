"""add unique constraint to region name per parent

Revision ID: 48fdb4246c7e
Revises: 6e7ad61d7e05
Create Date: 2025-08-22 19:58:01.996895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48fdb4246c7e'
down_revision: Union[str, Sequence[str], None] = '6e7ad61d7e05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('regions', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('_parent_name_uc'), ['parent_id', 'name'])

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('regions', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('_parent_name_uc'), type_='unique')