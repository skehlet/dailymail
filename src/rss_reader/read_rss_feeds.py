import feedparser
from db import (
    get_last_seen_etag,
    store_seen_etag,
    have_already_processed_id,
    store_processed_id,
)

URLS = [
    "https://yourlocalepidemiologist.substack.com/feed",
]


def process_rss_entries(url, entries):
    for entry in entries:
        id = entry.id

        if have_already_processed_id(url, id):
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

        store_processed_id(url, id)


def read_feed(url):
    etag = get_last_seen_etag(url)
    feed = feedparser.parse(
        url,
        etag=etag,
    )

    print(f"URL: {url}")
    print(f"Status: {feed.status}")
    print(f"Etag: {feed.etag}")

    if feed.etag != etag:
        store_seen_etag(url, feed.etag)

    process_rss_entries(url, feed.entries)


def read_rss_feeds():
    for url in URLS:
        read_feed(url)


if __name__ == "__main__":
    read_rss_feeds()
