"""add password_hash to users

Revision ID: 738d1f8b2c4c
Revises: 217adf331603
Create Date: 2026-08-22 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "738d1f8b2c4c"
down_revision: Union[str, Sequence[str], None] = "217adf331603"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
