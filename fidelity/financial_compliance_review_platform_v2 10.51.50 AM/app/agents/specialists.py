from app.domain.schemas import AgentOutput, Finding, Evidence, Severity


class Specialist:
    name = "base"

    async def run(self, payload):
        return AgentOutput(agent_name=self.name)


def ev(p):
    return Evidence(
        policy_id=p["id"],
        policy_code=p["code"],
        policy_version=p["version"],
        quote=p["text"][:300],
    )


class PerformanceAgent(Specialist):
    name = "performance"

    async def run(self, payload):
        fs = []
        if any(
            x in payload.statement.lower()
            for x in ("guaranteed return", "assured profit", "risk-free return")
        ):
            for p in payload.policies[:2]:
                if any(
                    k in p["text"].lower()
                    for k in ("return", "performance", "guarantee")
                ):
                    fs.append(
                        Finding(
                            category="performance",
                            severity=Severity.HIGH,
                            statement="Potential guaranteed-performance claim",
                            rationale="Absolute performance language requires substantiation and review.",
                            evidence=[ev(p)],
                        )
                    )
        return AgentOutput(agent_name=self.name, findings=fs)


class RiskAgent(Specialist):
    name = "risk"

    async def run(self, payload):
        fs = []
        if any(
            x in payload.statement.lower()
            for x in ("no risk", "risk-free", "cannot lose", "guaranteed")
        ):
            fs = [
                Finding(
                    category="risk",
                    severity=Severity.HIGH,
                    statement="Potentially inadequate risk disclosure",
                    rationale="Absolute language may obscure investment risk.",
                    evidence=[ev(p) for p in payload.policies[:2]],
                )
            ]
        return AgentOutput(agent_name=self.name, findings=fs)


class FeesAgent(Specialist):
    name = "fees"

    async def run(self, payload):
        fs = []
        if any(
            x in payload.statement.lower()
            for x in ("no fees", "zero fee", "free of charge", "no commission")
        ):
            matches = [
                p
                for p in payload.policies
                if any(
                    k in (p["text"] + " " + p["title"]).lower()
                    for k in ("fee", "commission", "charge", "expense")
                )
            ]
            fs = [
                Finding(
                    category="fees",
                    severity=Severity.MEDIUM,
                    statement="Fee claim needs validation",
                    rationale="Verify scope, exclusions, conditions, and policy version.",
                    evidence=[ev(p) for p in matches[:3]],
                )
            ]
        return AgentOutput(agent_name=self.name, findings=fs)


class PolicyResearchAgent(Specialist):
    name = "policy_research"

    async def run(self, payload):
        return AgentOutput(
            agent_name=self.name,
            notes=[f"Reviewed {len(payload.policies)} retrieved policies"],
        )
