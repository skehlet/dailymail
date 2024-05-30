import os

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
REPLY_FROM = os.environ.get("REPLY_FROM", "summarize@ai.stevekehlet.com")


def show_settings():
    print(f"{LLM=}")
    print(f"{REPLY_FROM=}")
