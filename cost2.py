import boto3
import datetime

ec2_client = boto3.client("ec2")
rds_client = boto3.client("rds")

RETENTION_DAYS = 45

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
            old_unused_amis.append({"ImageId": image["ImageId"], "CreationDate": image["CreationDate"]})

    return old_unused_amis

def get_old_rds_snapshots():
    response = rds_client.describe_db_snapshots(SnapshotType="manual")
    old_snapshots = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)

    for snapshot in response["DBSnapshots"]:
        snapshot_date = snapshot["SnapshotCreateTime"].replace(tzinfo=None)
        if snapshot_date < cutoff_date:
            old_snapshots.append({"DBSnapshotIdentifier": snapshot["DBSnapshotIdentifier"], "SnapshotCreateTime": str(snapshot_date)})

    return old_snapshots

def main():
    old_unused_amis = get_old_unused_amis()
    old_rds_snapshots = get_old_rds_snapshots()

    print("\n=== Old Unused AMIs (Not Bound to Any Instance) ===")
    if old_unused_amis:
        for ami in old_unused_amis:
            print(f"AMI ID: {ami['ImageId']}, Created On: {ami['CreationDate']}")
    else:
        print("No old unused AMIs found.")

    print("\n=== Old RDS Snapshots ===")
    if old_rds_snapshots:
        for snapshot in old_rds_snapshots:
            print(f"Snapshot ID: {snapshot['DBSnapshotIdentifier']}, Created On: {snapshot['SnapshotCreateTime']}")
    else:
        print("No old RDS snapshots found.")

if __name__ == "__main__":
    main()
