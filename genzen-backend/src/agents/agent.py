import os, uuid
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from src.connections.db import checkpointer, memory_store
from src.agents.tools import mental_health, remember_information, recall_information
from src.agents.classification_tools import predict_suicide_depression
from src.connections.lifespan import rag_pipeline
from src.agents.pii_masker import anonymize_pii
from src.utils.config_setting import Settings
    
load_dotenv()
settings = Settings()

model_name = os.getenv("OPENAI_MODEL_NAME")

def rag_rerank(query: str):
    """
    Retrieves and reranks documents based on a user query using the RAG pipeline's 
    `retrieve_with_rerank` method.

    Args:
        query (str): The input query for which relevant documents are to be retrieved and reranked.

    Returns:
        List[Document]: A list of top reranked documents based on the input query.
    """
    # Ensure the base retriever is initialized by calling the initialization function
    if rag_pipeline.base_retriever is None:
        # Initialize retrievers manually if necessary
        print("Base retriever is not initialized, initializing now...")
        rag_pipeline.initialize_retrievers()  # Manually call this only if base_retriever is None

    # Call retrieve_with_rerank
    return rag_pipeline.retrieve_with_rerank(query)

# Tool

tools = [mental_health, rag_rerank, remember_information, recall_information]

# Define LLM with bound tools
llm = ChatOpenAI(model=model_name)
llm_with_tools = llm.bind_tools(tools)
                               
# System message
sys_msg_advice = SystemMessage(content="""You are a helpful student assistant tasked with mental health counseling. 
                               When counseling, make sure to use the **answer** directly from the mental_health tool output.
                               If the mental_health tool output includes 'Providing Suggestions' as counseling_strategy, 
                               retrieve additional information using the rag_rerank tool. 
                               If rag_rerank tool is called, answer the question(user_text) only based on the context information the rag_rerank tool provided.
                               Do NOT use bullet points in the answer. Answer should be in 5 sentences and use the key words in the user_text to start the answer.
                               """)
                            #    use the predict_suicide_depression tool first to determine the depression class.
                            #    If the mental_health tool output includes 'Providing Suggestions' as counseling_strategy, 
                            #    retrieve additional information using the ragpipeline tool.
                            #    Use the predict_suicide_depression tool only when a meaningful conversation
                            #    related to mental health has started, and avoid triggering it for casual greetings
                            #    like 'hello' or similar small talk.
no_advice_context = "Avoid giving advices or suggestions. Make sure the  'counseling_strategy' mental_health tool output is not 'Providing Suggestions'."
sys_msg_no_advice = SystemMessage(content=sys_msg_advice.content + no_advice_context)

# Node
def assistant(state: MessagesState):
    """Handles assistant responses, memory operations, and decides next actions."""
    
    # Extract all user messages as conversation history
    user_history = "\n".join(msg.content for msg in state["messages"])

    # Get the latest user message
    user_text = state["messages"][-1].content if state["messages"] else ""

    # Get user_id from config if available
    user_id = state.get("configurable", {}).get("user_id", "default_user")
    
    # Check if the user has chosen to receive advice
    allow_advice = settings.allow_advice  # Default to True
    print('allow advice is set up to',allow_advice) #debug log
    
    if allow_advice:
        sys_msg = sys_msg_advice
    else:
        sys_msg = sys_msg_no_advice
    print('sys_msg is:',sys_msg.content) #debug log
    
    # Expanded trigger phrases to capture more user information
    trigger_facts = [
        "my name is", "i am", "i'm studying", "i love", "i study",
        "i'm interested in", "i like", "i enjoy", "i want to",
        "my major is", "i'm majoring in", "i'm a student of"
    ]

    try:
        # Check if message contains any trigger phrases
        if any(trigger in user_text.lower() for trigger in trigger_facts):
            memory_id = uuid.uuid4().hex

            # Store personal fact with structured data
            memory_store.put(
                (str(user_id), "facts"), 
                memory_id,
                {
                    "content": user_text,
                    "timestamp": str(datetime.now()),
                    "type": "personal_fact",
                    "metadata": {
                        "source": "user_message",
                        "trigger": next((t for t in trigger_facts if t in user_text.lower()), None),
                        "message_length": len(user_text),
                        "has_name": any(trigger in user_text.lower() for trigger in ["my name is", "i am", "i'm"]),
                        "has_study": any(trigger in user_text.lower() for trigger in ["studying", "study", "major"]),
                        "has_interests": any(trigger in user_text.lower() for trigger in ["love", "like", "enjoy", "interested"])
                    }
                }
            )
            print(f"Stored personal fact: {user_text}")  # Debug logging
    except Exception as e:
        print(f"Error storing personal fact: {e}")

    # Retrieve relevant memories if available
    memories = []
    try:
        # Try to retrieve from personal facts
        try:
            # Get all facts for the user using a pattern match
            facts = memory_store.get((str(user_id), "facts"), "*")  # Use * as wildcard
            if facts:
                for fact in facts:
                    if isinstance(fact, dict) and "content" in fact:
                        memories.append(f"I remember that {fact['content']}")
                        print(f"Retrieved fact: {fact['content']}")  # Debug logging
        except Exception as e:
            print(f"Error retrieving facts: {e}")

        # Try to retrieve recent conversations
        try:
            # Get recent conversations using a pattern match
            conversations = memory_store.get((str(user_id), "conversations"), "*")  # Use * as wildcard
            if conversations:
                # Sort by timestamp and get last 3
                recent_convs = sorted(
                    conversations, 
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True
                )[:3]
                for conv in recent_convs:
                    if isinstance(conv, dict) and "content" in conv:
                        memories.append(f"Previous conversation: {conv['content']}")
                        print(f"Retrieved conversation: {conv['content']}")  # Debug logging
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            
    except Exception as e:
        print(f"Error retrieving memories: {e}")
    
    # Add memories to system message if available
    memory_context = ""
    if memories:
        memory_context = "\n\nUser context from previous conversations:\n" + "\n".join(memories)
        print(f"Memory context: {memory_context}")  # Debug logging

    context_system_message = SystemMessage(content=sys_msg.content + memory_context)

    # Call LLM with tool support
    response = llm_with_tools.invoke([context_system_message] + state["messages"])

    # Store important insights from this conversation
    if user_text and len(user_text) > 5:  # Only store substantial messages
        try:
            # Store this interaction for future reference
            memory_id = uuid.uuid4().hex
            memory_store.put(
                (str(user_id), "conversations"),
                memory_id,
                {
                    "content": user_text,
                    "response": response.content,
                    "timestamp": str(datetime.now()),
                    "type": "conversation",
                    "metadata": {
                        "thread_id": state.get("configurable", {}).get("thread_id", "unknown_thread"),
                        "message_length": len(user_text),
                        "has_trigger": any(trigger in user_text.lower() for trigger in trigger_facts),
                        "response_length": len(response.content)
                    }
                }
            )
            print(f"Stored conversation: {user_text}")  # Debug logging
        except Exception as e:
            print(f"Error storing conversation memory: {e}")
    
    return {
        "messages": [response],
        "user_history": user_history,
        "user_text": anonymize_pii(user_text),
    }

