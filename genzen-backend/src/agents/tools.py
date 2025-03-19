import boto3
import json
from typing import Dict
import timeit

def mental_health(user_history: str, user_text: str) -> Dict:
    """Calls the SageMaker endpoint for mental health counseling response."""

    sm_runtime = boto3.client('sagemaker-runtime')
    endpoint = 'huggingface-pytorch-tgi-inference-2025-03-18-22-23-42-734'

    # Format the input prompt
    prompt = f"""
    Given a student's Conversation History and Current Message, extract the relevant metadata, including emotion type, emotion intensity (1-5), problem type, and counseling strategy.
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

    start_time = timeit.default_timer()
    print(f"Time start: {start_time}")
    # Invoke SageMaker endpoint
    response = sm_runtime.invoke_endpoint(
        EndpointName=endpoint, 
        ContentType='application/json', 
        Body=json.dumps(payload)
    )
    end_time = timeit.default_timer()
    print(f"Time end: {end_time}")
    print(f"Time taken: {end_time - start_time} seconds")
    # Process response
    result_body = json.loads(response['Body'].read().decode('utf-8'))

    # Extract and parse structured JSON response
    response_text = result_body[0]['generated_text']

    print('--response----------------------------')
    print(response_text)
    print('--response----------------------------')



    structured_response = response_text.split("### Counselor Structured JSON Response:")[1].strip()

    print('--structured response----------------------------')
    print(structured_response)
    print('--structured response----------------------------')

    return json.loads(structured_response)  # Convert string response into JSON
