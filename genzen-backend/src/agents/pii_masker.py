import boto3
import json
import numpy as np
from src.utils.config_setting import Settings

settings = Settings()

pii_endpoint = "PII-endpoint"

def apply_redaction(masked_text, start, end, pii_type):
    for j in range(start, end):
        masked_text[j] = ""
    masked_text[start] = f" [{pii_type}]"
    return masked_text

def mask_text(text, entities):
    masked_text = list(text)
    redaction_start = 0 
    redaction_end = 0
    is_redacting = False
    current_pii_type = "" 
    for i, entity in enumerate(entities):
        start = entity["start"]
        end = entity["end"]
        if start == end: 
            continue
        pii_type = entity["entity"].strip("I-")
        
        if not is_redacting: 
            is_redacting = True
            redaction_start = start
            redaction_end = end
            current_pii_type = pii_type
        elif start == redaction_end:
            redaction_end = end 
        else:
            # End current redaction and start a new one 
            masked_text = apply_redaction(masked_text, redaction_start, redaction_end, current_pii_type) 
            redaction_start = start
            redaction_end = end
            current_pii_type = pii_type
    if is_redacting: 
        masked_text = apply_redaction(masked_text, redaction_start, redaction_end, current_pii_type)
    return ''.join(masked_text)

def anonymize_pii(text: str) -> str:
    """
    Calls the SageMaker endpoint for PII classification and outputs user text with masked PII.
    In debug mode, returns the original text without masking.
    """
    # In debug mode, return original text
    if settings.DEBUG:
        return text
        
    try:
        sm_runtime = boto3.client('sagemaker-runtime', region_name='us-east-2')
        
        payload = {
            "inputs": text
        }

        response = sm_runtime.invoke_endpoint(
            EndpointName=pii_endpoint, 
            ContentType='application/json', 
            Body=json.dumps(payload).encode('utf-8')
        )    

        result = json.loads(response["Body"].read().decode("utf-8"))

        return mask_text(text, result)
    except Exception as e:
        print(f"Error in PII masking: {e}")
        # If there's an error, return original text
        return text

if __name__ == "__main__": 

    user_text = "My name is Jordan and I'm feeling overwhelmed with schoolwork. I feel like I'm the only Asian here sometimes, I want to go back to San Jose. How do I delete my account jordanfx97"
    print(anonymize_pii(user_text))
