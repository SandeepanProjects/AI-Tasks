from app.agents.query_rewriter import rewrite_query

from app.rag.retriever import retrieve_context

from app.rag.context_builder import build_context


def rag_node(state):

    rewritten_query = rewrite_query(
        state["question"]
    )

    documents = retrieve_context(
        rewritten_query
    )

    context = build_context(
        documents
    )

    state["context"] = context

    return state