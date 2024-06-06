import json
import time
import random
import openai
from app_s3 import read_from_s3, delete_from_s3
from app_queue import enqueue
from app_settings import SUMMARIZER_BUCKET, DIGEST_QUEUE, IMMEDIATE_QUEUE
from google_alerts import is_google_alert, get_topic_from_google_alert_title
from summarize import llm_summarize_text


def process_record(s3_notification):
    # print(s3_notification)

    if not "eventSource" in s3_notification or s3_notification["eventSource"] != "aws:s3":
        raise Exception("Not an S3 notification event")

    key = s3_notification["s3"]["object"]["key"]
    record = json.loads(read_from_s3(SUMMARIZER_BUCKET, key))
    # record has fields: feed_title, feed_description, url, published, title, content
    # or for immediate links: url, title, content
    print(record)

    # STOP if there is no content
    if record["content"] == "":
        print(f"No content for {key}")
        return

    # if the feed_title is a Google Alert, extract the topic
    if is_google_alert(record["feed_title"]):
        topic = get_topic_from_google_alert_title(record["feed_title"])
        print(f"Google Alert Topic: {topic}")
    else:
        topic = None

    # Now, summarize the content. Retry on rate limit errors.
    tries_left = 3
    while tries_left > 0:
        try:
            summary = llm_summarize_text(record["content"], topic)
            break
        except openai.RateLimitError:
            sleep_time = random.randint(10, 30)
            print(f"Rate limit error encounter, sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
            tries_left -= 1

    del record["content"]
    record["summary"] = summary

    if "immediate" in record:
        # Send to immediate queue
        enqueue(IMMEDIATE_QUEUE, json.dumps(record))

    else:
        # Send to digest queue
        # But skip if it's NOT RELEVANT
        # TODO: consider forcing the LLM to generate JSON responses. But this is working fine for now.
        if "NOT RELEVANT" in summary:
            print("The content is NOT RELEVANT to the topic, not enqueuing into the digest queue")
        else:
            enqueue(DIGEST_QUEUE, json.dumps(record))

    delete_from_s3(SUMMARIZER_BUCKET, key)

    print("=" * 80)
    print(f"Successfully summarized content for {key}")
    print("=" * 80)
