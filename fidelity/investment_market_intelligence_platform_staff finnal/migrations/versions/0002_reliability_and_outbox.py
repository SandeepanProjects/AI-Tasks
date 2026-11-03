"""Add request-hash idempotency and transactional outbox.

Revision ID: 0002_reliability_and_outbox
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_reliability_and_outbox"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("idempotency_keys", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("idempotency_keys", sa.Column("request_hash", sa.String(64), nullable=True))
    op.execute("UPDATE idempotency_keys SET id = gen_random_uuid(), request_hash = repeat('0', 64)")
    op.alter_column("idempotency_keys", "id", nullable=False)
    op.alter_column("idempotency_keys", "request_hash", nullable=False)
    op.drop_constraint("idempotency_keys_pkey", "idempotency_keys", type_="primary")
    op.create_primary_key("pk_idempotency_keys", "idempotency_keys", ["id"])
    op.create_unique_constraint("uq_idempotency_tenant_key", "idempotency_keys", ["tenant_id", "key"])

    op.add_column("reviews", sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workflow_checkpoints", sa.Column("tenant_id", sa.String(128), nullable=True))
    op.execute("UPDATE workflow_checkpoints SET tenant_id = COALESCE((SELECT tenant_id FROM reviews WHERE reviews.id = workflow_checkpoints.review_id), 'legacy')")
    op.alter_column("workflow_checkpoints", "tenant_id", nullable=False)
    op.create_index("ix_workflow_checkpoints_tenant_id", "workflow_checkpoints", ["tenant_id"])

    # Older demo seeds could insert duplicate chunks; keep one copy per tenant/hash before
    # enforcing the production deduplication invariant.
    op.execute("DELETE FROM evidence_chunks a USING evidence_chunks b WHERE a.tenant_id = b.tenant_id AND a.content_hash = b.content_hash AND a.id > b.id")
    op.create_unique_constraint("uq_evidence_tenant_content_hash", "evidence_chunks", ["tenant_id", "content_hash"])
    op.create_index("ix_evidence_embedding_hnsw", "evidence_chunks", ["embedding"],
                    postgresql_using="hnsw", postgresql_ops={"embedding": "vector_cosine_ops"})
    op.create_index("ix_evidence_content_fts", "evidence_chunks",
                    [sa.text("to_tsvector('english'::regconfig, content)")], postgresql_using="gin")

    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_outbox_events_tenant_id", "outbox_events", ["tenant_id"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_published_at", "outbox_events", ["published_at"])
    op.create_index("ix_outbox_pending_created", "outbox_events", ["completed_at", "published_at", "created_at"])

    # Tenant isolation for application-owned metadata tables.
    op.execute("ALTER TABLE idempotency_keys ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE idempotency_keys FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY idempotency_tenant_isolation ON idempotency_keys USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")
    op.execute("ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_events FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY audit_tenant_isolation ON audit_events USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")
    op.execute("ALTER TABLE workflow_checkpoints ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE workflow_checkpoints FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY checkpoint_tenant_isolation ON workflow_checkpoints USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")


def downgrade():
    op.execute("DROP POLICY IF EXISTS checkpoint_tenant_isolation ON workflow_checkpoints")
    op.execute("DROP POLICY IF EXISTS audit_tenant_isolation ON audit_events")
    op.execute("DROP POLICY IF EXISTS idempotency_tenant_isolation ON idempotency_keys")
    op.execute("ALTER TABLE workflow_checkpoints DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE idempotency_keys DISABLE ROW LEVEL SECURITY")
    op.drop_table("outbox_events")
    op.drop_column("reviews", "processing_started_at")
    op.drop_index("ix_workflow_checkpoints_tenant_id", table_name="workflow_checkpoints")
    op.drop_column("workflow_checkpoints", "tenant_id")
    op.drop_index("ix_evidence_content_fts", table_name="evidence_chunks")
    op.drop_index("ix_evidence_embedding_hnsw", table_name="evidence_chunks")
    op.drop_constraint("uq_evidence_tenant_content_hash", "evidence_chunks", type_="unique")
    op.drop_constraint("uq_idempotency_tenant_key", "idempotency_keys", type_="unique")
    op.drop_constraint("pk_idempotency_keys", "idempotency_keys", type_="primary")
    op.create_primary_key("idempotency_keys_pkey", "idempotency_keys", ["key"])
    op.drop_column("idempotency_keys", "request_hash")
    op.drop_column("idempotency_keys", "id")
