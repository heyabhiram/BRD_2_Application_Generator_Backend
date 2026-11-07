import os
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.core.config import settings

# Load environment
load_dotenv()

def get_llm(model: str = None, temperature: float = 0.2) -> ChatOpenAI:
    """
    Returns configured ChatOpenAI instance using the project standard client.
    verify=False is enforced per requirements.
    """
    http_client = httpx.Client(verify=False, timeout=120.0)
    selected_model = model or settings.LLM_MODEL
    
    return ChatOpenAI(
        base_url=settings.LLM_BASE_URL,
        model=selected_model,
        api_key=settings.LLM_API_KEY,
        http_client=http_client,
        temperature=temperature
    )

# Default LLM instance
client = httpx.Client(verify=False, timeout=120.0)
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL", settings.LLM_BASE_URL),
    model=os.getenv("LLM_MODEL", settings.LLM_MODEL),
    api_key=os.getenv("LLM_API_KEY", settings.LLM_API_KEY),
    http_client=client,
    temperature=0.2
)

