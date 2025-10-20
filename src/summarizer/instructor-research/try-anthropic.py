# Standard library imports
import os
from typing import List

# Third-party imports
# import anthropic
import instructor
from pydantic import BaseModel, Field

# Set up environment (typically handled before script execution)
# os.environ["ANTHROPIC_API_KEY"] = "your-api-key"  # Uncomment and replace with your API key if not set

# Define your models with proper type annotations
class Properties(BaseModel):
    """Model representing a key-value property."""
    name: str = Field(description="The name of the property")
    value: str = Field(description="The value of the property")


class User(BaseModel):
    """Model representing a user with properties."""
    name: str = Field(description="The user's full name")
    age: int = Field(description="The user's age in years")
    properties: List[Properties] = Field(description="List of user properties")

client = instructor.from_provider(
    "anthropic/claude-3-haiku-20240307",
    mode=instructor.Mode.ANTHROPIC_TOOLS
)

try:
    # Extract structured data
    user_response = client.chat.completions.create(
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": "Extract structured information based on the user's request."
            },
            {
                "role": "user",
                "content": "Create a user for a model with a name, age, and properties.",
            }
        ],
        response_model=User,
    )

    # Print the result as formatted JSON
    print(user_response.model_dump_json(indent=2))

    # Expected output:
    # {
    #   "name": "John Doe",
    #   "age": 35,
    #   "properties": [
    #     {
    #       "name": "City",
    #       "value": "New York"
    #     },
    #     {
    #       "name": "Occupation",
    #       "value": "Software Engineer"
    #     }
    #   ]
    # }
except instructor.exceptions.InstructorError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")