import json
from urllib.parse import urlparse, parse_qs
import feedparser
from app_settings import RSS_FEEDS_PARAMETER_NAME, SCRAPER_QUEUE
from db import (
    get_feed_metadata,
    store_feed_metadata,
    id_already_processed,
    mark_id_as_processed,
)
from app_queue import enqueue
import boto3


def read_rss_feeds():
    for url in get_rss_feeds():
        read_feed(url)


def get_rss_feeds():
    # fetch the list of rss feeds from AWS parameter store
    ssm = boto3.client("ssm")
    parameter = ssm.get_parameter(Name=RSS_FEEDS_PARAMETER_NAME)
    return json.loads(parameter["Parameter"]["Value"])


def read_feed(feed_url):
    print(f"URL: {feed_url}")
    (previous_etag, previous_last_modified) = get_feed_metadata(feed_url)
    print(f"Previous Etag: {previous_etag}")
    print(f"Previous Last modified: {previous_last_modified}")

    d = feedparser.parse(
        feed_url,
        etag=previous_etag,
        modified=previous_last_modified,
    )

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

    process_rss_entries(feed_url, feed_title, feed_description, d.entries)

    # Note Google Alerts does NOT provide either ETag nor Last-Modified
    if etag != previous_etag or last_modified != previous_last_modified:
        store_feed_metadata(feed_url, etag, last_modified)


def process_rss_entries(url, feed_title, feed_description, entries):
    for entry in entries:
        article_id = entry.id

        if id_already_processed(url, article_id):
            print(f"Already seen {url}/{article_id}")
            continue

        article_title = entry.title
        article_link = remove_redirectors_from_link(entry.link)
        article_description = entry.description
        article_published = entry.published
        article_content = entry.summary

        print(f"=== {article_id}")
        print(f"Title: {article_title}")
        print(f"Link: {article_link}")
        print(f"Description: {article_description}")
        print(f"Published: {article_published}")
        print(f"Content: {article_content}")
        print("")

        if not article_content:
            # Skip if article_content is empty. For
            # https://www.platformer.news/rss/ at least, that would seem to
            # indicate an entry is paid-only.
            print("Skipping empty content")
        else:
            record = {
                "feed_title": feed_title,
                "feed_description": feed_description,
                "title": article_title,
                "link": article_link,
                "description": article_description,
                "published": article_published,
            }
            write_to_queue(record)

        mark_id_as_processed(url, article_id)


def remove_redirectors_from_link(link):
    """
    For example:
    https://www.google.com/url?rct=j&sa=t&url=https://www.caranddriver.com/news/a46717089/vw-id-buzz-super-bowl-ad-sale-date/&ct=ga&cd=CAEYACoUMTMxODg2NDY3Mzc0MzM4Mzc1OTMyGjUwNWZiNzdjNjQ5ODI4MzI6Y29tOmVuOlVT&usg=AOvVaw28L7Vbwdv_m3WH6gCBCnK8
    Extract out that `url` part of the query string, and return it
    """
    if link.startswith("https://www.google.com/url?"):
        return parse_qs(urlparse(link).query)["url"][0]
    else:
        return link


def write_to_queue(entry):
    enqueue(SCRAPER_QUEUE, json.dumps(entry))


if __name__ == "__main__":
    read_rss_feeds()
