import os
from dotenv import load_dotenv

load_dotenv()

def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY")

def get_langchain_api_key():
    return os.getenv("LANGCHAIN_API_KEY")

def get_tavily_api_key():
    return os.getenv("TAVILY_API_KEY")

def validate_api_keys():
    """Validate that all required API keys are present"""
    required_keys = {
        "GOOGLE_API_KEY": get_google_api_key(),
        "LANGCHAIN_API_KEY": get_langchain_api_key(),
        "TAVILY_API_KEY": get_tavily_api_key()
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    return True

# Set environment variables for LangChain tracing
if get_langchain_api_key():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "langgraph-yt"
    os.environ["LANGCHAIN_API_KEY"] = get_langchain_api_key()

# Set Google API key for Gemini models
if get_google_api_key():
    os.environ["GOOGLE_API_KEY"] = get_google_api_key()
