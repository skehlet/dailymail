import boto3
from app_settings import DIGEST_QUEUE

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]


def read_from_digest_queue():
    messages = read_all_from_queue()
    for message in messages:
        print(message)
        # delete_messages_from_queue([message])


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            print("Queue empty")
            return messages
        messages.extend(response["Messages"])


def delete_messages_from_queue(messages):
    for message in messages:
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
        print(f"Deleted message {message['MessageId']}")
