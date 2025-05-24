#!/usr/bin/env python

import boto3
import time
from datetime import datetime, timedelta

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
processed_ids_table = dynamodb.Table("DailyMail-RssReaderProcessedIds")
feed_metadata_table = dynamodb.Table("DailyMail-RssReaderFeedMetadata")

# Calculate timestamp for today (midnight)
today_start = datetime.combine(datetime.today(), datetime.min.time())
today_timestamp = int(today_start.timestamp())

print("Deleting today's processed RSS entries...")

# Scan for processed_ids records updated today
response = processed_ids_table.scan(
    FilterExpression="updated_at >= :today",
    ExpressionAttributeValues={":today": today_timestamp}
)

# Delete the processed_ids records
processed_count = 0
for item in response.get("Items", []):
    processed_ids_table.delete_item(
        Key={"url": item["url"], "id": item["id"]}
    )
    processed_count += 1
    print(f"Deleted processed ID: {item['url']} - {item['id']}")

print(f"Deleted {processed_count} processed ID records from today")

print("\nDeleting all feed metadata to force fresh RSS fetches...")

# Delete ALL feed metadata to force fresh fetches (ignore etag/last_modified)
response = feed_metadata_table.scan()
metadata_count = 0
for item in response.get("Items", []):
    feed_metadata_table.delete_item(
        Key={"url": item["url"]}
    )
    metadata_count += 1
    print(f"Deleted feed metadata: {item['url']}")

print(f"Deleted {metadata_count} feed metadata records")
print(f"\nTotal: {processed_count} processed IDs + {metadata_count} feed metadata = {processed_count + metadata_count} records deleted")
print("RSS reader will now fetch all entries from all feeds as if running for the first time.")
