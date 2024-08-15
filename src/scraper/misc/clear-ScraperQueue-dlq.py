#!/usr/bin/env python

# delete all messages in the DailyMail-DigestQueue-dlq queue

import boto3

source_queue = "DailyMail-ScraperQueue-dlq"

sqs = boto3.client("sqs")

while True:
    resp = sqs.receive_message(QueueUrl=source_queue, MaxNumberOfMessages=10, WaitTimeSeconds=0)
    if "Messages" not in resp:
        break
    for message in resp["Messages"]:
        print(message["Body"])
        sqs.delete_message(QueueUrl=source_queue, ReceiptHandle=message["ReceiptHandle"])
