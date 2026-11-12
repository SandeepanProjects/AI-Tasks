from alembic import op
import sqlalchemy as sa
revision = "0003_outbox_idempotency"
down_revision = "0002_tenant_rls"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("reviews", sa.Column("worker_lease_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("reviews", sa.Column("worker_task_id", sa.String(128), nullable=True))
    op.add_column("policies", sa.Column("document_hash", sa.String(64), nullable=True))
    op.create_index("ix_policies_document_hash", "policies", ["document_hash"])
    op.add_column("policies", sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("policies", sa.Column("source_uri", sa.String(2048), nullable=True))
    op.create_table("outbox_events", sa.Column("id", sa.String(64), primary_key=True), sa.Column("tenant_id", sa.String(128), nullable=False, index=True), sa.Column("aggregate_id", sa.String(64), nullable=False, index=True), sa.Column("event_type", sa.String(128), nullable=False, index=True), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_outbox_events_published_at", "outbox_events", ["published_at"])
    op.create_table("idempotency_records", sa.Column("id", sa.String(64), primary_key=True), sa.Column("tenant_id", sa.String(128), nullable=False, index=True), sa.Column("idempotency_key", sa.String(256), nullable=False), sa.Column("request_hash", sa.String(64), nullable=False), sa.Column("resource_id", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_idempotency_tenant_key"))
    op.execute("ALTER TABLE idempotency_records ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE idempotency_records FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY idempotency_tenant_policy ON idempotency_records USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")

def downgrade():
    op.drop_column("policies", "source_uri")
    op.drop_column("policies", "chunk_index")
    op.drop_index("ix_policies_document_hash", table_name="policies")
    op.drop_column("policies", "document_hash")
    op.drop_column("reviews", "worker_task_id")
    op.drop_column("reviews", "worker_lease_until")
    op.execute("DROP POLICY IF EXISTS idempotency_tenant_policy ON idempotency_records")
    op.drop_table("idempotency_records")
    op.drop_index("ix_outbox_events_published_at", table_name="outbox_events")
    op.drop_table("outbox_events")
