#!/usr/bin/env python

import boto3
import time
from datetime import datetime, timedelta

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
processed_ids_table = dynamodb.Table("DailyMail-RssReaderProcessedIds")

# Calculate timestamp for today (midnight)
today_start = datetime.combine(datetime.today(), datetime.min.time())
today_timestamp = int(today_start.timestamp())

# Scan for records updated today
response = processed_ids_table.scan(
    FilterExpression="updated_at >= :today",
    ExpressionAttributeValues={":today": today_timestamp}
)

# Delete the records
count = 0
for item in response.get("Items", []):
    processed_ids_table.delete_item(
        Key={"url": item["url"], "id": item["id"]}
    )
    count += 1
    print(f"Deleted: {item['url']} - {item['id']}")

print(f"Deleted {count} records from today")
