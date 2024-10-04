import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
IMMEDIATE_EMAIL_FROM = os.environ.get("IMMEDIATE_EMAIL_FROM", "summary@ai.stevekehlet.com")
IMMEDIATE_EMAIL_TO = os.environ.get("IMMEDIATE_EMAIL_TO", "steve.kehlet@gmail.com")
MY_TIMEZONE = "US/Pacific"


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{IMMEDIATE_EMAIL_FROM=}")
    print(f"{IMMEDIATE_EMAIL_TO=}")
    print(f"{MY_TIMEZONE=}")

