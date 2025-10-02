# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

```
RAG_Agent_LangGraph/
├── app/                           # Core application modules
│   ├── agent.py                   # LangGraph agent definition and workflow
│   ├── config.py                  # Environment variables and API key management
│   ├── schemas.py                 # Pydantic models for structured outputs
│   ├── tools.py                   # RAG search, web search, and calculator tools
│   └── vector_store.py           # ChromaDB vector store management
├── agent-chat-ui/                # Frontend chat interface for testing agents
│   └── agent-chat-ui/            # Next.js application for LangGraph agents
├── docs/                         # Document storage (PDF, DOCX files)
├── examples/                     # LangGraph examples and references
│   ├── langgraph/                # Full LangGraph repository with examples
│   │   └── examples/rag/         # RAG-specific LangGraph implementations
│   └── RAG_AI_Agent_using_LangGraph_original.ipynb
├── chroma_db_1/                  # Vector database persistence (auto-created)
├── main.py                       # CLI application entry point
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
└── .env                         # API keys (create from template)
```

## Commands

### Running the Application
```bash
python main.py
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Frontend Chat UI (for Testing Agents)
```bash
cd agent-chat-ui/agent-chat-ui
pnpm install
pnpm dev
```
The frontend will be available at `http://localhost:3000`

### Environment Setup
- Create `.env` with required API keys:
  - `GOOGLE_API_KEY`
  - `LANGCHAIN_API_KEY` 
  - `TAVILY_API_KEY`
  - `OPENAI_API_KEY` (for embeddings and LLM)

## Architecture

This is a LangGraph-based RAG (Retrieval-Augmented Generation) agent that combines local knowledge base search with web search capabilities.

### Core Components

**Agent Flow (app/agent.py)**
- Router → RAG lookup → Judge → Web search (if needed) → Answer
- Uses OpenAI GPT-4.1-mini for routing and judging, GPT-4o-mini for final answers
- State management via LangGraph with conversation memory

**Knowledge Base (app/vector_store.py)**
- Document ingestion from `docs/` directory (PDF, DOCX)
- ChromaDB vector store with OpenAI embeddings (text-embedding-3-small)
- Automatic index creation on first run
- Persistent storage in `chroma_db_1/`

**Search Tools (app/tools.py)**
- RAG search: Retrieves top-3 chunks from local knowledge base
- Web search: Tavily API for up-to-date information
- Calculator: Basic math evaluation (uses eval - security consideration)

**Entry Point (main.py)**
- CLI interface with conversation loop
- Thread-based conversation state management
- API key validation on startup

### Data Flow
1. User query → Router determines strategy (direct answer/RAG/greeting)
2. RAG node retrieves documents, Judge evaluates sufficiency  
3. If insufficient, Web search supplements information
4. Answer node synthesizes response from available context

### File Organization
- `app/config.py`: Environment variable handling and LangChain tracing setup
- `app/schemas.py`: Pydantic models for structured outputs (routing decisions, judgments)
- `docs/`: Place PDF/DOCX documents here for knowledge base ingestion
- `chroma_db_1/`: Vector database persistence directory (auto-created)

## LangGraph Examples Reference

The `examples/langgraph/examples/` directory contains comprehensive LangGraph implementations that can serve as references for building new agents:

### RAG Examples (`examples/langgraph/examples/rag/`)
- `langgraph_adaptive_rag.ipynb`: Adaptive RAG with routing between RAG and web search
- `langgraph_agentic_rag.ipynb`: Agentic RAG with tool use and reasoning
- `langgraph_crag.ipynb`: Corrective RAG with answer grading and web search fallback
- `langgraph_self_rag.ipynb`: Self-reflective RAG with answer quality assessment
- `langgraph_*_local.ipynb`: Local model variants using open-source LLMs

### Other Useful Examples
- `chatbots/`: Conversational agent patterns with memory
- `customer-support/`: Multi-step customer service workflows
- `code_assistant/`: Code generation and debugging agents
- `human_in_the_loop/`: Agents with human approval steps
- `extraction/`: Information extraction workflows

### Key Patterns to Reference
- **State Management**: How different examples handle conversation state and memory
- **Tool Integration**: Various approaches to tool calling and result processing
- **Error Handling**: Fallback strategies and error recovery patterns
- **Routing Logic**: Decision-making patterns for multi-path workflows
- **Human-in-the-Loop**: Interactive approval and intervention patterns

Use these examples as templates when extending the current RAG agent or building new LangGraph workflows.

## Agent Chat UI - Frontend Testing Interface

The `agent-chat-ui/agent-chat-ui/` directory contains a Next.js web application that provides a chat interface for testing LangGraph agents. This eliminates the need for CLI testing and provides a more user-friendly way to interact with agents.

### Key Features
- **Universal LangGraph Integration**: Can connect to any LangGraph server with a `messages` key
- **Real-time Streaming**: Supports streaming responses from LangGraph agents
- **Artifact Rendering**: Displays additional content in side panels (charts, documents, etc.)
- **Message Filtering**: Control message visibility with tags (`langsmith:nostream`, `langsmith:do-not-render`)
- **Production Ready**: Built-in authentication and deployment patterns

### Setup & Configuration
1. **Local Development**:
   ```bash
   cd agent-chat-ui/agent-chat-ui
   cp .env.example .env
   # Edit .env with your configuration:
   # NEXT_PUBLIC_API_URL=http://localhost:2024
   # NEXT_PUBLIC_ASSISTANT_ID=agent
   pnpm install && pnpm dev
   ```

2. **Connect to Current RAG Agent**: 
   - The current CLI agent needs to be adapted to run as a LangGraph server
   - Use LangGraph's built-in server functionality or LangGraph Platform
   - Set `NEXT_PUBLIC_API_URL` to your agent's endpoint

### Usage Patterns
- **Development**: Test new agent implementations with immediate visual feedback
- **Debugging**: See agent reasoning steps and tool calls in real-time
- **Demos**: Showcase agent capabilities with a polished interface
- **Integration Testing**: Validate multi-turn conversations and state management

### Authentication Options
- **Local**: Direct connection to LangGraph server (development only)
- **API Passthrough**: Proxy requests through Next.js API routes (production)
- **Custom Auth**: LangGraph custom authentication for advanced access control

This frontend is essential for testing and demonstrating LangGraph agents, providing a much better user experience than CLI interfaces.