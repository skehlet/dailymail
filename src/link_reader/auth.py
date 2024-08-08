import base64
import json
import boto3
from app_settings import LINK_READER_CREDS_PARAMETER_NAME
from shared import get_value_from_parameter_store


def create_basic_auth_header_value(username, password):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def get_username_password_from_basic_auth_header(header_value):
    if not header_value.startswith("Basic "):
        return False

    auth_string = header_value[6:]
    username, password = base64.b64decode(auth_string).decode().split(':', 1)
    # print(f"Username: {username}")
    # print(f"Password: {password}")
    return (username, password)


def authenticate(event) -> bool:
    # print(f"Authenticate: {event}")

    if not "headers" in event:
        return False
    if not "authorization" in event["headers"]:
        return False

    auth_header = event["headers"]["authorization"]
    (username, password) = get_username_password_from_basic_auth_header(auth_header)
    (expected_username, expected_password) = get_link_reader_creds()
    if username != expected_username or password != expected_password:
        return False

    return True


def get_link_reader_creds():
    creds = get_value_from_parameter_store(LINK_READER_CREDS_PARAMETER_NAME)
    creds_json = json.loads(creds)
    username = creds_json.get("USERNAME")
    password = creds_json.get("PASSWORD")
    return (username, password)
