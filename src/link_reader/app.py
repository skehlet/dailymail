import json
from urllib.parse import urlparse, parse_qs
from app_settings import SCRAPER_QUEUE
import boto3


sqs = boto3.client("sqs")


def process_record(record):
    print(record)

    # record = {
    #     "feed_title": feed_title,
    #     "feed_description": feed_description,
    #     "title": article_title,
    #     "link": article_link,
    #     "description": article_description,
    #     "published": article_published,
    # }
    # write_to_queue(record)


def enqueue(queue_name, obj):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(obj))


# if __name__ == "__main__":
#     process_record()
