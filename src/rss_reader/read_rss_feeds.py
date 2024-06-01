import json
import feedparser
from app_settings import RSS_FEEDS
from db import (
    get_feed_metadata,
    store_feed_metadata,
    id_already_processed,
    mark_id_as_processed,
)
from app_queue import enqueue


def read_rss_feeds():
    for url in RSS_FEEDS:
        read_feed(url)


def read_feed(url):
    print(f"URL: {url}")
    (previous_etag, previous_last_modified) = get_feed_metadata(url)
    print(f"Previous Etag: {previous_etag}")
    print(f"Previous Last modified: {previous_last_modified}")

    d = feedparser.parse(
        url,
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
    print(f"Title: {d.feed.get('title', 'Unknown')}")
    print(f"Description: {d.feed.get('description', 'Unknown')}")
    print(f"Published: {d.feed.get('published', 'Unknown')}")

    process_rss_entries(url, d.entries)

    if etag != previous_etag or last_modified != previous_last_modified:
        store_feed_metadata(url, etag, last_modified)


def process_rss_entries(url, entries):
    for entry in entries:
        article_id = entry.id

        if id_already_processed(url, article_id):
            print(f"Already seen {url}/{article_id}")
            continue

        article_title = entry.title
        article_link = entry.link
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

        record = {
            "id": article_id,
            "title": article_title,
            "link": article_link,
            "description": article_description,
            "published": article_published,
        }

        write_to_queue(record)

        mark_id_as_processed(url, article_id)


def write_to_queue(entry):
    enqueue("DailyMail-ScrapeQueue", json.dumps(entry))


if __name__ == "__main__":
    read_rss_feeds()
