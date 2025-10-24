import json
import boto3
import os
from datetime import datetime

sns = boto3.client('sns')

# Hardcode SNS topic ARN for local testing (only for test — remove later)
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:eu-west-2:975050024946:dynamodb-update-alerts-adish")

def lambda_handler(event=None, context=None):
    # Sample DynamoDB MODIFY event
    if event is None or 'Records' not in event:
        event = {
            "Records": [
                {
                    "eventID": "1",
                    "eventName": "MODIFY",
                    "eventVersion": "1.1",
                    "eventSource": "aws:dynamodb",
                    "awsRegion": "eu-west-2",
                    "dynamodb": {
                        "Keys": {"UserId": {"S": "101"}},
                        "OldImage": {
                            "UserId": {"S": "101"},
                            "Status": {"S": "Pending"},
                            "Score": {"N": "80"}
                        },
                        "NewImage": {
                            "UserId": {"S": "101"},
                            "Status": {"S": "Approved"},
                            "Score": {"N": "90"}
                        },
                        "StreamViewType": "NEW_AND_OLD_IMAGES",
                        "SequenceNumber": "111",
                        "SizeBytes": 26
                    },
                    "eventSourceARN": "arn:aws:dynamodb:eu-west-2:123456789012:table/MyDynamoDBTable/stream/2025-10-19T10:00:00.000"
                }
            ]
        }

    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        event_name = record['eventName']  # INSERT, MODIFY, REMOVE
        table_name = record['eventSourceARN'].split('/')[1]

        # Only handle updates (MODIFY)
        if event_name == 'MODIFY':
            old_image = record['dynamodb'].get('OldImage', {})
            new_image = record['dynamodb'].get('NewImage', {})

            # Convert DynamoDB JSON to readable format
            old_item = {k: list(v.values())[0] for k, v in old_image.items()}
            new_item = {k: list(v.values())[0] for k, v in new_image.items()}

            changed_fields = []
            for key in new_item.keys():
                old_val = old_item.get(key)
                new_val = new_item.get(key)
                if old_val != new_val:
                    changed_fields.append(f"{key}: '{old_val}' → '{new_val}'")

            # Construct message
            message = (
                f"🔔 *DynamoDB Item Updated Alert*\n"
                f"Table: {table_name}\n"
                f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"Changes:\n" + "\n".join(changed_fields)
            )

            print("Sending SNS notification...")
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"🔔 DynamoDB Update in {table_name}",
                Message=message
            )
            print("SNS alert sent successfully.")

        else:
            print(f"Ignored event type: {event_name}")

    return {"statusCode": 200, "message": "Processed successfully"}

# For local test execution
if __name__ == "__main__":
    lambda_handler()
