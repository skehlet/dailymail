import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
RSS_FEEDS_PARAMETER_NAME = "DAILY_MAIL_RSS_FEEDS"
SCRAPER_QUEUE = "DailyMail-ScraperQueue"


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{RSS_FEEDS_PARAMETER_NAME=}")
    print(f"{SCRAPER_QUEUE=}")