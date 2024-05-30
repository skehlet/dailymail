import feedparser
import boto3
from botocore.exceptions import ClientError

URLS = [
    "https://yourlocalepidemiologist.substack.com/feed",
]
ETAG_TABLE_NAME = "dailymail-rss-reader-etag-table"

dynamodb = boto3.client("dynamodb")


def read_rss_feeds():
    for url in URLS:
        hit_feed(url)


def fetch_stored_etag(url):
    key = {"url": {"S": url}}
    try:
        response = dynamodb.get_item(TableName=ETAG_TABLE_NAME, Key=key)
        if "Item" not in response:
            print(f"No etag found in DynamoDB table for URL {url}.")
            return None
        etag = response["Item"]["etag"]["S"]
        print(f"Retrieved etag '{etag}' from DynamoDB table for URL {url}.")
        return etag
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(
            f"Error retrieving etag from DynamoDB table: {error_code} - {error_message}"
        )
        raise e


def dump_rss_entries(entries):
    for entry in entries:
        id = entry.id
        article_title = entry.title
        article_link = entry.link
        article_published_at = entry.published  # Unicode string
        article_published_at_parsed = entry.published_parsed  # Time object
        # article_author = entry.author  DOES NOT EXIST
        content = entry.summary
        # article_tags = entry.tags  DOES NOT EXIST
        print(f"[{article_title}]({article_link})")
        print(f"Id {id}")
        print(f"Published at {article_published_at}")
        # print ("Published by {}".format(article_author))
        print(f"Content {content}")
        print("")


def hit_feed(url):
    etag = fetch_stored_etag(url)
    feed = feedparser.parse(
        url,
        etag=etag,
    )

    print(f"Status: {feed.status}")
    print(f"Etag: {feed.etag}")

    dump_rss_entries(feed.entries)

    # Put the etag in the DynamoDB table
    item = {"url": {"S": url}, "etag": {"S": feed.etag}}
    try:
        dynamodb.put_item(TableName=ETAG_TABLE_NAME, Item=item)
        print(
            f"Successfully stored etag '{feed.etag}' for URL '{url}' in DynamoDB table."
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error storing etag in DynamoDB table: {error_code} - {error_message}")
        raise e
