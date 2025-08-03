import boto3

s3 = boto3.resource("s3")


def write_to_s3(bucket_name, key, data):
    s3.Bucket(bucket_name).put_object(Key=key, Body=data)
