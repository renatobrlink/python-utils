import boto3

s3 = boto3.client('s3')
cloudtrail = boto3.client('cloudtrail')

#################################################

## Nome do Bucket
bName = 'ctrailus-rdmb'

#################################################

bucketUsCTrail = s3.create_bucket(
    ACL = 'private',
    Bucket = bName,
    CreateBucketConfiguration={
        'LocationConstraint': 'us-west-1'
    },
)

s3Policy = s3.put_bucket_policy(
    Bucket = bName,
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
			"Resource": "arn:aws:s3:::ctrailus-rdmb"
		},
		{
			"Sid": "AWSCloudTrailWrite20150319",
			"Effect": "Allow",
			"Principal": {
				"Service": "cloudtrail.amazonaws.com"
			},
			"Action": "s3:PutObject",
			"Resource": "arn:aws:s3:::ctrailus-rdmb/*",
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}"""
)

enableCTrail = cloudtrail.create_trail(
    Name='USTrail',
    S3BucketName=bName,
    S3KeyPrefix='USTrail',
    IncludeGlobalServiceEvents=True,
    IsMultiRegionTrail=True,
    EnableLogFileValidation=True
)