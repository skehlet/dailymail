import boto3

sqs = boto3.client('sqs')

def enqueue(queue_name, obj):
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    sqs.send_message(QueueUrl=queue_url, MessageBody=obj)
