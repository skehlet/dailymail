import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
SCRAPER_QUEUE = "DailyMail-ScraperQueue"
LINK_READER_CREDS_PARAMETER_NAME = "DAILYMAIL_LINK_READER_CREDS"


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{SCRAPER_QUEUE=}")