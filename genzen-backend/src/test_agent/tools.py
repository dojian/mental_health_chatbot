from langchain_core.tools import tool



@tool
def empathic_dialogue(query: str) -> str:
    """
    Tool to provide empathic response.
    
    Args:
        query (str): The input query.
    
    Returns:
        str: The empathic response.
    """
    return "I understand that you are feeling sad. I am here to listen and provide support. Please share your feelings with me."