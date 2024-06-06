#!/usr/bin/env python

# find all objects in the S3 bucket skehlet-dailymail-summarizer in the
# incoming/ directory and copy them to new names and delete the old files

import sys
import uuid
import boto3

s3 = boto3.client("s3")

BUCKET_NAME = "skehlet-dailymail-summarizer"
PREFIX = "incoming/"

response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
if "Contents" not in response:
    print("No objects found")
    sys.exit(1)

# for each object in the incoming/ directory, copy it to a new object, then delete the old object
for obj in response["Contents"]:
    new_guid = uuid.uuid4()
    new_key = f"incoming/{new_guid}"
    s3.copy_object(
        Bucket=BUCKET_NAME,
        CopySource={"Bucket": BUCKET_NAME, "Key": obj["Key"]},
        Key=new_key)
    s3.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])
    print(f"Copied {obj['Key']} to {new_key}")
