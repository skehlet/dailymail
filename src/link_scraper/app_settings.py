import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")

def show_settings():
    print(f"{BUILD_ID=}")
