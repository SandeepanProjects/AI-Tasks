from app.domain.schemas import Finding


def validate(findings: list[dict], policies: list[dict], tenant_id: str) -> None:
    by_id = {p["id"]: p for p in policies if p.get("tenant_id") == tenant_id}
    for raw in findings:
        finding = Finding.model_validate(raw)
        for evidence in finding.evidence:
            policy = by_id.get(evidence.policy_id)
            if not policy:
                raise ValueError(
                    "Evidence references policy outside retrieved tenant scope"
                )
            if (
                evidence.policy_version != policy["version"]
                or evidence.policy_code != policy["code"]
            ):
                raise ValueError("Evidence policy identity/version mismatch")
            if evidence.quote not in policy["text"]:
                raise ValueError(
                    "Evidence quote is not an exact substring of source policy"
                )
