import boto3
import datetime
import os

ec2_client = boto3.client("ec2")
rds_client = boto3.client("rds")

RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 45))

def get_instances_using_amis():
    response = ec2_client.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}])
    used_amis = set()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            used_amis.add(instance["ImageId"])

    return used_amis

def get_old_unused_amis():
    response = ec2_client.describe_images(Owners=["self"])
    shared_response = ec2_client.describe_images(Filters=[{"Name": "is-public", "Values": ["false"]}])

    all_images = response["Images"] + shared_response["Images"]
    old_unused_amis = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)
    used_amis = get_instances_using_amis()

    for image in all_images:
        creation_date = datetime.datetime.strptime(image["CreationDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if creation_date < cutoff_date and image["ImageId"] not in used_amis:
            old_unused_amis.append({
                "ImageId": image["ImageId"],
                "Name": image.get("Name", "N/A"),
                "CreationDate": image["CreationDate"]
            })

    return old_unused_amis

def get_old_rds_snapshots():
    response = rds_client.describe_db_snapshots(SnapshotType="manual")
    old_snapshots = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)

    # Get active DB instances
    active_dbs = {db["DBInstanceIdentifier"] for db in rds_client.describe_db_instances()["DBInstances"]}

    for snapshot in response["DBSnapshots"]:
        snapshot_date = snapshot["SnapshotCreateTime"].replace(tzinfo=None)
        if snapshot_date < cutoff_date and snapshot["DBInstanceIdentifier"] not in active_dbs:
            old_snapshots.append({
                "DBSnapshotIdentifier": snapshot["DBSnapshotIdentifier"],
                "DBInstanceIdentifier": snapshot["DBInstanceIdentifier"],
                "SnapshotCreateTime": str(snapshot_date)
            })

    return old_snapshots

def get_old_unused_ebs_volumes():
    response = ec2_client.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])
    old_volumes = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)

    for volume in response["Volumes"]:
        if "CreateTime" in volume:
            volume_date = volume["CreateTime"].replace(tzinfo=None)
            if volume_date < cutoff_date:
                old_volumes.append({
                    "VolumeId": volume["VolumeId"],
                    "Size": volume["Size"],
                    "CreateTime": str(volume_date)
                })

    return old_volumes

def lambda_handler(event, context):
    old_unused_amis = get_old_unused_amis()
    old_rds_snapshots = get_old_rds_snapshots()
    old_unused_ebs_volumes = get_old_unused_ebs_volumes()

    return {
        "statusCode": 200,
        "body": {
            "old_unused_amis": old_unused_amis,
            "old_rds_snapshots": old_rds_snapshots,
            "old_unused_ebs_volumes": old_unused_ebs_volumes
        }
    }
