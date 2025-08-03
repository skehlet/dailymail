import os
from google import genai
from dailymail_shared.my_parameter_store import get_value_from_parameter_store


LLM = os.getenv("LLM", "gemini-2.5-flash")
GEMINI_CONTEXT_WINDOW_SIZE = int(os.getenv("CONTEXT_WINDOW_SIZE", "50000"))


def get_gemini_api_key():
    return get_value_from_parameter_store("GEMINI_API_KEY")


def get_gemini_client():
    return genai.Client(api_key=get_gemini_api_key())


def call_gemini_with_structured_outputs(contents, output_class):
    client = get_gemini_client()
    response = client.models.generate_content(
        model=LLM,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_schema": output_class
        }
    )
    print(f"Response: {response.text}")
    return response.parsed
