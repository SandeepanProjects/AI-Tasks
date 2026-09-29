from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
import uuid

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("created_by", sa.String(256), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("assets", sa.JSON(), nullable=False),
        sa.Column("lookback_days", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("report", sa.JSON(), nullable=True),
        sa.Column("reviewer_id", sa.String(256), nullable=True),
        sa.Column("reviewer_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reviews_tenant_id", "reviews", ["tenant_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])
    op.create_table(
        "evidence_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("source_name", sa.String(256), nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_evidence_chunks_tenant_id", "evidence_chunks", ["tenant_id"])
    op.create_index("ix_evidence_chunks_observed_at", "evidence_chunks", ["observed_at"])
    op.create_index("ix_evidence_tenant_observed", "evidence_chunks", ["tenant_id", "observed_at"])

def downgrade():
    op.drop_table("evidence_chunks")
    op.drop_table("reviews")
