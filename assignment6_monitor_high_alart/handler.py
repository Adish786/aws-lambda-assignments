import boto3
import datetime
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
# NOTE: Billing metrics are always in 'us-east-1'
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
sns = boto3.client('sns')

# Environment variables
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')  # e.g., arn:aws:sns:eu-west-2:123456789012:aws-billing-alerts
COST_THRESHOLD = float(os.environ.get('COST_THRESHOLD', 50.0))  # Default to $50 if not set


def lambda_handler(event, context):
    """Check AWS billing and send SNS alert if cost exceeds threshold."""
    try:
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(days=1)

        logger.info(f"Checking billing data from {start_time} to {end_time}...")

        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/Billing',
            MetricName='EstimatedCharges',
            Dimensions=[{'Name': 'Currency', 'Value': 'USD'}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Maximum']
        )

        datapoints = response.get('Datapoints', [])
        if not datapoints:
            logger.warning("No billing data found in CloudWatch.")
            return {"statusCode": 204, "message": "No billing data found."}

        # Extract latest billing datapoint
        latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
        current_cost = latest['Maximum']
        logger.info(f"Current AWS billing amount: ${current_cost:.2f}")

        # Compare with threshold
        if current_cost > COST_THRESHOLD:
            message = (
                f"🚨 *AWS Billing Alert*\n\n"
                f"Your AWS cost is **${current_cost:.2f}**, exceeding the threshold of ${COST_THRESHOLD:.2f}.\n"
                f"Time: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )

            if SNS_TOPIC_ARN:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="🚨 AWS Billing Alert",
                    Message=message
                )
                logger.info(f"SNS alert sent successfully to topic: {SNS_TOPIC_ARN}")
            else:
                logger.error("SNS_TOPIC_ARN is not set. Cannot send notification.")

        else:
            logger.info(f"Billing within threshold (${COST_THRESHOLD:.2f}). No alert sent.")

        return {
            "statusCode": 200,
            "current_cost": current_cost,
            "threshold": COST_THRESHOLD
        }

    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS API error: {e}")
        return {"statusCode": 500, "error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"statusCode": 500, "error": str(e)}
