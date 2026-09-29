from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.graph.state import CopilotState
from app.services.guardrails import InputGuardrail, OutputGuardrail
from app.services.retriever import VectorRetriever

def build_graph(db):
    retriever = VectorRetriever(db)
    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        temperature=0,
    )
    input_guard = InputGuardrail()
    output_guard = OutputGuardrail()

    async def guard_input(state: CopilotState):
        result = input_guard.validate(state["question"])
        if not result.allowed:
            return {"guardrail_error": result.reason}
        return {"question": result.text}

    async def retrieve(state: CopilotState):
        if state.get("guardrail_error"):
            return {"context": ""}
        chunks = await retriever.search(
            state["tenant_id"], state["question"], top_k=5
        )
        return {"context": "\n\n".join(c.content for c in chunks)}

    async def generate(state: CopilotState):
        if state.get("guardrail_error"):
            return {"answer": state["guardrail_error"], "risk_score": 0.0}

        prompt = f'''You are an enterprise financial knowledge copilot.
Use only the supplied context. If context is insufficient, explicitly say so.
Never invent account-specific facts.

CONTEXT:
{state.get("context", "")}

QUESTION:
{state["question"]}
'''
        response = await llm.ainvoke(prompt)
        answer = response.content if isinstance(response.content, str) else str(response.content)

        # Replace this example rule with a calibrated domain policy engine.
        risk = 0.85 if any(term in state["question"].lower()
                            for term in ("transfer", "wire", "beneficiary",
                                         "close account")) else 0.10

        return {
            "answer": answer,
            "risk_score": risk,
            "requires_human_approval": risk >= settings.hitl_risk_threshold,
        }

    async def human_gate(state: CopilotState):
        if not state.get("requires_human_approval"):
            return {}

        decision = interrupt({
            "type": "human_approval",
            "thread_id": state["thread_id"],
            "question": state["question"],
            "answer": state["answer"],
            "risk_score": state["risk_score"],
            "message": "Human approval required before finalizing this response.",
        })
        return {"human_decision": decision}

    async def output_guard(state: CopilotState):
        if state.get("human_decision", {}).get("approved") is False:
            return {"answer": "Human reviewer declined the response."}

        result = output_guard.validate(state["answer"])
        return {
            "answer": result.text if result.allowed
            else "Response blocked by output policy."
        }

    graph = StateGraph(CopilotState)
    graph.add_node("guard_input", guard_input)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_node("human_gate", human_gate)
    graph.add_node("output_guardrail", output_guard)

    graph.add_edge(START, "guard_input")
    graph.add_edge("guard_input", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "human_gate")
    graph.add_edge("human_gate", "output_guardrail")
    graph.add_edge("output_guardrail", END)

    # Demo checkpoint. Use a durable checkpointer in production.
    return graph.compile(checkpointer=MemorySaver())
