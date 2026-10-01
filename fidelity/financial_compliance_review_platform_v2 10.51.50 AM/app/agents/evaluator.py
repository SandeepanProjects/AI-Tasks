REQUIRED = {"performance", "risk", "fees", "policy_research"}


def evaluate(outputs):
    present = {o["agent_name"] for o in outputs.values()}
    missing = sorted(REQUIRED - present)
    return {"passed": not missing, "missing": missing}
