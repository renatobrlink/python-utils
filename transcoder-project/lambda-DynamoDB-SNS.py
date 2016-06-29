from __future__ import print_function

import json
import urllib
import boto3
import time

print('Loading function')

##### Instanciando os servicos
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

##### Acessando Tabela do DynamoDB
table = dynamodb.Table('Videos')

##### EndPoint do CloudFront
cloudfront = ('http://d397nnvlvhwg5r.cloudfront.net/')

##### ARN do Topic do SNS
topicARN = ('arn:aws:sns:us-east-1:939664253159:videos')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    try:
        ##### Obtendo resposta do Evento   
        response = s3.get_object(Bucket=bucket, Key=key)
        
        ##### Inserindo no DynamoDB os dados do acesso ao video e Status.
        put_item_dynamo = table.put_item(
            Item = {
                'Nome': key,
                'Info': response['ContentType'],
                'Status': '0',
                'Link': cloudfront + key
                }
        )
	        
        ##### Enviando alerta de video disponivel.
        snsPublish = sns.publish(
            TopicArn = topicARN,
            Message = 'Novo video disponivel. Para acessar o video acessar o Link: '+ cloudfront + key,
            Subject = 'Demo Summit! Tem novidade ai.',
            MessageStructure = 'Raw',
        )
        
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
