import json
import uuid
from app_settings import SUMMARIZER_BUCKET
from app_sns import parse_sns_message
from app_ses import is_sender_verified
from gmail_forwarding_confirmation import (
    is_gmail_forwarding_confirmation,
    send_gmail_forwarding_confirmation_back_to_originator,
)
from shared.app_s3 import write_to_s3


def process_record(sns_record):
    # print(json.dumps(sns_record))
    if sns_record["EventSource"] != "aws:sns":
        raise Exception("Not an SNS event")

    message = sns_record["Sns"]["Message"]

    (email_sender, email_to, email_date, email_subject, body) = parse_sns_message(
        message
    )
    print(f"Sender: {email_sender}")
    print(f"To: {email_to}")
    print(f"Date: {email_date}")
    print(f"Subject: {email_subject}")
    print(f"Body: {body[:100]}")

    # If it's a Gmail forwarding confirmation, parse out the originator and send it back
    if is_gmail_forwarding_confirmation(email_subject):
        send_gmail_forwarding_confirmation_back_to_originator(email_subject, body)
        return

    # Confirm the email_sender is on the list of SES verified identities.
    # Drop the email if it's not.
    if not is_sender_verified(email_sender):
        print(f"Sender {email_sender} is not verified. Dropping email.")
        return

    # construct a record and store it in the summarizer bucket
    record = {
        "type": "email",
        "feed_title": email_sender,
        "feed_description": "",
        "title": email_subject,
        "content": body,
        "url": "",
        "description": "",
        "published": email_date,
    }

    write_to_summarizer_bucket(record)

    print(f"Successfully extracted email contents and wrote them to {SUMMARIZER_BUCKET}")


def write_to_summarizer_bucket(record):
    key = f"incoming/{uuid.uuid4()}"
    write_to_s3(SUMMARIZER_BUCKET, key, json.dumps(record))


if __name__ == "__main__":
    with open("misc/sample-email-over-sns.json", encoding="utf-8") as f:
        process_record(json.load(f))
