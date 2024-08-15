import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
DIGEST_QUEUE = "DailyMail-DigestQueue"
IMMEDIATE_QUEUE = "DailyMail-ImmediateQueue"
LLM = os.environ["LLM"] # set in lambda terraform
CONTEXT_WINDOW_SIZE = int(os.environ["CONTEXT_WINDOW_SIZE"]) # set in lambda terraform
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2")


def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{LLM=}")
    print(f"{CONTEXT_WINDOW_SIZE=}")
    print(f"{BEDROCK_REGION=}")
