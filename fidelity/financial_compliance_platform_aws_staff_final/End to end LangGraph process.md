Let's understand the end-to-end LangGraph workflow in your Financial Compliance Review Platform, starting from the moment a user submits a query or uploads a financial document until the final compliance decision.

I'll explain it from a Senior AI Engineer interview perspective.

# 1. Overall LangGraph architecture

LangGraph is the orchestration engine. It controls which component executes, what data is passed between components, and what happens next based on the results.

\#chatgpt-mermaid-\_r_jl\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_jl\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_jl\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_jl\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_jl\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_jl\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_jl\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_jl\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_jl\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_jl\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_jl\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_jl\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_jl\_ p{margin:0;}#chatgpt-mermaid-\_r_jl\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_jl\_ .label text,#chatgpt-mermaid-\_r_jl\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .node rect,#chatgpt-mermaid-\_r_jl\_ .node circle,#chatgpt-mermaid-\_r_jl\_ .node ellipse,#chatgpt-mermaid-\_r_jl\_ .node polygon,#chatgpt-mermaid-\_r_jl\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .rough-node .label text,#chatgpt-mermaid-\_r_jl\_ .node .label text,#chatgpt-mermaid-\_r_jl\_ .image-shape .label,#chatgpt-mermaid-\_r_jl\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_jl\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .rough-node .label,#chatgpt-mermaid-\_r_jl\_ .node .label,#chatgpt-mermaid-\_r_jl\_ .image-shape .label,#chatgpt-mermaid-\_r_jl\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_jl\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_jl\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_jl\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_jl\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_jl\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_jl\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_jl\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_jl\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_jl\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_jl\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_jl\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_jl\_ .icon-shape,#chatgpt-mermaid-\_r_jl\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_jl\_ .icon-shape p,#chatgpt-mermaid-\_r_jl\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_jl\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_jl\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_jl\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_jl\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_jl\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_jl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_jl\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_jl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_jl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_jl\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_jl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_jl\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_jl\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_jl\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_jl\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_jl\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .node rect,#chatgpt-mermaid-\_r_jl\_ .node circle,#chatgpt-mermaid-\_r_jl\_ .node ellipse,#chatgpt-mermaid-\_r_jl\_ .node polygon,#chatgpt-mermaid-\_r_jl\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_jl\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_jl\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_jl\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_jl\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_jl\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}User submits query / PDFFastAPIAuthentication & ValidationCreate Review RequestLangGraph EntryDocument ProcessingClaim ExtractionPolicy Retrieval Agent - RAGCompliance Analysis AgentRisk AssessmentGuardrails / ValidationValidation Passed?Retry / Error HandlingEvaluatorFindings Complete?Human ReviewDecisionSave Approved ResultSave Rejection / CommentsPostgreSQL + Audit LogReturn Result to UserNoYesNoYesApproveReject

This is the enhanced target workflow. Your reviewed implementation has a simpler linear workflow, so treat the conditional retry, evaluator loop, and durable human pause/resume as improvements unless verified in the code.

# 2. Step-by-step LangGraph execution

## Step 1: User sends a request

For example:

"What are the compliance risks associated with promising guaranteed 15% annual returns?"

FastAPI receives:

```
{
  "query": "Can we advertise guaranteed 15% annual returns?",
  "tenant_id": "BANK01",
  "user_id": "USER101"
}
```

The API validates the request and sends it to the application service.

## Step 2: Initialize LangGraph state

This is very important.

LangGraph maintains a shared state object that moves between nodes.

For example:

```
from typing import TypedDict, Anyclass ComplianceState(TypedDict, total=False):    query: str    document_text: str    claims: list    retrieved_policies: list    findings: list    risk_level: str    validation_passed: bool    evaluation_result: dict    approval_status: str    tenant_id: str    review_id: str
```

Think of this state as a shared context.

Each node reads the information it needs and updates the state.

For example:

- Claim extraction adds claims.
- Retrieval adds policy evidence.
- Compliance analysis adds findings.
- Risk assessment adds risk levels.

## Step 3: Document processing node

The first node handles the uploaded document, if the user submitted one.

Responsibilities:

- Extract PDF text.
- Clean the extracted text.
- Preserve page information.
- Prepare content for claim extraction.

If the user sends only a natural-language query, this node can be bypassed.

## Step 4: Claim extraction node

This node identifies important financial claims.

Example input:

```
Investors are guaranteed 15% annual returns
with minimal investment risk.
```

Example output:

```
{
  "claims": [
    {
      "claim": "Guaranteed 15% annual returns",
      "type": "RETURN_GUARANTEE"
    },
    {
      "claim": "Minimal investment risk",
      "type": "RISK_DISCLOSURE"
    }
  ]
}
```

