from pydantic import BaseModel
from shared.my_openai import call_openai_with_structured_outputs, CONTEXT_WINDOW_SIZE, SUMMARIZER_SYSTEM_PROMPT


class OverallSummary(BaseModel):
    """
    OverallSummary object returned by the model, parsed from the response.
    """

    overall_summary: str


def create_overall_summary_for_feeds_with_multiple_records(feeds):
    prompt = """\
Review the following article summaries and generate an overall summary in three
to four sentences. Present the key developments and themes directly, focusing on
what’s most significant today.
"""
    max_text_length = CONTEXT_WINDOW_SIZE - len(SUMMARIZER_SYSTEM_PROMPT) - len(prompt) - 100

    for feed_title, records in feeds:
        if len(records) >= 2:
            summaries = []
            for record in records:
                # print(f"{feed_title}: {record['title']} - {record['published']}")
                summaries.append(
                    f"""\
Title: {record["title"]}
                                 
{record["summary"]}

Of Interest: {record["notable_aspects"]}
"""
                )
            text = f"""\
Topic: {feed_title}

{"\n\n".join(summaries)}
"""
            text = text[:max_text_length]
            print(f"Combined summaries to summarize: {text}")
            messages = [
                {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
                {"role": "user", "content": text},
            ]
            overall_summary_dict = call_openai_with_structured_outputs(messages, OverallSummary)
            records.insert(
                0,
                {"overall_summary": overall_summary_dict["overall_summary"]},
            )

    return feeds
