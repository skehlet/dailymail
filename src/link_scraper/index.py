import json
import traceback
from app_settings import show_settings
from scrape_urls import process_records

def handler(event, context): # pylint: disable=unused-argument
    try:
        show_settings()
        process_records(event["Records"])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"result": "OK"}),
        }

    except Exception as e:
        response = traceback.format_exc()
        print("=== BEGIN stack trace ===")
        print(response)
        print("=== END stack trace ===")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": str(e),
        }
