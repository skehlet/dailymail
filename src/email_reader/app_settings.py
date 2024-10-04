import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
DIGEST_EMAIL_FROM = os.environ.get("DIGEST_EMAIL_FROM", "digest@ai.stevekehlet.com")


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
    print(f"{DIGEST_EMAIL_FROM=}")
