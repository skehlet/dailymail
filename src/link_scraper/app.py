import uuid
import json
from scrape import fetch_site_content
from app_s3 import write_to_s3
from app_settings import SUMMARIZER_BUCKET

def process_record(record):
    # print(record)

    # TODO: What to do about exceptions? e.g. JSON parse errors. I think
    # it'll just work to fail, and let it retry however many times, and then
    # fail it into the DLQ

    if not "eventSource" in record or record['eventSource'] != 'aws:sqs':
        raise Exception("Not an SQS event")

    body = json.loads(record['body'])
    print(f"Body: {body}")

    # Records have fields: id, title, link, description, published
    # See ../rss_reader/app.py
    # print(f"Link: {body['link']}")

    # Now that we have the link, we can scrape it
    (my_page_title, my_content) = fetch_site_content(body['link'])
    print(f"Title: {my_page_title}")
    print(f"Content: {my_content}")

    # Now store it in S3
    record = {
        "url": body['link'],
        "published": body['published'],
        "title": my_page_title,
        "content": my_content,
    }
    write_to_summarizer_bucket(record)

    print("=" * 80)
    print(f"Successfully scraped link contents and wrote them to {SUMMARIZER_BUCKET}")
    print("=" * 80)


def write_to_summarizer_bucket(record):
    key = f"incoming/{uuid.uuid4()}"
    write_to_s3(SUMMARIZER_BUCKET, key, json.dumps(record))