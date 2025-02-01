"""Initial migration

Revision ID: 52ede70d4645
Revises: 
Create Date: 2025-02-01 12:40:51.971568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52ede70d4645'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Додаємо стовпець owner_id як nullable
    op.add_column('contacts', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('contacts', sa.Column('owner_id', sa.Integer(), nullable=True))  # спочатку nullable
    # Оновлюємо записи, встановлюючи значення для owner_id (наприклад, 1 або інше значення)
    op.execute('UPDATE contacts SET owner_id = 1 WHERE owner_id IS NULL')
    # Тепер додаємо зовнішній ключ
    op.create_foreign_key(None, 'contacts', 'users', ['owner_id'], ['id'])
    # Тепер робимо owner_id NOT NULL
    op.alter_column('contacts', 'owner_id', nullable=False)

def downgrade() -> None:
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'owner_id')
    op.drop_column('contacts', 'created_at')


