import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
DIGEST_QUEUE = "DailyMail-DigestQueue"
EMAIL_INLINE_CSS_STYLE = "color:#444; font: 16px/1.5 -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji"

def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{DIGEST_QUEUE=}")