The extracted claims are added to LangGraph state.

## Step 5: Policy retrieval node (RAG)

Now we need to find relevant compliance policies.

The retrieval node performs:

1. Query preparation.
2. Embedding generation.
3. Vector similarity search.
4. Metadata filtering.
5. Policy chunk retrieval.
6. Keyword fallback when necessary.

Example:

```
Claim:
Guaranteed 15% annual returns

Retrieved policies:
POL101: Investment returns cannot be guaranteed.
POL102: Investment risks must be disclosed.
```

These retrieved policies are added to the shared state.

## Step 6: Compliance analysis node

Now the LLM receives:

- Original query.
- Extracted claims.
- Retrieved policy evidence.
- Compliance analysis instructions.

It compares each claim with the policy evidence.

Example:

```
{
  "claim": "Guaranteed 15% annual returns",
  "policy_reference": "POL101",
  "violation": true,
  "reason": "The claim promises a guaranteed investment return.",
  "evidence": "Investment returns cannot be guaranteed."
}
```

The key point: the LLM is not expected to invent compliance rules. It analyzes claims against retrieved policy evidence.

## Step 7: Risk assessment node

This node determines the severity of the findings.

For example:

```
Guaranteed investment returns
          |
          v
Compliance violation detected
          |
          v
Risk classification
          |
          v
HIGH
```

We can use deterministic rules for risk mapping and an LLM for more nuanced contextual analysis if needed.

## Step 8: Guardrails node

Before accepting the result, we validate:

- Is the JSON valid?
- Are all mandatory fields present?
- Does the policy reference exist?
- Is there supporting evidence?
- Is the tenant authorized to access the policy?
- Is the risk classification valid?

If validation fails, the workflow can retry or move to an error-handling path.

## Step 9: Evaluator node

This component evaluates the quality of the findings.

For example:

- Did we identify all relevant claims?
- Is the retrieved evidence relevant?
- Is the violation supported by the policy?
- Is the explanation complete?

If the findings are incomplete, the workflow can send them back for bounded re-analysis.

Avoid unlimited loops. We should set a maximum retry count.

## Step 10: Human-in-the-loop node

This is particularly important for financial compliance.

LangGraph can pause the workflow using an interrupt and save its state using a persistent checkpointer.

The compliance officer receives the findings.

They can:

- Approve.
- Reject.
- Request changes.

After the decision, the workflow resumes from the saved state.

This is the enhanced durable HITL implementation; an ordinary approval API alone does not automatically provide LangGraph checkpoint-and-resume functionality.

## Step 11: Persistence node

After the final decision, we store:

- Review status.
- Compliance findings.
- Risk classifications.
- Policy references.
- Human approval details.
- Audit information.

These are stored in PostgreSQL.

# 3. How do we actually build the LangGraph?

Here is a simplified implementation to understand the orchestration.

```
from langgraph.graph import StateGraph, START, ENDdef analyze_compliance(state):    findings = compliance_analysis_service(        state["claims"],        state["retrieved_policies"]    )    return {"findings": findings}def assess_risk(state):    risk = risk_assessment_service(        state["findings"]    )    return {"risk_level": risk}def validate_results(state):    passed = validate_compliance_findings(        state["findings"]    )    return {"validation_passed": passed}def save_results(state):    review_repository.save(state)    return {"approval_status": "PENDING_REVIEW"}workflow = StateGraph(ComplianceState)workflow.add_node("extract", extract_claims)workflow.add_node("retrieve", retrieve_policies)workflow.add_node("analyze", analyze_compliance)workflow.add_node("risk", assess_risk)workflow.add_node("validate", validate_results)workflow.add_node("save", save_results)workflow.add_edge(START, "extract")workflow.add_edge("extract", "retrieve")workflow.add_edge("retrieve", "analyze")workflow.add_edge("analyze", "risk")workflow.add_edge("risk", "validate")def validation_router(state):    if state["validation_passed"]:        return "save"    return "analyze"workflow.add_conditional_edges(    "validate",    validation_router,    {        "save": "save",        "analyze": "analyze"    })workflow.add_edge("save", END)graph = workflow.compile()
```

This demonstrates the core orchestration pattern. A production implementation should add a retry counter, error paths, durable checkpointing, authorization checks, and a real human approval interrupt.

# 4. How do all the components communicate?

This is another important interview question.

