import time
import boto3

ec2 = boto3.client('ec2')
rscec2 = boto3.resource('ec2')

#### Setando Variaveis
imageid = 'ami-08111162'
tagEnv = 'Saori'
sgname = 'SG-VPC-SSH'

##### Codigo inicial

##### Funcao para Checagem de criacao de servico com Sucesso
def rsccheck(rscrtn,rsc,rscid):
        if rscrtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s criado com sucesso, segue o ID: %s" % (rsc,rscid)  
        else:
            print "Erro ao criar o recurso %s!" % rsc

##### Funcao para Checagem de atachamento de servico com Sucesso
def atccheck(atcrtn,rsc,rscatc):
        if atcrtn['ResponseMetadata']['HTTPStatusCode'] == 200:
            print "Recurso %s atachado com sucesso ao recurso %s" % (rscatc,rsc)  
        else:
            print "Erro ao atachar o recurso %s!" % rscatc


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
rscvpc = 'VPC'

##### Criando uma VPC nova.
vpc_new = ec2.create_vpc(
	CidrBlock = '172.24.0.0/16'
	) 

##### Obtendo o VPC ID
vpcid = vpc_new['Vpc']['VpcId']

##### Checando criacao do recurso
rsccheck(vpc_new,rscvpc,vpcid)
    
##### Setando Tag na VPC Criada
rsctag = tagrsc(vpcid)

##### Checando Tag
tagcheck(rsctag,rscvpc)

#############################################################

##### Servico AWS
rscig = 'Insternet Gateway'

##### Criando um Internet Gateway novo.
ig_new = ec2.create_internet_gateway()

##### Obtendo o VPC ID
igid = ig_new['InternetGateway']['InternetGatewayId']

##### Checando criacao do recurso
rsccheck(ig_new,rscig,igid)
    
##### Setando Tag na VPC Criada
rsctag = tagrsc(igid)

##### Checando Tag
tagcheck(rsctag,rscig)

##### Atachar o IG a VPC
attach_ig = ec2.attach_internet_gateway(
    InternetGatewayId=igid,
    VpcId=vpcid
)

##### Checando atachamento do recurso
atccheck(attach_ig,rscvpc,rscig)

#############################################################

##### Servico AWS
rscsubA = 'SubnetA'

##### Criando a Subnet na AZ A
subnet_azA = ec2.create_subnet(
	CidrBlock = '172.24.24.0/24',
	VpcId = vpcid,
	AvailabilityZone = 'us-east-1a'
	) 

##### Obtendo ID da Subnet
subnetidA = subnet_azA['Subnet']['SubnetId']

##### Checando criacao do recurso
rsccheck(subnet_azA,rscsubA,subnetidA)

##### Setando Tag na VPC Criada
rsctag = tagrsc(subnetidA)

##### Checando Tag
tagcheck(rsctag,rscsubA)

#############################################################

##### Servico AWS
rscsubE = 'SubnetE'

##### Criando a Subnet na AZ E
subnet_azE = ec2.create_subnet(
    CidrBlock = '172.24.25.0/24',
    VpcId = vpcid,
    AvailabilityZone = 'us-east-1e'
    ) 

##### Obtendo ID da Subnet
subnetidE = subnet_azE['Subnet']['SubnetId']

##### Checando criacao do recurso
rsccheck(subnet_azE,rscsubE,subnetidE)

##### Setando Tag na VPC Criada
rsctag = tagrsc(subnetidE)

##### Checando Tag
tagcheck(rsctag,rscsubE)

#############################################################

##### Servico AWS
rscsg = 'SecurityGroup'

##### Criando o Security Group
securityGroupSSH = ec2.create_security_group(
    GroupName = sgname,
    Description = 'Acesso SSH',
    VpcId = vpcid
)

##### Obtendo ID do Security Group
sgid = securityGroupSSH['GroupId']

##### Obtendo dados do SG
sg = rscec2.SecurityGroup(sgid)

##### Autorizando acesso
sgauthorize = sg.authorize_ingress(
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'UserIdGroupPairs': [
                {
                    'GroupId': sgid,
                    'VpcId': vpcid
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
rsccheck(securityGroupSSH,rscsg,sgid)

##### Setando Tag na VPC Criada
rsctag = tagrsc(sgid)

##### Checando Tag
tagcheck(rsctag,rscsg)

#############################################################

##### Servico AWS
rscinA = 'Instacia AZ A'
rscinE = 'Instacia AZ E'

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
rsccheck(instanceazA,rscinA,instanceazAID)

##### Setando Tag na VPC Criada
rsctag = tagrsc(instanceazAID)

##### Checando Tag
tagcheck(rsctag,rscinA)

##### Servico AWS
rsceipA = 'EIP Instacia AZ A'

##### Alocando EIP para utilizar
eipazA = ec2.allocate_address(
    Domain='vpc'
)

##### Obtendo o PuclibIP Instancia A
publicipA = eipazA['PublicIp']

##### Obtendo o ID do PublicIP da Instancia A
eipidA = eipazA['AllocationId']

##### Checando criacao do recurso
rsccheck(eipazA,rsceipA,eipidA)

##### Associando o IP para a Instancia A
associateipA = ec2.associate_address(
    InstanceId=instanceazAID,
    PublicIp=publicipA
#    AllocationId=eipidA
)

##### Checando atachmaneto do recurso
atccheck(associateipA,rscinA,rsceipA)

##### Exibindo o IP na AZ A e atachado a instancia AZ A
print "Recurso %s possui o IP: %s" % (rsceipA,publicipA)
   
##### Instancia AZ E
##### Obtendo ID da instancia 
instanceazEID = instanceazE['Instances'][0]['InstanceId']

##### Checando criacao do recurso
rsccheck(instanceazE,rscinE,instanceazEID)

##### Setando Tag na VPC Criada
rsctag = tagrsc(instanceazEID)

##### Checando Tag
tagcheck(rsctag,rscinE)

##### Servico AWS
rsceipE = 'EIP Instacia AZ E'

##### Alocando EIP para utilizar
eipazE = ec2.allocate_address(
    Domain='vpc'
)

##### Obtendo o PuclibIP Instancia E
publicipE = eipazE['PublicIp']

##### Obtendo o ID do PublicIP da Instancia E
eipidE = eipazE['AllocationId']

##### Checando criacao do recurso
rsccheck(eipazE,rsceipE,eipidE)

##### Associando o IP para a Instancia A
associateipE = ec2.associate_address(
    InstanceId=instanceazEID,
    PublicIp=publicipE
#    AllocationId=eipidA
)

##### Checando criacao do recurso
atccheck(associateipE,rscinE,rsceipE)

##### Exibindo o IP na AZ E e atachado a instancia AZ E
print "Recurso %s possui o IP: %s" % (rsceipE,publicipE)