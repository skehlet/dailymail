import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SCRAPER_QUEUE = "DailyMail-ScraperQueue"
LINK_READER_CREDS_PARAMETER_NAME = "DAILYMAIL_LINK_READER_CREDS"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SCRAPER_QUEUE=}")