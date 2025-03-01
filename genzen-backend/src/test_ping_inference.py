import boto3
import sagemaker
import json

# create a runtime client
sm_runtime = boto3.client('sagemaker-runtime')

# endpoint name
endpoint = 'huggingface-pytorch-tgi-inference-2025-03-01-18-53-32-220'
 
# payload
payload = {
	"inputs": "I feel sad today. I missed one question from my calculus homework on the power rule",
}

# Send image via InvokeEndpoint API
response = sm_runtime.invoke_endpoint(
    EndpointName=endpoint, 
    ContentType='application/json', 
    Body=json.dumps(payload))

# Unpack response
result_body = json.loads(response['Body'].read().decode('utf-8'))
print(result_body[0]['generated_text'].split('</think>')[1])