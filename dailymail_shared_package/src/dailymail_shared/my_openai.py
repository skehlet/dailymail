import os
import random
import time
import openai
from dailymail_shared.my_parameter_store import get_value_from_parameter_store


LLM = os.getenv("LLM", "gpt-4o-mini")
CONTEXT_WINDOW_SIZE = int(os.getenv("CONTEXT_WINDOW_SIZE", 50000))


def get_openai_api_key():
    return get_value_from_parameter_store("OPENAI_API_KEY")


def get_openai_client():
    return openai.OpenAI(
        api_key=get_openai_api_key(),
        timeout=60,
    )


def call_openai_with_structured_outputs(messages, output_class):
    client = get_openai_client()
    tries_left = 3
    while tries_left > 0:
        try:
            completion = client.beta.chat.completions.parse(
                model=LLM,
                messages=messages,
                temperature=0,
                response_format=output_class,
            )
            response = completion.choices[0].message
            if response.refusal:
                raise Exception(response.refusal)
            response_obj = completion.choices[0].message.parsed
            print(response_obj.model_dump_json(indent=2))
            return response_obj.dict()

        except openai.RateLimitError:
            sleep_time = random.randint(10, 30)
            print(f"Got rate limit error, sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
            tries_left -= 1

    raise Exception("OpenAI API call failed after multiple tries")
