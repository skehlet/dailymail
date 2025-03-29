import json
import boto3
from datetime import datetime
from pydantic import BaseModel
from app_settings import BEDROCK_MODEL_ID, BEDROCK_REGION

# Initialize Bedrock client
client = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION
)


class NewsletterContent(BaseModel):
    """
    NewsletterContent model for structured output from Claude
    """
    opening_paragraph: str
    categorized_content: dict


def generate_newsletter_digest(feeds):
    """
    Generate a newsletter digest using Claude
    
    Args:
        feeds: A list of tuples, each containing (feed_title, records)
        
    Returns:
        dict: A dictionary with the newsletter content
    """
    
    # Create the input for Claude
    prompt = """
You are creating a daily news digest email newsletter. Your task is to organize the provided news summaries 
into a well-structured, informative newsletter. Follow these guidelines:

1. Start with a concise opening paragraph that:
   - Directly summarizes 3-5 key stories from across categories
   - Mentions specific, eye-catching details or statistics
   - Avoids greetings like "welcome" or unnecessary pleasantries
   - Maintains a professional, informative tone
2. Organize stories alphabetically by topic/category
3. For each category, provide:
   - An overall summary of key developments (3-4 sentences)
   - A list of sources (URLs) with a brief 1-2 sentence highlight for each article that captures what's most interesting or notable about it
4. Use a professional tone focusing on information delivery
5. Focus on delivering substantive information clearly and concisely
6. Format properly for an email newsletter

DO NOT: 
- Include filler content, greetings, or casual phrases
- Make up additional stories not in the source material
- Use clickbait language or sensationalism

The newsletter should be well-organized, informative, and easy to scan. The article highlights should give readers a clear reason to click on each link.
"""
    
    # Convert feeds into a format Claude can work with
    feed_data = []
    
    for feed_title, records in feeds:
        category_data = {
            "category": feed_title,
            "articles": []
        }
        
        for record in records:
            # Skip the overall summary records that were inserted previously
            if "overall_summary" in record:
                continue
                
            article = {
                "title": record.get("title", ""),
                "url": record.get("url", ""),
                "published": record.get("published", ""),
                "summary": record.get("summary", ""),
                "notable_aspects": record.get("notable_aspects", ""),
                "domain": record.get("domain", "")
            }
            category_data["articles"].append(article)
            
        feed_data.append(category_data)
    
    # Create the news content for Claude
    news_content = json.dumps(feed_data, indent=2)
    
    # Format the input for Claude
    news_info = f"""
Here is the news content to organize into a newsletter:

{news_content}
"""
    
    # Define the tool schema for structured output
    tool_list = [
        {
            "toolSpec": {
                "name": "create_newsletter",
                "description": "Create a newsletter from the provided news content",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "opening_paragraph": {
                                "type": "string",
                                "description": "A concise opening paragraph highlighting key stories"
                            },
                            "categorized_content": {
                                "type": "object",
                                "description": "News content organized by category",
                                "additionalProperties": {
                                    "type": "object",
                                    "properties": {
                                        "summary": {
                                            "type": "string",
                                            "description": "Overall summary of the category"
                                        },
                                        "sources": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {"type": "string"},
                                                    "url": {"type": "string"},
                                                    "highlight": {"type": "string", "description": "A brief 1-2 sentence highlight of what's most notable or interesting about this article"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["opening_paragraph", "categorized_content"]
                    }
                }
            }
        }
    ]
    
    # Set up conversation messages
    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt},
                {"text": news_info}
            ]
        }
    ]
    
    try:
        # Make API call to Bedrock
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 4000,
                "temperature": 0.2
            },
            toolConfig={
                "tools": tool_list,
                "toolChoice": {"tool": {"name": "create_newsletter"}}
            }
        )
        
        # Extract the tool use from the response
        content_blocks = response["output"]["message"]["content"]
        tool_use_block = None
        
        for block in content_blocks:
            if "toolUse" in block:
                tool_use_block = block["toolUse"]
                break
        
        if not tool_use_block:
            raise Exception("No tool use found in the response")
        
        # Extract the result from the tool use
        result = tool_use_block["input"]
        
        # Return the newsletter content
        return result
        
    except Exception as e:
        print(f"Error generating newsletter: {str(e)}")
        # Provide fallback content in case of error
        return {
            "opening_paragraph": f"Here are today's news highlights for {datetime.now().strftime('%A, %B %d, %Y')}.",
            "categorized_content": {}
        }
