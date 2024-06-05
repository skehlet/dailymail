import html
import json
import boto3
from app_settings import DIGEST_QUEUE, EMAIL_INLINE_CSS_STYLE

sqs = boto3.client("sqs")
queue_url = sqs.get_queue_url(QueueName=DIGEST_QUEUE)["QueueUrl"]


def read_from_digest_queue():
    messages = read_all_from_queue()
    if len(messages) == 0:
        print("No messages in queue")
        return

    grouped_records = {}
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

        record = json.loads(message["Body"])

        print("-" * 80)
        print(f"Feed Title: {record['feed_title']}")
        print(f"Feed Description: {record['feed_description']}")
        print(f"Title: {record['title']}")
        print(f"URL: {record['url']}")
        print(f"Published: {record['published']}")
        print(f"Summary: {record['summary']}")

        # Group records by feed_title
        if record["feed_title"] not in grouped_records:
            grouped_records[record["feed_title"]] = []
        grouped_records[record["feed_title"]].append(record)

    # Produce HTML message
    # TODO: really need to look into Jinja2 or something
    sections = []
    for feed_title, records in sorted(grouped_records.items()):
        summaries = []
        # TODO: need to sort records by published date
        # TODO: also need to reformat the date, and convert to Pacific time
        for record in records:
            summaries.append(
                format_summary_using_html(
                    record["url"], record["title"], record['published'], record["summary"]
                )
            )
        section = f"""<div style="font-size: 24px; font-weight: bold; margin-top: 25px">{feed_title}</div>\n"""
        section += "\n".join(summaries)
        sections.append(section)

    email = f"""<span style="{EMAIL_INLINE_CSS_STYLE}">\n"""
    email += "\n<hr>\n".join(sections)
    email += "</span>"

    # Email it using SES
    print(email)

    delete_messages_from_queue(messages)


def read_all_from_queue():
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=0)
        if "Messages" not in response:
            return messages
        messages.extend(response["Messages"])


def format_summary_using_html(url, site_title, published_on, summary):
    safe_url = html.escape(url)
    safe_site_title = html.escape(site_title)
    safe_summary = ""
    for paragraph in summary.strip().split("\n\n"):
        if paragraph:
            safe_summary += f"<p>{html.escape(paragraph)}</p>\n"
    return f"""\
<div style="padding-top: 10px">
    <b><a href="{safe_url}">{safe_site_title}</a></b> {published_on}
</div>
<span>
    {safe_summary.strip()}
</span>
"""


def delete_messages_from_queue(messages):
    # process messages in batches of 10
    for i in range(0, len(messages), 10):
        batch = messages[i : i + 10]
        entries = [
            {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
            for message in batch
        ]
        sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)


if __name__ == "__main__":
    read_from_digest_queue()
