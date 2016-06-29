from __future__ import print_function

import json
import urllib
import boto3
import time

print('Loading function')

jsonFinal = '{"'

##### Instanciando os servicos
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

##### Acessando Tabela do DynamoDB
#table = dynamodb.Table('Videos')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    try:
        ##### Obtendo resposta do Evento   
        response = s3.get_object(Bucket=bucket, Key=key)
        
        getListVideos = dynamodb.scan(
            TableName='Videos',
            AttributesToGet=[
            'Link',
            'Nome'
            ]
        )
        
        for objeto in getListVideos['Items']:
            nomeDoVideo = objeto['Nome']['S']
            linkDoVideo = objeto['Link']['S']
            print (nomeDoVideo)
            print (linkDoVideo)
        
        
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
