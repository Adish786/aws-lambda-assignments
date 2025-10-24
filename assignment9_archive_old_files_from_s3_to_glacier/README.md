
Steps to Implement
1. S3 Setup
Go to S3 → Create bucket (e.g., archive-demo-bucket).
Upload a mix of old and new files. (To simulate older files, adjust system date before uploading or use test files with older timestamps if available.)

2. IAM Role for Lambda
Go to IAM → Roles → Create Role.
Trusted entity: Lambda.
Attach policy:
AmazonS3FullAccess (demo; in production, restrict permissions to specific bucket + actions).
Name it: LambdaS3GlacierRole.

3. Lambda Function
Go to AWS Lambda → Create Function.
Runtime: Python 3.x.
Execution role: LambdaS3GlacierRole.
📌 Lambda handler (handler.py)

4. Testing
Deploy and manually trigger Lambda with test event (no special input needed).
Check CloudWatch Logs → should print archived file names.
Go to S3 → Bucket → Objects → verify older files’ Storage class = GLACIER.

