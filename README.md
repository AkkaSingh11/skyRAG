# skyRAG - Gemini-Powered LangGraph RAG Agent

An Open Agentic RAG system for educational purposes built with LangGraph and Google Gemini models. This project implements a sophisticated RAG (Retrieval-Augmented Generation) agent with adaptive routing, local knowledge base search, web search capabilities, and a modern web-based chat interface.

## 🚀 Features

- **Gemini Integration**: Uses Google's Gemini 2.5 Flash for all LLM operations and gemini-embedding-001 for embeddings
- **Adaptive RAG**: Intelligent routing between local knowledge base, web search, and direct answers
- **Web Chat UI**: Modern Next.js frontend for seamless conversation
- **FastAPI Server**: Production-ready API with streaming support and CORS
- **Multi-format Documents**: Supports PDF and DOCX document ingestion
- **LangSmith Integration**: Built-in tracing and monitoring

## 📁 Project Structure

```
skyRAG/
├── app/                           # Core application modules
│   ├── agent.py                   # Original OpenAI-based agent (legacy)
│   ├── gemini_agent.py           # New Gemini-based LangGraph agent ⭐
│   ├── server.py                 # FastAPI server for LangGraph integration ⭐
│   ├── config.py                 # Environment variables and API key management
│   ├── schemas.py                # Pydantic models for structured outputs
│   ├── tools.py                  # RAG search, web search, and calculator tools
│   └── vector_store.py          # ChromaDB with Gemini embeddings ⭐
├── agent-chat-ui/                # Frontend chat interface
│   └── agent-chat-ui/           # Next.js application for LangGraph agents
├── docs/                        # Document storage (PDF, DOCX files)
├── examples/                    # LangGraph examples and references
├── chroma_db_gemini/           # Gemini embeddings vector database ⭐
├── main.py                     # Original CLI application (legacy)
├── start_server.py             # Server startup script ⭐
├── requirements.txt            # Python dependencies
├── pyproject.toml             # uv package management
└── .env                       # API keys configuration
```

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and pnpm
- uv package manager (recommended)

### 1. Install Python Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Ensure your `.env` file contains:
```env
GOOGLE_API_KEY="your-google-api-key"
LANGCHAIN_API_KEY="your-langchain-api-key"  
TAVILY_API_KEY="your-tavily-api-key"
```

### 3. Add Documents (Optional)

Place PDF or DOCX files in the `docs/` directory for knowledge base indexing.

## 🚀 Running the Application

### Backend Server

Start the Gemini RAG agent server:
```bash
uv run python start_server.py
```

The server will be available at `http://localhost:2024`

**Health Check**: `curl http://localhost:2024/`

### Frontend Chat UI

In a separate terminal:
```bash
cd agent-chat-ui/agent-chat-ui
pnpm install
pnpm dev
```

Access the chat interface at `http://localhost:3000`

## 🧠 How It Works

### Adaptive RAG Flow

1. **Router Node**: Analyzes user query and decides routing strategy
   - `end`: Simple greetings/small talk
   - `rag`: Knowledge base lookup needed
   - `answer`: Direct response without external info

2. **RAG Node**: Retrieves relevant documents from local knowledge base
   - Uses Gemini embeddings for semantic search
   - Judge evaluates if retrieved info is sufficient

3. **Web Search Node**: Fallback for insufficient local information
   - Powered by Tavily API for real-time web results

4. **Answer Node**: Synthesizes final response using available context

### Technology Stack

- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: gemini-embedding-001  
- **Vector Store**: ChromaDB
- **Framework**: LangGraph with FastAPI
- **Frontend**: Next.js with agent-chat-ui
- **Package Management**: uv

## 🔌 API Endpoints

- `GET /`: Health check
- `POST /chat`: Simple chat interface
- `POST /invoke`: LangGraph agent invocation
- `POST /stream`: Streaming responses

## 🧪 Testing

### Quick Tests

Test the server directly:
```bash
# Health check
curl http://localhost:2024/

# Simple chat
curl -X POST http://localhost:2024/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"content": "Hello!", "type": "human"}]}'

# Web search test
curl -X POST http://localhost:2024/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"content": "Latest AI news 2025", "type": "human"}]}'
```

## 🎯 Migration from OpenAI

This project now uses Google Gemini models exclusively:

- **Before**: OpenAI GPT models + text-embedding-3-small
- **After**: Gemini 2.5 Flash + gemini-embedding-001

The original OpenAI-based implementation remains in `app/agent.py` for reference.

## 📝 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Google AI Studio API key
- `LANGCHAIN_API_KEY`: LangSmith tracing (optional)
- `TAVILY_API_KEY`: Web search functionality

### Frontend Configuration

The chat UI is pre-configured in `agent-chat-ui/agent-chat-ui/.env`:
```env
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=agent
```

## 🔧 Development

### Local Development
The server runs with auto-reload enabled for development convenience.

### Adding New Tools
Extend `app/tools.py` with additional LangChain tools as needed.

### Customizing Agent Logic
Modify `app/gemini_agent.py` to adjust routing logic or add new nodes.

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google AI Studio](https://aistudio.google.com/)
- [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)

## 🆘 Troubleshooting

**Server won't start**: Check API keys in `.env` file
**No responses**: Verify Google API key has Gemini access
**Frontend connection issues**: Ensure backend is running on port 2024
