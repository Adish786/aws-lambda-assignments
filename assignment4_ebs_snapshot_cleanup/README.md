# AWS Lambda EBS Snapshot Automation

This AWS Lambda function automates the process of creating snapshots for a specified EBS volume and cleaning up snapshots older than a defined retention period. It helps maintain backups while managing storage costs by deleting outdated snapshots.

## Features

- Creates a snapshot of the specified EBS volume.
- Deletes snapshots older than the configured retention period.
- Logs created and deleted snapshot details.
- Can be triggered manually or via scheduled events (e.g., EventBridge).

## Prerequisites

- AWS account with appropriate IAM permissions.
- EC2 volume ID to back up.
- AWS Lambda execution role with permissions:
  - `ec2:CreateSnapshot`
  - `ec2:DeleteSnapshot`
  - `ec2:DescribeSnapshots`

## Lambda Function Code

The function code (Python 3.x) is as follows:

