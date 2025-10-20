import instructor
from pydantic import BaseModel


# Define what you want
class User(BaseModel):
    name: str
    age: int


# Extract it from natural language
client = instructor.from_provider("openai/gpt-4o-mini")
user = client.chat.completions.create(
    response_model=User,
    messages=[{"role": "user", "content": "John is 25 years old"}],
)

print(user)  # User(name='John', age=25)
