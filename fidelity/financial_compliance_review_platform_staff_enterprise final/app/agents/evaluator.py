REQUIRED = {"performance", "risk", "fees", "policy_research"}

def evaluate(outputs: dict, findings: list[dict], policies: list[dict]) -> dict:
    present = {output["agent_name"] for output in outputs.values()}
    missing = sorted(REQUIRED - present)
    evidence_ids = {policy["id"] for policy in policies}
    invalid, missing_evidence = [], []
    for finding in findings:
        evidence = finding.get("evidence", [])
        if not evidence: missing_evidence.append(finding.get("statement", "<unknown>"))
        for item in evidence:
            if item.get("policy_id") not in evidence_ids: invalid.append(item.get("policy_id"))
    return {"passed": not missing and not invalid and not missing_evidence and bool(policies),
        "missing_agents": missing, "invalid_evidence_policy_ids": invalid,
        "findings_without_evidence": missing_evidence, "has_policy_context": bool(policies),
        "finding_count": len(findings), "policy_count": len(policies)}
