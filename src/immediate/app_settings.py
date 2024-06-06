import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
IMMEDIATE_EMAIL_FROM = os.environ.get("IMMEDIATE_EMAIL_FROM", "summary@ai.stevekehlet.com")
IMMEDIATE_EMAIL_TO = os.environ.get("IMMEDIATE_EMAIL_TO", "steve.kehlet@gmail.com")
MY_TIMEZONE = "US/Pacific"


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{IMMEDIATE_EMAIL_FROM=}")
    print(f"{IMMEDIATE_EMAIL_TO=}")
    print(f"{MY_TIMEZONE=}")

