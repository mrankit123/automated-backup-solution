import boto3
import time
from datetime import datetime

# Initialize AWS clients
rds = boto3.client('rds')
s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    # RDS instance and S3 bucket details
    db_instance_id = 'automated-backup-solution1'
    s3_bucket_name = 'automated-backup-solution-2'

    # Step 1: Create an RDS snapshot
    snapshot_id = f"{db_instance_id}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    try:
        response = rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id
        )
        print(f"Snapshot {snapshot_id} creation started.")
    except Exception as e:
        print(f"Error creating snapshot: {str(e)}")
        raise e

    # Step 2: Wait for the snapshot to be available
    waiter = rds.get_waiter('db_snapshot_available')
    try:
        waiter.wait(DBSnapshotIdentifier=snapshot_id)
        print(f"Snapshot {snapshot_id} is now available.")
    except Exception as e:
        print(f"Error waiting for snapshot: {str(e)}")
        raise e

    # Step 3: Upload snapshot metadata to S3
    metadata = {
        "snapshot_id": snapshot_id,
        "db_instance": db_instance_id,
        "created_at": str(datetime.now())
    }
    s3_key = f"backups/{snapshot_id}.json"
    try:
        s3.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=str(metadata)
        )
        print(f"Snapshot metadata uploaded to S3 bucket {s3_bucket_name}.")
    except Exception as e:
        print(f"Error uploading metadata to S3: {str(e)}")
        raise e
