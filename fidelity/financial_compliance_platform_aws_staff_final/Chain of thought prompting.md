Let's understand Chain-of-Thought (CoT) prompting in the context of your Financial Compliance Review Platform.

## 1. What is Chain-of-Thought prompting?

Chain-of-Thought prompting is a technique that encourages an LLM to work through a complex problem in structured steps rather than jumping directly to an answer.

For example, instead of asking:

"Is this financial claim compliant?"

We ask the model to evaluate several aspects:

1. Identify the financial claim.
2. Identify the relevant compliance policy.
3. Compare the claim against the policy.
4. Determine whether there is a potential violation.
5. Assign a risk category.
6. Provide an evidence-based conclusion.

The goal is more consistent analysis.

## 2. Example in our project

Suppose the uploaded document contains:

"Investors are guaranteed 15% annual returns with zero risk."

Our RAG system retrieves:

- POL101: Investment returns cannot be guaranteed.
- POL102: Financial risks must be disclosed accurately.

We construct a structured analysis prompt.

Prompt:

```
You are a financial compliance analyst.

Analyze the financial claim using the
provided compliance policies.

Perform these tasks:

1. Identify the financial claims.
2. Identify applicable policy references.
3. Compare each claim against the policies.
4. Identify potential violations.
5. Classify the risk level.
6. Provide supporting evidence.
7. Recommend corrective action.

Do not make unsupported conclusions.
Return a structured JSON response.
```

## 3. Expected output

```
{
  "claim": "Guaranteed 15% annual returns with zero risk",
  "policy_reference": ["POL101", "POL102"],
  "violation": true,
  "risk_level": "HIGH",
  "findings": [
    {
      "issue": "Guaranteed return statement",
      "evidence": "POL101 prohibits guaranteed returns."
    },
    {
      "issue": "Zero-risk representation",
      "evidence": "POL102 requires accurate risk disclosure."
    }
  ],
  "recommendation": "Remove guaranteed return and zero-risk claims."
}
```

Notice that we ask the model to perform a structured analysis, but we don't need it to expose its private internal reasoning.

## 4. Different prompting techniques

| Technique              | How it works                               | Application                         |
| ---------------------- | ------------------------------------------ | ----------------------------------- |
| Zero-shot              | Give instructions without examples         | Basic compliance checking           |
| Few-shot               | Provide sample inputs and outputs          | Consistent violation classification |
| Chain-of-Thought style | Encourage structured intermediate analysis | Complex policy comparisons          |
| Role prompting         | Assign a specific role                     | Financial compliance analyst        |
| Contextual prompting   | Supply retrieved policies                  | RAG-based analysis                  |
| Structured output      | Require a defined JSON schema              | Downstream validation               |

## 5. How does it fit into LangGraph?

\#chatgpt-mermaid-\_r_tk\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_tk\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_tk\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_tk\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_tk\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_tk\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_tk\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_tk\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_tk\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_tk\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_tk\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_tk\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_tk\_ p{margin:0;}#chatgpt-mermaid-\_r_tk\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_tk\_ .label text,#chatgpt-mermaid-\_r_tk\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .node rect,#chatgpt-mermaid-\_r_tk\_ .node circle,#chatgpt-mermaid-\_r_tk\_ .node ellipse,#chatgpt-mermaid-\_r_tk\_ .node polygon,#chatgpt-mermaid-\_r_tk\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .rough-node .label text,#chatgpt-mermaid-\_r_tk\_ .node .label text,#chatgpt-mermaid-\_r_tk\_ .image-shape .label,#chatgpt-mermaid-\_r_tk\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_tk\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .rough-node .label,#chatgpt-mermaid-\_r_tk\_ .node .label,#chatgpt-mermaid-\_r_tk\_ .image-shape .label,#chatgpt-mermaid-\_r_tk\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_tk\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_tk\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_tk\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_tk\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_tk\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_tk\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_tk\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_tk\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_tk\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_tk\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_tk\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_tk\_ .icon-shape,#chatgpt-mermaid-\_r_tk\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_tk\_ .icon-shape p,#chatgpt-mermaid-\_r_tk\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_tk\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_tk\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_tk\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_tk\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_tk\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_tk\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_tk\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_tk\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_tk\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_tk\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_tk\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_tk\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_tk\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_tk\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_tk\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_tk\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .node rect,#chatgpt-mermaid-\_r_tk\_ .node circle,#chatgpt-mermaid-\_r_tk\_ .node ellipse,#chatgpt-mermaid-\_r_tk\_ .node polygon,#chatgpt-mermaid-\_r_tk\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_tk\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_tk\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_tk\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_tk\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_tk\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Extracted Financial ClaimsRAG Policy RetrievalRetrieved Policy EvidenceStructured Analysis PromptLLM Compliance AnalysisStructured FindingsRisk AssessmentPydantic ValidationHuman Review

The prompt is constructed inside the compliance analysis node.

For example:

```
def compliance_analysis_node(state):    prompt = build_prompt(        claims=state["claims"],        policies=state["retrieved_policies"]    )    response = llm.invoke(prompt)    findings = validate_findings(response)    return {        "findings": findings    }
```

## 6. What if the interviewer asks: How do you prevent hallucinations when using CoT?

You can answer:

"We don't rely on prompting alone to prevent hallucinations. We combine structured analysis instructions with RAG-based evidence grounding. The model receives relevant policy documents as context, and we require policy references for every identified violation. We validate the output schema and verify policy references against the database. If the retrieved evidence is insufficient, the model must indicate that rather than inventing a compliance rule."

One important distinction: Chain-of-Thought prompting does not guarantee correct answers, and we should not depend on exposing hidden reasoning traces. In production, asking for concise analysis steps, evidence, and conclusions is generally more reliable and auditable.

## 7. Senior AI Engineer interview follow-up

An interviewer may ask:

"What is the difference between Chain-of-Thought prompting and ReAct prompting?"

- CoT: Encourages structured reasoning through a problem.
- ReAct: Combines reasoning with actions or tool calls, observes the results, and continues.

In our platform, an enhanced ReAct-style workflow could retrieve policies, inspect evidence, and request additional retrieval when evidence is insufficient. LangGraph would control those tool interactions.

That distinction is worth understanding because it connects prompt engineering directly to agentic AI architecture.