from __future__ import print_function

import json
import urllib
import boto3
import time

print('Loading function')

##### Instanciando os servicos
s3 = boto3.client('s3')
etranscoder = boto3.client('elastictranscoder')

##### Id da Pipeline
pipelineId = ('1463433351875-xzcffu')

##### Id do Preset 
presetId = ('1351620000001-000010')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    try:
        ##### Obtendo resposta do Evento   
        response = s3.get_object(Bucket=bucket, Key=key)
       
        ##### Realizando o Transcoding do Video
        transcoder = etranscoder.create_job(
            PipelineId = pipelineId,
            Input={
                'Key': key
            },
            Output={
                'Key': key,
                'PresetId': presetId
            }
        )
        
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
