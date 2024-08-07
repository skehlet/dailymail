import time
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
feed_metadata_table = dynamodb.Table("DailyMail-RssReaderFeedMetadata")
processed_ids_table = dynamodb.Table("DailyMail-RssReaderProcessedIds")

CLEANUP_AFTER_SECS = 90 * 24 * 60 * 60 # 90 days


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
    now = int(time.time())
    try:
        feed_metadata_table.update_item(
            Key={"url": url},
            UpdateExpression="SET etag = :etag, last_modified = :last_modified, updated_at = :updated_at",
            ExpressionAttributeValues={
                ":etag": {"S": etag},
                ":last_modified": {"S": last_modified},
                ":updated_at": now,
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
    now = int(time.time())
    try:
        processed_ids_table.put_item(Item={
            "url": url,
            "id": id,
            "updated_at": now,
        })
        # print(f"Successfully recorded we have seen {url}+{id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error marking {url}+{id} as processed: {error_code} - {error_message}"
        )
        raise e


def cleanup_processed_ids():
    now = int(time.time())
    try:
        response = processed_ids_table.scan(
            FilterExpression=Attr('updated_at').exists()
        )
        print(f"cleanup_processed_ids: reviewing {len(response["Items"])} records")
        for item in response["Items"]:
            updated_at = int(item["updated_at"])
            if updated_at < (now - CLEANUP_AFTER_SECS):
                processed_ids_table.delete_item(Key={"url": item["url"], "id": item["id"]})
                print(f"Deleted old processed id {item['url']}+{item['id']}")
            # else:
            #     print(f"Record {item["url"]}+{item["id"]} safe from deletion ({updated_at})")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error cleaning up processed ids: {error_code} - {error_message}"
        )
        raise e


def add_updated_at_field_where_missing():
    now = int(time.time())
    try:
        response = processed_ids_table.scan(
            FilterExpression=Attr('updated_at').not_exists()
        )
        print(f"add_updated_at_field_where_missing: reviewing {len(response["Items"])} records")
        for item in response["Items"]:
            processed_ids_table.update_item(
                Key={"url": item["url"], "id": item["id"]},
                UpdateExpression="SET updated_at = :updated_at",
                ExpressionAttributeValues={
                    ":updated_at": now,
                },
            )
            print(f"Added updated_at field to {item['url']}+{item['id']}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error adding updated_at field: {error_code} - {error_message}"
        )
        raise e


def clear_updated_at_fields():
    try:
        response = processed_ids_table.scan(
            FilterExpression=Attr('updated_at').exists()
        )
        print(f"clear_updated_at_fields: reviewing {len(response["Items"])} records")
        for item in response["Items"]:
            processed_ids_table.update_item(
                Key={"url": item["url"], "id": item["id"]},
                UpdateExpression="REMOVE updated_at",
            )
            print(f"Cleared updated_at field from {item['url']}+{item['id']}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"DynamoDB error clearing updated_at fields: {error_code} - {error_message}"
        )
        raise e
