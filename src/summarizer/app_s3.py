import boto3

s3 = boto3.resource("s3")


def delete_from_s3(bucket_name, key):
    s3.Object(bucket_name, key).delete()
