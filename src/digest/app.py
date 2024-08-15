import json
from datetime import datetime, timezone
from urllib.parse import urlparse
import boto3
from dateutil.parser import parse
from jinja2 import Template
from app_settings import (
    DIGEST_QUEUE,
    MY_TIMEZONE,
    DIGEST_EMAIL_FROM,
    DIGEST_EMAIL_TO,
)
from overall_summary import create_overall_summary_for_feeds_with_multiple_records
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


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def process_messages(messages):
    feeds = cleanup_group_and_sort_messages(messages)
    feeds = create_overall_summary_for_feeds_with_multiple_records(feeds)
    create_html_email_and_send_it(feeds)
    delete_messages_from_queue(messages)


def cleanup_group_and_sort_messages(messages):
    records_by_feed = {}
    for message in messages:
        print(json.dumps(message))
        record = json.loads(message["Body"])

        # This felt like quick hack at the time, just get this working, but it's been working for a while now.
        # Set default values for fields on the record
        # This lets us handle records from the rss_reader and the link_reader
        default_values = {
            "feed_title": "Miscellaneous",
            "feed_description": "",
            "title": "(No title)",
            "url": "",
            "published": "(No publish date)",
            "summary": "(No summary)",
            "notable_aspects": "",
            "relevance": "",
            "relevance_explanation": "",
        }
        for field, default in default_values.items():
            if field not in record:
                record[field] = default

        # parse and reformat dates
        if "published" in record and record["published"] != default_values["published"]:
            try:
                parsed_published = parse(record["published"], fuzzy=True)
                parsed_published = utc_to_local(parsed_published, MY_TIMEZONE)
                record["published"] = parsed_published.strftime("%Y-%m-%d %H:%M:%S %Z")
            except Exception as e:
                print(f"Error parsing date: {e}, ignoring and proceeding...")

        print("-" * 80)
        print(f"Feed Title: {record['feed_title']}")
        print(f"Feed Description: {record['feed_description']}")
        print(f"Title: {record['title']}")
        print(f"URL: {record['url']}")
        print(f"Published: {record['published']}")
        print(f"Summary: {record['summary']}")
        print(f"Notable Aspects: {record['notable_aspects']}")
        print(f"Relevance: {record['relevance']}")
        print(f"Relevance Explanation: {record['relevance_explanation']}")

        # parse out domain from the url, if provided
        if "url" in record and record["url"]:
            record["domain"] = urlparse(record["url"]).netloc

        # Group records by feed_title
        if record["feed_title"] not in records_by_feed:
            records_by_feed[record["feed_title"]] = []
        records_by_feed[record["feed_title"]].append(record)

    feeds = sorted(records_by_feed.items())
    for _, records in feeds:
        # sort records (this is done in place) by date, descending
        records.sort(key=lambda x: x["published"], reverse=True)
    return feeds


def create_html_email_and_send_it(feeds):
    # Produce HTML message
    with open("digest.html.jinja", encoding="utf8") as f:
        email = Template(f.read()).render(
            EMAIL_INLINE_CSS_STYLE=EMAIL_INLINE_CSS_STYLE,
            feeds=feeds,
        )
    # Email it using SES
    subject = f"Your Daily Digest — {utc_to_local(datetime.now(timezone.utc), MY_TIMEZONE).strftime('%Y-%m-%d %H:%M %Z')}"
    print("-" * 80)
    print(f"Subject: {subject}")
    print("Body:")
    print(email)
    send_email(DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, subject, html=email)


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
