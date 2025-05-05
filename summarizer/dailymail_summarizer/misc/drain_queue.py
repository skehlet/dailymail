#!/usr/bin/env python

# read and discard all messages from a given SQS queue
# DailyMail-DigestQueue

import boto3
import sys

if len(sys.argv) != 2:
    print("Usage: %s <queue_name>" % sys.argv[0])
    sys.exit(1)

queue_name = sys.argv[1]


sqs = boto3.client("sqs")

queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
while True:
    response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
    if "Messages" not in response:
        print("Queue empty")
        break
    for message in response["Messages"]:
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
        print(f"Deleted message {message['MessageId']}")
