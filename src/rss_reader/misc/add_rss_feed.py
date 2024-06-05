#!/usr/bin/env python

# Add the provided rss feed to the DAILY_MAIL_RSS_FEEDS parameter in AWS parameter store

import sys
import boto3
import json

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <feed> [<feed> ...]")
    sys.exit(1)

ssm = boto3.client("ssm")

# fetch existing rss feeds from parameter store
# catch and ignore ParameterNotFound
try:
    response = ssm.get_parameter(Name="DAILY_MAIL_RSS_FEEDS")
    existing_feeds = json.loads(response["Parameter"]["Value"])
except ssm.exceptions.ParameterNotFound:
    existing_feeds = []

print(f"Existing feeds: {existing_feeds}")

# now append the provided rss feeds, removing any duplicates
rss_feeds = existing_feeds + sys.argv[1:]
rss_feeds = list(set(rss_feeds))
print(f"New feeds: {rss_feeds}")

# store them as JSON in parameter store
ssm.put_parameter(
    Name="DAILY_MAIL_RSS_FEEDS",
    Value=json.dumps(rss_feeds),
    Type="String",
    Overwrite=True,
)
