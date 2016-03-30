import time
import boto3

#### Setando Variaveis

imageid = 'ami-08111162'
tagEnv = 'Shyriu'

##### Codigo inicial

ec2 = boto3.client('ec2')

vpc_new = ec2.create_vpc(
	CidrBlock = '172.24.0.0/16'
	) 

vpcid = vpc_new['Vpc']['VpcId']
print "VPC criada com Sucesso, segue ID: %s" % vpcid

vpctag = ec2.create_tags(
    Resources=[vpcid],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'VPC'
if vpctag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

subnet_azA = ec2.create_subnet(
	CidrBlock = '172.24.24.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1a'
	) 

subnetidA = subnet_azA['Subnet']['SubnetId']
print "Subnet AZ A criada com Sucesso, segue ID: %s" % subnetidA

subnetAtag = ec2.create_tags(
    Resources=[subnetidA],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'subnetA'
if subnetAtag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

subnet_azE = ec2.create_subnet(
	CidrBlock = '172.24.25.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1e'
	) 

subnetidE = subnet_azE['Subnet']['SubnetId']
print "Subnet AZ E criada com Sucesso, segue ID: %s" % subnetidE

subnetEtag = ec2.create_tags(
    Resources=[subnetidE],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'subnetE'
if subnetEtag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

securityGroupSSH = ec2.create_security_group(
    GroupName = 'SG-VPC-SSH',
    Description = 'Acesso SSH',
    VpcId = vpcid
)

sgid = securityGroupSSH['GroupId']
print "SecurityGroup criado com Sucesso, segue ID: %s" % sgid

sgtag = ec2.create_tags(
    Resources=[sgid],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'SecurityGroup'
if sgtag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

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

# Iniciando o While
state = 'pending'
count = 0

while state != 'running' and count <= 30:
	print "Aguardando instancia ser iniciada tentativa numero %d. (30s)" % count
	instance = ec2.describe_instances(
	Filters=[
        {
            'Name': 'instance-id',
            'Values': [instanceazA['Instances'][0]['InstanceId']
            ]
        },
    ])
	time.sleep(30)
	if instance['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':
		state = 'running'
	else:
		count = count + 1
   
instanceazAID = instanceazA['Instances'][0]['InstanceId']

instanceAtag = ec2.create_tags(
    Resources=[instanceazAID],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'Instancia A'
if instanceAtag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

#instanceazAIP = instanceazA['Instances'][0]['PublicIpAddress']
print "Instancia da AZ A criada com Sucesso, segue ID: %s" % instanceazAID
#print "IP da Instancia da AZ A: %s" % instanceazAIP

instanceazEID = instanceazE['Instances'][0]['InstanceId']

instanceEtag = ec2.create_tags(
    Resources=[instanceazEID],
    Tags=[
        {
            'Key': 'Name',
            'Value': tagEnv
        },
    ]
)

awssrv = 'Instancia E'
if instanceEtag['ResponseMetadata']['HTTPStatusCode'] == 200:
	print "Tag no service %s criada com sucesso!" % awssrv
else:
	print "Erro ao criar a tag no servico %s!" % awssrv

#instanceazEIP = instanceazE['Instances'][0]['PublicIpAddress']
print "Instancia da AZ E criada com Sucesso, segue ID: %s" % instanceazEID
#print "IP da Instancia da AZ E: %s" % instanceazEIP