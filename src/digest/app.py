import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import boto3
from dateutil.parser import parse
from jinja2 import Template
from .app_settings import (
    DIGEST_QUEUE,
    MY_TIMEZONE,
    DIGEST_EMAIL_FROM,
    DIGEST_EMAIL_TO,
)
from dailymail_shared.my_email_lib import send_email, EMAIL_INLINE_CSS_STYLE
from dailymail_shared.my_datetime import utc_to_local
from dailymail_shared.google_alerts import is_google_alert, get_topic_from_google_alert_title
from .my_digest import generate_newsletter_digest
from .ledger import load_ledger, save_ledger
from .alert_news import check_alert_for_news

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]
TEMPLATE_PATH = Path(__file__).with_name("digest.html.jinja")


def read_from_digest_queue():
    messages = read_all_from_queue()
    if len(messages) == 0:
        print("No messages in queue")
        return
    process_messages(messages)
    delete_messages_from_queue(messages)


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def process_messages(messages, dry_run=False):
    feeds = cleanup_group_and_sort_messages(messages)
    feeds, alert_updates = check_alerts_for_news(feeds)
    sent = create_email_and_send_it(feeds, alert_updates, dry_run=dry_run)
    # Only remember what we've told the reader once it has actually been sent
    if sent and not dry_run:
        for update in alert_updates:
            save_ledger(update.updated_ledger)


def check_alerts_for_news(feeds):
    """
    Compare each Google Alert feed against its ledger of already-reported facts.
    Returns the remaining (non-alert) feeds, plus an AlertUpdate for each alert topic with something new.
    If the check fails for a topic, its feed is kept with the regular feeds so nothing is lost.
    """
    today = utc_to_local(datetime.now(timezone.utc), MY_TIMEZONE).strftime("%Y-%m-%d")
    remaining_feeds = []
    alert_updates = []
    for feed_title, records in feeds:
        topic = get_topic_from_google_alert_title(feed_title) if is_google_alert(feed_title) else None
        if not topic:
            remaining_feeds.append((feed_title, records))
            continue
        try:
            interest = next((r["feed_context"] for r in records if r.get("feed_context")), None)
            update = check_alert_for_news(topic, records, load_ledger(topic), today, interest)
        except Exception as e:
            print(f"Error checking alert {topic!r} for news: {e}, including it unfiltered")
            remaining_feeds.append((feed_title, records))
            continue
        if update.developments:
            alert_updates.append(update)
        else:
            print(f"Nothing new for alert {topic!r} across {len(records)} articles, omitting")
    return remaining_feeds, alert_updates


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
        }
        for field, default in default_values.items():
            if record.get(field) is None:
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

        # Group records by feed_title
        if record["feed_title"] not in records_by_feed:
            records_by_feed[record["feed_title"]] = []
        records_by_feed[record["feed_title"]].append(record)

    feeds = sorted(records_by_feed.items())
    for _, records in feeds:
        # sort records (this is done in place) by date, descending
        records.sort(key=lambda x: x["published"], reverse=True)
    return feeds


def create_email_and_send_it(feeds, alert_updates, dry_run=False):
    # Generate the newsletter using our improved approach
    newsletter = generate_newsletter_digest(feeds)
    if not newsletter and not alert_updates:
        print("No news today, nothing to send.")
        return False
    
    # Get current date formatted for display
    today_date = utc_to_local(datetime.now(timezone.utc), MY_TIMEZONE).strftime('%A, %B %d, %Y')
    
    # Produce HTML message using the updated template
    with TEMPLATE_PATH.open(encoding="utf8") as f:
        email = Template(f.read()).render(
            EMAIL_INLINE_CSS_STYLE=EMAIL_INLINE_CSS_STYLE,
            newsletter=newsletter,
            alert_updates=alert_updates,
            today_date=today_date,
        )
    
    # Email it using SES
    subject = f"Today's News Digest — {today_date}"
    print("-" * 80)
    print(f"Subject: {subject}")
    print("Body:")
    print(email)
    if dry_run:
        print("Dry run, not sending")
        return False
    send_email(DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, subject, html=email)
    return True


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
        process_messages(messages, dry_run=True)


if __name__ == "__main__":
    # read_from_digest_queue() # if you use this, you might want to comment out delete_messages_from_queue as well 
    local_test()