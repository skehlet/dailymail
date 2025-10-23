"""
Unified LLM interface for structured outputs across different providers.
Provides a simple, consistent API to switch between Gemini, OpenAI, and Instructor.
"""
import os
from enum import Enum
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class LLMProvider(Enum):
    """Available LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    INSTRUCTOR = "instructor"


def get_provider_from_env() -> LLMProvider:
    """
    Determine which provider to use based on LLM_PROVIDER environment variable.
    Falls back to GEMINI if not specified.
    
    Returns:
        LLMProvider enum value
    """
    provider_str = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    try:
        return LLMProvider(provider_str)
    except ValueError:
        print(f"Warning: Unknown LLM_PROVIDER '{provider_str}', defaulting to gemini")
        return LLMProvider.GEMINI


def call_llm_structured(
    prompt: str,
    response_model: Type[T],
    provider: LLMProvider = None
) -> T:
    """
    Call an LLM with structured output using the specified provider.
    
    Args:
        prompt: The prompt/content to send to the LLM
        response_model: Pydantic model class for structured output
        provider: Which LLM provider to use (defaults to LLM_PROVIDER env var)
    
    Returns:
        Instance of response_model with the LLM's structured response
    """
    if provider is None:
        provider = get_provider_from_env()
    
    print(f"Using LLM provider: {provider.value}")
    
    if provider == LLMProvider.GEMINI:
        return _call_gemini(prompt, response_model)
    elif provider == LLMProvider.OPENAI:
        return _call_openai(prompt, response_model)
    elif provider == LLMProvider.INSTRUCTOR:
        return _call_instructor(prompt, response_model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _call_gemini(prompt: str, response_model: Type[T]) -> T:
    """Call Gemini with structured outputs."""
    from dailymail_shared.my_gemini import call_gemini_with_structured_outputs
    
    # Gemini expects 'contents' parameter
    result = call_gemini_with_structured_outputs(
        contents=prompt,
        output_class=response_model
    )
    
    # Gemini returns the parsed object directly, which should be a dict
    # We need to convert it to the Pydantic model
    if isinstance(result, dict):
        return response_model(**result)
    else:
        # If it's already the right type, return it
        return result


def _call_openai(prompt: str, response_model: Type[T]) -> T:
    """Call OpenAI with structured outputs."""
    from dailymail_shared.my_openai import call_openai_with_structured_outputs
    
    # OpenAI expects messages format
    messages = [{"role": "user", "content": prompt}]
    
    result = call_openai_with_structured_outputs(
        messages=messages,
        output_class=response_model
    )
    
    # OpenAI returns a dict, convert to Pydantic model
    if isinstance(result, dict):
        return response_model(**result)
    else:
        return result


def _call_instructor(prompt: str, response_model: Type[T]) -> T:
    """Call Instructor with structured outputs."""
    from dailymail_shared.my_instructor import get_instructor_client, get_structured_output
    
    client = get_instructor_client()
    
    # Instructor returns the Pydantic model directly
    result = get_structured_output(client, prompt, response_model)
    return result


# Convenience function for backwards compatibility
def get_context_window_size() -> int:
    """
    Get the context window size based on the current provider.
    
    Returns:
        int: Context window size in characters/tokens
    """
    provider = get_provider_from_env()
    
    # Allow override via environment variable
    if env_size := os.getenv("CONTEXT_WINDOW_SIZE"):
        return int(env_size)
    
    # Default sizes per provider (can be overridden by CONTEXT_WINDOW_SIZE env var)
    if provider == LLMProvider.GEMINI:
        return 50000  # Conservative for Gemini
    elif provider == LLMProvider.OPENAI:
        return 50000  # Conservative for GPT models
    elif provider == LLMProvider.INSTRUCTOR:
        return 50000  # Conservative default
    
    return 50000  # Safe default
