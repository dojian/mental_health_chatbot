import boto3
import json
from typing import Dict

def mental_health(user_history: str, user_text: str) -> Dict:
    """Calls the SageMaker endpoint for mental health counseling response."""

    sm_runtime = boto3.client('sagemaker-runtime')
    endpoint = 'huggingface-pytorch-tgi-inference-2025-03-09-23-30-16-495'

    # Format the input prompt
    prompt = f"""Given a student's Conversation History and Current Message, extract the relevant metadata, including emotion type, emotion intensity (1-5), problem type, and counseling strategy.
Then answer the student's Current Message as a counselor based on the metadata. Keep it concise but affirmative.
The counselor must return a Structured JSON Response with these fields: "emotion_type","emotion_intensity", "problem_type", "counseling_strategy","answer".

### Student:
**Conversation History:**
{user_history}

**Current Message:**
{user_text}

### Counselor Structured JSON Response:
"""

    # Prepare payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "num_return_sequences": 1,
            "temperature": 0.6,  # Balances creativity and coherence
            "top_p": 0.9,        # Reduces repeated phrases
            "use_cache": True
        }
    }

    # Invoke SageMaker endpoint
    response = sm_runtime.invoke_endpoint(
        EndpointName=endpoint, 
        ContentType='application/json', 
        Body=json.dumps(payload)
    )

    # Process response
    result_body = json.loads(response['Body'].read().decode('utf-8'))

    # Extract and parse structured JSON response
    response_text = result_body[0]['generated_text']
    structured_response = response_text.split("### Counselor Structured JSON Response:")[1].strip()

    return json.loads(structured_response)  # Convert string response into JSON
