import boto3
import json
import numpy as np
from typing import Dict
from src.utils.config_setting import Settings

settings = Settings()

suicide_model_tar = "modernBERT_suicide_base.tar.gz"
depression_models_tars = ['modernBERT_depression.tar.gz', 'mental-BERT_depression.tar.gz', 'mental-roberta_depression.tar.gz']
suicide_translation = {0: "misc", 2: "suicide"}
depression_translation = {0: "minimal depression", 1: "mild depression", 2: "severe depression"}
classification_endpoint = "huggingface-multi-model-classification-ep"


def convert_to_float(response_body): 
    probas = response_body.decode("utf-8")
    probas = probas.strip("[]").split(" ")
    probas = [float(i) for i in probas if i != ""]
    return probas 

def predict_suicide_depression(user_text: str) -> str:
    """
    Calls the SageMaker endpoint for suicide/depression prediction.
	Output:
    	- "misc": did not detect depression nor suicide 
    	- "suicide": detected suicide 
    	- "minimal depression": detected no depression or very minimal depression
    	- "mild depression": detected mild form of depression 
    	- "severe depression": detected severe detection  
    """
    session = boto3.Session(profile_name=settings.AWS_PROFILE)
    sm_runtime = session.client('sagemaker-runtime', region_name=settings.AWS_REGION)
    #sm_runtime = boto3.client('sagemaker-runtime', profile ="default")
    # Invoke SageMaker endpoint to classify suicide or depression
    response_suicide = sm_runtime.invoke_endpoint(
    	TargetModel = suicide_model_tar,
        EndpointName= classification_endpoint, 
        ContentType='text/csv', 
        Body=user_text.encode(encoding="UTF-8")
    )

    # Process response
    response_body_suicide = response_suicide['Body'].read()
    suicide_probas = convert_to_float(response_body_suicide)
    prediction_suicide = np.argmax(suicide_probas, axis = -1)

    # If model predicts depression, classify depression severity
    if prediction_suicide == 1:
        probas = []
        # Get probas from each depression model, take mean of the probas, and then take max proba as prediction 
        for depression_model_tar in depression_models_tars:
            response_depression = sm_runtime.invoke_endpoint(
                                            TargetModel = depression_model_tar,
                                            EndpointName= classification_endpoint, 
                                            ContentType='text/csv', 
                                            Body=user_text.encode(encoding="UTF-8")
                                                            )
            response_body_depression = response_depression["Body"].read()
            depression_probas = convert_to_float(response_body_depression)
            probas.append(np.array(depression_probas))
        probas = np.mean(probas, axis = 0)
        prediction_depression = np.argmax(probas, axis = -1)
        return depression_translation[prediction_depression]
    
    return suicide_translation[prediction_suicide]
