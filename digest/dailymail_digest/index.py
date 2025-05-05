import traceback
from app_settings import show_settings
from app import read_from_digest_queue


def handler(event, context):  # pylint: disable=unused-argument,redefined-outer-name
    try:
        show_settings()
        read_from_digest_queue()

    except Exception as e:
        stack_trace = traceback.format_exc()
        print("=== BEGIN stack trace ===")
        print(stack_trace)
        print("=== END stack trace ===")
        raise e
