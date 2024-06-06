import json
from app_settings import SCRAPER_QUEUE
import boto3


sqs = boto3.client("sqs")


def process_event(event):
    print(event)

    if not "queryStringParameters" in event:
        print("no query string parameters")
        return
    if not "url" in event["queryStringParameters"]:
        print("no url in query string parameters")
        return

    record = {
        "url": event["queryStringParameters"]["url"],
        "immediate": True,
    }

    enqueue(SCRAPER_QUEUE, json.dumps(record))


def enqueue(queue_name, obj):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    sqs.send_message(QueueUrl=queue_url, MessageBody=obj)
