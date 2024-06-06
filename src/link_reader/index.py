import json
import traceback
from app_settings import show_settings
from app import process_record
from auth import authenticate

def handler(event, context): # pylint: disable=unused-argument
    try:
        show_settings()
        if not authenticate(event):
            print("Authentication failed")
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"result": "Authentication failed"}),
            }

        for record in event["Records"]:
            process_record(record)

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
