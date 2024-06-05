import json
from app_s3 import read_from_s3, delete_from_s3
from app_queue import enqueue
from app_settings import SUMMARIZER_BUCKET, DIGEST_QUEUE
from google_alerts import is_google_alert, get_topic_from_google_alert_title
from summarize import llm_summarize_text


def process_record(record):
    # print(record)

    if not "eventSource" in record or record["eventSource"] != "aws:s3":
        raise Exception("Not an S3 notification event")

    key = record["s3"]["object"]["key"]
    body = json.loads(read_from_s3(SUMMARIZER_BUCKET, key))
    # body has fields: feed_title, feed_description, url, published, title, content
    print(body)

    # STOP if there is no content
    if body["content"] == "":
        print(f"No content for {key}")
        return

    # if the feed_title is a Google Alert, extract the topic
    if is_google_alert(body["feed_title"]):
        topic = get_topic_from_google_alert_title(body["feed_title"])
        print(f"Google Alert Topic: {topic}")
    else:
        topic = None

    # now, summarize the content
    summary = llm_summarize_text(body["content"], topic)

    # Skip enqueuing to the next step if it's NOT RELEVANT
    # TODO: consider forcing the LLM to generate JSON responses. But this is working fine for now.
    if "NOT RELEVANT" in summary:
        print("The content is NOT RELEVANT to the topic, not enqueuing into the digest queue")
    else:
        outgoing_record = {
            "feed_title": body["feed_title"],
            "feed_description": body["feed_description"],
            "url": body["url"],
            "published": body["published"],
            "title": body["title"],
            "summary": summary,
        }
        enqueue(DIGEST_QUEUE, json.dumps(outgoing_record))

    delete_from_s3(SUMMARIZER_BUCKET, key)

    print("=" * 80)
    print(f"Successfully summarized content for {key}")
    print("=" * 80)