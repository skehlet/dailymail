import openai
from shared.my_parameter_store import get_value_from_parameter_store


def get_openai_api_key():
    return get_value_from_parameter_store("OPENAI_API_KEY")


def get_openai_client():
    return openai.OpenAI(
        api_key=get_openai_api_key(),
        timeout=60,
    )
