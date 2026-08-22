"""add unique user email constraint

Revision ID: b7c2d91e4f60
Revises: 9f4a7c1d2e8b
Create Date: 2026-08-22 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c2d91e4f60"
down_revision: Union[str, Sequence[str], None] = "9f4a7c1d2e8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            WITH duplicate_users AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY email
                        ORDER BY created_at, id
                    ) AS duplicate_rank
                FROM users
                WHERE email IS NOT NULL
            )
            UPDATE users
            SET email = LEFT(users.email, 200)
                || '+duplicate-'
                || users.id::text
            FROM duplicate_users
            WHERE users.id = duplicate_users.id
              AND duplicate_users.duplicate_rank > 1
            """
        )
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_users_email", "users", type_="unique")