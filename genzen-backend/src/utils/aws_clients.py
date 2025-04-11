import boto3
import os
from botocore.config import Config
from src.utils.config_setting import Settings

s3_client = None
sagemaker_runtime_client = None
session = None

settings = Settings()

def init_aws_clients():
    global s3_client, sagemaker_runtime_client, session

    region = os.environ.get('AWS_REGION', getattr(settings, "AWS_REGION", 'us-east-2'))

    session = boto3.Session(region_name=region)

    s3_client = session.client('s3')

    sagemaker_config = Config(
        read_timeout=120,
        retries={"max_attempts": 3, "mode": "adaptive"}
    )

    sagemaker_runtime_client = session.client('sagemaker-runtime', config=sagemaker_config)

    return {
        's3': s3_client,
        'sagemaker_runtime': sagemaker_runtime_client,
        'session': session
    }

def get_s3_client():
    global s3_client
    if s3_client is None:
        init_aws_clients()
    return s3_client

def get_sagemaker_runtime_client():
    global sagemaker_runtime_client
    if sagemaker_runtime_client is None:
        init_aws_clients()
    return sagemaker_runtime_client
