import json
import traceback
from app_settings import show_settings
from app import process_sqs_record


def handler(event, context):  # pylint: disable=unused-argument,redefined-outer-name
    try:
        show_settings()
        for record in event["Records"]:
            process_sqs_record(record)

    except Exception as e:
        stack_trace = traceback.format_exc()
        print("=== BEGIN stack trace ===")
        print(stack_trace)
        print("=== END stack trace ===")
        raise e


if __name__ == "__main__":
    with open("misc/example-event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
        handler(event, {})
