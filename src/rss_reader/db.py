import time
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
feed_metadata_table = dynamodb.Table("DailyMail-RssReaderFeedMetadata")
processed_ids_table = dynamodb.Table("DailyMail-RssReaderProcessedIds")

CLEANUP_AFTER_SECS = 365 * 24 * 60 * 60 # 365 days


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
    cutoff_time = now - CLEANUP_AFTER_SECS
    total_deleted = 0
    items_processed = 0
    batch_size = 25  # Maximum items per batch
    
    try:
        # Scan parameters for pagination
        scan_params = {
            'FilterExpression': Attr('updated_at').exists() & Attr('updated_at').lt(cutoff_time)
        }
        
        done = False
        start_key = None
        
        while not done:
            if start_key:
                scan_params['ExclusiveStartKey'] = start_key
                
            response = processed_ids_table.scan(**scan_params)
            items = response.get('Items', [])
            items_processed += len(items)
            
            # Process in smaller batches
            for i in range(0, len(items), batch_size):
                batch_items = items[i:i+batch_size]
                
                # Batch delete for efficiency
                with processed_ids_table.batch_writer() as batch:
                    for item in batch_items:
                        batch.delete_item(Key={"url": item["url"], "id": item["id"]})
                        total_deleted += 1
                
                # Add a small delay between batches to avoid throttling
                if i + batch_size < len(items):
                    time.sleep(0.5)  # 500ms delay between batches
            
            # Add a larger delay between scan pages
            if response.get('LastEvaluatedKey'):
                time.sleep(1)  # 1 second delay between scan pages
            
            # Check if we need to continue scanning
            start_key = response.get('LastEvaluatedKey')
            done = start_key is None
        
        print(f"cleanup_processed_ids: Processed {items_processed} records. Deleted {total_deleted} old records (older than {CLEANUP_AFTER_SECS/86400:.1f} days).")
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"DynamoDB error cleaning up processed ids: {error_code} - {error_message}")
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
