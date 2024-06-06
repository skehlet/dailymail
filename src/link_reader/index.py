import json
import traceback
from app_settings import show_settings
from app import process_event
from auth import authenticate, create_basic_auth_header_value
from my_errors import StatusCodeError


def handler(event, context):  # pylint: disable=unused-argument
    try:
        show_settings()
        if not authenticate(event):
            print("Authentication failed")
            raise StatusCodeError("Authentication failed", status_code=401)

        process_event(event)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"result": "OK"}),
        }

    except StatusCodeError as e:
        return create_lambda_response(e.status_code, str(e))

    except Exception as e:
        stack_trace = traceback.format_exc()
        print("=== BEGIN stack trace ===")
        print(stack_trace)
        print("=== END stack trace ===")
        return create_lambda_response(500, str(e))


def create_lambda_response(status_code, message):
    print(f"Response: {status_code}: {message}")
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": {"result": message},
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
