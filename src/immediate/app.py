import json
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from app_settings import IMMEDIATE_EMAIL_FROM, IMMEDIATE_EMAIL_TO, MY_TIMEZONE
from shared.my_email_lib import send_email


def process_record(sqs_record):
    print(sqs_record)

    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    record = json.loads(sqs_record["body"])
    print(f"Record: {record}")

    # {
    #     "url": "https://yourlocalepidemiologist.substack.com/p/7-ways-our-health-is-tied-to-the",
    #     "summary": "....."
    # }

    # need some of the email logic from ../digest

    # Email it using SES
    subject = f"Your Summary - {utc_to_local(datetime.now(timezone.utc)).strftime('%Y-%m-%d %H:%M %Z')}"
    print("-" * 80)
    print(f"Subject: {subject}")
    print("Body:")
    email = record["summary"]
    print(email)
    send_email(IMMEDIATE_EMAIL_FROM, IMMEDIATE_EMAIL_TO, subject, html=email)


# TODO: copy/paste
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(MY_TIMEZONE))
