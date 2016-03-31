import time
import boto3

##### Iniciando Libs
ec2 = boto3.client('ec2')
rscec2 = boto3.resource('ec2')

##### Setando Variaveis nao Hardcoded

## Nome da Tag do Enviroment
tagEnv = 'Shyriu'

## Nome da Imagem da instancia
imageId = 'ami-08111162'

## Nome do SecurityGroup
sgName = 'SG-VPC-SSH'

## Nome da AZ 1 a ser utilizada
az1 = 'us-east-1a'

## Cidr Block a ser usado no AZ 1
cidAz1 = '172.24.24.0/24'

## Nome da AZ 1 a ser utilizada
az2 = 'us-east-1e'

## Cidr Block a ser usado no AZ 2
cidAz2 = '172.24.25.0/24'

##### Codigo inicial

##### Funcao para Checagem de criacao de servico com Sucesso
def rscCheck(rscRtn,rsc,rscId):
        if rscRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s criado com sucesso, segue o ID: %s" % (rsc,rscId)  
        else:
            print "Erro ao criar o recurso %s!" % rsc

##### Funcao para Checagem de atachamento de servico com Sucesso
def atcCheck(atcRtn,rsc,rscAtc):
        if atcRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s atachado com sucesso ao recurso %s!" % (rscAtc,rsc)  
        else:
            print "Erro ao atachar o recurso %s!" % rscAtc


##### Funcao para Tagueamento de recursos.
def tagRsc(rscId):
    rscTag = ec2.create_tags(
        Resources=[rscId],
        Tags=[
            {
                'Key': 'Name',
                'Value': tagEnv
            },
            ]
        )
    return rscTag;

##### Fincao para Checagem de Tag setada no Servico
def tagCheck(tagRtn,rsc):
        if tagRtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Tag no recurso %s criada com sucesso!" % rsc
        else:
            print "Erro ao criar a tag no recurso %s!" % rsc

#############################################################

##### Servico AWS
rscVpc = 'VPC'

##### Criando uma VPC nova.
vpc = ec2.create_vpc(
	CidrBlock = '172.24.0.0/16'
	) 

##### Obtendo o VPC ID
vpcId = vpc['Vpc']['VpcId']

##### Checando criacao do recurso
rscCheck(vpc,rscVpc,vpcId)
    
##### Setando Tag na VPC Criada
rscTag = tagRsc(vpcId)

##### Checando Tag
tagCheck(rscTag,rscVpc)

#############################################################

##### Servico AWS
rscIg = 'Insternet Gateway'

##### Criando um Internet Gateway novo.
ig = ec2.create_internet_gateway()

##### Obtendo o VPC ID
igId = ig['InternetGateway']['InternetGatewayId']

##### Checando criacao do recurso
rscCheck(ig,rscIg,igId)
    
##### Setando Tag na VPC Criada
rscTag = tagRsc(igId)

##### Checando Tag
tagCheck(rscTag,rscIg)

##### Atachar o IG a VPC
atcIg = ec2.attach_internet_gateway(
    InternetGatewayId=igId,
    VpcId=vpcId
)

##### Checando atachamento do recurso
atcCheck(atcIg,rscVpc,rscIg)

#############################################################

##### Servico AWS
rscSub1 = 'Subnet A'

##### Criando a Subnet na AZ 1
subnetAz1 = ec2.create_subnet(
	CidrBlock = cidAz1,
	VpcId = vpcId,
	AvailabilityZone = az1
	) 

##### Obtendo ID da Subnet
subnetId1 = subnetAz1['Subnet']['SubnetId']

##### Checando criacao do recurso
rscCheck(subnetAz1,rscSub1,subnetId1)

##### Setando Tag na VPC Criada
rscTag = tagRsc(subnetId1)

##### Checando Tag
tagCheck(rscTag,rscSub1)

#############################################################

##### Servico AWS
rscSub2 = 'Subnet E'

##### Criando a Subnet na AZ 2
subnetAz2 = ec2.create_subnet(
    CidrBlock = cidAz2,
    VpcId = vpcId,
    AvailabilityZone = az2
    ) 

##### Obtendo ID da Subnet
subnetId2 = subnetAz2['Subnet']['SubnetId']

##### Checando criacao do recurso
rscCheck(subnetAz2,rscSub2,subnetId2)

##### Setando Tag na VPC Criada
rscTag = tagRsc(subnetId2)

##### Checando Tag
tagCheck(rscTag,rscSub2)

#############################################################

##### Servico AWS
rscSg = 'SecurityGroup'

