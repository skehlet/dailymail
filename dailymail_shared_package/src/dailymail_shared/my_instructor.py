"""
Shared instructor utilities for LLM structured outputs across the dailymail application.
"""
import json
import os
import instructor
from pydantic import BaseModel
from dailymail_shared.my_parameter_store import get_value_from_parameter_store

# Get environment variables
LLM = os.getenv("LLM", "gemini-2.5-flash-lite")
CONTEXT_WINDOW_SIZE = int(os.getenv("CONTEXT_WINDOW_SIZE", "50000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "10000"))

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
        print(f"Using instructor client for {PROVIDER_NAME}/{LLM} with ANTHROPIC_TOOLS mode")
        return instructor.from_provider(
            f"{PROVIDER_NAME}/{LLM}",
            api_key=api_key,
            mode=instructor.Mode.ANTHROPIC_TOOLS,
        )
    elif PROVIDER_NAME == "google":
        mode = instructor.Mode.GENAI_TOOLS
        print(f"Using instructor client for {PROVIDER_NAME}/{LLM} with {mode} mode")
        return instructor.from_provider(
            f"{PROVIDER_NAME}/{LLM}",
            api_key=api_key,
            mode=mode,
        )
    else:
        print(f"Using instructor client for {PROVIDER_NAME}/{LLM}")
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
        "max_retries": 3,
    }

    # Model-specific parameters
    if PROVIDER_NAME == "openai" or PROVIDER_NAME == "anthropic":
        params["max_tokens"] = MAX_OUTPUT_TOKENS
    elif PROVIDER_NAME == "google":
        params["generation_config"] = { "max_tokens": MAX_OUTPUT_TOKENS }

    print(f"Calling LLM with params: {params}")

    # Log the Pydantic model schema for debugging
    if hasattr(response_model, 'model_json_schema'):
        schema = response_model.model_json_schema()
        print("\n" + "="*80)
        print("PYDANTIC MODEL SCHEMA (what gets converted to tools):")
        print("="*80)
        print(json.dumps(schema, indent=2))
        print("="*80 + "\n")

    result = client.chat.completions.create(**params)

    # from instructor.core.hooks import HookName
    # # Attach one or more handlers
    # client.on(HookName.COMPLETION_KWARGS, lambda **kw: print("KWARGS:", kw))
    # client.on(HookName.COMPLETION_RESPONSE, lambda resp: print("RESPONSE:", type(resp)))
    # client.on(HookName.PARSE_ERROR, lambda e: print("PARSE ERROR:", e))
    # client.on(HookName.COMPLETION_LAST_ATTEMPT, lambda e: print("LAST ATTEMPT:", e))
    # client.on(HookName.COMPLETION_ERROR, lambda e: print("COMPLETION ERROR:", e))

    raw = getattr(result, "_raw_response", None)
    print("=" * 80)
    print(raw)
    print("=" * 80)

    return result
