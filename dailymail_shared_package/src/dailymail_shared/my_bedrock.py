"""
AWS Bedrock LLM interface for structured outputs using the Converse API.

Configuration via environment variables:
  BEDROCK_REGION  - AWS region (default: us-west-2)
  BEDROCK_LLM     - Full Bedrock model ID, e.g. us.anthropic.claude-haiku-4-5-20251001-v1:0
                    Required; no default. Structured-output support varies by model—
                    Claude 3.5+ models are known to work with this feature.

Note: The Converse structured-output feature (outputConfig / json_schema) may not handle
JSON schemas that contain $ref / $defs (produced by Pydantic for models with nested types).
If you hit schema errors with complex models, flatten the Pydantic model or use a simpler
schema without cross-references.
"""
import json
import os
from typing import Type, TypeVar

import boto3
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-west-2")
BEDROCK_LLM = os.getenv("BEDROCK_LLM", "")


def _enforce_additional_properties_false(schema: dict) -> dict:
    """
    Recursively set additionalProperties=false on every object node in a JSON schema.
    Bedrock's structured-output feature requires this to be explicit.
    """
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            schema["additionalProperties"] = False
        for value in schema.values():
            if isinstance(value, (dict, list)):
                _enforce_additional_properties_false(value)
    elif isinstance(schema, list):
        for item in schema:
            _enforce_additional_properties_false(item)
    return schema


def call_bedrock_with_structured_outputs(
    prompt: str,
    response_model: Type[T],
    system_prompt: str = None,
) -> T:
    """
    Call a Bedrock model via the Converse API with JSON-schema structured output.

    Args:
        prompt: User message content.
        response_model: Pydantic model class defining the expected output shape.
        system_prompt: Optional system-level instructions passed separately from the user message.

    Returns:
        An instance of response_model populated from the model's JSON response.
    """
    if not BEDROCK_LLM:
        raise ValueError(
            "BEDROCK_LLM environment variable must be set to a valid Bedrock model ID, "
            "e.g. us.anthropic.claude-haiku-4-5-20251001-v1:0"
        )

    bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

    schema = response_model.model_json_schema()
    _enforce_additional_properties_false(schema)

    kwargs = {
        "modelId": BEDROCK_LLM,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {
            "maxTokens": 4096,
        },
        "outputConfig": {
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": json.dumps(schema),
                        "name": response_model.__name__,
                        "description": (response_model.__doc__ or "").strip(),
                    }
                },
            }
        },
    }

    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    print(f"Calling Bedrock model: {BEDROCK_LLM} (region: {BEDROCK_REGION})")

    response = bedrock.converse(**kwargs)

    if response.get("stopReason") == "max_tokens":
        print("Warning: Bedrock output was truncated. Consider increasing maxTokens.")

    raw_text = response["output"]["message"]["content"][0]["text"]
    data = json.loads(raw_text)
    return response_model(**data)
