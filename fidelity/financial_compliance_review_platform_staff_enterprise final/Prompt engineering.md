Exactly. Prompt engineering is a very important part of your Financial Compliance Review Platform, because the LLM needs to compare financial claims against retrieved compliance policies without inventing rules or conclusions.

Let's understand how we use it in the project.

## 1. Where does prompt engineering fit in our architecture?

\#chatgpt-mermaid-\_r_rv\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_rv\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_rv\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_rv\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_rv\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_rv\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_rv\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_rv\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_rv\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_rv\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_rv\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_rv\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_rv\_ p{margin:0;}#chatgpt-mermaid-\_r_rv\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_rv\_ .label text,#chatgpt-mermaid-\_r_rv\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .node rect,#chatgpt-mermaid-\_r_rv\_ .node circle,#chatgpt-mermaid-\_r_rv\_ .node ellipse,#chatgpt-mermaid-\_r_rv\_ .node polygon,#chatgpt-mermaid-\_r_rv\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .rough-node .label text,#chatgpt-mermaid-\_r_rv\_ .node .label text,#chatgpt-mermaid-\_r_rv\_ .image-shape .label,#chatgpt-mermaid-\_r_rv\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_rv\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .rough-node .label,#chatgpt-mermaid-\_r_rv\_ .node .label,#chatgpt-mermaid-\_r_rv\_ .image-shape .label,#chatgpt-mermaid-\_r_rv\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_rv\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_rv\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_rv\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_rv\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_rv\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_rv\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_rv\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_rv\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_rv\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_rv\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_rv\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_rv\_ .icon-shape,#chatgpt-mermaid-\_r_rv\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_rv\_ .icon-shape p,#chatgpt-mermaid-\_r_rv\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_rv\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_rv\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_rv\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_rv\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_rv\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_rv\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_rv\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_rv\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_rv\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_rv\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_rv\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_rv\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_rv\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_rv\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_rv\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_rv\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .node rect,#chatgpt-mermaid-\_r_rv\_ .node circle,#chatgpt-mermaid-\_r_rv\_ .node ellipse,#chatgpt-mermaid-\_r_rv\_ .node polygon,#chatgpt-mermaid-\_r_rv\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_rv\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_rv\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_rv\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_rv\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_rv\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}User Query / Uploaded PDFClaim ExtractionRAG Policy RetrievalRetrieved Policy ContextPrompt EngineeringLLMStructured ComplianceFindingsRisk AssessmentGuardrails and Validation

Prompt engineering happens primarily before the LLM call.

We construct a prompt using three important inputs:

1. System instructions.
2. User query or extracted claims.
3. Retrieved compliance policy context.

## 2. Example: System prompt

This defines the LLM's role and rules.

```
SYSTEM_PROMPT = """You are an enterprise financial complianceanalysis assistant.Your responsibility is to analyze financialclaims against the provided compliance policies.Rules:1. Only use the supplied policy context.2. Never invent compliance regulations.3. Identify potentially misleading financial claims.4. Explain why a claim may violate a policy.5. Always provide supporting policy references.6. If evidence is insufficient, explicitly   mention that.7. Do not make final approval decisions.8. Return the result in the required JSON format."""
```

## 3. Example: Dynamic user prompt

This is constructed at runtime using the user's actual query and retrieved policies.

```
USER_PROMPT = """Analyze the following financial claim.Financial Claim:{claim}Retrieved Compliance Policies:{policy_context}Perform the following:1. Identify potential compliance violations.2. Explain the reason.3. Identify the supporting policy.4. Assign a risk level.5. Suggest corrective action.Return structured JSON."""
```

Here, `{claim}` and `{policy_context}` are dynamically populated.

## 4. Complete prompt execution flow

Suppose the advisor uploads a document containing:

"Investors are guaranteed 15% annual returns."

Our RAG pipeline retrieves:

```
Policy POL101:
Investment returns cannot be guaranteed.

Policy POL102:
Investment risks must be disclosed.
```

The final prompt sent to the LLM contains:

System prompt

You are a financial compliance analysis assistant. Analyze claims using only the supplied policy evidence.

Claim

Investors are guaranteed 15% annual returns.

Retrieved context

- POL101: Investment returns cannot be guaranteed.
- POL102: Investment risks must be disclosed.

Expected output

Identify the violation, explain the reason, provide policy references, assign risk, and recommend corrective action.

## 5. Other prompt engineering techniques we can use

| Technique                     | Application                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| Role prompting                | Define the compliance analyst's role                                |
| Contextual prompting          | Inject retrieved policy evidence                                    |
| Few-shot prompting            | Provide examples of compliant and non-compliant claims              |
| Structured output prompting   | Force JSON responses                                                |
| Constraint-based prompting    | Prevent unsupported conclusions                                     |
| Chain-of-thought alternatives | Request concise reasoning summaries and evidence-based explanations |
| Prompt versioning             | Track changes to prompts over time                                  |

For financial compliance, I would particularly emphasize contextual prompting, structured outputs, few-shot examples, and evidence constraints.

## 6. How do you evaluate whether your prompt is working?

We shouldn't assume a prompt is good just because the LLM generates a convincing answer.

We evaluate:

- Does it identify actual violations?
- Does it cite the correct policy?
- Does it avoid unsupported claims?
- Does it identify missing disclosures?
- Does it produce valid structured output?

We can use an evaluation dataset and metrics such as precision, recall, and faithfulness.

## 7. Interview question

Interviewer: How did you implement prompt engineering in your financial compliance platform?

Your answer:

"We designed role-based and context-aware prompts for our compliance analysis workflow. We maintained system instructions separately from dynamic user inputs.

At runtime, our RAG pipeline retrieved relevant compliance policy chunks from PostgreSQL using pgvector. We injected those retrieved chunks, along with extracted financial claims, into the analysis prompt.

We also used structured output requirements to ensure the LLM returned consistent compliance findings, including violation status, risk level, policy references, explanation, and recommendations.

We emphasized evidence grounding and instructed the model not to invent policies or make unsupported compliance conclusions. Finally, we validated the generated responses using Pydantic and deterministic guardrails."

Next important concept to understand: How to manage prompt templates, versions, token limits, and model parameters in a production LangGraph application.