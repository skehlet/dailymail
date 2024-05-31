import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
feed_metadata_table = dynamodb.Table("DailyMail-RssReaderFeedMetadata")
processed_ids_table = dynamodb.Table("DailyMail-RssReaderProcessedIds")


def get_feed_metadata(url):
    try:
        response = feed_metadata_table.get_item(Key={"url": url})
        if "Item" not in response:
            # print(f"URL {url}: no metadata found")
            return (None, None)
        etag = ""
        last_modified = ""
        if "etag" in response["Item"]:
            etag = response["Item"]["etag"]["S"]
        if "last_modified" in response["Item"]:
            last_modified = response["Item"]["last_modified"]["S"]
        # print(f"URL {url} metadata: etag: {etag}, last_modified: {last_modified}")
        return (etag, last_modified)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error retrieving metadata for {url}: {error_code} - {error_message}"
        )
        raise e


def store_feed_metadata(url, etag, last_modified):
    try:
        feed_metadata_table.update_item(
            Key={"url": url},
            UpdateExpression="SET etag = :etag, last_modified = :last_modified",
            ExpressionAttributeValues={
                ":etag": {"S": etag},
                ":last_modified": {"S": last_modified},
            },
        )
        # print(
        #     f"URL {url} metadata stored: etag: {etag}, last_modified: {last_modified}"
        # )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error storing metadata for {url}: {error_code} - {error_message}"
        )
        raise e


def id_already_processed(url, id) -> bool:
    try:
        response = processed_ids_table.get_item(Key={"url": url, "id": id})
        if "Item" not in response:
            # print(f"No, we have not yet seen {url}+{id}")
            return False
        # print(f"Yes, we have already seen {url}+{id}")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error checking if {url}+{id} has already been processed: {error_code} - {error_message}"
        )
        raise e


def mark_id_as_processed(url, id):
    try:
        processed_ids_table.put_item(Item={"url": url, "id": id})
        # print(f"Successfully recorded we have seen {url}+{id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error marking {url}+{id} as processed: {error_code} - {error_message}"
        )
        raise e
