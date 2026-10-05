from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table("reviews",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("tenant_id",sa.String(128),nullable=False),sa.Column("created_by",sa.String(256),nullable=False),
      sa.Column("question",sa.Text(),nullable=False),sa.Column("assets",sa.JSON(),nullable=False),
      sa.Column("lookback_days",sa.Integer(),nullable=False),sa.Column("purpose",sa.String(40),nullable=False),
      sa.Column("status",sa.String(40),nullable=False),sa.Column("report",sa.JSON(),nullable=True),
      sa.Column("reviewer_id",sa.String(256)),sa.Column("reviewer_comment",sa.Text()),
      sa.Column("version",sa.Integer(),nullable=False,server_default="1"),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_reviews_tenant_id","reviews",["tenant_id"]); op.create_index("ix_reviews_status","reviews",["status"])
    op.create_table("idempotency_keys",sa.Column("key",sa.String(256),primary_key=True),
      sa.Column("tenant_id",sa.String(128),nullable=False),sa.Column("review_id",postgresql.UUID(as_uuid=True),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_idempotency_keys_tenant_id","idempotency_keys",["tenant_id"])
    op.create_table("evidence_chunks",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("tenant_id",sa.String(128),nullable=False),sa.Column("source_name",sa.String(256),nullable=False),
      sa.Column("source_uri",sa.Text(),nullable=False),sa.Column("observed_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("content",sa.Text(),nullable=False),sa.Column("content_hash",sa.String(64),nullable=False),
      sa.Column("embedding",Vector(384)),sa.Column("metadata",sa.JSON(),nullable=False))
    op.create_index("ix_evidence_chunks_tenant_id","evidence_chunks",["tenant_id"])
    op.create_index("ix_evidence_tenant_observed","evidence_chunks",["tenant_id","observed_at"])
    op.create_table("audit_events",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("tenant_id",sa.String(128),nullable=False),sa.Column("actor_id",sa.String(256),nullable=False),
      sa.Column("action",sa.String(128),nullable=False),sa.Column("resource_id",sa.String(128),nullable=False),
      sa.Column("details",sa.JSON(),nullable=False),sa.Column("occurred_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_audit_tenant","audit_events",["tenant_id"])
    op.create_table("workflow_checkpoints",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("review_id",postgresql.UUID(as_uuid=True),nullable=False),sa.Column("node",sa.String(128),nullable=False),
      sa.Column("state",sa.JSON(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_checkpoint_review","workflow_checkpoints",["review_id"])
    op.execute("""ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
                 ALTER TABLE reviews FORCE ROW LEVEL SECURITY;
                 CREATE POLICY reviews_tenant_isolation ON reviews USING (tenant_id = current_setting('app.tenant_id', true))
                 WITH CHECK (tenant_id = current_setting('app.tenant_id', true));""")
    op.execute("""ALTER TABLE evidence_chunks ENABLE ROW LEVEL SECURITY;
                 ALTER TABLE evidence_chunks FORCE ROW LEVEL SECURITY;
                 CREATE POLICY evidence_tenant_isolation ON evidence_chunks USING (tenant_id = current_setting('app.tenant_id', true))
                 WITH CHECK (tenant_id = current_setting('app.tenant_id', true));""")
def downgrade():
    op.execute("DROP POLICY IF EXISTS reviews_tenant_isolation ON reviews")
    op.execute("DROP POLICY IF EXISTS evidence_tenant_isolation ON evidence_chunks")
    for t in ["workflow_checkpoints","audit_events","evidence_chunks","idempotency_keys","reviews"]: op.drop_table(t)
