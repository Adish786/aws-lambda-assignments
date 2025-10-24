import boto3
import datetime

ec2 = boto3.client('ec2')
RETENTION_DAYS = 30  # Snapshots older than this will be deleted

def lambda_handler(event, context):
    volume_id = event.get('volume_id')  # Get volume_id from event
    if not volume_id:
        volume_id = 'vol-02fe99c007fbf9cf3'  # Replace with your actual volume ID
        print(f"No volume_id in event; using fallback: {volume_id}")

    # Calculate cutoff date for deletion
    delete_date = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)

    # List all snapshots for the volume owned by self
    snapshots = ec2.describe_snapshots(
        Filters=[{'Name': 'volume-id', 'Values': [volume_id]}],
        OwnerIds=['self']
    )['Snapshots']

    # Delete snapshots older than retention period first
    for snap in snapshots:
        start_time = snap['StartTime'].replace(tzinfo=None)  # naive datetime
        if start_time < delete_date:
            snap_id = snap['SnapshotId']
            ec2.delete_snapshot(SnapshotId=snap_id)
            print(f"Deleted snapshot {snap_id} created on {start_time}")

    # Now create a new snapshot for the volume
    snapshot = ec2.create_snapshot(
        VolumeId=volume_id,
        Description=f"Automated snapshot of volume {volume_id} on {datetime.datetime.now()}"
    )
    print(f"Created snapshot {snapshot['SnapshotId']} for volume {volume_id}")

    return {
        'created_snapshot': snapshot['SnapshotId'],
        'message': f"Snapshots older than {RETENTION_DAYS} days deleted for volume {volume_id}"
    }
