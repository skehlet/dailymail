import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
DIGEST_QUEUE = "DailyMail-DigestQueue"
EMAIL_INLINE_CSS_STYLE = "color:#444; font: 16px/1.5 -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji"
MY_TIMEZONE = "US/Pacific"
DIGEST_EMAIL_FROM = os.environ.get("DIGEST_EMAIL_FROM", "digest@ai.stevekehlet.com")
DIGEST_EMAIL_TO = os.environ.get("DIGEST_EMAIL_TO", "steve.kehlet@gmail.com")


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{MY_TIMEZONE=}")
    print(f"{DIGEST_EMAIL_FROM=}")
