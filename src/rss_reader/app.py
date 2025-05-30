import json
from urllib.parse import urlparse, parse_qs
import feedparser
from app_settings import RSS_FEEDS_PARAMETER_NAME, SCRAPER_QUEUE
from db import (
    get_feed_metadata,
    store_feed_metadata,
    id_already_processed,
    mark_id_as_processed,
    cleanup_processed_ids,
)
from app_queue import enqueue
import boto3


def read_rss_feeds():
    for feed_config in get_rss_feeds():
        if isinstance(feed_config, str):
            feed_url = feed_config
            feed_context = None
        else:
            feed_url = feed_config["url"]
            feed_context = feed_config.get("context")
        read_feed(feed_url, feed_context)
    cleanup_processed_ids()


def get_rss_feeds():
    # fetch the list of rss feeds from AWS parameter store
    ssm = boto3.client("ssm")
    parameter = ssm.get_parameter(Name=RSS_FEEDS_PARAMETER_NAME)
    return json.loads(parameter["Parameter"]["Value"])


def read_feed(feed_url, feed_context=None):
    print(f"URL: {feed_url}")
    (previous_etag, previous_last_modified) = get_feed_metadata(feed_url)
    print(f"Previous Etag: {previous_etag}")
    print(f"Previous Last modified: {previous_last_modified}")

    d = feedparser.parse(
        feed_url,
        etag=previous_etag,
        modified=previous_last_modified,
    )

    # I've had AttributeErrors where status is missing (network issue? unknown network problem?). Check and handle. 
    if not hasattr(d, "status"):
        print("No status attribute in feedparser response, not sure why, just skipping this feed for now")
        return

    print(f"Status: {d.status}")
    if "etag" in d:
        etag = d.etag
        print(f"Etag: {etag}")
    else:
        etag = None
    if "modified" in d:
        last_modified = d.modified
        print(f"Last modified: {last_modified}")
    else:
        last_modified = None
    feed_title = d.feed.get("title", "Unknown")
    feed_description = d.feed.get("description", "Unknown")

    print(f"Feed title: {feed_title}")
    print(f"Feed description: {feed_description}")
    print(f"Feed published: {d.feed.get('published', 'Unknown')}")

    process_rss_entries(feed_url, feed_title, feed_description, feed_context, d.entries)

    # Note Google Alerts does NOT provide either ETag nor Last-Modified
    if etag != previous_etag or last_modified != previous_last_modified:
        store_feed_metadata(feed_url, etag, last_modified)


def process_rss_entries(url, feed_title, feed_description, feed_context, entries):
    for entry in entries:
        if "link" not in entry:
            print("Skipping entry without link")
            continue

        article_url = remove_redirectors_from_url(entry.link)

        if "id" in entry:
            article_id = entry.id
        else:
            article_id = article_url

        if id_already_processed(url, article_id):
            print(f"Already seen {url}/{article_id}")
            continue

        article_title = entry.title
        article_description = entry.description
        article_published = entry.published
        article_content = entry.summary

        print(f"=== {article_id}")
        print(f"Title: {article_title}")
        print(f"URL: {article_url}")
        # print(f"Description: {article_description}")
        print(f"Published: {article_published}")
        # print(f"Content: {article_content}")
        print("")

        record = {
            "type": "rss_entry",
            "feed_title": feed_title,
            "feed_description": feed_description,
            "feed_context": feed_context,
            "title": article_title,
            "url": article_url,
            "description": article_description,
            "published": article_published,
        }
        write_to_queue(record)

        mark_id_as_processed(url, article_id)


def remove_redirectors_from_url(url):
    """
    For example:
    https://www.google.com/url?rct=j&sa=t&url=https://www.caranddriver.com/news/a46717089/vw-id-buzz-super-bowl-ad-sale-date/&ct=ga&cd=CAEYACoUMTMxODg2NDY3Mzc0MzM4Mzc1OTMyGjUwNWZiNzdjNjQ5ODI4MzI6Y29tOmVuOlVT&usg=AOvVaw28L7Vbwdv_m3WH6gCBCnK8
    Extract out that `url` part of the query string, and return it
    """
    if url.startswith("https://www.google.com/url?"):
        return parse_qs(urlparse(url).query)["url"][0]
    else:
        return url


def write_to_queue(entry):
    enqueue(SCRAPER_QUEUE, json.dumps(entry))


if __name__ == "__main__":
    read_rss_feeds()
    # from db import (
    #     add_updated_at_field_where_missing,
    #     clear_updated_at_fields,
    # )
    # # clear_updated_at_fields()
    # # add_updated_at_field_where_missing()
    # cleanup_processed_ids()
