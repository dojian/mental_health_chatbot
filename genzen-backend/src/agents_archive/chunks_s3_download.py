#rag
#load pickle file from s3
import boto3
import pickle

s3 = boto3.client('s3')
response = s3.get_object(Bucket='my-genzen-bucket', Key='data/data--contextual-retrieval-2025-02-15-41.pkl')
text_chunks = pickle.loads(response['Body'].read())
print(type(text_chunks))  # Should be dict

