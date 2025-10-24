Steps to Implement

1. DynamoDB Setup
Go to DynamoDB → Tables → Create Table.
Example table name: EmployeeData.
Partition key: EmployeeID (String).
Insert a few sample items:
{ "EmployeeID": "E001", "Name": "Adish", "Role": "DevOps" }
{ "EmployeeID": "E002", "Name": "Ravi", "Role": "Backend" }

2. SNS Setup
Go to Amazon SNS → Topics → Create topic.
Type: Standard
Name: DynamoDBUpdateAlertTopic
Create a subscription:
Protocol: Email
Endpoint: your email address
Confirm subscription from your inbox.

3. IAM Role for Lambda
Go to IAM → Roles → Create Role.
Trusted entity: Lambda.
Attach policies:
AmazonDynamoDBFullAccess (demo; in production restrict to stream access).
AmazonSNSFullAccess.
Name it: LambdaDynamoDBStreamRole.
(Alternative secure custom policy available on request.)

4. Lambda Function
Go to AWS Lambda → Create function.
Runtime: Python 3.x.
Execution role: LambdaDynamoDBStreamRole.
📌 Lambda handler (handler.py)

✅ Environment Variable in Lambda Console:
SNS_TOPIC_ARN → copy from your SNS topic.

5. DynamoDB Stream
Go to DynamoDB → Tables → EmployeeData → Exports and streams.
Enable DynamoDB Streams with New and old images.
Attach your Lambda function as the Stream consumer.

6. Testing
Update an item in the table, e.g.:
Update EmployeeID E001 -> Role = "Cloud Engineer"

Lambda will trigger.
You will receive an email alert:
DynamoDB Item Updated
Old Data: {"EmployeeID": "E001", "Name": "Adish", "Role": "DevOps"}
New Data: {"EmployeeID": "E001", "Name": "Adish", "Role": "Cloud Engineer"}

Check CloudWatch Logs → confirm function executed successfully.
