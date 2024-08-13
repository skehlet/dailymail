import json
import time
import random
import openai
from app_s3 import read_from_s3, delete_from_s3
from app_queue import enqueue
from app_settings import SUMMARIZER_BUCKET, DIGEST_QUEUE, IMMEDIATE_QUEUE
from google_alerts import is_google_alert, get_topic_from_google_alert_title
from summarize import llm_summarize_text


def process_sqs_record(sqs_record):
    # print(sqs_record)

    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    # {
    #     "messageId": "1d12c895-e3d6-4918-baae-0a5f76b7bbf5",
    #     "receiptHandle": "AQEBX1Sb7Ogy6BG3+NFoyTZq/wprS/ZJ85edxb+bt3eRfGsV6W7QNngw1XQySBuf9Sw2eytg6B7j0gH1GDz0aIqmnwByRiWh5nK2qNKaa5fxcGe3jYgWRfmvqqEhPt/st8lkmPYQxlnQCt4omuNy3QaiVW01UsoQtD97JvEiyA8jeGlYiCFMHjs+dF4H4HVH4KIIKilyNQuAmAXgiz57Pqgdt7XNxMXZ6oim2ebEOjdAX8Rr0dDpCVqlc4N6svks/h9x7wrWv4iGLeGq/VAf9UI6dYS+z23jfrxKuFWaJ5JBTr/uk5R3vaPG6chMqHmudTe7DirL/16ulhetIn53d9bshkEncaW1R/tKSyZy0CCqbC39Xstr8urk59rsCBAFgXV/Ib8YsXwy4CkzHLQLd1ksqJBduyeGDg8TK0eZPhd6RU4=",
    #     "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-west-2\",\"eventTime\":\"2024-06-06T21:58:41.434Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AROAXSBDWAHN3VFJDKGBT:DailyMail-Scraper\"},\"requestParameters\":{\"sourceIPAddress\":\"52.89.31.99\"},\"responseElements\":{\"x-amz-request-id\":\"H29QT00WDDFAAJMY\",\"x-amz-id-2\":\"MvRr9X23iKDLTpeOMza\/u9VtNZQAr3diRxA1Lyu8jxBkS\/xgmnJ8tVDZF4CbvDWYMtteq1vPUamV9w3Gp\/UznVbif2J8vunn\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"tf-s3-queue-20240606214636744500000001\",\"bucket\":{\"name\":\"skehlet-dailymail-summarizer\",\"ownerIdentity\":{\"principalId\":\"AWSI8VF2BUGCP\"},\"arn\":\"arn:aws:s3:::skehlet-dailymail-summarizer\"},\"object\":{\"key\":\"incoming\/5c3d2fe3-a84d-415d-b424-48c188be7bf8\",\"size\":12685,\"eTag\":\"7d2162c5becd09e8980d41eab549fe84\",\"sequencer\":\"006662311166568017\"}}}]}",
    #     "attributes": {
    #         "ApproximateReceiveCount": "1",
    #         "AWSTraceHeader": "Root=1-66623100-222a9d7cb7b9dbae7b7eb76e;Parent=2534599940abebe6;Sampled=0",
    #         "SentTimestamp": "1717711122679",
    #         "SenderId": "AROAUWHQT37XQVCB4XU5S:S3-PROD-END",
    #         "ApproximateFirstReceiveTimestamp": "1717711122680"
    #     },
    #     "messageAttributes": {},
    #     "md5OfMessageAttributes": null,
    #     "md5OfBody": "20c610356e06e1a6dccbeeb9abb9d290",
    #     "eventSource": "aws:sqs",
    #     "eventSourceARN": "arn:aws:sqs:us-west-2:519765885403:DailyMail-SummarizerQueue",
    #     "awsRegion": "us-west-2"
    # }

    s3_records = json.loads(sqs_record["body"])
    # print(f"S3 Records: {s3_records}")

    # {
    #     "Records": [
    #         {
    #             "eventVersion": "2.1",
    #             "eventSource": "aws:s3",
    #             "awsRegion": "us-west-2",
    #             "eventTime": "2024-06-06T21:58:41.434Z",
    #             "eventName": "ObjectCreated:Put",
    #             "userIdentity": {
    #                 "principalId": "AWS:AROAXSBDWAHN3VFJDKGBT:DailyMail-Scraper"
    #             },
    #             "requestParameters": {
    #                 "sourceIPAddress": "52.89.31.99"
    #             },
    #             "responseElements": {
    #                 "x-amz-request-id": "H29QT00WDDFAAJMY",
    #                 "x-amz-id-2": "MvRr9X23iKDLTpeOMza/u9VtNZQAr3diRxA1Lyu8jxBkS/xgmnJ8tVDZF4CbvDWYMtteq1vPUamV9w3Gp/UznVbif2J8vunn"
    #             },
    #             "s3": {
    #                 "s3SchemaVersion": "1.0",
    #                 "configurationId": "tf-s3-queue-20240606214636744500000001",
    #                 "bucket": {
    #                     "name": "skehlet-dailymail-summarizer",
    #                     "ownerIdentity": {
    #                         "principalId": "AWSI8VF2BUGCP"
    #                     },
    #                     "arn": "arn:aws:s3:::skehlet-dailymail-summarizer"
    #                 },
    #                 "object": {
    #                     "key": "incoming/5c3d2fe3-a84d-415d-b424-48c188be7bf8",
    #                     "size": 12685,
    #                     "eTag": "7d2162c5becd09e8980d41eab549fe84",
    #                     "sequencer": "006662311166568017"
    #                 }
    #             }
    #         }
    #     ]
    # }
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

    # if type=rss_entry and the feed_title is a Google Alert, extract the topic
    if "type" in record and record["type"] == "rss_entry" and is_google_alert(record["feed_title"]):
        topic = get_topic_from_google_alert_title(record["feed_title"])
        print(f"Google Alert Topic: {topic}")
    else:
        topic = None

    # should not be needed, all upstream sources to this point provide url and title
    default_values = {
        "url": "Unknown URL",
        "title": "Unknown title",
    }
    for field, default in default_values.items():
        if field not in record:
            record[field] = default

    # Now, summarize the content. Retry on rate limit errors.
    # TODO: retry logic should be moved into the llm/summarize module
    tries_left = 3
    while tries_left > 0:
        try:
            summary = llm_summarize_text(record["url"], record["title"], record["content"], topic)
            break
        except openai.RateLimitError:
            sleep_time = random.randint(10, 30)
            print(f"Got rate limit error, sleeping for {sleep_time} seconds")
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

    print(f"Successfully summarized content for {key}")
