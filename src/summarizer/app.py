import json
from app_s3 import read_from_s3, delete_from_s3
from app_queue import enqueue
from app_settings import SUMMARIZER_BUCKET, DIGEST_QUEUE, IMMEDIATE_QUEUE
from google_alerts import is_google_alert, get_topic_from_google_alert_title
from summarize import summarize_text, summarize_google_alert


def process_sqs_record(sqs_record):
    # print(sqs_record)
    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")
    s3_records = json.loads(sqs_record["body"])
    for s3_record in s3_records["Records"]:
        process_s3_record(s3_record)


def process_s3_record(s3_record):
    # print(s3_record)
    if not "eventSource" in s3_record or s3_record["eventSource"] != "aws:s3":
        raise Exception("Not an S3 event")

    key = s3_record["s3"]["object"]["key"]
    record = json.loads(read_from_s3(SUMMARIZER_BUCKET, key))
    # records with type=rss_entry have fields: feed_title, feed_description, url, published, title, content
    # records with type=immediate have fields: url, title, content
    # print(record)

    # STOP if there is no content
    if "content" not in record or record["content"] == "":
        print(f"No content for {key}")
        return

    if "type" in record and record["type"] == "rss_entry" and is_google_alert(record["feed_title"]):
        # if type=rss_entry and the feed_title is a Google Alert, extract the topic and summarize
        topic = get_topic_from_google_alert_title(record["feed_title"])
        print(f"Google Alert Topic: {topic}")
        summary_dict = summarize_google_alert(topic, record["url"], record["title"], record["content"])
    else:
        # else just summarize the text
        summary_dict = summarize_text(record["url"], record["title"], record["content"])

    # copy all fields from summary_dict to record
    for field in summary_dict:
        record[field] = summary_dict[field]

    del record["content"]

    if "immediate" in record:
        # Send to immediate queue
        enqueue(IMMEDIATE_QUEUE, json.dumps(record))

    else:
        # Send to digest queue
        # But skip if it's a Google Alert summary and NOT RELEVANT
        if "relevance" in summary_dict and summary_dict["relevance"] == "NOT RELEVANT":
            print("The content is NOT RELEVANT to the topic, so discarding")
        else:
            enqueue(DIGEST_QUEUE, json.dumps(record))

    delete_from_s3(SUMMARIZER_BUCKET, key)

    print(f"Successfully summarized content for {key}")
