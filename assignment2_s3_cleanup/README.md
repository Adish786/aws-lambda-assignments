S3 Log Cleaner Lambda

This AWS Lambda function automatically deletes objects in an S3 bucket that are older than a specified number of days. It helps manage storage costs and keep buckets clean.

📌 Features

Deletes objects older than a given retention period.
Retention period is configurable via environment variables.
Uses AWS boto3 SDK.
Supports pagination for large buckets.

🛠 Requirements
AWS Account with permission to use:
S3 (AmazonS3FullAccess or restricted permissions)
Lambda
CloudWatch (if scheduling cleanup automatically)
Python 3.9+ (runtime used in Lambda)
If testing locally:
pip install -r requirements.txt

requirements.txt:

boto3

⚙️ Setup Steps
1. Create an S3 Bucket

Go to the S3 Console.

Create or choose a bucket containing logs/files to manage.

2. Create a Lambda Function

Go to the Lambda Console → Create Function.

Runtime: Python 3.13 (or higher).

Execution Role: Attach policy AmazonS3FullAccess.

3. Configure Environment Variables

In the Lambda Console → Configuration → Environment Variables:

Key	Value	Description
BUCKET_NAME	your-s3-bucket-name	The target S3 bucket
RETENTION_DAYS	30 (default)	Number of days to retain objects
