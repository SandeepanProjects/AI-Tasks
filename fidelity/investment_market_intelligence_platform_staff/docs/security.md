# Security model

- Tenant comes only from authenticated principal claims.
- Every repository lookup includes tenant scope.
- PostgreSQL RLS is enabled by migration; application DB role must not own/bypass tables.
- Reviewer approval requires reviewer/admin role and explicit lifecycle state.
- LLM input treats retrieved text as untrusted data.
- Tools are typed and allow-listed; no arbitrary SQL, shell, URL fetch, trade execution, or wallet signing.
- Report citations are checked against the actual retrieved evidence set.
- Audit events capture actor, action, resource and decision metadata.
- Secrets must come from environment/secret manager; never commit `.env`.
- Production identity should be OIDC/JWKS with key rotation rather than local HS256.
