#Upload .pkl file to s3
import boto3

s3 = boto3.client('s3')

# Upload the local pickle file to S3
s3.upload_file(
    Filename='/Users/dongan/data--contextual-retrieval-2025-02-15-41.pkl',
    Bucket='my-genzen-bucket',
    Key='data/data--contextual-retrieval-2025-02-15-41.pkl' #where it saved on s3
)