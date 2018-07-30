#!/usr/bin/python

import boto3
import sys
import os
import random
import time

client = boto3.client('ec2')


ImageId=""
InstanceType= ""

VpcId= ""

SubnetId=""

KeyName=""

# change this later to accomodate more than one SG
GroupId=""

InstanceId= sys.argv[1]


def createAmi(InstanceId):
    response = client.create_image(

    Description="Clone-of-"+InstanceId,

    InstanceId=InstanceId,
    Name=InstanceId+'-clone'+str(random.randint(1,100)),
    NoReboot=True
)
    ImageId=response["ImageId"]
    status=""
    while status!="available":
        response=client.describe_images(ImageIds=[ImageId])
        status=response["Images"][0]["State"]
        print ("AMI  Status: "+status)
        time.sleep(200)

    print("Image Created!")
    return ImageId









def runClone(ImageId):
    details= client.describe_instances(InstanceIds=[InstanceId])
    InstanceType= details["Reservations"][0]["Instances"][0]["InstanceType"]

    VpcId= details["Reservations"][0]["Instances"][0]["VpcId"]

    SubnetId=details["Reservations"][0]["Instances"][0]["SubnetId"]

    # change this later to accomodate more than one SG
    GroupId=details["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]


    KeyName= details["Reservations"][0]["Instances"][0]["KeyName"]

    #response=client.run_instances(ImageId=ImageId , SecurityGroupIds=[GroupId] ,SubnetId=SubnetId , InstanceType=InstanceType , KeyName=KeyName, MinCount=1, MaxCount=1)
    response=client.run_instances(ImageId=ImageId , InstanceType=InstanceType , SecurityGroupIds=[GroupId],MinCount=1, MaxCount=1)
    print("Your Cloned Instance Id is:  "+response["Instances"][0]["InstanceId"] )

    newInstanceId=response["Instances"][0]["InstanceId"]
    client.create_tags(
    Resources=[newInstanceId],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'Clone'
        }
    ]
)




print("Starting...")
ImageId=createAmi(InstanceId)
print("Extracting Details...")

runClone(ImageId)
