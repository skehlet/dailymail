import uuid
import json
from scrape import fetch_site_content
from app_settings import SUMMARIZER_BUCKET
from shared.app_s3 import write_to_s3


def process_record(sqs_record):
    # print(sqs_record)

    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    record = json.loads(sqs_record["body"])
    print(f"Record: {record}")

    # Records with type=rss_entry have fields: feed_title, feed_description, title, url, description, published
    # Records with type=url have fields: url
    print(f"URL: {record['url']}")
    scrape_url(record)


def scrape_url(record):
    """
    Given a record with a url, scrape the content and write it to the summarizer bucket
    """
    # Now that we have the url, we can scrape it
    (fetched_title, fetched_content, is_paywalled) = fetch_site_content(record["url"])
    print(f"Title: {fetched_title}")
    content_brief = fetched_content.replace("\n", " ")[:100]
    print(f"Content (first 100 chars): {content_brief}")
    print(f"Is paywalled: {is_paywalled}")

    # STOP if there is no content
    if not fetched_content:
        print("No content found, skipping")
        return

    # STOP if the content appears to be paywalled
    if is_paywalled:
        print("Content appears to be paywalled, skipping")
        return

    # Now update the record and write it to the summarizer bucket
    record["title"] = fetched_title
    record["content"] = fetched_content

    write_to_summarizer_bucket(record)

    print(f"Successfully scraped url contents and wrote them to {SUMMARIZER_BUCKET}")


def write_to_summarizer_bucket(record):
    key = f"incoming/{uuid.uuid4()}"
    write_to_s3(SUMMARIZER_BUCKET, key, json.dumps(record))


if __name__ == "__main__":
    scrape_url({
        "url": "https://www.platformer.news/riaa-ai-lawsuit-suno-udio/", # paywalled
    })
