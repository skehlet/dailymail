import json
import traceback
from app_settings import show_settings
from app import read_rss_feeds


def handler(event, context):  # pylint: disable=unused-argument
    try:
        show_settings()
        read_rss_feeds()

    except Exception as e:
        stack_trace = traceback.format_exc()
        print("=== BEGIN stack trace ===")
        print(stack_trace)
        print("=== END stack trace ===")
        raise e
