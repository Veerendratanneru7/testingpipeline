import boto3
import datetime

ec2_client = boto3.client("ec2")
rds_client = boto3.client("rds")

RETENTION_DAYS = 45

def get_old_unused_amis():
    response = ec2_client.describe_images(Owners=["self"])
    old_unused_amis = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)

    for image in response["Images"]:
        creation_date = datetime.datetime.strptime(image["CreationDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if creation_date < cutoff_date:
            old_unused_amis.append(image["ImageId"])

    return old_unused_amis

def delete_ami(image_id):
    print(f"Deregistering AMI: {image_id}")
    ec2_client.deregister_image(ImageId=image_id)

def get_old_rds_snapshots():
    response = rds_client.describe_db_snapshots(SnapshotType="manual")
    old_snapshots = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)

    for snapshot in response["DBSnapshots"]:
        snapshot_date = snapshot["SnapshotCreateTime"].replace(tzinfo=None)
        if snapshot_date < cutoff_date:
            old_snapshots.append(snapshot["DBSnapshotIdentifier"])

    return old_snapshots

def delete_rds_snapshot(snapshot_id):
    print(f"Deleting RDS Snapshot: {snapshot_id}")
    rds_client.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)

def lambda_handler(event, context):
    old_unused_amis = get_old_unused_amis()
    for ami in old_unused_amis:
        delete_ami(ami)

    old_rds_snapshots = get_old_rds_snapshots()
    for snapshot in old_rds_snapshots:
        delete_rds_snapshot(snapshot)

    print("Cleanup completed for old unused AMIs and RDS snapshots.")
