import json
from shared.my_email_lib import get_primary_email_content


def parse_email_from_sns_message(sns_message):
    message = json.loads(sns_message)
    # Use Return-Path since forwarded mail will show the original sender (e.g.
    # googlealerts-noreply@google.com) as the From address
    email_sender = message["mail"]["commonHeaders"]["returnPath"]
    email_to = message["mail"]["commonHeaders"]["to"][0]
    email_date = message["mail"]["commonHeaders"]["date"]
    email_subject = message["mail"]["commonHeaders"]["subject"]
    email_content = message["content"]

    # The docs say the content is base64-encoded, but it's not
    # print("=== BEGIN email_content")
    # print(email_content)
    # print("=== END email_content")

    # # decoded_email_content = base64.b64decode(email_content).decode('utf-8')
    # decoded_email_content = base64.b64decode(email_content)
    # print("=== BEGIN decoded Content")
    # print(decoded_email_content)
    # print("=== END decoded Content")

    # try:
    #     decoded_email_content = decoded_email_content.decode('utf-8')
    #     print("No problems decoding to utf-8")
    # except Exception as e:
    #     print(str(e))
    #     decoded_email_content = decoded_email_content.decode('latin-1')
    #     print("Decoded to latin-1 instead, may have data loss")

    return (email_sender, email_to, email_date, email_subject, email_content)


def parse_sns_message(sns_message):
    (email_sender, email_to, email_date, email_subject, email_content) = (
        parse_email_from_sns_message(sns_message)
    )
    body = get_primary_email_content(email_content)
    return (email_sender, email_to, email_date, email_subject, body)