Compliance OfficerLLMPostgreSQLRAG ServiceLangGraphCeleryFastAPIUserCompliance OfficerLLMPostgreSQLRAG ServiceLangGraphCeleryFastAPIUser#chatgpt-mermaid-\_r_l3\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_l3\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_l3\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_l3\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_l3\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_l3\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_l3\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_l3\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_l3\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_l3\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_l3\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_l3\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_l3\_ p{margin:0;}#chatgpt-mermaid-\_r_l3\_ .actor{stroke:rgb(31, 78, 148);fill:rgb(9, 23, 44);stroke-width:1;}#chatgpt-mermaid-\_r_l3\_ rect.actor.outer-path[data-look="neo"]{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ rect.note[data-look="neo"]{stroke:rgb(58, 132, 63);fill:rgb(48, 48, 48);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ text.actor>tspan{fill:rgb(237, 237, 237);stroke:none;}#chatgpt-mermaid-\_r_l3\_ .actor-line{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ .innerArc{stroke-width:1.5;stroke-dasharray:none;}#chatgpt-mermaid-\_r_l3\_ .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ [id$="-arrowhead"] path{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ .sequenceNumber{fill:#505050;}#chatgpt-mermaid-\_r_l3\_ [id$="-sequencenumber"]{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ [id$="-crosshead"] path{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_l3\_ .messageText{fill:rgb(237, 237, 237);stroke:none;}#chatgpt-mermaid-\_r_l3\_ .labelBox{stroke:rgba(255, 255, 255, 0.15);fill:rgb(0, 0, 0);filter:none;}#chatgpt-mermaid-\_r_l3\_ .labelText,#chatgpt-mermaid-\_r_l3\_ .labelText>tspan{fill:rgb(237, 237, 237);stroke:none;}#chatgpt-mermaid-\_r_l3\_ .loopText,#chatgpt-mermaid-\_r_l3\_ .loopText>tspan{fill:rgb(237, 237, 237);stroke:none;}#chatgpt-mermaid-\_r_l3\_ .sectionTitle,#chatgpt-mermaid-\_r_l3\_ .sectionTitle>tspan{fill:rgb(237, 237, 237);stroke:none;}#chatgpt-mermaid-\_r_l3\_ .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:rgba(255, 255, 255, 0.15);fill:rgba(255, 255, 255, 0.15);}#chatgpt-mermaid-\_r_l3\_ .note{stroke:rgb(58, 132, 63);fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_l3\_ .noteText,#chatgpt-mermaid-\_r_l3\_ .noteText>tspan{fill:rgb(237, 237, 237);stroke:none;font-weight:normal;}#chatgpt-mermaid-\_r_l3\_ .activation0{fill:rgb(48, 48, 48);stroke:hsl(0, 0%, 8.8235294118%);}#chatgpt-mermaid-\_r_l3\_ .activation1{fill:rgb(48, 48, 48);stroke:hsl(0, 0%, 8.8235294118%);}#chatgpt-mermaid-\_r_l3\_ .activation2{fill:rgb(48, 48, 48);stroke:hsl(0, 0%, 8.8235294118%);}#chatgpt-mermaid-\_r_l3\_ .actorPopupMenu{position:absolute;}#chatgpt-mermaid-\_r_l3\_ .actorPopupMenuPanel{position:absolute;fill:rgb(9, 23, 44);box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#chatgpt-mermaid-\_r_l3\_ .actor-man circle,#chatgpt-mermaid-\_r_l3\_ line{fill:rgb(9, 23, 44);stroke-width:2px;}#chatgpt-mermaid-\_r_l3\_ g rect.rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_l3\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_l3\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_l3\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_l3\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_l3\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_l3\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_l3\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Submit query / documentCreate review recordEnqueue reviewStart workflowExtract claimsRetrieve policiesVector searchRelevant policy chunksRetrieved evidenceClaims + policy contextCompliance findingsRisk assessment and validationSave findingsRequest approvalApprove / RejectSave decision and auditReview status / result

# 5. Five concepts you must understand for the interview

| Concept          | Simple explanation                               |
| ---------------- | ------------------------------------------------ |
| State            | Shared data between workflow nodes               |
| Node             | Individual processing function                   |
| Edge             | Defines which node executes next                 |
| Conditional edge | Decides the next node dynamically                |
| Checkpointer     | Saves workflow state for recovery and resumption |

My suggestion: Before memorizing the code, make sure you can explain this sentence:

"LangGraph orchestrates our compliance workflow using a shared state. Each node performs a specialized responsibility, such as claim extraction, policy retrieval, compliance analysis, risk assessment, and validation. Conditional edges control workflow execution, and persistent checkpoints support recovery and human approval workflows."

That explanation demonstrates a much stronger understanding than simply saying that you used LangGraph.