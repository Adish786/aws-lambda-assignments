
Steps to Implement
1. SNS Setup
Go to Amazon SNS → Topics → Create Topic.
Type: Standard
Name: ELB5xxErrorAlertTopic
Create a subscription:
Protocol: Email / SMS
Endpoint: your email address or phone number
Confirm subscription from your inbox or phone.

2. IAM Role for Lambda
Go to IAM → Roles → Create Role.
Trusted entity: Lambda.
Attach the following policies:
CloudWatchReadOnlyAccess
AmazonSNSFullAccess
Name the role: LambdaELB5xxMonitorRole.

3. Lambda Function
Go to AWS Lambda → Create Function.
Runtime: Python 3.x.
Assign IAM role: LambdaELB5xxMonitorRole.
📌 Lambda handler (handler.py)
✅ Environment Variables in Lambda Console:
SNS_TOPIC_ARN → Your SNS topic ARN
LOAD_BALANCER_NAME → Name of your ALB/NLB
ERROR_THRESHOLD → e.g., 10

4. CloudWatch Event Rule
Go to CloudWatch → Rules → Create Rule.
Event Source: Schedule → rate(5 minutes)
Target: Your Lambda function

5. Testing
Simulate a 5xx error spike (e.g., by misconfiguring a backend temporarily).
Wait for CloudWatch metrics to capture it (up to 5 minutes).
Verify:
CloudWatch Logs → Lambda execution log shows error count.
SNS Alert Email/SMS received with details.