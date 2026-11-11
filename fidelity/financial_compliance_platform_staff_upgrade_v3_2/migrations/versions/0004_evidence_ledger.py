"""Add tenant-scoped evidence provenance ledger."""
from alembic import op
import sqlalchemy as sa

revision = "0004_evidence_ledger"
down_revision = "0003_outbox_idempotency"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "evidence_ledger",
        sa.Column("evidence_id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("review_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(128), nullable=False),
        sa.Column("document_version", sa.String(64), nullable=False),
        sa.Column("chunk_id", sa.String(128), nullable=False),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(512), nullable=True),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("quote_sha256", sa.String(64), nullable=False),
        sa.Column("retrieval_method", sa.String(64), nullable=False),
        sa.Column("retrieval_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "evidence_id", name="uq_evidence_tenant_id"),
    )
    op.create_index("ix_evidence_ledger_tenant_id", "evidence_ledger", ["tenant_id"])
    op.create_index("ix_evidence_ledger_review_id", "evidence_ledger", ["review_id"])
    op.create_index("ix_evidence_ledger_document_id", "evidence_ledger", ["document_id"])
    op.execute("ALTER TABLE evidence_ledger ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE evidence_ledger FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY evidence_tenant_isolation ON evidence_ledger USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")

def downgrade():
    op.drop_table("evidence_ledger")
