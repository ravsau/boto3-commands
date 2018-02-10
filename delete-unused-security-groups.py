import boto3

ec2 = boto3.resource('ec2')
ec2 = boto3.client('ec2')


response = ec2.describe_security_groups()


for i in response["SecurityGroups"]:
    id= i["GroupId"]
    print ( i["GroupId"])
    try:
        ec2.delete_security_group(GroupId=id)
    except:
        print ("dependent")



