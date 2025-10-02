from app.agent import get_agent
from langchain_core.messages import HumanMessage, AIMessage
import app.config as config

def main():
    config.get_google_api_key()
    config.get_langchain_api_key()
    config.get_tavily_api_key()
    
    agent = get_agent()
    
    thread_id = "thread-12"
    config_thread = {"configurable": {"thread_id": thread_id}}
    
    print("RAG Agent CLI (type 'quit' or 'exit' to stop)")
    print("-" * 50)

    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"quit", "exit"}:
            break

        try:
            result = agent.invoke(
                {"messages": [HumanMessage(content=q)]},
                config=config_thread
            )

            last_message = next((m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None)

            if last_message:
                print(f"Agent: {last_message.content}")
            else:
                print("Agent: No response generated")

        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")

if __name__ == "__main__":
    main()
