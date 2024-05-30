import sys
import feedparser
import boto3
from botocore.exceptions import ClientError

if len(sys.argv) < 2:
    print("Usage: python3 main.py <url> [<etag>]")
    sys.exit(1)

url = sys.argv[1]
if len(sys.argv) > 2:
    etag = sys.argv[2]
else:
    etag = None

feed = feedparser.parse(
    url,
    etag=etag,
)

print(f"Status: {feed.status}")
print(f"Etag: {feed.etag}")

for entry in feed.entries:

    id = entry.id
    article_title = entry.title
    article_link = entry.link
    article_published_at = entry.published # Unicode string
    article_published_at_parsed = entry.published_parsed # Time object
    # article_author = entry.author  DOES NOT EXIST
    content = entry.summary
    # article_tags = entry.tags  DOES NOT EXIST


    print (f"[{article_title}]({article_link})")
    print (f"Id {id}")
    print (f"Published at {article_published_at}")
    # print ("Published by {}".format(article_author))
    print(f"Content {content}")
    print("")


# Set up the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the table name and the item to be stored
table_name = 'pfs-etag-table'
item = {
    'url': {'S': url},
    'etag': {'S': feed.etag}
}

try:
    # Put the item in the DynamoDB table
    response = dynamodb.put_item(
        TableName=table_name,
        Item=item
    )
    print(f"Successfully stored etag '{feed.etag}' for URL '{sys.argv[1]}' in DynamoDB table.")
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    print(f"Error storing etag in DynamoDB table: {error_code} - {error_message}")
