import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SCRAPER_QUEUE = "DailyMail-ScraperQueue"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SCRAPER_QUEUE=}")