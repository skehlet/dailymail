#!/usr/bin/env python

import boto3
import sys

queue = "DailyMail-DigestQueue"

sqs = boto3.client("sqs")

messages = []
while True:
    resp = sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=0,
    )
    if "Messages" not in resp:
        break
    messages.extend(resp["Messages"])

print(f"Found {len(messages)} messages")

for message in messages:
    sqs.delete_message(QueueUrl=queue, ReceiptHandle=message["ReceiptHandle"])

print(f"Deleted {len(messages)} messages")

for message in messages:
    sqs.send_message(QueueUrl=queue, MessageBody=message["Body"])

print(f"Requeued {len(messages)} messages")
