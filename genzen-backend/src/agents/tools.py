import boto3
import json
from typing import Dict
from src.utils.config_setting import Settings
from src.utils.aws_clients import get_sagemaker_runtime_client

settings = Settings()

def mental_health(user_history: str, user_text: str) -> Dict:
    """Calls the SageMaker endpoint for mental health counseling response."""

    # Explicitly specify the default profile
    # session = boto3.Session(profile_name=settings.AWS_PROFILE)
    sm_runtime = get_sagemaker_runtime_client()
    if sm_runtime is None:
        print("SageMaker runtime client is None")
        return json.dumps({
            "emotion_type": "unknown",
            "emotion_intensity": 3,
            "problem_type": "technical_issue",
            "counseling_strategy": "Affirmation and Reassurance",
            "answer": "I'm sorry, but I encountered a technical issue while trying to access support information."
        })
    
    try:
        endpoint = settings.MENTAL_HEALTH_ENDPOINT
        

        # Format the input prompt
        prompt_advice = f"""Given a student's Conversation History and Current Message, extract the relevant metadata, including emotion type, emotion intensity (1-5), problem type, and counseling strategy.
        Then answer the student's Current Message as a counselor based on the metadata. Keep it concise but affirmative. Make sure your response is friendly, empathetic, and relevant to the current message.

        **Constraints:** The counselor must not use personal experiences, references to friends, or imagined scenarios. Provide only general suggestions based on the provided context.

        The counselor must return **only** a Structured JSON Response with these fields: "emotion_type", "emotion_intensity", "problem_type", "counseling_strategy", "answer". Do not include any additional text before or after the JSON.

        ### Student:
        **Conversation History:**
        {user_history}

        **Current Message:**
        {user_text}

        ### Counselor Structured JSON Response:
        ```json
        """
        no_advice_context = "Only use 'Question', 'Affirmation and Reassurance', 'Restatement or Paraphrasing' as 'counseling_strategy'."
        prompt_no_advice = prompt_advice + no_advice_context
        if settings.allow_advice:
            prompt = prompt_advice
        else:
            prompt = prompt_no_advice
        # Prepare payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                #"num_return_sequences": 1,
                "temperature": 0.6,  # Balances creativity and coherence
                "top_p": 0.9,        # Reduces repeated phrases
                "use_cache": True,
                "stop": ["### Student:"]  # Stops generation if this appears
            }
        }

        # Invoke SageMaker endpoint
        response = sm_runtime.invoke_endpoint(
            EndpointName=endpoint, 
            ContentType='application/json', 
            Body=json.dumps(payload).encode('utf-8')
        )

        # Process response
        result_body = json.loads(response['Body'].read().decode('utf-8'))

        # Extract and parse structured JSON response
        response_text = result_body[0]['generated_text']
        structured_response = response_text.split("### Counselor Structured JSON Response:")[1].strip()

        return structured_response
    except Exception as e:
        print(f"Error in mental_health tool: {str(e)}")
        return json.dumps({
            "emotion_type": "unknown",
            "emotion_intensity": 3,
            "problem_type": "technical_issue",
            "counseling_strategy": "Affirmation and Reassurance",
            "answer": "I'm sorry, but I encountered a technical issue while trying to access support information."
        })

def remember_information(information: str, key: str = None) -> str:
    """
    Store important information about the user for future reference.
    Args:
        information (str): The information to store.
        key (str, optional): The key to store the information under. Defaults to None.
    """
    return f" I'll remember that {information}"

def recall_information(topic: str) -> str:
    """
    Recall information previously stored about the user.
    Args:
        topic (str): The topic to recall information about.
    """
    return f"Searching for information about {topic}..."
        