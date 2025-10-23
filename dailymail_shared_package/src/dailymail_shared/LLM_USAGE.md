# LLM Provider Usage Guide

## Overview

The `my_llm.py` module provides a unified interface for calling different LLM providers with structured outputs. This allows you to easily switch between Gemini, OpenAI, and Instructor without changing your code.

## Switching Between Providers

Set the `LLM_PROVIDER` environment variable to choose your provider:

```bash
# Use Gemini (default, recommended)
export LLM_PROVIDER=gemini

# Use OpenAI
export LLM_PROVIDER=openai

# Use Instructor (multi-provider wrapper)
export LLM_PROVIDER=instructor
```

If `LLM_PROVIDER` is not set, it defaults to **gemini**.

## Provider-Specific Configuration

Each provider also has its own specific configuration:

### Gemini
```bash
export LLM=gemini-2.5-flash-lite  # Model to use
export CONTEXT_WINDOW_SIZE=50000   # Optional: override default
```

### OpenAI
```bash
export LLM=gpt-4o-mini             # Model to use
export CONTEXT_WINDOW_SIZE=50000   # Optional: override default
```

### Instructor
```bash
export LLM=gemini-2.5-flash-lite   # Can be gemini-*, gpt-*, or claude-*
export CONTEXT_WINDOW_SIZE=50000   # Optional: override default
export MAX_OUTPUT_TOKENS=10000     # Optional: max tokens in response
```

## Usage Example

```python
from pydantic import BaseModel, Field
from dailymail_shared.my_llm import call_llm_structured, get_context_window_size

class ArticleSummary(BaseModel):
    summary: str = Field(description="A concise summary of the article")
    key_points: list[str] = Field(description="Main points from the article")
    sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")

# Call the LLM with structured output
prompt = f"""
Analyze this article and provide a structured summary:

{article_text[:get_context_window_size()]}
"""

result: ArticleSummary = call_llm_structured(prompt, ArticleSummary)

print(f"Summary: {result.summary}")
print(f"Key Points: {', '.join(result.key_points)}")
print(f"Sentiment: {result.sentiment}")
```

## Why This Design?

This lightweight abstraction was created because:

1. **Instructor limitations**: While Instructor provides multi-provider support, it has been observed to truncate outputs and not work as reliably as native implementations.

2. **Direct control**: Using provider-specific APIs (especially Gemini) gives better control and more reliable results.

3. **Easy switching**: The unified interface makes it trivial to switch providers for testing or when one provider has issues.

4. **Minimal overhead**: Just a thin wrapper around existing implementations - no complex middleware.

## Implementation Details

The module includes three private functions that wrap the existing implementations:

- `_call_gemini()` - Uses `my_gemini.call_gemini_with_structured_outputs()`
- `_call_openai()` - Uses `my_openai.call_openai_with_structured_outputs()`
- `_call_instructor()` - Uses `my_instructor.get_structured_output()`

All three return Pydantic model instances for consistency.

## Recommendation

**Use Gemini** (`LLM_PROVIDER=gemini`) as the default provider. It has proven to be more reliable with structured outputs than going through Instructor's abstraction layer.
