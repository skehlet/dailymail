import json
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from dailymail_shared.my_openai import call_openai_with_structured_outputs

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
    notable_aspects: str = Field(..., description="1-2 notable or unexpected aspects about this set of articles as complete sentences, not as a list.")

class OpeningParagraph(BaseModel):
    """Model for validating the opening paragraph response."""
    text: str = Field(..., description="The opening paragraph text")

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
Then, identify 1-2 notable aspects about the collection of articles as a whole, and provide a brief highlight for each source article.

Your output should follow this exact structure:
- A "summary" field with 3-4 sentences summarizing key developments across all articles
- A "notable_aspects" field with 1-2 complete sentences highlighting unexpected information, unique perspectives, or important implications from these articles as a group
  - Write these as flowing prose sentences, not as a bulleted or numbered list
  - Focus on elements that add depth beyond the main summary
  - Identify potential consequences, historical context, or statistical outliers worth attention
- A "sources" list where each item has:
  - "title": The article title
  - "url": The article URL 
  - "highlight": A 1-2 sentence highlight of what's most interesting about this specific article

Focus on delivering substantive information clearly and concisely. Do not include introductions, 
pleasantries, or notes about your task. Just the requested content.
"""

    articles_info = f"Here are the articles to summarize:\n\n{articles_json}"
    
    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": articles_info}
    ]
    
    # Make the API call using the OpenAI structured outputs method
    try:
        result = call_openai_with_structured_outputs(messages, MultiArticleSummary)
        return MultiArticleSummary.model_validate(result)
    except Exception as e:
        print(f"Error generating multi-article summary: {e}")
        raise

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
        # Use full summaries for better content representation
        sample_summaries = []
        for article in feed["articles"][:2]:  # Include up to 2 sample articles
            summary = article.get("summary", "")
            if summary:
                sample_summaries.append(summary)
        
        feed_info.append({
            "category": feed["category"],
            "article_count": len(feed["articles"]),
            "sample_summaries": sample_summaries
        })
    
    feed_info_json = json.dumps(feed_info, indent=2)
    
    prompt = """
Create a concise opening paragraph (2-3 sentences) for a newsletter that highlights 3-5 key stories 
across different categories. The paragraph should:

- Directly mention specific, interesting details from the article summaries provided
- Focus on the substantive content from the summaries, not just category names
- Maintain a professional, informative tone
- Avoid greetings or pleasantries
- Prioritize facts and developments over clickbait or sensational claims

For example: "Today, the tech world saw a major breakthrough in AI that exceeds human performance on cognitive tasks, 
while the finance sector showed resilience despite ongoing inflation concerns."

Your response should be ONLY the paragraph text with no additional explanations or notes.
"""

    info_text = f"Here is information about the feeds to highlight:\n\n{feed_info_json}"
    
    # Make the API call to OpenAI
    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": info_text}
    ]
    
    try:
        result = call_openai_with_structured_outputs(messages, OpeningParagraph)
        return result["text"]
    except Exception as e:
        print(f"Error generating opening paragraph: {e}")
        # Fallback to a generic opening
        return "Today's news digest covers a variety of important topics from multiple sources."

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
                    notable_aspects=multi_summary.notable_aspects,
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
            if content.notable_aspects:
                print(f"Notable Aspects: {content.notable_aspects}")
            print("Sources:")
            for source in content.sources:
                print(f"- {source.title} ({source.url})")
                if not content.is_single_article:
                    print(f"  Highlight: {source.highlight}")