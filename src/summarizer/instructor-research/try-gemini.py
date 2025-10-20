import instructor
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


# Using from_provider (recommended)
client = instructor.from_provider(
    "google/gemini-2.5-flash-lite",
)

# note that client.chat.completions.create will also work
resp = client.messages.create(
    messages=[
        {
            "role": "user",
            "content": "Extract Jason is 25 years old.",
        }
    ],
    response_model=User,
)

print(resp)  # User(name='Jason', age=25)