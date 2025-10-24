# AWS Lambda: Monitor Unencrypted S3 Buckets

This AWS Lambda function scans all S3 buckets in your AWS account and detects buckets without server-side encryption enabled. It helps enhance your AWS security posture by automating the detection of unencrypted buckets.

## Features

- Lists all S3 buckets in the account.
- Checks each bucket for server-side encryption.
- Identifies and logs buckets without encryption.
- Returns a list of unencrypted buckets on execution.

## Prerequisites

- AWS Account with appropriate permissions.
- AWS Lambda execution role with `AmazonS3ReadOnlyAccess` policy attached.

## Setup Instructions

### 1. Create IAM Role for Lambda

- Go to the AWS IAM console.
- Create a new role with the Lambda service as the trusted entity.
- Attach the `AmazonS3ReadOnlyAccess` managed policy to this role.

### 2. Deploy Lambda Function

- Open the AWS Lambda console.
- Create a new function with Python 3.x runtime.
- Assign the IAM role created in the previous step.
- Copy and paste the Lambda code into the function editor.

### 3. Verify and Run

- Save the Lambda function.
- Manually invoke the Lambda function.
- Check the CloudWatch logs for detailed output.
- The logs will list all S3 buckets checked and identify those without server-side encryption.

## Lambda Function Code Example

