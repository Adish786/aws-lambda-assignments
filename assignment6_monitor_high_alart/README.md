
Steps to Implement

1. SNS Setup
Go to Amazon SNS → Topics → Create topic.
Type: Standard
Name: BillingAlertTopic
After creation → Create subscription:
Protocol: Email
Endpoint: your email address
Confirm the email subscription from your inbox.

2. IAM Role
Go to IAM → Roles → Create Role.
Trusted entity: Lambda.
Attach these policies:
CloudWatchReadOnlyAccess (to read billing metrics)
AmazonSNSFullAccess (to publish alerts)
Name it: LambdaBillingAlertRole.

3. Lambda Function
Go to AWS Lambda → Create function.
Runtime: Python 3.x.
Assign role: LambdaBillingAlertRole.
📌 Lambda handler (handler.py):

✅ Environment Variables to configure in Lambda console:
BILLING_THRESHOLD → 50
SNS_TOPIC_ARN → copy ARN from your BillingAlertTopic

4. Event Source (Bonus – Automated Scheduling)
Go to Amazon EventBridge (CloudWatch Events) → Rules → Create rule.
Schedule expression: rate(1 day) (runs daily).
Target: Your Lambda function.

5. Testing
Manual Test:
In Lambda console → Test with an empty payload {}.
Check logs in CloudWatch Logs.

Email Alert:
If billing exceeds $50, you’ll get an email:
⚠️ AWS Billing Alert: Your estimated charges are $57.34, which exceeds threshold $50.
If below, log will show: Billing is under threshold.