def extract_claim_evidence(claim,records):
    """Bound excerpts while preserving source row IDs for citation validation."""
    terms={w.lower().strip(".,:;!?") for w in claim.split() if len(w)>3}
    out=[]
    for r in records:
        out.append({"policy_id":r["policy_id"],"policy_code":r["policy_code"],"title":r["title"],"excerpt":r["text"][:1200],"term_overlap":len(terms & set(r["text"].lower().split()))})
    return sorted(out,key=lambda x:x["term_overlap"],reverse=True)
