import json
import traceback
from app_settings import show_settings
from app import process_sqs_record

def handler(event, context): # pylint: disable=unused-argument,redefined-outer-name
    try:
        show_settings()
        for record in event["Records"]:
            process_sqs_record(record)

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

if __name__ == "__main__":
    with open("misc/example-event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
        handler(event, {})
