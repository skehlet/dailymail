import json
import traceback
from app_settings import show_settings
from app import read_from_digest_queue

def handler(event, context): # pylint: disable=unused-argument,redefined-outer-name
    try:
        show_settings()
        read_from_digest_queue()

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
