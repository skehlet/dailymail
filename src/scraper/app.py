import uuid
import json
from scrape import fetch_site_content
from app_s3 import write_to_s3
from app_settings import SUMMARIZER_BUCKET


def process_record(sqs_record):
    # print(sqs_record)

    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    record = json.loads(sqs_record["body"])
    print(f"Record: {record}")

    # {
    #     "feed_title": "Your Local Epidemiologist",
    #     "feed_description": "Providing a direct line of public health science to you",
    #     "title": "7 ways our health is tied to the planet’s",
    #     "url": "https://yourlocalepidemiologist.substack.com/p/7-ways-our-health-is-tied-to-the",
    #     "description": "Happy Earth Day!",
    #     "published": "Mon, 22 Apr 2024 21:09:53 GMT"
    # }

    # Records have fields: feed_title, feed_description, title, url, description, published
    # See ../rss_reader/app.py
    # print(f"URL: {record['url']}")

    # Now that we have the url, we can scrape it
    (fetched_title, fetched_content) = fetch_site_content(record["url"])
    print(f"Title: {fetched_title}")
    content_brief = fetched_content.replace("\n", " ")[:100]
    print(f"Content (first 100 chars): {content_brief}")

    # STOP if there is no content
    if not fetched_content:
        print("=" * 80)
        print("No content found, skipping")
        print("=" * 80)
        return

    # Now update the record and write it to the summarizer bucket
    record["title"] = fetched_title
    record["content"] = fetched_content

    write_to_summarizer_bucket(record)

    print("=" * 80)
    print(f"Successfully scraped url contents and wrote them to {SUMMARIZER_BUCKET}")
    print("=" * 80)


def write_to_summarizer_bucket(record):
    key = f"incoming/{uuid.uuid4()}"
    write_to_s3(SUMMARIZER_BUCKET, key, json.dumps(record))
