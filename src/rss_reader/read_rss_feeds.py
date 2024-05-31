import feedparser
import boto3
from botocore.exceptions import ClientError

URLS = [
    "https://yourlocalepidemiologist.substack.com/feed",
]
ETAG_TABLE_NAME = "dailymail-rss-reader-etag-table"
ID_TABLE_NAME = "dailymail-rss-reader-id-table"

dynamodb = boto3.resource("dynamodb")
etag_table = dynamodb.Table(ETAG_TABLE_NAME)
id_table = dynamodb.Table(ID_TABLE_NAME)


def read_rss_feeds():
    for url in URLS:
        hit_feed(url)


def fetch_stored_etag(url):
    try:
        response = etag_table.get_item(Key={"url": url})
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


def store_etag(url, etag):
    try:
        etag_table.update_item(
            Key={"url": url},
            UpdateExpression="SET etag = :etag",
            ExpressionAttributeValues={":etag": {"S": etag}},
        )
        print(f"Successfully stored etag '{etag}' for URL '{url}' in DynamoDB table.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error storing etag in DynamoDB table: {error_code} - {error_message}")
        raise e


def fetch_stored_id(url, id) -> bool:
    try:
        response = id_table.get_item(Key={"url": url, "id": id})
        if "Item" not in response:
            print(f"No, we have not yet seen {url}/{id}")
            return False
        print(f"Yes, we have already seen {url}/{id}")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error checking DynamoDB for {url}/{id}: {error_code} - {error_message}")
        raise e


def store_id(url, id):
    try:
        id_table.put_item(Item={"url": url, "id": id})
        print(f"Successfully recorded we have seen {url}/{id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error updating DynamoDB for {url}/{id}: {error_code} - {error_message}")
        raise e


# def dump_rss_entries(entries):
#     for entry in entries:
#         id = entry.id
#         article_title = entry.title
#         article_link = entry.link
#         article_published_at = entry.published  # Unicode string
#         article_published_at_parsed = entry.published_parsed  # Time object
#         # article_author = entry.author  DOES NOT EXIST
#         content = entry.summary
#         # article_tags = entry.tags  DOES NOT EXIST
#         print(f"[{article_title}]({article_link})")
#         print(f"Id: {id}")
#         print(f"Published: {article_published_at}")
#         # print ("Published by {}".format(article_author))
#         print(f"Content: {content}")
#         print("")


def process_rss_entries(url, entries):
    for entry in entries:
        id = entry.id

        if fetch_stored_id(url, id):
            print(f"Already seen {url}/{id}")
            continue

        article_title = entry.title
        article_link = entry.link
        article_published_at = entry.published  # Unicode string
        article_published_at_parsed = entry.published_parsed  # Time object
        # article_author = entry.author  DOES NOT EXIST
        content = entry.summary
        # article_tags = entry.tags  DOES NOT EXIST
        print(f"[{article_title}]({article_link})")
        print(f"Id: {id}")
        print(f"Published: {article_published_at}")
        # print ("Published by {}".format(article_author))
        print(f"Content: {content}")
        print("")

        store_id(url, id)


def hit_feed(url):
    etag = fetch_stored_etag(url)
    feed = feedparser.parse(
        url,
        etag=etag,
    )

    print(f"URL: {url}")
    print(f"Status: {feed.status}")
    print(f"Etag: {feed.etag}")

    if feed.etag != etag:
        store_etag(url, feed.etag)

    # dump_rss_entries(feed.entries)

    process_rss_entries(url, feed.entries)


if __name__ == "__main__":
    read_rss_feeds()
