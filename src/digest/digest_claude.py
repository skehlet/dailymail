import json
import boto3
from pydantic import BaseModel, ValidationError, Field
from typing import List, Dict, Optional
from app_settings import BEDROCK_MODEL_ID, BEDROCK_REGION

# --- Configuration ---
MAX_RETRIES = 1  # Number of retries if validation fails

# --- Initialize Bedrock Client ---
client = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION
)
print(f"Bedrock client initialized for region: {BEDROCK_REGION}")

# --- Pydantic Models for Validation ---

class NewsletterSource(BaseModel):
    """Represents a single source article within a category."""
    title: str = Field(..., description="The title of the source article.")
    url: str = Field(..., description="The URL of the source article.")
    highlight: str = Field(..., description="A brief 1-2 sentence highlight of what's most notable or interesting about this article.")

class CategoryContent(BaseModel):
    """Represents the content for a single news category."""
    summary: str = Field(..., description="Overall summary of the category's key developments (3-4 sentences).")
    sources: List[NewsletterSource] = Field(..., description="A list of source articles for this category.")
    notable_aspects: str = Field(default="", description="Notable aspects for single-article feeds")
    is_single_article: bool = Field(default=False, description="Flag to identify if this is a single article feed")

class MultiArticleSummary(BaseModel):
    """Model for validating the summary response for multiple articles in a feed."""
    summary: str = Field(..., description="Overall summary of the feed's key developments (3-4 sentences).")
    sources: List[NewsletterSource] = Field(..., description="A list of source articles with highlights.")

class NewsletterContent(BaseModel):
    """Final newsletter content structure assembled by Python."""
    opening_paragraph: str
    categorized_content: Dict[str, CategoryContent]

# --- Functions to Process Single Feed with Multiple Articles ---

def generate_multi_article_summary(feed_title: str, articles: list) -> MultiArticleSummary:
    """
    Generate a summary for a feed that contains multiple articles.
    
    Args:
        feed_title: The title of the feed
        articles: List of article records
        
    Returns:
        MultiArticleSummary: A validated summary of multiple articles
    """
    articles_json = json.dumps(articles, indent=2)
    
    prompt = f"""
You are summarizing multiple articles from the feed: "{feed_title}".

Create a concise summary that captures the key themes across these articles (3-4 sentences).
Then, for each source article, provide a brief 1-2 sentence highlight that captures what's most notable or interesting.

Your output should follow this exact structure:
- A "summary" field with 3-4 sentences summarizing key developments across all articles
- A "sources" list where each item has:
  - "title": The article title
  - "url": The article URL 
  - "highlight": A 1-2 sentence highlight of what's most interesting about this specific article

Focus on delivering substantive information clearly and concisely. Do not include introductions, 
pleasantries, or notes about your task. Just the requested content.
"""

    articles_info = f"Here are the articles to summarize:\n\n{articles_json}"
    
    # Define tool schema
    tool_list = [
        {
            "toolSpec": {
                "name": "create_multi_article_summary",
                "description": "Create a summary for multiple articles from the same feed.",
                "inputSchema": {
                    "json": MultiArticleSummary.model_json_schema()
                }
            }
        }
    ]
    
    # Prepare messages
    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt},
                {"text": articles_info}
            ]
        }
    ]
    
    # Make the API call to Bedrock
    attempts = 0
    last_error = None
    
    # Save initial messages for potential reset
    initial_messages = messages[:]
    
    while attempts <= MAX_RETRIES:
        attempts += 1
        try:
            response = client.converse(
                modelId=BEDROCK_MODEL_ID,
                messages=messages,
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.1
                },
                toolConfig={
                    "tools": tool_list,
                    "toolChoice": {"tool": {"name": "create_multi_article_summary"}}
                }
            )
            
            # Extract the tool use block
            content_blocks = response["output"]["message"]["content"]
            tool_use_block = None
            
            for block in content_blocks:
                if "toolUse" in block:
                    tool_use_block = block["toolUse"]
                    break
            
            if not tool_use_block:
                raise Exception(f"No tool use block found in response (attempt {attempts})")
            
            # Extract the result
            raw_result = tool_use_block.get("input", {})
            
            # Create a working copy to manipulate
            processed_result = dict(raw_result)
            
            # Check if sources is a string and try to parse it
            if "sources" in processed_result and isinstance(processed_result["sources"], str):
                print(f"Sources is a string, attempting to parse: {processed_result['sources'][:100]}...")
                try:
                    parsed_sources = json.loads(processed_result["sources"])
                    processed_result["sources"] = parsed_sources
                    print(f"Successfully parsed sources as JSON")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse sources as JSON: {e}")
                    # Fall back to creating a simpler structure
                    raise ValueError(f"Could not parse sources string as JSON: {e}")
            
            # Validate the result
            try:
                validated_result = MultiArticleSummary.model_validate(processed_result)
                return validated_result
            except ValidationError as e:
                print(f"Validation error: {e}")
                print(f"Raw result that failed validation: {raw_result}")
                raise
            
        except Exception as e:
            print(f"Error on attempt {attempts}: {e}")
            last_error = e
            
            # For "Messages following `toolUse` blocks" errors, we need to start with a fresh conversation
            if "Messages following `toolUse` blocks" in str(e):
                print("Detected Bedrock conversation state error. Restarting with fresh conversation...")
                # Reset to initial messages
                messages = initial_messages[:]
                if attempts <= MAX_RETRIES:
                    continue
                else:
                    break
                
            if attempts <= MAX_RETRIES:
                # For other errors, add feedback and retry
                try:
                    if "output" in response and "message" in response["output"]:
                        messages.append(response["output"]["message"])
                except:
                    # If we can't access the response or there's an issue adding the message,
                    # just restart with the initial messages
                    messages = initial_messages[:]
                
                messages.append({
                    "role": "user",
                    "content": [{"text": f"The previous response had an error: {e}. Please provide a complete and properly formatted JSON response with a 'summary' field and 'sources' array."}]
                })
            else:
                break
    
    # If we got here, all attempts failed
    raise Exception(f"Failed to generate multi-article summary after {attempts} attempts: {last_error}")

