"""Init DB

Revision ID: 2adaa6a9c4fb
Revises:
Create Date: 2022-11-12 20:18:29.005771+07:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2adaa6a9c4fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "configs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("path", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text('NOW()'))
    )
    pass

    op.create_table(
        "users",
        sa.Column('uuid', sa.String(50), primary_key=True),
        sa.Column("telegram_userid", sa.BigInteger(), unique=True, index=True),
        sa.Column("telegram_username", sa.String(), unique=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text('false')),
        sa.Column("created_at", sa.DateTime, server_default=sa.text('NOW()'))
    )

    op.create_table(
        "bot_chatcontexts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("serialized_handler", sa.JSON, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text('true')),
        sa.Column("created_at", sa.DateTime, server_default=sa.text('NOW()'), index=True),
    )

    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), unique=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text('true')),
        sa.Column("created_at", sa.DateTime, server_default=sa.text('NOW()'), index=True),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text('NOW()'))
    )

    op.create_table(
        "expense_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(2), nullable=False),
        sa.Column("transaction_type", sa.String()),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text('NOW()'), index=True),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text('NOW()'))
    )
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX trgm_idx_expense_items_subject ON expense_items USING gin (subject gin_trgm_ops);")


def downgrade() -> None:
    op.drop_table("configs")
    op.drop_table("users")
    op.drop_table("bot_chatcontexts")
    op.drop_table("expense_categories")
    op.drop_index("trgm_idx_expense_items_subject")
    op.drop_table("expense_items")
    pass
