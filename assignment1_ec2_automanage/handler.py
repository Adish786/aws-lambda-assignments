import boto3

def stop_ec2_instance(event, context):
    ec2 = boto3.client('ec2')
    instance_ids = ['i-033231fd0fca97167']  # replace with your instance ID
    ec2.stop_instances(InstanceIds=instance_ids)
    print('Stopped EC2 instance:', instance_ids)
    return {
        'statusCode': 200,
        'body': f'Successfully stopped EC2 instance: {instance_ids}'
    }

def start_ec2_instance(event, context):
    ec2 = boto3.client('ec2')
    instance_ids = ['i-033231fd0fca97167']  # replace with your instance ID
    ec2.start_instances(InstanceIds=instance_ids)
    print('Started EC2 instance:', instance_ids)
    return {
        'statusCode': 200,
        'body': f'Successfully started EC2 instance: {instance_ids}'
    }

def lambda_handler(event, context):
    # Determine which action to perform based on event input
    action = event.get('action', 'stop')  # default to stop if no action specified
    
    if action == 'start':
        return start_ec2_instance(event, context)
    elif action == 'stop':
        return stop_ec2_instance(event, context)
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid action. Use "start" or "stop".'
        }