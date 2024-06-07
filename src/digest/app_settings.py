import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
DIGEST_QUEUE = "DailyMail-DigestQueue"
MY_TIMEZONE = "US/Pacific"
DIGEST_EMAIL_FROM = os.environ.get("DIGEST_EMAIL_FROM", "digest@ai.stevekehlet.com")
DIGEST_EMAIL_TO = os.environ.get("DIGEST_EMAIL_TO", "steve.kehlet@gmail.com")


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{MY_TIMEZONE=}")
    print(f"{DIGEST_EMAIL_FROM=}")
