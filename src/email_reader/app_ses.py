import email
import re
import boto3

def get_verified_email_addresses():
    client = boto3.client("ses", region_name="us-west-2")
    response = client.list_identities(
        IdentityType='EmailAddress',
        MaxItems=50,
    )
    return response['Identities']

def cleanup_email_address(from_email):
    # Steve Kehlet <steve.kehlet@gmail.com>
    parsed_address = email.utils.parseaddr(from_email)[1]
    # steve.kehlet+caf_=summarize=ai.stevekehlet.com@gmail.com is not verified. Dropping email.
    plus_portion_removed = re.sub(r'\+[^)]*@', '@', parsed_address)
    return plus_portion_removed

def is_sender_verified(from_email):
    clean_email_address = cleanup_email_address(from_email)
    return clean_email_address in get_verified_email_addresses()
