import json
import boto3
from app_settings import DIGEST_QUEUE

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]


def read_from_digest_queue():
    messages = read_all_from_queue()
    for message in messages:
        print(message)

        # {
        #     "MessageId": "bca83085-df3e-4e0c-a7f3-8714aafe24f5",
        #     "ReceiptHandle": "AQEBbamIWsIKB8Q7GOVbdUx7lI3eU5piR2X6VCIW0G7Z8z6CbOyInSfZ+P3mK2BIpHMeOVL85OKvc+SJv+u2RGHwG1Lgpq0e6aADuhrMQfb3T5kOE03RA0NroWkxT0yVmpcoc3k2GFkMYuRThqZDmMmmbf1L+hDfzyc9I40Ic97ogPlQLSNguYiIKjzIARPVDxFXDmXq3ApIZQfhSDhJDEC5RRPtswCAOARYnLGsXiW1n4kifzIly8zymPpqF42AyBFRQiWkEAC7nG5ZWTu0lwyBtsVgr3kyTsURx8SM4w4jwEaFXglMCodah2BswnCK8V919btvKfTjtHdPkZd3IgbPvPc0IWghKKRgoScXAeMkm2J74yXOnvHL0jS/Xp7Agy3gQUWyZ1l7hezsZ3wESKI/nA==",
        #     "MD5OfBody": "e433bfd06141b54917141983d384aced",
        #     "Body": "{\"feed_title\": \"Google Alert - Red dead redemption \\\\u201cpc\\\\u201d\", \"feed_description\": \"Unknown\", \"url\": \"https:\/\/www.pcguide.com\/news\/nvidias-project-g-assist-brings-the-ai-chatbot-experience-to-pc-gamers\/\", \"published\": \"2024-06-03T10:56:28Z\", \"title\": \"Nvidia\\'s Project G-Assist brings the AI chatbot experience to PC gamers - here\\'s how - PC Guide\", \"summary\": \"Summary: The text discusses Nvidia\\'s announcement of Project G-Assist, an AI-powered assistant designed to help PC gamers by providing real-time information and optimizing game performance without the need to pause the game. The AI can answer in-game questions, offer strategies, and tweak system settings for better performance. Although currently a demo, it promises to enhance gaming experiences by reducing the need to search for external resources.\\\\n\\\\nRELEVANT: The text mentions that Project G-Assist can optimize settings for games like Red Dead Redemption 2, making it directly relevant to the topic of Red Dead Redemption on PC.\\\\n\\\\nOf interest: One interesting aspect is that G-Assist uses AI vision to understand what is happening on the screen and provide context-specific advice. Another notable point is its ability to optimize game performance by adjusting settings such as HDR and G-Sync to make full use of your PC\\'s capabilities.\"}"
        # }
        # Body:
        # {
        #     "feed_title": "Google Alert - Red dead redemption \\u201cpc\\u201d",
        #     "feed_description": "Unknown",
        #     "url": "https://www.pcguide.com/news/nvidias-project-g-assist-brings-the-ai-chatbot-experience-to-pc-gamers/",
        #     "published": "2024-06-03T10:56:28Z",
        #     "title": "Nvidia\'s Project G-Assist brings the AI chatbot experience to PC gamers - here\'s how - PC Guide",
        #     "summary": "Summary: The text discusses Nvidia\'s announcement of Project G-Assist, an AI-powered assistant designed to help PC gamers by providing real-time information and optimizing game performance without the need to pause the game. The AI can answer in-game questions, offer strategies, and tweak system settings for better performance. Although currently a demo, it promises to enhance gaming experiences by reducing the need to search for external resources.\\n\\nRELEVANT: The text mentions that Project G-Assist can optimize settings for games like Red Dead Redemption 2, making it directly relevant to the topic of Red Dead Redemption on PC.\\n\\nOf interest: One interesting aspect is that G-Assist uses AI vision to understand what is happening on the screen and provide context-specific advice. Another notable point is its ability to optimize game performance by adjusting settings such as HDR and G-Sync to make full use of your PC\'s capabilities."
        # }

        body = json.loads(message["Body"])

        print("-" * 80)
        print(f"Feed Title: {body['feed_title']}")
        print(f"Feed Description: {body['feed_description']}")
        print(f"Title: {body['title']}")
        print(f"URL: {body['url']}")
        print(f"Published: {body['published']}")
        print(f"Summary: {body['summary']}")

    # Group messages by feed_title

    # Produce HTML message

    # Email it using SES

    delete_messages_from_queue(messages)


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def delete_messages_from_queue(messages):
    sqs.delete_message_batch(
        QueueUrl=queue_url,
        Entries=[
            {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
            for message in messages
        ],
    )


if __name__ == "__main__":
    read_from_digest_queue()
