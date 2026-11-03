from alembic import op

revision = "0002_tenant_rls"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE INDEX IF NOT EXISTS ix_policies_embedding_hnsw ON policies USING hnsw (embedding vector_cosine_ops)")
    op.execute("ALTER TABLE policies ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE policies FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY policies_tenant_policy ON policies USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")
    op.execute("ALTER TABLE reviews ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE reviews FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY reviews_tenant_policy ON reviews USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")
    op.execute("ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_events FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY audit_tenant_policy ON audit_events USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")

def downgrade():
    op.execute("DROP POLICY IF EXISTS audit_tenant_policy ON audit_events")
    op.execute("DROP POLICY IF EXISTS reviews_tenant_policy ON reviews")
    op.execute("DROP POLICY IF EXISTS policies_tenant_policy ON policies")
    op.execute("ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE reviews DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE policies DISABLE ROW LEVEL SECURITY")
    op.execute("DROP INDEX IF EXISTS ix_policies_embedding_hnsw")
