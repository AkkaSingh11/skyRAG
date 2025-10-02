from typing import Annotated, TypedDict, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from app.schemas import RouteDecision, RagJudge
from app.tools import rag_search_tool, web_search_tool

# LLM instances
router_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0).with_structured_output(RouteDecision)
judge_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0).with_structured_output(RagJudge)
answer_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

# State
class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    route: Literal["rag", "answer", "end"]
    rag: str
    web: str

# Nodes
def router_node(state: AgentState) -> AgentState:
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    messages = [
        ("system", (
            "You are a router that decides how to handle user queries:\n"
            "- Use 'end' for pure greetings/small-talk (also provide a 'reply')\n"
            "- Use 'rag' when knowledge base lookup is needed\n"
            "- Use 'answer' when you can answer directly without external info"
        )),
        ("user", query)
    ]
    result: RouteDecision = router_llm.invoke(messages)
    out = {"messages": state["messages"], "route": result.route}
    if result.route == "end":
        out["messages"] = state["messages"] + [AIMessage(content=result.reply or "Hello!")]
    return out

def rag_node(state: AgentState) -> AgentState:
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    chunks = rag_search_tool.invoke({"query": query})
    judge_messages = [
        ("system", (
            "You are a judge evaluating if the retrieved information is sufficient "
            "to answer the user's question. Consider both relevance and completeness."
        )),
        ("user", f"Question: {query}\n\nRetrieved info: {chunks}\n\nIs this sufficient to answer the question?")
    ]
    verdict: RagJudge = judge_llm.invoke(judge_messages)
    return {**state, "rag": chunks, "route": "answer" if verdict.sufficient else "web"}

def web_node(state: AgentState) -> AgentState:
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    snippets = web_search_tool.invoke({"query": query})
    return {**state, "web": snippets, "route": "answer"}

def answer_node(state: AgentState) -> AgentState:
    user_q = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    ctx_parts = []
    if state.get("rag"):
        ctx_parts.append("Knowledge Base Information:\n" + state["rag"])
    if state.get("web"):
        ctx_parts.append("Web Search Results:\n" + state["web"])
    context = "\n\n".join(ctx_parts) if ctx_parts else "No external context available."
    prompt = f"""Please answer the user's question using the provided context.

Question: {user_q}

Context:
{context}

Provide a helpful, accurate, and concise response based on the available information."""
    ans = answer_llm.invoke([HumanMessage(content=prompt)]).content
    return {**state, "messages": state["messages"] + [AIMessage(content=ans)]}

# Routing helpers
def from_router(st: AgentState) -> Literal["rag", "answer", "end"]:
    return st["route"]

def after_rag(st: AgentState) -> Literal["answer", "web"]:
    return st["route"]

def after_web(_) -> Literal["answer"]:
    return "answer"

# Graph
def get_agent():
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("rag_lookup", rag_node)
    g.add_node("web_search", web_node)
    g.add_node("answer", answer_node)
    g.set_entry_point("router")
    g.add_conditional_edges("router", from_router, {"rag": "rag_lookup", "answer": "answer", "end": END})
    g.add_conditional_edges("rag_lookup", after_rag, {"answer": "answer", "web": "web_search"})
    g.add_edge("web_search", "answer")
    g.add_edge("answer", END)
    return g.compile(checkpointer=MemorySaver())