#msg for classification tool
def severe_depr_msg(state:MessagesState):
    response = """It sounds like things have been really challenging for you and you’re feeling like you want to escape. As a chatbot, I am not equipped nor have the expertise to help talk through your situation. Please try seeking a mental health professional to discuss your difficult situation. 
For affordable options, you can search for a clinician on Open Path (https://openpathcollective.org/find-a-clinician). 
Help is available; if you need someone to talk with immediately, you can call or text 988 any time. The service is free and confidential."""
    return {"messages":[response]}

def mild_depr_msg(state:MessagesState):
    response = """I am really sorry you are going through this; it must be difficult for you. Although it might not seem like it now, the way you’re feeling will change. While I am not equipped nor have the expertise to help talk through your situation, you do not need to go through this alone. If you are able to, talking with a mental health professional or finding a support group are viable options. 
For affordable options, you can search for a clinician on Open Path (https://openpathcollective.org/find-a-clinician)"""
    return {"messages":[response]}
def decide_class(state) -> dict:
    # Use the last user message to classify
    user_text = state["messages"][-1].content if state["messages"] else ""
    predicted_cls = predict_suicide_depression(user_text)
    print("the classification is",predicted_cls) #debug

    # different response based on class
    if predicted_cls in ("suicide", "severe depression"):
        print("Routing to: suicide_severe_depression")  # debug
        return {"route": "suicide_severe_depression"}  # Wrap return value in a dictionary
    elif predicted_cls == "mild depression":
        return {"route": "mild_depression"}
    else:
        return {"route": "assistant"}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("classifier",decide_class)

builder.add_node("suicide_severe_depression", severe_depr_msg)
builder.add_node("mild_depression", mild_depr_msg)
builder.add_node("assistant",assistant)

builder.add_node("tools", ToolNode(tools))
#builder.add_node("rag", ragpipeline)
#builder.add_node("tools", ToolNode(tools))

#logic
builder.add_edge(START, "classifier")

builder.add_conditional_edges(
    "classifier",
    lambda state: state["route"]
)
builder.add_edge("suicide_severe_depression", END)
builder.add_edge("mild_depression", END)
#builder.add_edge("assistant", "tools")

builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)

builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile() #checkpointer=checkpointer, interrupt_before =["action"]

# if __name__ == "__main__": 
#     messages=[HumanMessage(content="My major is computer science. How do I find a mentor for career advice? Can you give me some suggestions?")]
#     #I am Lily. I feel sad about my calculus homework. I don't know if i will be about to understand the chain rule.
#     # Invoke graph
#     result=graph. invoke({"messages": messages})

#     # Print the messages
#     for m in result['messages']:
#         m.pretty_print()