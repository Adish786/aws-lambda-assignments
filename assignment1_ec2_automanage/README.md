Automate-Start-Stop-EC2-Instances

import boto3

def lambda_handler(event, context): ec2 = boto3.client('ec2') instance_ids = ['i-033231fd0fca97167'] # replace with your instance ID ec2.stop_instances(InstanceIds=instance_ids) print('Stopped EC2 instance:', instance_ids)

================================================= 

import boto3

def lambda_handler(event, context): ec2 = boto3.client('ec2') instance_ids = ['i-033231fd0fca97167'] # replace with your instance ID ec2.start_instances(InstanceIds=instance_ids) print('Started EC2 instance:', instance_ids)
