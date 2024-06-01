import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
# TODO: move to dynamic location, e.g. ParameterStore?
RSS_FEEDS = [
    "https://yourlocalepidemiologist.substack.com/feed",
]
SCRAPER_QUEUE = "DailyMail-ScraperQueue"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{RSS_FEEDS=}")
