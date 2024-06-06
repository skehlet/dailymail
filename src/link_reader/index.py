import json
import traceback
from app_settings import show_settings
from app import process_event
from auth import authenticate, create_basic_auth_header_value


def handler(event, context):  # pylint: disable=unused-argument
    try:
        show_settings()
        if not authenticate(event):
            print("Authentication failed")
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"result": "Authentication failed"}),
            }

        process_event(event)

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


def main():
    import sys

    username = sys.argv[1]
    password = sys.argv[2]
    with open("misc/example-event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
        event["headers"]["authorization"] = create_basic_auth_header_value(
            username, password
        )
        handler(event, {})


if __name__ == "__main__":
    main()
