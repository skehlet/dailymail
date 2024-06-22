import re
from app_settings import DIGEST_EMAIL_FROM
from shared.my_email_lib import send_email

def is_gmail_forwarding_confirmation(email_subject):
    # Subject: (Gmail Forwarding Confirmation - Receive Mail from steve.kehlet@gmail.com
    return "Gmail Forwarding Confirmation" in email_subject

def send_gmail_forwarding_confirmation_back_to_originator(email_subject, body):
    # Subject: (Gmail Forwarding Confirmation - Receive Mail from steve.kehlet@gmail.com
    matches = re.search(r'Receive Mail from (\S+)', email_subject)
    if matches is None or len(matches.groups()) != 1:
        raise Exception("Could not parse out originator")
    originator = matches.group(1)
    send_email(
        DIGEST_EMAIL_FROM,
        originator,
        f"Fwd: {email_subject}",
        body,
    )
