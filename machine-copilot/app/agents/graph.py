"""LangGraph wiring: Planner -> Retriever -> Responder.

A blocked-at-planning question (safety-bypass intent) still flows through
Retriever and Responder rather than short-circuiting the graph, because
each node already checks `state["blocked"]` and passes through immediately —
this keeps the graph shape uniform and the audit trail complete (every
question, blocked or not, goes through the same three logged steps).
"""
from langgraph.graph import StateGraph, END

from app.agents.state import CopilotState
from app.agents.nodes import plan, retrieve, respond


def build_graph():
    graph = StateGraph(CopilotState)
    graph.add_node("planner", plan)
    graph.add_node("retriever", retrieve)
    graph.add_node("responder", respond)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "responder")
    graph.add_edge("responder", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_query(question: str, machine_id: str, machine_model: str, thread_id: str = "default") -> CopilotState:
    graph = get_graph()
    initial_state: CopilotState = {
        "machine_id": machine_id,
        "machine_model": machine_model,
        "thread_id": thread_id,
        "question": question,
    }
    return graph.invoke(initial_state)
