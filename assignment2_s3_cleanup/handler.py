import boto3
from datetime import datetime, timezone, timedelta

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('s3-bucket-cleanup-adish')

    days_to_keep = 1 # Define the age threshold in days
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

    # For versioned buckets, delete old versions; else just delete old objects
    for obj_version in bucket.object_versions.all():
        if obj_version.last_modified < cutoff_date:
            obj_version.delete()

    return {'statusCode': 200, 'body': 'Old files deleted.'}
