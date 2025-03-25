from langchain_openai import ChatOpenAI
from src.utils.config_setting import Settings

settings = Settings()


def get_llm_client(model_name: str = "gpt-4o-mini", temperature: float = 0.9) -> ChatOpenAI:
    """
    Get a client for the LLM.
    """
    openai_api_key = settings.OPENAI_API_KEY
    model = ChatOpenAI(model=model_name, temperature=temperature)
    return model