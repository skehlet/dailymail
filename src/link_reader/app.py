import json
import boto3
from app_settings import SCRAPER_QUEUE
from my_errors import StatusCodeError


sqs = boto3.client("sqs")


def process_event(event):
    # print(event)

    if not "queryStringParameters" in event:
        raise StatusCodeError("Missing query string parameters", status_code=400)
    if not "url" in event["queryStringParameters"]:
        raise StatusCodeError("No url in query string parameters", status_code=400)

    record = {
        "url": event["queryStringParameters"]["url"],
        "immediate": True,
    }

    print(json.dumps(record))

    enqueue(SCRAPER_QUEUE, json.dumps(record))


def enqueue(queue_name, obj):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    sqs.send_message(QueueUrl=queue_url, MessageBody=obj)
