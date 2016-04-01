import time
import boto3

s3 = boto3.client('s3')
cloudtrail = boto3.client('cloudtrail')

#################################################

## Nome do Bucket
bucketName = 'ctrailus-rdmb'

## Region do Bucket
regionName = 'us-west-1'

## Nome na Trilha do Cloudtrail
trailName = 'USTrail'


#################################################

##### Funcao para Checagem de criacao do recurso com Sucesso
def rscCheck(rscRtn,rsc,rscId):
        if rscRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s criado com sucesso, segue o ID do Request: %s" % (rsc,rscId)  
        else:
            print "Erro ao criar o recurso %s!" % rsc

#################################################

##### Recurso AWS
rscBkt = 'Bucket Cloudtrail'

bucketUsCTrail = s3.create_bucket(
    ACL = 'private',
    Bucket = bucketName,
    CreateBucketConfiguration = {
        'LocationConstraint': regionName
    },
)

##### Obtendo o request ID
RequestId = bucketUsCTrail['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(bucketUsCTrail,rscBkt,RequestId)

s3Policy = s3.put_bucket_policy(
    Bucket = bucketName,
    Policy = """{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSCloudTrailAclCheck20150319",
			"Effect": "Allow",
			"Principal": {
				"Service": "cloudtrail.amazonaws.com"
			},
			"Action": "s3:GetBucketAcl",
			"Resource": "arn:aws:s3:::%s"
		},
		{
			"Sid": "AWSCloudTrailWrite20150319",
			"Effect": "Allow",
			"Principal": {
				"Service": "cloudtrail.amazonaws.com"
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
}""" % (bucketName,bucketName)
)

##### Recurso AWS
rscCTrail = 'Trilha do Cloudtrail'

##### Criando trilha no CloudTrial
enableCTrail = cloudtrail.create_trail(
	Name = trailName,
    S3BucketName = bucketName,
    S3KeyPrefix = trailName,
    IncludeGlobalServiceEvents = True,
    IsMultiRegionTrail = True,
    EnableLogFileValidation = True
)

##### Obtendo o request ID
RequestId = enableCTrail['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(enableCTrail,rscCTrail,RequestId)

##### Obtendo ARN do recurso
arnCTrail = enableCTrail['TrailARN']

##### Recurso AWS
rscCTrailLogs = 'Habilitar logs no Cloudtrail'

##### Habilitando Logs no Cloudtrail
enableCtrailLogs = cloudtrail.start_logging(
    Name = arnCTrail
)

##### Obtendo o request ID
RequestId = enableCTrail['ResponseMetadata']['RequestId']

##### Checando criacao do recurso
rscCheck(enableCtrailLogs,rscCTrailLogs,RequestId)