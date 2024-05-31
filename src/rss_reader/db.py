import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
etag_table = dynamodb.Table("dailymail-rss-reader-etag-table")
id_table = dynamodb.Table("dailymail-rss-reader-id-table")


def get_last_seen_etag(url):
    try:
        response = etag_table.get_item(Key={"url": url})
        if "Item" not in response:
            print(f"No etag found in DynamoDB table for URL {url}.")
            return None
        etag = response["Item"]["etag"]["S"]
        print(f"Retrieved etag '{etag}' from DynamoDB table for URL {url}.")
        return etag
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"Error retrieving etag from DynamoDB table: {error_code} - {error_message}"
        )
        raise e


def store_seen_etag(url, etag):
    try:
        etag_table.update_item(
            Key={"url": url},
            UpdateExpression="SET etag = :etag",
            ExpressionAttributeValues={":etag": {"S": etag}},
        )
        print(f"Successfully stored etag '{etag}' for URL '{url}' in DynamoDB table.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error storing etag in DynamoDB table: {error_code} - {error_message}")
        raise e


def have_already_processed_id(url, id) -> bool:
    try:
        response = id_table.get_item(Key={"url": url, "id": id})
        if "Item" not in response:
            print(f"No, we have not yet seen {url}+{id}")
            return False
        print(f"Yes, we have already seen {url}+{id}")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error checking DynamoDB for {url}+{id}: {error_code} - {error_message}")
        raise e


def store_processed_id(url, id):
    try:
        id_table.put_item(Item={"url": url, "id": id})
        print(f"Successfully recorded we have seen {url}+{id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error updating DynamoDB for {url}+{id}: {error_code} - {error_message}")
        raise e
