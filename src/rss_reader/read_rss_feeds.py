import feedparser
from db import (
    get_feed_metadata,
    store_feed_metadata,
    id_already_processed,
    mark_id_as_processed,
)

# TODO: move to dynamic location, e.g. ParameterStore?
URLS = [
    "https://yourlocalepidemiologist.substack.com/feed",
]


def process_rss_entries(url, entries):
    for entry in entries:
        id = entry.id

        if id_already_processed(url, id):
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

        mark_id_as_processed(url, id)


def read_feed(url):
    print(f"URL: {url}")
    (etag, last_modified) = get_feed_metadata(url)
    print(f"Previous Etag: {etag}")
    print(f"Previous Last modified: {last_modified}")

    d = feedparser.parse(
        url,
        etag=etag,
        modified=last_modified,
    )

    print(f"Status: {d.status}")
    if "etag" in d:
        new_etag = d.etag
        print(f"Etag: {new_etag}")
    else:
        new_etag = None
    if "modified" in d:
        new_last_modified = d.modified
        print(f"Last modified: {new_last_modified}")
    else:
        new_last_modified = None
    print(f"Title: {d.feed.get('title', 'Unknown')}")
    print(f"Description: {d.feed.get('description', 'Unknown')}")
    print(f"Published: {d.feed.get('published', 'Unknown')}")

    if new_etag != etag or new_last_modified != last_modified:
        store_feed_metadata(url, new_etag, new_last_modified)

    process_rss_entries(url, d.entries)


def read_rss_feeds():
    for url in URLS:
        read_feed(url)


if __name__ == "__main__":
    read_rss_feeds()
