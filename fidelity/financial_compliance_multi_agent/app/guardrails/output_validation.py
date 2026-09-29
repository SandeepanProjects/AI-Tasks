from app.schemas.agent import ReviewResult

def validate_result(payload,allowed_policy_ids):
    normalized={"summary":payload.get("summary","Review completed."),"claims":payload.get("claims",[]),"findings":payload.get("findings",[]),"overall_risk":payload.get("overall_risk","medium"),"recommended_action":payload.get("recommended_action","human_review"),"metadata":payload.get("metadata",{})}
    for f in normalized["findings"]:
        if any(int(pid) not in allowed_policy_ids for pid in f.get("policy_ids",[])):
            raise ValueError("Finding cites unknown policy chunk ID")
    result=ReviewResult(**normalized).model_dump(); result["citations_validated"]=True
    return result
