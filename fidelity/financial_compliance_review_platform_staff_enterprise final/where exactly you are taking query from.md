Good question. The query comes from the financial advisor or compliance officer through the application's frontend.

In our project, there are actually two possible inputs:

1. An uploaded financial document that needs compliance review.
2. A natural-language question from a user about a compliance policy.

Let's understand the flow.

## 1. Where does the query come from?

Imagine a financial advisor is using our compliance platform.

They open a web application and upload a document or enter a question.

For example:

"What are the compliance risks associated with promising guaranteed 15% annual returns to investors?"

The request travels through this architecture:

\#chatgpt-mermaid-\_r_nh\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_nh\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_nh\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_nh\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_nh\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_nh\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_nh\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_nh\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_nh\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_nh\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_nh\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_nh\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_nh\_ p{margin:0;}#chatgpt-mermaid-\_r_nh\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_nh\_ .label text,#chatgpt-mermaid-\_r_nh\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .node rect,#chatgpt-mermaid-\_r_nh\_ .node circle,#chatgpt-mermaid-\_r_nh\_ .node ellipse,#chatgpt-mermaid-\_r_nh\_ .node polygon,#chatgpt-mermaid-\_r_nh\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .rough-node .label text,#chatgpt-mermaid-\_r_nh\_ .node .label text,#chatgpt-mermaid-\_r_nh\_ .image-shape .label,#chatgpt-mermaid-\_r_nh\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_nh\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .rough-node .label,#chatgpt-mermaid-\_r_nh\_ .node .label,#chatgpt-mermaid-\_r_nh\_ .image-shape .label,#chatgpt-mermaid-\_r_nh\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_nh\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_nh\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_nh\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_nh\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_nh\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_nh\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_nh\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_nh\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_nh\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_nh\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_nh\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_nh\_ .icon-shape,#chatgpt-mermaid-\_r_nh\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_nh\_ .icon-shape p,#chatgpt-mermaid-\_r_nh\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_nh\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_nh\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_nh\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_nh\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_nh\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_nh\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_nh\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_nh\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_nh\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_nh\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_nh\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_nh\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_nh\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_nh\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_nh\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_nh\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .node rect,#chatgpt-mermaid-\_r_nh\_ .node circle,#chatgpt-mermaid-\_r_nh\_ .node ellipse,#chatgpt-mermaid-\_r_nh\_ .node polygon,#chatgpt-mermaid-\_r_nh\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_nh\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_nh\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_nh\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_nh\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_nh\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Financial Advisor / ComplianceOfficerWeb Application / FrontendFastAPI REST APIJWT AuthenticationReview / Query ServiceRAG PipelinePostgreSQL + pgvectorLLMResponse to Frontend

## 2. What happens when the user sends a question?

Let's take this example:

User query:

"Can we advertise guaranteed 15% annual returns?"

Step 1: Frontend

The user enters the question in a chat box or compliance-review interface.

Step 2: FastAPI

The frontend sends an HTTP POST request.

Example:

```
POST /compliance/query
```

Request body:

```
{
  "query": "Can we advertise guaranteed 15% annual returns?"
}
```

Step 3: Query Service

FastAPI passes the query to the application service.

The service validates the user, tenant, and permissions.

Step 4: RAG Pipeline

We convert the question into an embedding and search relevant policy chunks in PostgreSQL using pgvector.

For example, we might retrieve:

- Policy 101: Investment returns cannot be guaranteed.
- Policy 102: Historical performance must not imply future returns.
- Policy 103: Investment risks must be disclosed.

Step 5: LLM

We pass three things to the LLM:

- Original user question.
- Retrieved compliance policies.
- System instructions.

The LLM generates an evidence-based answer.

Step 6: Response

Example:

```
{
  "answer": "Advertising guaranteed 15% annual returns may violate compliance policy.",
  "risk_level": "HIGH",
  "policy_reference": ["POL101"],
  "recommendation": "Remove the guaranteed return claim."
}
```

## 3. But what if the user uploads a PDF instead of asking a question?

That's a different entry point.

For example, a financial advisor uploads `investment_proposal.pdf`.

The flow becomes:

```
PDF Upload
    |
    v
FastAPI
    |
    v
Document Storage (S3)
    |
    v
Document Processing
    |
    v
Claim Extraction
    |
    v
RAG Policy Retrieval
    |
    v
Compliance Analysis
    |
    v
Risk Assessment
    |
    v
Human Approval
    |
    v
PostgreSQL
```

## 4. One important distinction for your interview

| User input                    | What the platform does                     |
| ----------------------------- | ------------------------------------------ |
| Natural-language question     | Answers using compliance-policy RAG        |
| Uploaded PDF                  | Performs document compliance review        |
| Compliance officer's question | Retrieves policies and explains violations |
| Approval/rejection            | Records the human decision                 |

My question to check your understanding:

If the interviewer asks:

"Where does the user query enter your AI architecture, and how does it reach the LLM?"

You should be able to explain:

"The query originates from the frontend application. It reaches our FastAPI endpoint through an HTTP request. The API authenticates the user and passes the request to the query service. The query service invokes our RAG pipeline, which retrieves relevant compliance policies from PostgreSQL using pgvector. Finally, the original query and retrieved context are passed to the LLM to generate a grounded response."

This is the complete query-to-answer flow.