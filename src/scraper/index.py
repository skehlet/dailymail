import json
import traceback
from app_settings import show_settings
from app import process_record


def handler(event, context):  # pylint: disable=unused-argument,redefined-outer-name
    try:
        show_settings()
        failed = []
        for record in event["Records"]:
            # Handle timeout exceptions, e.g.:
            # requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='www.emergentmind.com', port=443): Read timed out. (read timeout=20)
            try:
                process_record(record)
            except Exception as e:
                print(f"Read timeout: {e}")
                failed.append(record["messageId"])

        return { "batchItemFailures": [{"itemIdentifier": f} for f in failed] } if failed else {}


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
