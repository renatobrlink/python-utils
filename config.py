import time
import boto3

##### Iniciando Libs
s3 = boto3.client('s3')
sns = boto3.client('sns')
config = boto3.client('config')
iam = boto3.client('iam')

#################################################

## Nome do Bucket
bucketName = 'config-rdmb'

## Region do Bucket
regionName = 'us-west-1'

## Nome do Delivery Channel
deliveryChannelName = 'rbbarbos-config'

## Nome do Prefixo no S3
prefixName = 'USConfig'

## Nome do topico do SNS
topicSnsName = 'Config'

## Nome do Configuration Recorder
configurationRecorderName = "AllConfigs"

## Nome da Role do AWS Config no IAM
iamRoleName = 'ConfigReadAll'

## ARN da Policy do AWS Config
iamPolicyConfigARN = 'arn:aws:iam::aws:policy/service-role/AWSConfigRole'

## ARN da Policy do S3
iamPolicyS3ARN = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'

#################################################

##### Funcao para Checagem de criacao do recurso com Sucesso
def rscCheck(rscRtn,rsc,rscId):
        if rscRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s criado com sucesso, segue o ID do Request: %s" % (rsc,rscId)  
        else:
            print "Erro ao criar o recurso %s!" % rsc

##### Funcao para Checagem de atachamento de servico com Sucesso
def atcCheck(atcRtn,rsc,rscAtc):
        if atcRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s atachado com sucesso ao recurso %s!" % (rscAtc,rsc)  
        else:
            print "Erro ao atachar o recurso %s!" % rscAtc

#################################################

##### Recurso AWS
rscBkt = 'Bucket AWS Config'

bucketUsConfig = s3.create_bucket(
    ACL = 'private',
    Bucket = bucketName,
    CreateBucketConfiguration = {
        'LocationConstraint': regionName
    },
)

##### Obtendo o request ID
RequestId = bucketUsConfig['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(bucketUsConfig,rscBkt,RequestId)

##### Setando policy no Bucket do S3
s3Policy = s3.put_bucket_policy(
    Bucket = bucketName,
    Policy = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSConfigBucketPermissionsCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": [
         "config.amazonaws.com"
        ]
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::%s"
    },
    {
      "Sid": " AWSConfigBucketDelivery",
      "Effect": "Allow",
      "Principal": {
        "Service": [
         "config.amazonaws.com"    
        ]
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::%s/*",
      "Condition": { 
        "StringEquals": { 
          "s3:x-amz-acl": "bucket-owner-full-control" 
        }
      }
    }
  ]
}   """ % (bucketName,bucketName)
)

##### Recurso AWS
rscSnsTopic = 'SNS Topic'

##### Criando o Topico SNS
snsTopic = sns.create_topic(
    Name = topicSnsName
)

##### Obtendo o request ID
RequestId = snsTopic['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(snsTopic,rscSnsTopic,RequestId)

##### Obtendo ARN do recurso
arnConfig = snsTopic['TopicArn']

##### Recurso AWS
rscIamRole = 'IAM Role'

##### Criando Role IAM
createIamRole = iam.create_role(
    RoleName = iamRoleName,
    AssumeRolePolicyDocument = """{
    	"Version": "2012-10-17", 
    	"Statement": [
        	{
        		"Action": "sts:AssumeRole", 
        		"Principal": {
            		"Service": "config.amazonaws.com"
        		}, 
        		"Effect": "Allow", 
        		"Sid": ""
        	}
    	]
	}"""
)

##### Obtendo o request ID
RequestId = createIamRole['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(createIamRole,rscIamRole,RequestId)

##### Obtendo ARN do recurso
arnIamRole = createIamRole['Role']['Arn']

##### Atachando Policy na Role
atcPolicyConfig = iam.attach_role_policy(
    RoleName = iamRoleName,
    PolicyArn = iamPolicyConfigARN
)

##### Checando atachmaneto do recurso
atcCheck(atcPolicyConfig,iamRoleName,iamPolicyConfigARN)

##### Atachando Policy na Role
atcPolicyS3 = iam.attach_role_policy(
    RoleName = iamRoleName,
    PolicyArn = iamPolicyS3ARN
)

##### Checando atachmaneto do recurso
atcCheck(atcPolicyS3,iamRoleName,iamPolicyS3ARN)

##### Aguardando replicacao da Role do S3
print "Aguardando replicacao de Policy do S3. (15s)"
time.sleep(15)

##### Recurso AWS
rscConfigConfRec = 'Config Configuration Recorder'

##### Configurando Configuration Recorder
configurationRecorder = config.put_configuration_recorder(
    ConfigurationRecorder = {
        'name': configurationRecorderName,
        'roleARN': arnIamRole,
        'recordingGroup': {
            'allSupported': True,
            'includeGlobalResourceTypes': True
        }
    }
)

##### Obtendo o request ID
RequestId = configurationRecorder['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(configurationRecorder,rscConfigConfRec,RequestId)

##### Recurso AWS
rscDeliveryChannel = 'Delivery Channel'

##### Criando trilha no CloudTrial
deliveryChannel = config.put_delivery_channel(
    DeliveryChannel={
        'name': deliveryChannelName,
        's3BucketName': bucketName,
        's3KeyPrefix': prefixName,
        'snsTopicARN': arnConfig,
        'configSnapshotDeliveryProperties': {
            'deliveryFrequency': 'One_Hour'
        }
    }
)

##### Obtendo o request ID
RequestId = deliveryChannel['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(deliveryChannel,rscDeliveryChannel,RequestId)

##### Recurso AWS
rscStartConfRec = 'Inicializar AWS Config'

##### Iniciando o Configuration Recorder
startConfigurationRecorder = config.start_configuration_recorder(
    ConfigurationRecorderName = configurationRecorderName
)

##### Obtendo o request ID
RequestId = startConfigurationRecorder['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(startConfigurationRecorder,rscStartConfRec,RequestId)