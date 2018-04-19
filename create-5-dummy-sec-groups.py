import boto3

ec2 = boto3.resource('ec2')
ec2 = boto3.client('ec2')


for i  in range(5):
	response = ec2.create_security_group(
    Description='dummy-sg',
    GroupName=str(i)+"-sg-dummy"
)


