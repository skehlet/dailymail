import html
import json
import boto3
from dateutil.parser import parse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app_settings import DIGEST_QUEUE, EMAIL_INLINE_CSS_STYLE, MY_TIMEZONE

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]


def read_from_digest_queue():
    messages = read_all_from_queue()
    if len(messages) == 0:
        print("No messages in queue")
        return
    process_messages(messages)


def process_messages(messages):
    grouped_records = {}
    for message in messages:
        print(json.dumps(message))
        record = json.loads(message["Body"])

        if parsed_published := parse(record["published"], fuzzy=True):
            parsed_published = utc_to_local(parsed_published)
            record["published"] = parsed_published.strftime("%Y-%m-%d %H:%M:%S %Z")

        print("-" * 80)
        print(f"Feed Title: {record['feed_title']}")
        print(f"Feed Description: {record['feed_description']}")
        print(f"Title: {record['title']}")
        print(f"URL: {record['url']}")
        print(f"Published: {record['published']}")
        print(f"Summary: {record['summary']}")

        # Group records by feed_title
        if record["feed_title"] not in grouped_records:
            grouped_records[record["feed_title"]] = []
        grouped_records[record["feed_title"]].append(record)

    # Produce HTML message
    # TODO: really need to look into Jinja2 or something
    sections = []
    for feed_title, records in sorted(grouped_records.items()):
        summaries = []
        # reverse sort records by record['published']
        records.sort(key=lambda x: x["published"], reverse=True)
        for record in records:
            summaries.append(
                format_summary_using_html(
                    record["url"],
                    record["title"],
                    record["published"],
                    record["summary"],
                )
            )
        section = f"""<div style="font-size: 24px; font-weight: bold; margin-top: 25px">{feed_title}</div>\n"""
        section += "\n".join(summaries)
        sections.append(section)

    print("-" * 80)
    email = f"""<span style="{EMAIL_INLINE_CSS_STYLE}">\n"""
    email += "\n<hr>\n".join(sections)
    email += "</span>"

    # Email it using SES
    print(email)

    delete_messages_from_queue(messages)


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def format_summary_using_html(url, site_title, published_on, summary):
    safe_url = html.escape(url)
    safe_site_title = html.escape(site_title)
    safe_summary = ""
    for paragraph in summary.strip().split("\n\n"):
        if paragraph:
            safe_summary += f"<p>{html.escape(paragraph)}</p>\n"
    return f"""\
<div style="padding-top: 10px">
    <div><b><a href="{safe_url}">{safe_site_title}</a></b></dib>
    <div>{published_on}</div>
</div>
<span>
    {safe_summary.strip()}
</span>
"""


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(MY_TIMEZONE))


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
