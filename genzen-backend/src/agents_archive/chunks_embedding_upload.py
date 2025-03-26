import boto3

# Initialize the S3 client
s3 = boto3.client('s3')

# Upload the embeddings to S3
s3.upload_file(
    Filename='/Users/dongan/embeddings.pkl',
    Bucket='my-genzen-bucket',
    Key='data/embeddings.pkl' #where it saved on s3
)