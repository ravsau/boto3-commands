
## TODO: Change the format
## TODO: Add options to bypass naming if name already present


# most credit to the original: https://gist.github.com/brandond/6b4d22eaefbd66895f230f68f27ee586
# Don't pay too much attention to the names of the function. functions were copied from another script so the unexpected names (some have ansible and you may ask why is ansible there)
# Tag snapshots based on their associated AMI and volumes based on attached instance.

# format:
#    (AMI:db5|db5) /dev/sda1 (1/4)
#    (AMI:db5|db5) /dev/sdb (2/4)


# Best practice: create IAM user
# Simplest privilege to get it to work with reasonable security:  use predefined policy "ReadOnlyAccess" 
# and add your own custom policy that grants  "ec2:CreateTags" 


import copy
import logging
import os
import boto3

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))

ec2 = boto3.client('ec2')
logger = logging.getLogger(__name__)

def tag_snapshots():
    snapshots = {}

    for response in ec2.get_paginator('describe_snapshots').paginate(OwnerIds=['self']):
        snapshots.update([(snapshot['SnapshotId'], snapshot) for snapshot in response['Snapshots']])

    for image in ec2.describe_images(Owners=['self'])['Images']:
        tags = boto3_tag_list_to_ansible_dict(image.get('Tags', []))
        # to tag volumes, e.g., (1/3) (2/3) (3/3)
        devnum = 0
        numberofdevs=len(image['BlockDeviceMappings'])
        for device in image['BlockDeviceMappings']:
            if 'SnapshotId' in device['Ebs']:
                devnum += 1
                snapshot = snapshots[device['Ebs']['SnapshotId']]
                snapshot['Used'] = True
                cur_tags = boto3_tag_list_to_ansible_dict(snapshot.get('Tags', []))
                new_tags = copy.deepcopy(cur_tags)
                new_tags.update(tags)
                new_tags['ImageId'] = image['ImageId']
                # here's where to change formatting
                new_tags['Name'] = 'AMI:' + image['Name'] + ' ' + device['DeviceName'] + ' (' + str(devnum) + '/' + str(numberofdevs) + ')'
                if new_tags != cur_tags:
                    logger.info('{0}: Tags changed to {1}'.format(snapshot['SnapshotId'], new_tags))
                    ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=ansible_dict_to_boto3_tag_list(new_tags))

    for snapshot in snapshots.values():
        if 'Used' not in snapshot:
            cur_tags = boto3_tag_list_to_ansible_dict(snapshot.get('Tags', []))
            name = cur_tags.get('Name', snapshot['SnapshotId'])
            if not name.startswith('UNUSED'):
                logger.warning('{0} Unused!'.format(snapshot['SnapshotId']))
                cur_tags['Name'] = 'UNUSED ' + name
                ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=ansible_dict_to_boto3_tag_list(cur_tags))


def tag_volumes():
    volumes = {}
    for response in ec2.get_paginator('describe_volumes').paginate():
        volumes.update([(volume['VolumeId'], volume) for volume in response['Volumes']])

    for response in ec2.get_paginator('describe_instances').paginate():
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                tags = boto3_tag_list_to_ansible_dict(instance.get('Tags', []))
                # to tag the number volumes on an instance, e.g., (1/3) (2/3) (3/3)
                devnum = 0
                numberofdevs=len(instance['BlockDeviceMappings'])
                for device in instance['BlockDeviceMappings']:
                    devnum += 1
                    volume = volumes[device['Ebs']['VolumeId']]
                    volume['Used'] = True
                    cur_tags = boto3_tag_list_to_ansible_dict(volume.get('Tags', []))
                    new_tags = copy.deepcopy(cur_tags)
                    new_tags.update(tags)
                    # here's where to change formatting
                    new_tags['Name'] = tags['Name'] + ' ' + device['DeviceName'] + ' (' + str(devnum) + '/' + str(numberofdevs) + ')'
                    if new_tags != cur_tags:
                        logger.info('{0} Tags changed to {1}'.format(volume['VolumeId'], new_tags))
                        ec2.create_tags(Resources=[volume['VolumeId']], Tags=ansible_dict_to_boto3_tag_list(new_tags))

    for volume in volumes.values():
        if 'Used' not in volume:
            cur_tags = boto3_tag_list_to_ansible_dict(volume.get('Tags', []))
            name = cur_tags.get('Name', volume['VolumeId'])
            if not name.startswith('UNUSED'):
                logger.warning('{0} Unused!'.format(volume['VolumeId']))
                cur_tags['Name'] = 'UNUSED ' + name
                ec2.create_tags(Resources=[volume['VolumeId']], Tags=ansible_dict_to_boto3_tag_list(cur_tags))


def tag_everything():
    tag_snapshots()
    tag_volumes()


def boto3_tag_list_to_ansible_dict(tags_list):
    tags_dict = {}
    for tag in tags_list:
        if 'key' in tag and not tag['key'].startswith('aws:'):
            tags_dict[tag['key']] = tag['value']
        elif 'Key' in tag and not tag['Key'].startswith('aws:'):
            tags_dict[tag['Key']] = tag['Value']

    return tags_dict

def ansible_dict_to_boto3_tag_list(tags_dict):
    tags_list = []
    for k, v in tags_dict.items():
        tags_list.append({'Key': k, 'Value': v})

    return tags_list


def handler(event, context):
    tag_everything()


if __name__ == '__main__':
    tag_everything()
