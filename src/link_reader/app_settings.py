import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SCRAPER_QUEUE = "DailyMail-ScraperQueue"
LINK_READER_CREDS_SECRET_NAME = "DAILYMAIL_LINK_READER_CREDS"
LINK_READER_SECRETS_REGION = "us-west-2"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SCRAPER_QUEUE=}")