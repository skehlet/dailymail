#!/usr/bin/env python

# move all messages from the DailyMail-DigestQueue-dlq queue to the DailyMail-DigestQueue queue

import boto3
import sys

source_queue = "DailyMail-DigestQueue-dlq"
dest_queue = "DailyMail-DigestQueue"

sqs = boto3.client("sqs")

while True:
    resp = sqs.receive_message(QueueUrl=source_queue, MaxNumberOfMessages=10, WaitTimeSeconds=0)
    if "Messages" not in resp:
        break
    for message in resp["Messages"]:
        sqs.send_message(QueueUrl=dest_queue, MessageBody=message["Body"])
        sqs.delete_message(QueueUrl=source_queue, ReceiptHandle=message["ReceiptHandle"])
