from typing import Annotated, TypedDict, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import RouteDecision, RagJudge
from app.tools import rag_search_tool, web_search_tool
from app.config import validate_api_keys

# Validate API keys before initializing models
validate_api_keys()

# LLM instances using Gemini models
router_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    convert_system_message_to_human=True
).with_structured_output(RouteDecision)

judge_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    convert_system_message_to_human=True
).with_structured_output(RagJudge)

answer_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.7,
    convert_system_message_to_human=True
)

# State
class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    route: Literal["rag", "answer", "end"]
    rag: str
    web: str

# Nodes
def router_node(state: AgentState) -> AgentState:
    """Route user query to appropriate processing path"""
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    
    # For Gemini, we need to convert system messages to human messages
    prompt = (
        "You are a router that decides how to handle user queries:\n"
        "- Use 'end' for pure greetings/small-talk (also provide a 'reply')\n"
        "- Use 'rag' when knowledge base lookup is needed\n"
        "- Use 'answer' when you can answer directly without external info\n\n"
        f"User query: {query}\n\n"
        "Respond with the appropriate route and reply if needed."
    )
    
    result: RouteDecision = router_llm.invoke([HumanMessage(content=prompt)])
    out = {"messages": state["messages"], "route": result.route}
    if result.route == "end":
        out["messages"] = state["messages"] + [AIMessage(content=result.reply or "Hello!")]
    return out

def rag_node(state: AgentState) -> AgentState:
    """Retrieve documents from knowledge base and judge sufficiency"""
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    chunks = rag_search_tool.invoke({"query": query})
    
    judge_prompt = (
        "You are a judge evaluating if the retrieved information is sufficient "
        "to answer the user's question. Consider both relevance and completeness.\n\n"
        f"Question: {query}\n\n"
        f"Retrieved info: {chunks}\n\n"
        "Is this sufficient to answer the question? Respond with true for sufficient, false for insufficient."
    )
    
    verdict: RagJudge = judge_llm.invoke([HumanMessage(content=judge_prompt)])
    return {**state, "rag": chunks, "route": "answer" if verdict.sufficient else "web"}

def web_node(state: AgentState) -> AgentState:
    """Perform web search for additional information"""
    query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    snippets = web_search_tool.invoke({"query": query})
    return {**state, "web": snippets, "route": "answer"}

def answer_node(state: AgentState) -> AgentState:
    """Generate final answer using available context"""
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
def get_gemini_agent():
    """Create and compile the Gemini-based RAG agent"""
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