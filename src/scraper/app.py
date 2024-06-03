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

    if not "eventSource" in record or record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    body = json.loads(record["body"])
    print(f"Body: {body}")

    # {
    #     "feed_title": "Your Local Epidemiologist",
    #     "feed_description": "Providing a direct line of public health science to you",
    #     "title": "7 ways our health is tied to the planet’s",
    #     "link": "https://yourlocalepidemiologist.substack.com/p/7-ways-our-health-is-tied-to-the",
    #     "description": "Happy Earth Day!",
    #     "published": "Mon, 22 Apr 2024 21:09:53 GMT"
    # }

    # Records have fields: feed_title, feed_description, title, link, description, published
    # See ../rss_reader/app.py
    # print(f"Link: {body['link']}")

    # Now that we have the link, we can scrape it
    (fetched_title, fetched_content) = fetch_site_content(body["link"])
    print(f"Title: {fetched_title}")
    print(f"Content: {fetched_content}")

    # Now store it in S3
    record = {
        "feed_title": body["feed_title"],
        "feed_description": body["feed_description"],
        "url": body["link"],
        "published": body["published"],
        "title": fetched_title,
        "content": fetched_content,
    }
    write_to_summarizer_bucket(record)

    print("=" * 80)
    print(f"Successfully scraped link contents and wrote them to {SUMMARIZER_BUCKET}")
    print("=" * 80)


def write_to_summarizer_bucket(record):
    key = f"incoming/{uuid.uuid4()}"
    write_to_s3(SUMMARIZER_BUCKET, key, json.dumps(record))
