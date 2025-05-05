#!/usr/bin/env python

"""
Script to fetch messages from DailyMail-DigestQueue and save them to 
example-messages.json in the same directory as this script.
This script can be run from any directory.
"""

import boto3
import json
import os
import sys

# Set the queue name
QUEUE_NAME = "DailyMail-DigestQueue"

def main():
    # Find the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "example-messages.json")
    
    print(f"Script directory: {script_dir}")
    print(f"Output will be saved to: {output_file}")
    
    # Initialize SQS client
    sqs = boto3.client("sqs")
    
    try:
        # Get queue URL
        queue_url_response = sqs.get_queue_url(QueueName=QUEUE_NAME)
        queue_url = queue_url_response["QueueUrl"]
        print(f"Found queue URL: {queue_url}")
    except Exception as e:
        print(f"Error getting queue URL: {e}")
        sys.exit(1)
    
    # Collect all messages
    all_messages = []
    
    print("Fetching messages from queue...")
    while True:
        # Receive messages but don't delete them
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,  # Short timeout to make messages available again quickly
            WaitTimeSeconds=0
        )
        
        if "Messages" not in response:
            print("No more messages in queue")
            break
        
        messages = response["Messages"]
        all_messages.extend(messages)
        
        # Allow the visibility timeout to expire naturally
        # This way messages will return to the queue
        print(f"Retrieved {len(messages)} more messages")
    
    if not all_messages:
        print("No messages found in queue")
        sys.exit(0)
    
    # Write messages to file
    print(f"Writing {len(all_messages)} messages to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, indent=2)
    
    print(f"Successfully wrote {len(all_messages)} messages to {output_file}")
    print("Messages remain in the queue for processing")

if __name__ == "__main__":
    main()