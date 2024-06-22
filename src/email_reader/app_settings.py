import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")