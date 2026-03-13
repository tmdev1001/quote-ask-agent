"""Initial models: Customer, Conversation, ConversationMessage, ConversationState, Document, Quote, AuditLog.

Revision ID: 20250312000000
Revises:
Create Date: 2025-03-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20250312000000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("cpf", sa.String(length=32), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("telegram_user_id", sa.String(length=64), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_cpf"), "customers", ["cpf"], unique=False)
    op.create_index(op.f("ix_customers_telegram_user_id"), "customers", ["telegram_user_id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("channel_user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("flow_name", sa.String(length=64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_channel"), "conversations", ["channel"], unique=False)
    op.create_index(op.f("ix_conversations_channel_user_id"), "conversations", ["channel_user_id"], unique=False)
    op.create_index(op.f("ix_conversations_customer_id"), "conversations", ["customer_id"], unique=False)

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("message_type", sa.String(length=32), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_messages_conversation_id"), "conversation_messages", ["conversation_id"], unique=False)

    op.create_table(
        "conversation_states",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("current_step", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("collected_fields_json", sa.JSON(), nullable=True),
        sa.Column("missing_fields_json", sa.JSON(), nullable=True),
        sa.Column("last_tool_action", sa.String(length=128), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversation_id", name=op.f("uq_conversation_states_conversation_id")),
    )
    op.create_index(op.f("ix_conversation_states_conversation_id"), "conversation_states", ["conversation_id"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=64), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("extracted_fields_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_conversation_id"), "documents", ["conversation_id"], unique=False)

    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("quote_code", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("monthly_price", sa.Float(), nullable=False),
        sa.Column("annual_price", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("checkout_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quotes_conversation_id"), "quotes", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_quotes_customer_id"), "quotes", ["customer_id"], unique=False)
    op.create_index(op.f("ix_quotes_quote_code"), "quotes", ["quote_code"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_data_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_conversation_id"), "audit_logs", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_conversation_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_quotes_quote_code"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_customer_id"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_conversation_id"), table_name="quotes")
    op.drop_table("quotes")
    op.drop_index(op.f("ix_documents_conversation_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_conversation_states_conversation_id"), table_name="conversation_states")
    op.drop_table("conversation_states")
    op.drop_index(op.f("ix_conversation_messages_conversation_id"), table_name="conversation_messages")
    op.drop_table("conversation_messages")
    op.drop_index(op.f("ix_conversations_customer_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_channel_user_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_channel"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_index(op.f("ix_customers_telegram_user_id"), table_name="customers")
    op.drop_index(op.f("ix_customers_cpf"), table_name="customers")
    op.drop_table("customers")
