def process_records(records):
    for record in records:
        print(record)
        # if record['EventSource'] != 'aws:sns':
        #     raise Exception("Not an SNS event")

        # message = record['Sns']['Message']

        # (email_sender, email_to, email_date, email_subject, body) = parse_sns_message(message)
        # print(f"Sender: {email_sender}")
        # print(f"To: {email_to}")
        # print(f"Date: {email_date}")
        # print(f"Subject: {email_subject}")

        # # Confirm the email_sender is on the list of SES verified identities.
        # # Drop the email if it's not.
        # if not is_sender_verified(email_sender):
        #     print(f"Sender {email_sender} is not verified. Dropping email.")
        #     continue # don't summarize this email

        # # If it's a Gmail forwarding confirmation, parse out the originator and send it back
        # if is_gmail_forwarding_confirmation(email_subject):
        #     send_gmail_forwarding_confirmation_back_to_originator(email_subject, body)
        #     continue # don't summarize this email

        # summary = summarize(email_subject, body)

        # send_email(
        #     email_sender,
        #     f"Your summary of: {email_subject}",
        #     html=summary,
        # )

        # print("=" * 80)
        # print(f"Successfully emailed a summary to {email_sender}")
        # print("=" * 80)
