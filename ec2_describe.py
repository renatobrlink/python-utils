import boto3
ec2 = boto3.client('ec2')
instances = ec2.describe_instances(Filters=[
        {
            'Name': 'instance-id',
            'Values': [
                'i-07508e2445a6b797f',
            ]
        },
    ])

#for instance in instances['Reservations']:
#	for instanceId in instance['Instances']:
#	    variavel = instanceId['InstanceId']
ec2_teste = instances['Reservations'][0]['Instances'][0]['InstanceId']
print ec2_teste
