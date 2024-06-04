import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
DIGEST_QUEUE = "DailyMail-DigestQueue"

def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{DIGEST_QUEUE=}")