##### Criando o Security Group
sgVpcSSH = ec2.create_security_group(
    GroupName = sgName,
    Description = 'Acesso SSH',
    VpcId = vpcId
)

##### Obtendo ID do Security Group
sgId = sgVpcSSH['GroupId']

##### Obtendo dados do SG
sg = rscec2.SecurityGroup(sgId)

##### Autorizando acesso
sgAuthorize = sg.authorize_ingress(
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'UserIdGroupPairs': [
                {
                    'GroupId': sgId,
                    'VpcId': vpcId
                },
            ],
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                },
            ]
        },
    ]
)

##### Checando criacao do recurso
rscCheck(sgVpcSSH,rscSg,sgId)

##### Setando Tag na VPC Criada
rscTag = tagRsc(sgId)

##### Checando Tag
tagCheck(rscTag,rscSg)

#############################################################

##### Servico AWS
rscIn1 = 'Instacia AZ A'
rscIn2 = 'Instacia AZ E'

##### Criando instancia AZ 1
instanceAz1 = ec2.run_instances(
	ImageId = imageId,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetId1,
    SecurityGroupIds = [sgId]
	)

##### Criando instancia AZ 2
instanceAz2 = ec2.run_instances(
	ImageId = imageId,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetId2,
    SecurityGroupIds = [sgId]
	)

##### Estado da instancia
state = 'pending'

##### Contador
count = 0

##### Iniciando o While para checagem de estado do servidor.
while state != 'running' and count <= 30:
	print "Aguardando instancias serem iniciadas, tentativa numero %d. (30s)" % count
	instance = ec2.describe_instances(
	Filters=[
        {
            'Name': 'instance-id',
            'Values': [instanceAz1['Instances'][0]['InstanceId']
            ]
        },
    ])
	time.sleep(30)
	if instance['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':
		state = 'running'
	else:
		count = count + 1


##### Instancia AZ 1
##### Obtendo ID da instancia 
InstanceAz1Id = instanceAz1['Instances'][0]['InstanceId']

##### Checando criacao do recurso
rscCheck(instanceAz1,rscIn1,InstanceAz1Id)

##### Setando Tag na VPC Criada
rscTag = tagRsc(InstanceAz1Id)

##### Checando Tag
tagCheck(rscTag,rscIn1)

##### Servico AWS
rscEipAz1 = 'EIP Instacia AZ A'

##### Alocando EIP para utilizar
eipAz1 = ec2.allocate_address(
    Domain='vpc'
)

##### Obtendo o PuclibIP Instancia 1
publicIp1 = eipAz1['PublicIp']

##### Obtendo o ID do PublicIP da Instancia 1
eipId1 = eipAz1['AllocationId']

##### Checando criacao do recurso
rscCheck(eipAz1,rscEipAz1,eipId1)

##### Associando o IP para a Instancia 1
associateIp1 = ec2.associate_address(
    InstanceId=InstanceAz1Id,
    PublicIp=publicIp1
#    AllocationId=eipId1
)

##### Checando atachmaneto do recurso
atcCheck(associateIp1,rscIn1,rscEipAz1)

##### Exibindo o IP na AZ 1 e atachado a instancia AZ 1
print "Recurso %s possui o IP: %s" % (rscEipAz1,publicIp1)
   
##### Instancia AZ 2
##### Obtendo ID da instancia 
instanceAz2Id = instanceAz2['Instances'][0]['InstanceId']

##### Checando criacao do recurso
rscCheck(instanceAz2,rscIn2,instanceAz2Id)

##### Setando Tag na VPC Criada
rscTag = tagRsc(instanceAz2Id)

##### Checando Tag
tagCheck(rscTag,rscIn2)

##### Servico AWS
rscIp2 = 'EIP Instacia AZ E'

##### Alocando EIP para utilizar
eipAz2 = ec2.allocate_address(
    Domain='vpc'
)

##### Obtendo o PuclibIP Instancia 2
publicipE = eipAz2['PublicIp']

##### Obtendo o ID do PublicIP da Instancia 2
eipidE = eipAz2['AllocationId']

##### Checando criacao do recurso
rscCheck(eipAz2,rscIp2,eipidE)

##### Associando o IP para a Instancia 2
associateipE = ec2.associate_address(
    InstanceId=instanceAz2Id,
    PublicIp=publicipE
#    AllocationId=eipId1
)

##### Checando criacao do recurso
atcCheck(associateipE,rscIn2,rscIp2)

##### Exibindo o IP na AZ 2 e atachado a instancia AZ 2
print "Recurso %s possui o IP: %s" % (rscIp2,publicipE)