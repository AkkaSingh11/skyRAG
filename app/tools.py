from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from app.vector_store import get_retriever
from app.config import get_tavily_api_key

@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions. Use this for any math calculations."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

def get_tavily_search():
    """Lazy initialization of Tavily search"""
    return TavilySearch(max_results=3, topic="general", tavily_api_key=get_tavily_api_key())

@tool
def web_search_tool(query: str) -> str:
    """Up-to-date web info via Tavily"""
    try:
        tavily = get_tavily_search()
        result = tavily.invoke({"query": query})
        if isinstance(result, dict) and 'results' in result:
            formatted_results = []
            for item in result['results']:
                title = item.get('title', 'No title')
                content = item.get('content', 'No content')
                url = item.get('url', '')
                formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}")
            return "\n\n".join(formatted_results) if formatted_results else "No results found"
        else:
            return str(result)
    except Exception as e:
        return f"WEB_ERROR::{e}"

@tool
def rag_search_tool(query: str) -> str:
    """Top-3 chunks from KB (empty string if none)"""
    retriever = get_retriever()
    if not retriever:
        return "RAG_ERROR::Retriever not initialized."
    try:
        docs = retriever.invoke(query, k=3)
        return "\n\n".join(d.page_content for d in docs) if docs else ""
    except Exception as e:
        return f"RAG_ERROR::{e}"

tools = [calculator, web_search_tool, rag_search_tool]
