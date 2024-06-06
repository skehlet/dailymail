import os

BUILD_ID = os.environ.get("BUILD_ID", "Unknown")
SUMMARIZER_BUCKET = os.environ.get("SUMMARIZER_BUCKET", "skehlet-dailymail-summarizer")
DIGEST_QUEUE = "DailyMail-DigestQueue"
IMMEDIATE_QUEUE = "DailyMail-ImmediateQueue"
LLM = os.environ.get(
    "LLM",
    # "mistral.mixtral-8x7b-instruct-v0:1",
    # "mistral.mistral-large-2402-v1:0",
    "gpt-4o",
)
CONTEXT_WINDOW_SIZE = int(os.environ.get(
    "CONTEXT_WINDOW_SIZE",
    # "32000", # mistral
    "128000", # gpt-4o
))
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2")

def show_settings():
    print(f"{BUILD_ID=}")
    print(f"{SUMMARIZER_BUCKET=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{LLM=}")
    print(f"{CONTEXT_WINDOW_SIZE=}")
    print(f"{BEDROCK_REGION=}")
