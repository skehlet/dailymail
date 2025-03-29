import os

PIPELINE_EXECUTION_ID = os.environ.get("PIPELINE_EXECUTION_ID", "Unknown")
DIGEST_QUEUE = "DailyMail-DigestQueue"
MY_TIMEZONE = "US/Pacific"
DIGEST_EMAIL_FROM = os.environ.get("DIGEST_EMAIL_FROM", "digest@ai.stevekehlet.com")
DIGEST_EMAIL_TO = os.environ.get("DIGEST_EMAIL_TO", "steve.kehlet@gmail.com")
# Claude model ID for digest generation
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2")


def show_settings():
    print(f"{PIPELINE_EXECUTION_ID=}")
    print(f"{DIGEST_QUEUE=}")
    print(f"{MY_TIMEZONE=}")
    print(f"{DIGEST_EMAIL_FROM=}")
    print(f"{DIGEST_EMAIL_TO=}")
    print(f"{BEDROCK_MODEL_ID=}")
    print(f"{BEDROCK_REGION=}")
