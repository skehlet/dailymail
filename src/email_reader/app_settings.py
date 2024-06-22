import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
DIGEST_EMAIL_FROM = os.environ.get("DIGEST_EMAIL_FROM", "digest@ai.stevekehlet.com")


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
    print(f"{DIGEST_EMAIL_FROM=}")
