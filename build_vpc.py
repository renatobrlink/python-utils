import time
import boto3

ec2 = boto3.client('ec2')

#### Setando Variaveis

imageid = 'ami-08111162'
tagEnv = 'Yoga'

##### Codigo inicial

##### Funcao para Checagem de criacao de servico com Sucesso
def rsccheck(rscrtn,rsc,rscid):
        if rscrtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s criado com sucesso, segue o ID: %s" % (rsc,rscid)  
        else:
            print "Erro ao criar o recurso %s!" % rsc

##### Funcao para Tagueamento de recursos.
def tagrsc(rscid):
    rsctag = ec2.create_tags(
        Resources=[rscid],
        Tags=[
            {
                'Key': 'Name',
                'Value': tagEnv
            },
            ]
        )
    return rsctag;

##### Fincao para Checagem de Tag setada no Servico
def tagcheck(tagrtn,rsc):
        if tagrtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Tag no recurso %s criada com sucesso!" % rsc
        else:
            print "Erro ao criar a tag no recurso %s!" % rsc

#############################################################

##### Servico AWS
rsc = 'VPC'

##### Criando uma VPC nova.
vpc_new = ec2.create_vpc(
	CidrBlock = '172.24.0.0/16'
	) 

##### Obtendo o VPC ID
vpcid = vpc_new['Vpc']['VpcId']

##### Checando criacao do recurso
rsccheck(vpc_new,rsc,vpcid)
    
##### Setando Tag na VPC Criada
rsctag = tagrsc(vpcid)

##### Checando Tag
tagcheck(rsctag,rsc)

#############################################################

##### Servico AWS
rsc = 'SubnetA'

##### Criando a Subnet na AZ A
subnet_azA = ec2.create_subnet(
	CidrBlock = '172.24.24.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1a'
	) 

##### Obtendo ID da Subnet
subnetidA = subnet_azA['Subnet']['SubnetId']

##### Checando criacao do recurso
rsccheck(subnet_azA,rsc,subnetidA)

##### Setando Tag na VPC Criada
rsctag = tagrsc(subnetidA)

##### Checando Tag
tagcheck(rsctag,rsc)

#############################################################

##### Servico AWS
rsc = 'SubnetE'

##### Criando a Subnet na AZ E
subnet_azE = ec2.create_subnet(
    CidrBlock = '172.24.25.0/24',
    VpcId = vpcid,
    AvailabilityZone = 'us-east-1e'
    ) 

##### Obtendo ID da Subnet
subnetidE = subnet_azE['Subnet']['SubnetId']

##### Checando criacao do recurso
rsccheck(subnet_azE,rsc,subnetidE)

##### Setando Tag na VPC Criada
rsctag = tagrsc(subnetidE)

##### Checando Tag
tagcheck(rsctag,rsc)

#############################################################

##### Servico AWS
rsc = 'SecurityGroup'

##### Criando o Security Group
securityGroupSSH = ec2.create_security_group(
    GroupName = 'SG-VPC-SSH',
    Description = 'Acesso SSH',
    VpcId = vpcid
)

##### Obtendo ID do Security Group
sgid = securityGroupSSH['GroupId']

##### Checando criacao do recurso
rsccheck(securityGroupSSH,rsc,sgid)

##### Setando Tag na VPC Criada
rsctag = tagrsc(sgid)

##### Checando Tag
tagcheck(rsctag,rsc)

#############################################################

##### Servico AWS
rscA = 'Instacia AZ A'
rscE = 'Instacia AZ E'

##### Criando instancia Az A
instanceazA = ec2.run_instances(
	ImageId = imageid,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetidA,
    SecurityGroupIds = [sgid]
	)

##### Criando instancia Az E
instanceazE = ec2.run_instances(
	ImageId = imageid,
	MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    SubnetId = subnetidE,
    SecurityGroupIds = [sgid]
	)

##### Estado da instancia
state = 'pending'

##### Contador
count = 0

##### Iniciando o While para checagem de estado do servidor.
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

##### Instancia AZ A
##### Obtendo ID da instancia 
instanceazAID = instanceazA['Instances'][0]['InstanceId']

##### Checando criacao do recurso
rsccheck(instanceazA,rscA,instanceazAID)

##### Setando Tag na VPC Criada
rsctag = tagrsc(instanceazAID)

##### Checando Tag
tagcheck(rsctag,rscA)
   
##### Instancia AZ E
##### Obtendo ID da instancia 
instanceazEID = instanceazE['Instances'][0]['InstanceId']

##### Checando criacao do recurso
rsccheck(instanceazE,rscE,instanceazEID)

##### Setando Tag na VPC Criada
rsctag = tagrsc(instanceazEID)

##### Checando Tag
tagcheck(rsctag,rscE)


#instanceazAIP = instanceazA['Instances'][0]['PublicIpAddress']
#print "IP da Instancia da AZ A: %s" % instanceazAIP

#instanceazEIP = instanceazE['Instances'][0]['PublicIpAddress']
#print "IP da Instancia da AZ E: %s" % instanceazEIP