def generate_opening_paragraph(feed_data: List[dict]) -> str:
    """
    Generate an opening paragraph highlighting key stories across categories.
    
    Args:
        feed_data: List of processed feed data
        
    Returns:
        str: Opening paragraph
    """
    # Extract key information for the opening paragraph
    feed_info = []
    for feed in feed_data:
        feed_info.append({
            "category": feed["category"],
            "article_count": len(feed["articles"]),
            "sample_titles": [a["title"] for a in feed["articles"][:2]]  # Include up to 2 sample titles
        })
    
    feed_info_json = json.dumps(feed_info, indent=2)
    
    prompt = """
Create a concise opening paragraph (2-3 sentences) for a newsletter that highlights 3-5 key stories 
across different categories. The paragraph should:

- Directly mention specific, interesting details from key stories
- Maintain a professional, informative tone
- Avoid greetings or pleasantries
- Focus on substantive content

For example: "Today, the tech world saw a major breakthrough in AI with XYZ Corp's new model, 
while the finance sector reacted to unexpected inflation data."

Your response should be ONLY the paragraph text with no additional explanations or notes.
"""

    info_text = f"Here is information about the feeds to highlight:\n\n{feed_info_json}"
    
    # Make the API call to Bedrock
    response = client.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[
            {
                "role": "user", 
                "content": [
                    {"text": prompt},
                    {"text": info_text}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.2
        }
    )
    
    # Extract the text response
    message_content = response["output"]["message"]["content"]
    paragraph_text = ""
    
    for content_block in message_content:
        if "text" in content_block:
            paragraph_text += content_block["text"]
    
    return paragraph_text.strip()

# --- Main Function to Generate Newsletter ---

def generate_newsletter_digest(feeds: list) -> Optional[NewsletterContent]:
    """
    Generates a structured newsletter digest, preserving original summaries for 
    single-article feeds while summarizing multiple-article feeds.

    Args:
        feeds: A list of tuples, each containing (feed_title, list_of_records).
               Each record is expected to be a dictionary with article details.

    Returns:
        NewsletterContent: A structured newsletter content object, or None if no valid data.
    """
    # 1. Prepare feed data
    if not feeds:
        print("No feeds to process")
        return None
    
    processed_feeds = []
    
    for feed_title, records in feeds:
        if not records:  # Skip empty feeds
            continue
            
        articles = []
        for record in records:
            article = {
                "title": record.get("title", "(No Title)"),
                "url": record.get("url", ""),
                "published": record.get("published", "(No Date)"),
                "summary": record.get("summary", "(No Summary)"),
                "notable_aspects": record.get("notable_aspects", ""),
                "relevance": record.get("relevance", ""),
                "relevance_explanation": record.get("relevance_explanation", ""),
            }
            articles.append(article)
            
        if articles:  # Only include feeds with articles
            processed_feeds.append({
                "category": feed_title,
                "articles": articles
            })
    
    if not processed_feeds:
        print("No valid feed data to process")
        return None
    
    # 2. Generate opening paragraph
    opening_paragraph = generate_opening_paragraph(processed_feeds)
    
    # 3. Process each feed based on number of articles
    categorized_content = {}
    
    for feed in processed_feeds:
        feed_title = feed["category"]
        articles = feed["articles"]
        
        if len(articles) == 1:
            # For a single article, use the existing summary and notable aspects
            article = articles[0]
            
            # Create a source entry without a highlight (we'll use the notable aspects instead)
            source = NewsletterSource(
                title=article["title"],
                url=article["url"],
                highlight="See notable aspects below"  # Placeholder that won't be used in template
            )
            
            # Create category content using the original summary and notable aspects
            categorized_content[feed_title] = CategoryContent(
                summary=article["summary"],
                sources=[source],
                notable_aspects=article.get("notable_aspects", ""),
                is_single_article=True
            )
            
        else:
            # For multiple articles, generate a summary
            try:
                multi_summary = generate_multi_article_summary(feed_title, articles)
                
                categorized_content[feed_title] = CategoryContent(
                    summary=multi_summary.summary,
                    sources=multi_summary.sources,
                    is_single_article=False
                )
                
            except Exception as e:
                print(f"Error generating summary for feed '{feed_title}': {e}")
                # Fallback: create a simple summary and use each article's own summary
                
                # Create a basic summary that mentions the number of articles
                article_count = len(articles)
                summary = f"{article_count} articles related to {feed_title} were found."
                
                # Create source entries using each article's own summary
                sources = []
                for article in articles:
                    # Create a concise highlight from the article's summary and notable aspects
                    highlight_text = article.get("summary", "")
                    if len(highlight_text) > 120:
                        highlight_text = highlight_text[:117] + "..."
                        
                    source = NewsletterSource(
                        title=article["title"],
                        url=article["url"],
                        highlight=highlight_text
                    )
                    sources.append(source)
                
                # If no sources could be created, create a placeholder
                if not sources:
                    sources = [NewsletterSource(
                        title="Could not process articles",
                        url="#",
                        highlight="The articles could not be processed. Please check the original sources."
                    )]
                
                categorized_content[feed_title] = CategoryContent(
                    summary=summary,
                    sources=sources,
                    is_single_article=False
                )
    
    # 4. Assemble the final newsletter content
    newsletter = NewsletterContent(
        opening_paragraph=opening_paragraph,
        categorized_content=categorized_content
    )
    
    return newsletter


# --- Example Usage (Optional, for testing) ---
if __name__ == "__main__":
    # Test with example data
    test_feeds = [
        ("Technology News", [
            {"title": "AI Breakthrough Announced", "url": "http://example.com/ai", 
             "summary": "Researchers have developed a new AI model that exceeds human performance on cognitive tasks.",
             "notable_aspects": "The model requires 50% less computing power than previous versions."}
        ]),
        ("Finance Updates", [
            {"title": "Market Report Q3", "url": "http://example.com/market", 
             "summary": "Markets showed resilience despite inflation concerns.",
             "notable_aspects": "Tech stocks outperformed expectations."},
            {"title": "New Tax Regulations", "url": "http://example.com/tax", 
             "summary": "Government announces simplified tax filing procedures for small businesses.",
             "notable_aspects": "Expected to save businesses an average of $2000 annually."}
        ])
    ]
    
    newsletter = generate_newsletter_digest(test_feeds)
    if newsletter:
        print("Opening Paragraph:")
        print(newsletter.opening_paragraph)
        print("\nCategorized Content:")
        for category, content in newsletter.categorized_content.items():
            print(f"\n{category}:")
            print(f"Summary: {content.summary}")
            if hasattr(content, "is_single_article") and content.is_single_article:
                print(f"Notable Aspects: {content.notable_aspects}")
            print("Sources:")
            for source in content.sources:
                print(f"- {source.title} ({source.url})")
                if not (hasattr(content, "is_single_article") and content.is_single_article):
                    print(f"  Highlight: {source.highlight}")