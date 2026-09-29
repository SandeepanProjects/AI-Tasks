-- Apply using a migration/DB owner role. App role must not own tables or BYPASSRLS.
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews FORCE ROW LEVEL SECURITY;
CREATE POLICY reviews_tenant_isolation ON reviews
  USING (tenant_id = current_setting('app.tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE evidence_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_chunks FORCE ROW LEVEL SECURITY;
CREATE POLICY evidence_tenant_isolation ON evidence_chunks
  USING (tenant_id = current_setting('app.tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

-- In each transaction, set tenant context with:
-- SELECT set_config('app.tenant_id', :tenant_id, true);
-- Ensure transaction-local setting is applied before every tenant-scoped query.
