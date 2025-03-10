from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_client(model_name: str = "gpt-4o-mini", temperature: float = 0.9) -> ChatOpenAI:
    """
    Get a client for the LLM.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model=model_name, temperature=temperature)
    return model