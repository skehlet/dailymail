"""
Per-topic memory of what has already been reported for each Google Alert.

Each topic's ledger is a small JSON document in S3 at alerts/<slug>.json. It is
meant to be human-readable and hand-editable, e.g.:

    aws s3 cp s3://skehlet-dailymail-alert-ledger/alerts/gta-6-pc-release-date.json -

The bucket is versioned, so a bad update can be rolled back.
"""
import json
import re
from typing import List
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field
from .app_settings import ALERT_LEDGER_BUCKET

s3 = boto3.client("s3")


class LedgerFact(BaseModel):
    date: str = Field(description="Date the fact was first reported to the reader, YYYY-MM-DD.")
    fact: str = Field(description="One self-contained statement of fact or claim.")
    status: str = Field(description="CONFIRMED (official/verified) or RUMOR (leak, speculation, unnamed sources).")


class Ledger(BaseModel):
    topic: str
    facts: List[LedgerFact] = []


def topic_slug(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")


def ledger_key(topic: str) -> str:
    return f"alerts/{topic_slug(topic)}.json"


def load_ledger(topic: str) -> Ledger:
    try:
        response = s3.get_object(Bucket=ALERT_LEDGER_BUCKET, Key=ledger_key(topic))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"No ledger yet for topic {topic!r}, starting empty")
            return Ledger(topic=topic)
        raise
    return Ledger(**json.loads(response["Body"].read().decode("utf-8")))


def save_ledger(ledger: Ledger):
    s3.put_object(
        Bucket=ALERT_LEDGER_BUCKET,
        Key=ledger_key(ledger.topic),
        Body=json.dumps(ledger.model_dump(), indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Saved ledger for topic {ledger.topic!r} with {len(ledger.facts)} facts")
