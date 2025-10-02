from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import uuid
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.gemini_agent import get_gemini_agent
from app.config import validate_api_keys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Gemini RAG Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class MessageInput(BaseModel):
    content: str
    type: str = "human"

class InvokeRequest(BaseModel):
    input: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    messages: List[MessageInput]
    config: Optional[Dict[str, Any]] = None

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    try:
        validate_api_keys()
        agent = get_gemini_agent()
        logger.info("Gemini RAG Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "gemini-rag"}

@app.post("/invoke")
async def invoke_agent(request: InvokeRequest):
    """Invoke the agent with input messages"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Extract messages from input
        messages = request.input.get("messages", [])
        
        # Convert to LangChain message format
        lc_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get("type") == "human":
                    lc_messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("type") == "ai":
                    lc_messages.append(AIMessage(content=msg.get("content", "")))
            elif hasattr(msg, 'content'):
                if isinstance(msg, HumanMessage) or isinstance(msg, AIMessage):
                    lc_messages.append(msg)
        
        # Generate thread ID for conversation state
        thread_id = request.config.get("configurable", {}).get("thread_id") if request.config else None
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke agent
        result = agent.invoke(
            {"messages": lc_messages},
            config=config
        )
        
        # Convert response messages to dict format
        response_messages = []
        for msg in result.get("messages", []):
            response_messages.append({
                "type": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content
            })
        
        return {
            "output": {
                "messages": response_messages
            },
            "metadata": {
                "thread_id": thread_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_agent(request: InvokeRequest):
    """Stream agent responses"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    async def generate_stream():
        try:
            # Extract messages from input
            messages = request.input.get("messages", [])
            
            # Convert to LangChain message format
            lc_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    if msg.get("type") == "human":
                        lc_messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("type") == "ai":
                        lc_messages.append(AIMessage(content=msg.get("content", "")))
            
            # Generate thread ID for conversation state
            thread_id = request.config.get("configurable", {}).get("thread_id") if request.config else None
            if not thread_id:
                thread_id = str(uuid.uuid4())
            
            config = {"configurable": {"thread_id": thread_id}}
            
            # Stream agent execution
            for chunk in agent.stream(
                {"messages": lc_messages},
                config=config
            ):
                # Format chunk for streaming
                formatted_chunk = {
                    "event": "on_chain_stream",
                    "data": chunk
                }
                yield f"data: {json.dumps(formatted_chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Error streaming agent: {e}")
            error_chunk = {
                "event": "error",
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Convert messages to LangChain format
        lc_messages = []
        for msg in request.messages:
            if msg.type == "human":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                lc_messages.append(AIMessage(content=msg.content))
        
        # Generate thread ID
        thread_id = request.config.get("configurable", {}).get("thread_id") if request.config else str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get response
        result = agent.invoke({"messages": lc_messages}, config=config)
        
        # Extract last AI message
        last_message = result.get("messages", [])[-1]
        
        return {
            "response": last_message.content if hasattr(last_message, 'content') else str(last_message),
            "thread_id": thread_id
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2024)