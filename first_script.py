import time
import boto3

ec2 = boto3.client('ec2')

imageid = 'ami-08111162'

vpc_new = ec2.create_vpc(
	CidrBlock = '172.24.0.0/16'
	) 

vpcid = vpc_new['Vpc']['VpcId']
print "VPC criada com Sucesso, segue ID: %s" % vpcid

subnet_azA = ec2.create_subnet(
	CidrBlock = '172.24.24.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1a'
	) 

subnetidA = subnet_azA['Subnet']['SubnetId']
print "Subnet AZ A criada com Sucesso, segue ID: %s" % subnetidA

subnet_azE = ec2.create_subnet(
	CidrBlock = '172.24.25.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1e'
	) 

subnetidE = subnet_azE['Subnet']['SubnetId']
print "Subnet AZ E criada com Sucesso, segue ID: %s" % subnetidE

securityGroupSSH = ec2.create_security_group(
    GroupName = 'SG-VPC-SSH',
    Description = 'Acesso SSH',
    VpcId = vpcid
)

sgid = securityGroupSSH['GroupId']
print "SecurityGroup criado com Sucesso, segue ID: %s" % sgid

instanceazA = ec2.run_instances(
	ImageId = imageid,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetidA,
    SecurityGroupIds = [sgid]
	)

instanceazE = ec2.run_instances(
	ImageId = imageid,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetidE,
    SecurityGroupIds = [sgid]
	)

time.sleep(60)

instanceazAID = instanceazA['Instances']['InstanceID']
instanceazAIP = instanceazA['Instances']['PublicIpAddress']
print "Instancia da AZ A criada com Sucesso, segue ID: %s" % instanceazAID
print "IP da Instancia da AZ A: %s" % instanceazAIP

instanceazEID = instanceazE['Instances']['InstanceID']
instanceazEIP = instanceazE['Instances']['PublicIpAddress']
print "Instancia da AZ E criada com Sucesso, segue ID: %s" % instanceazEID
print "IP da Instancia da AZ E: %s" % instanceazEIP