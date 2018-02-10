
import boto3

client=boto3.client('ec2')



response=client.describe_instances()


for reservation in response["Reservations"]:

	for instance in reservation["Instances"]:

        	print(instance["InstanceId"] + "stopping")

        	id=[instance["InstanceId"]]

        	client.stop_instances(InstanceIds=id)





