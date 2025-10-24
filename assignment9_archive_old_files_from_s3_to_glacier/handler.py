import boto3
from datetime import datetime, timezone, timedelta
import os

# Initialize S3 client
s3 = boto3.client('s3')

# Number of months after which files should be archived
MONTHS_OLD = 6

def lambda_handler(event, context):
    # Read bucket name from environment variable (recommended)
    bucket_name = os.environ.get('BUCKET_NAME', 'your-s3-bucket-name')
    glacier_storage_class = 'GLACIER'  # or 'GLACIER_IR' (Instant Retrieval) if you prefer faster retrieval

    print(f"Checking for files older than {MONTHS_OLD} months in bucket: {bucket_name}")

    # Calculate the cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=MONTHS_OLD * 30)

    # List all objects in the bucket
    paginator = s3.get_paginator('list_objects_v2')
    archived_files = []

    for page in paginator.paginate(Bucket=bucket_name):
        if 'Contents' not in page:
            print("No files found in the bucket.")
            continue

        for obj in page['Contents']:
            key = obj['Key']
            last_modified = obj['LastModified']

            # Check if file is older than 6 months
            if last_modified < cutoff_date:
                # Get the current storage class (skip if already Glacier)
                current_storage_class = obj.get('StorageClass', 'STANDARD')
                if current_storage_class in ['GLACIER', 'DEEP_ARCHIVE', 'GLACIER_IR']:
                    print(f"Skipping {key} (already archived)")
                    continue

                try:
                    # Copy object to same location with Glacier storage class
                    s3.copy_object(
                        Bucket=bucket_name,
                        CopySource={'Bucket': bucket_name, 'Key': key},
                        Key=key,
                        StorageClass=glacier_storage_class,
                        MetadataDirective='COPY'
                    )

                    # Delete the old version
                    s3.delete_object(Bucket=bucket_name, Key=key)

                    archived_files.append(key)
                    print(f"Archived: {key}")

                except Exception as e:
                    print(f"Error archiving {key}: {str(e)}")

    print(f"\n✅ Archival complete. Total files moved: {len(archived_files)}")
    if archived_files:
        print("Archived files list:")
        for file in archived_files:
            print(f" - {file}")

    return {
        'statusCode': 200,
        'archived_files_count': len(archived_files),
        'archived_files': archived_files
    }
