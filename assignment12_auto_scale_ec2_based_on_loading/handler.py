import os
import boto3
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# clients
cw = boto3.client('cloudwatch')
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# Environment variables (set these in Lambda configuration)
ELB_NAME = os.environ.get('ELB_NAME')  # e.g. "app/my-alb/1234567890abcdef"
METRIC_NAMESPACE = os.environ.get('METRIC_NAMESPACE', 'AWS/ApplicationELB')  # default for ALB
METRIC_NAME = os.environ.get('METRIC_NAME', 'RequestCount')  # or 'ActiveConnectionCount' for NLB, etc.
METRIC_DIMENSION_NAME = os.environ.get('METRIC_DIMENSION_NAME', 'LoadBalancer')  # for AWS/ApplicationELB
HIGH_THRESHOLD = float(os.environ.get('HIGH_THRESHOLD', '80'))  # percent or absolute depending on metric
LOW_THRESHOLD = float(os.environ.get('LOW_THRESHOLD', '20'))
# Interpret thresholds relative to "per-instance" request capacity when using RequestCount.
AGGREGATION = os.environ.get('AGGREGATION', 'Average')  # Average, Sum, Maximum
PERIOD_SECONDS = int(os.environ.get('PERIOD_SECONDS', '300'))  # 5 minutes
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

# If you want Lambda to create instances directly:
AMI_ID = os.environ.get('AMI_ID')  # e.g. "ami-0123456789abcdef0"
INSTANCE_TYPE = os.environ.get('INSTANCE_TYPE', 't3.micro')
KEY_NAME = os.environ.get('KEY_NAME')  # optional
SECURITY_GROUP_IDS = os.environ.get('SECURITY_GROUP_IDS')  # comma-separated ids
SUBNET_ID = os.environ.get('SUBNET_ID')  # subnet to launch into (optional)
MIN_INSTANCES = int(os.environ.get('MIN_INSTANCES', '1'))  # do not go below
MAX_INSTANCES = int(os.environ.get('MAX_INSTANCES', '5'))  # cap max
INSTANCE_TAG_KEY = os.environ.get('INSTANCE_TAG_KEY', 'AutoScaleManaged')
INSTANCE_TAG_VALUE = os.environ.get('INSTANCE_TAG_VALUE', 'true')

# Which instances to count/manage: filter by tag.
MANAGED_FILTERS = [{'Name': f'tag:{INSTANCE_TAG_KEY}', 'Values': [INSTANCE_TAG_VALUE]}]

def publish_sns(subject: str, message: str):
    if not SNS_TOPIC_ARN:
        logger.warning("SNS_TOPIC_ARN not configured; skipping notification.")
        return
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
        logger.info("SNS published: %s", subject)
    except ClientError as e:
        logger.exception("Failed to publish SNS: %s", e)

def get_metric_value():
    """
    Fetch metric from CloudWatch for the last PERIOD_SECONDS window.
    Returns the requested statistic value (float) or None.
    """
    end = datetime.utcnow()
    start = end - timedelta(seconds=PERIOD_SECONDS)
    dims = [{'Name': METRIC_DIMENSION_NAME, 'Value': ELB_NAME}]
    try:
        resp = cw.get_metric_statistics(
            Namespace=METRIC_NAMESPACE,
            MetricName=METRIC_NAME,
            Dimensions=dims,
            StartTime=start,
            EndTime=end,
            Period=PERIOD_SECONDS,
            Statistics=[AGGREGATION]
        )
        datapoints = resp.get('Datapoints', [])
        if not datapoints:
            logger.info("No datapoints returned for metric query.")
            return None
        # pick the latest datapoint by timestamp
        latest = max(datapoints, key=lambda d: d['Timestamp'])
        value = latest.get(AGGREGATION)
        logger.info("Metric fetched: %s=%s (timestamp=%s)", METRIC_NAME, value, latest.get('Timestamp'))
        return float(value)
    except ClientError:
        logger.exception("Error fetching metric")
        return None

