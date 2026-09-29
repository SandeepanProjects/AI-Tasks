REQUIRED = {"performance", "risk", "fees", "policy_research"}


def evaluate(outputs: dict, findings: list[dict], policies: list[dict]) -> dict:
    present = {o["agent_name"] for o in outputs.values()}
    missing = sorted(REQUIRED - present)
    evidence_ids = {p["id"] for p in policies}
    invalid = []
    for f in findings:
        for e in f.get("evidence", []):
            if e.get("policy_id") not in evidence_ids:
                invalid.append(e.get("policy_id"))
    return {
        "passed": not missing and not invalid,
        "missing_agents": missing,
        "invalid_evidence_policy_ids": invalid,
        "finding_count": len(findings),
        "policy_count": len(policies),
    }
