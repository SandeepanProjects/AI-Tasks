from app.domain.schemas import Finding


class GuardrailViolation(ValueError):
    pass


def validate(findings, policies, tenant_id):
    allowed = {p["id"]: p for p in policies if p["tenant_id"] == tenant_id}
    for raw in findings:
        f = Finding.model_validate(raw)
        for e in f.evidence:
            p = allowed.get(e.policy_id)
            if not p:
                raise GuardrailViolation(
                    "Evidence references an unretrieved or cross-tenant policy"
                )
            if (e.policy_code, e.policy_version) != (p["code"], p["version"]):
                raise GuardrailViolation("Policy version mismatch")
            if e.quote not in p["text"]:
                raise GuardrailViolation("Evidence quote is not verbatim policy text")
