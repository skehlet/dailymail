import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
PAYWALL_TEXTS = [
    "This post is for paid subscribers",
    "This post is for paying subscribers only",
]


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
