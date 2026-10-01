import asyncio, json
from app.agents.specialists import RiskAgent, FeesAgent
from app.domain.schemas import AgentInput


async def main():
    cases = [
        ("risk-free investment", ["risk"]),
        ("no fees or commission", ["fees"]),
        ("read the prospectus", []),
    ]
    results = []
    for i, (text, expected) in enumerate(cases):
        p = AgentInput(
            review_id=str(i),
            tenant_id="eval",
            statement=text,
            policies=[],
            task_id="eval",
        )
        got = []
        for name, agent in [("risk", RiskAgent()), ("fees", FeesAgent())]:
            if (await agent.run(p)).findings:
                got.append(name)
        results.append(
            {
                "input": text,
                "expected": expected,
                "detected": got,
                "match": sorted(expected) == sorted(got),
            }
        )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
