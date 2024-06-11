import json
from datetime import datetime, timezone
import boto3
from dateutil.parser import parse
from urllib.parse import urlparse
from jinja2 import Template
from app_settings import (
    DIGEST_QUEUE,
    MY_TIMEZONE,
    DIGEST_EMAIL_FROM,
    DIGEST_EMAIL_TO,
)
from shared.my_email_lib import send_email, EMAIL_INLINE_CSS_STYLE
from shared.my_datetime import utc_to_local

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]


def read_from_digest_queue():
    messages = read_all_from_queue()
    if len(messages) == 0:
        print("No messages in queue")
        return
    process_messages(messages)


def process_messages(messages):
    records_by_feed = {}
    for message in messages:
        print(json.dumps(message))
        record = json.loads(message["Body"])

        if parsed_published := parse(record["published"], fuzzy=True):
            parsed_published = utc_to_local(parsed_published, MY_TIMEZONE)
            record["published"] = parsed_published.strftime("%Y-%m-%d %H:%M:%S %Z")

        # TODO: handle some of these fields not guaranteed to be there
        # I added `type` to help with this
        # Right now only type=rss_entry records come here so this shouldn't be a problem, for now
        print("-" * 80)
        print(f"Feed Title: {record['feed_title']}")
        print(f"Feed Description: {record['feed_description']}")
        print(f"Title: {record['title']}")
        print(f"URL: {record['url']}")
        print(f"Published: {record['published']}")
        print(f"Summary: {record['summary']}")

        # parse out domain from the url
        record["domain"] = urlparse(record["url"]).netloc

        # Group records by feed_title
        if record["feed_title"] not in records_by_feed:
            records_by_feed[record["feed_title"]] = []
        records_by_feed[record["feed_title"]].append(record)

    # Produce HTML message
    feeds = sorted(records_by_feed.items())
    for _, records in feeds:
        # sort records (this is done in place) by date, descending
        records.sort(key=lambda x: x["published"], reverse=True)

    with open("digest.html.jinja", encoding="utf8") as f:
        email = Template(f.read()).render(
            EMAIL_INLINE_CSS_STYLE=EMAIL_INLINE_CSS_STYLE,
            feeds=feeds,
        )

    # TODO: send to the LLM asking for it to pick the top articles

    # Review the following email, which is list of topics I find interesting with accompanying summaries of recent articles, and extract out the one or two most interesting articles. Your output should look like:
    #
    # TOP ARTICLES
    # 1. <First most interesting Article Name and HTML LINK>
    # 2. <Second most interesting Article Name and HTML LINK>
    #
    # <One or two sentence explanation of why those two articles were chosen as the most interesting>

    # Email it using SES
    subject = f"Your Daily Digest — {utc_to_local(datetime.now(timezone.utc), MY_TIMEZONE).strftime('%Y-%m-%d %H:%M %Z')}"
    print("-" * 80)
    print(f"Subject: {subject}")
    print("Body:")
    print(email)
    send_email(DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, subject, html=email)

    delete_messages_from_queue(messages)


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def delete_messages_from_queue(messages):
    # process messages in batches of 10
    for i in range(0, len(messages), 10):
        batch = messages[i : i + 10]
        entries = [
            {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
            for message in batch
        ]
        sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)


def local_test():
    with open("misc/example-messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
        process_messages(messages)


if __name__ == "__main__":
    # read_from_digest_queue()
    local_test()
