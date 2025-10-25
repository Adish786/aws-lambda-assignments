
Steps to Implement
1. SNS Setup
Go to SNS → Create Topic.
Choose Standard Topic.
Subscribe your email to this topic.
Note down the Topic ARN for use in Lambda.

2. IAM Role for Lambda
Create a new IAM role for Lambda.
Attach the following policies:
AmazonEC2FullAccess (start/terminate instances)
AmazonElasticLoadBalancingReadOnlyAccess (read ELB metrics)
AmazonSNSFullAccess (send notifications)
Name it: LambdaAutoScaleRole.

3. Lambda Function
Runtime: Python 3.x
Handler: lambda_function.lambda_handler
Execution role: LambdaAutoScaleRole

4. CloudWatch Events
Go to CloudWatch → Rules → Create Rule.
Schedule expression: rate(5 minutes).
Target: Lambda function created above.

5. Testing
Simulate high network load (e.g., via test traffic) → check if new instance is launched.
Simulate low network load → check if instance is terminated.
Confirm SNS notifications are received with scaling actions.
Check CloudWatch Logs for Lambda execution details.
