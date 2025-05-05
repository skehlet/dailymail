import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
DIGEST_QUEUE = "DailyMail-DigestQueue"
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2")


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{BEDROCK_REGION=}")
