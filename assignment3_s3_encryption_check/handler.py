import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()["Buckets"]
    unencrypted_buckets = []
    print("Listing all buckets and checking encryption:")
    for bucket in buckets:
        name = bucket["Name"]
        print(f"Checking bucket: {name}")  # Print all bucket names to console/logs
        try:
            enc = s3.get_bucket_encryption(Bucket=name)
            # Check if encryption rules exist
            rules = enc["ServerSideEncryptionConfiguration"]["Rules"]
            if not rules:
                unencrypted_buckets.append(name)
        except s3.exceptions.ClientError as e:
            # If encryption configuration is not found, treat as unencrypted
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                unencrypted_buckets.append(name)
    print("Buckets without server-side encryption:", unencrypted_buckets)
    return {'unencrypted_buckets': unencrypted_buckets}
