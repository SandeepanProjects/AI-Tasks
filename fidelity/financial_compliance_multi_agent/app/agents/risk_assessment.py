class RiskAssessmentAgent:
    def run(self,analysis):
        rank={"low":0,"medium":1,"high":2,"critical":3}
        for f in analysis.get("findings",[]):
            s=f.get("status","needs_review")
            f["risk"]="high" if s=="potential_violation" else "low" if s=="compliant" else "medium"
        overall=max((f.get("risk","medium") for f in analysis.get("findings",[])),key=lambda x:rank.get(x,1),default="medium")
        return {**analysis,"overall_risk":overall,"recommended_action":"block_and_escalate" if overall in ("high","critical") else "human_review"}
