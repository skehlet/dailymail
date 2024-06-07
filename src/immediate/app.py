import json
from app_settings import IMMEDIATE_EMAIL_FROM, IMMEDIATE_EMAIL_TO
from shared.my_email_lib import send_email, EMAIL_INLINE_CSS_STYLE
from jinja2 import Template


def process_record(sqs_record):
    print(sqs_record)

    if not "eventSource" in sqs_record or sqs_record["eventSource"] != "aws:sqs":
        raise Exception("Not an SQS event")

    record = json.loads(sqs_record["body"])
    print(f"Record: {record}")

    # {
    #     "type": "url",
    #     "url": "https://aws.amazon.com/bedrock/",
    #     "immediate": true,
    #     "title": "Build Generative AI Applications with Foundation Models - Amazon Bedrock - AWS",
    #     "summary": "Amazon Bedrock is a fully managed service that simplifies building and scaling generative AI applications by offering a variety of high-performing foundation models (FMs) from top AI companies through a single API. It allows users to experiment, customize models with their own data, and build task-executing agents securely without managing infrastructure. The service supports fine-tuning and Retrieval Augmented Generation (RAG) to enhance model responses and integrates seamlessly with AWS services. Amazon Bedrock also ensures data security, privacy, and responsible AI use through dedicated features.\n\nAn interesting aspect of Amazon Bedrock is its ability to privately fine-tune foundation models using labeled datasets, ensuring that user data is not used to train the original base models. Another notable feature is the automated RAG capability, which enriches model prompts with proprietary data for more accurate responses, removing the need for custom code."
    # }

    with open("immediate.html.jinja", encoding="utf8") as f:
        email = Template(f.read()).render(
            EMAIL_INLINE_CSS_STYLE=EMAIL_INLINE_CSS_STYLE,
            record=record,
        )

    # Email it using SES
    subject = f"Your summary of: {record['url']}"
    print(f"Subject: {subject}")
    print("Body:")
    print(email)
    send_email(IMMEDIATE_EMAIL_FROM, IMMEDIATE_EMAIL_TO, subject, html=email)
