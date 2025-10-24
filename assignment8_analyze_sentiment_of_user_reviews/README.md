
Steps to Implement
1. IAM Role Setup
Go to IAM → Roles → Create Role.
Trusted entity: Lambda.
Attach policy:
ComprehendFullAccess (demo purpose; in production, create a restricted policy).
Name the role: LambdaComprehendRole.

2. Lambda Function
Go to AWS Lambda → Create function.
Runtime: Python 3.x.
Execution role: LambdaComprehendRole.
📌 Lambda handler (handler.py)

3. Testing

Manually invoke the Lambda with sample payloads:

Example Event (Positive Review):

{
  "review": "I absolutely love this product! It exceeded all my expectations."
}


✅ Expected Output in Logs:

{
  "review": "I absolutely love this product! It exceeded all my expectations.",
  "sentiment": "POSITIVE",
  "confidence": {
    "Positive": 0.98,
    "Negative": 0.01,
    "Neutral": 0.01,
    "Mixed": 0.00
  }
}


Example Event (Negative Review):

{
  "review": "This is terrible. It stopped working after just two days."
}


✅ Expected Output:

{
  "review": "This is terrible. It stopped working after just two days.",
  "sentiment": "NEGATIVE",
  "confidence": {
    "Positive": 0.01,
    "Negative": 0.95,
    "Neutral": 0.03,
    "Mixed": 0.01
  }
}
