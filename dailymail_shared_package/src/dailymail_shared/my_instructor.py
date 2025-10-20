"""
Shared instructor utilities for LLM structured outputs across the dailymail application.
"""
import os
import instructor
from pydantic import BaseModel
from dailymail_shared.my_parameter_store import get_value_from_parameter_store

# Get environment variables
LLM = os.getenv("LLM", "gemini-2.5-flash-lite")
CONTEXT_WINDOW_SIZE = int(os.getenv("CONTEXT_WINDOW_SIZE", "50000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2000"))

# Determine provider from LLM name
if LLM.startswith("gpt"):
    PROVIDER_NAME = "openai"
    API_KEY_NAME = "OPENAI_API_KEY"
elif LLM.startswith("claude"):
    PROVIDER_NAME = "anthropic"
    API_KEY_NAME = "ANTHROPIC_API_KEY"
elif LLM.startswith("gemini"):
    PROVIDER_NAME = "google"
    API_KEY_NAME = "GEMINI_API_KEY"
else:
    raise Exception(f"Unsupported LLM provider in LLM={LLM}")


def get_instructor_client():
    """
    Initialize and return an instructor client configured for the selected LLM provider.
    
    Returns:
        instructor client configured for the active LLM
    """
    api_key = get_value_from_parameter_store(API_KEY_NAME)
    
    # Anthropic requires a specific mode to work properly with tool calling
    if PROVIDER_NAME == "anthropic":
        return instructor.from_provider(
            f"{PROVIDER_NAME}/{LLM}",
            api_key=api_key,
            mode=instructor.Mode.ANTHROPIC_TOOLS,
        )
    else:
        return instructor.from_provider(
            f"{PROVIDER_NAME}/{LLM}",
            api_key=api_key,
        )


def get_structured_output(client, content: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Call the LLM with structured output, handling provider-specific parameters.
    
    Args:
        client: The instructor client
        content: The prompt content to send to the LLM
        response_model: The Pydantic model class to use for structured output
    
    Returns:
        An instance of the response_model with the LLM's response
    """
    # Base parameters that all providers support
    params = {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "response_model": response_model,
        "max_retries": 2,
    }

    # Model-specific parameters
    if PROVIDER_NAME == "openai" or PROVIDER_NAME == "anthropic":
        params["max_tokens"] = MAX_OUTPUT_TOKENS
    elif PROVIDER_NAME == "google":
        params["generation_config"] = {"max_tokens": MAX_OUTPUT_TOKENS}
    
    return client.chat.completions.create(**params)