def count_managed_instances():
    """Count running/stopped instances that match our tag filters (and are EC2-managed by this function)."""
    try:
        resp = ec2.describe_instances(Filters=MANAGED_FILTERS + [{'Name': 'instance-state-name', 'Values': ['pending','running','stopping','stopped']}])
        instances = []
        for r in resp.get('Reservations', []):
            for i in r.get('Instances', []):
                instances.append(i)
        logger.info("Found %d managed instances", len(instances))
        return instances
    except ClientError:
        logger.exception("Failed to describe instances")
        return []

def start_new_instance():
    """Start a single new EC2 instance, tagged so it is managed."""
    if not AMI_ID:
        raise RuntimeError("AMI_ID not configured; cannot launch instance.")
    sg_ids = [x.strip() for x in SECURITY_GROUP_IDS.split(',')] if SECURITY_GROUP_IDS else None
    launch_args = {
        'ImageId': AMI_ID,
        'InstanceType': INSTANCE_TYPE,
        'MinCount': 1,
        'MaxCount': 1,
        'TagSpecifications': [{
            'ResourceType': 'instance',
            'Tags': [{'Key': INSTANCE_TAG_KEY, 'Value': INSTANCE_TAG_VALUE}]
        }]
    }
    if sg_ids:
        launch_args['SecurityGroupIds'] = sg_ids
    if KEY_NAME:
        launch_args['KeyName'] = KEY_NAME
    if SUBNET_ID:
        launch_args['SubnetId'] = SUBNET_ID

    try:
        resp = ec2.run_instances(**launch_args)
        instance_id = resp['Instances'][0]['InstanceId']
        logger.info("Launched instance %s", instance_id)
        publish_sns("Scale Up: Launched EC2", f"Launched instance {instance_id} due to high load.")
        return instance_id
    except ClientError:
        logger.exception("Failed to launch instance")
        return None

def terminate_one_instance(instances):
    """
    Terminate one instance from the provided list (prefer stopped or oldest running).
    Instances is list of instance dicts from describe_instances.
    """
    # select candidate: prefer instances in 'stopped', then oldest 'running'
    stopped = [i for i in instances if i['State']['Name'] == 'stopped']
    if stopped:
        target = stopped[0]
    else:
        # pick oldest running (by LaunchTime)
        running = [i for i in instances if i['State']['Name'] == 'running']
        if not running:
            logger.info("No running instances to terminate.")
            return None
        target = min(running, key=lambda i: i['LaunchTime'])

    inst_id = target['InstanceId']
    try:
        ec2.terminate_instances(InstanceIds=[inst_id])
        logger.info("Terminated instance %s", inst_id)
        publish_sns("Scale Down: Terminated EC2", f"Terminated instance {inst_id} due to low load.")
        return inst_id
    except ClientError:
        logger.exception("Failed to terminate instance")
        return None

def lambda_handler(event, context):
    logger.info("Auto-scale Lambda started")
    metric_value = get_metric_value()
    if metric_value is None:
        logger.warning("Metric not available; exiting without action.")
        return {"status": "no_metric"}

    # You must decide what metric_value represents: percent or absolute.
    # This sample assumes metric is percent-like (0-100). If metric is RequestCount, you may need to normalize to per-instance rate.
    try:
        managed = count_managed_instances()
        current_count = len([i for i in managed if i['State']['Name'] in ('pending', 'running', 'stopping', 'stopped')])
        logger.info("Current managed instance count: %d", current_count)
    except Exception as e:
        logger.exception("Failed to count managed instances: %s", e)
        current_count = 0

    # Scaling decisions
    # Scale up
    if metric_value >= HIGH_THRESHOLD and current_count < MAX_INSTANCES:
        logger.info("High threshold exceeded: %s >= %s", metric_value, HIGH_THRESHOLD)
        launched = start_new_instance()
        return {"action": "scale_up", "launched": launched}

    # Scale down
    if metric_value <= LOW_THRESHOLD and current_count > MIN_INSTANCES:
        logger.info("Low threshold met: %s <= %s", metric_value, LOW_THRESHOLD)
        terminated = terminate_one_instance(managed)
        return {"action": "scale_down", "terminated": terminated}

    logger.info("No scaling action required. metric=%s thresholds=(%s,%s) count=%d", metric_value, LOW_THRESHOLD, HIGH_THRESHOLD, current_count)
    return {"action": "no_action", "metric": metric_value}
