import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
RSS_FEEDS_PARAMETER_NAME = "DAILY_MAIL_RSS_FEEDS"
SCRAPER_QUEUE = "DailyMail-ScraperQueue"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{RSS_FEEDS_PARAMETER_NAME=}")
    print(f"{SCRAPER_QUEUE=}")