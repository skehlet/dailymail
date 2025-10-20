import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import instructor
from dailymail_shared.my_instructor import get_instructor_client, get_structured_output, CONTEXT_WINDOW_SIZE

# --- Pydantic Models for Validation ---

class NewsletterSource(BaseModel):
    """Represents a single source article within a category."""
    title: str = Field(description="The title of the source article.")
    url: str = Field(description="The URL of the source article.")
    highlight: str = Field(
        description="1-2 sentence highlight capturing the single most important or interesting finding from this specific article."
    )

class CategoryContent(BaseModel):
    """Represents the content for a single news category."""
    summary: str = Field(
        description="3-4 sentence synthesis of the most important developments and recurring themes from all articles in this category. "
        "Write as an integrated narrative, not a list."
    )
    sources: List[NewsletterSource] = Field(
        description="List of source articles with highlights for each."
    )
    notable_aspects: str = Field(
        default="",
        description="1-2 flowing prose sentences describing what is most notable, unexpected, or important about this collection. "
        "Focus on trends, contradictions, surprising data, or broader implications. Don't repeat the summary."
    )
    is_single_article: bool = Field(
        default=False, 
        description="Flag to identify if this is a single article feed"
    )

class MultiArticleSummary(BaseModel):
    """Summary response for multiple articles in a feed."""
    summary: str = Field(
        description="3-4 sentence synthesis of the most important developments and recurring themes from all articles. "
        "Write as an integrated narrative for a busy executive, not a list."
    )
    sources: List[NewsletterSource] = Field(
        description="List of source articles. Each highlight must be unique and capture what sets that article apart from the others."
    )
    notable_aspects: str = Field(
        description="1-2 flowing prose sentences on what's most notable, unexpected, or important about this collection as a group. "
        "Focus on new trends, contradictions, surprising data, or broader implications."
    )

class NewsletterContent(BaseModel):
    """Final newsletter content structure assembled by Python."""
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
    
    contents = f"""\
You are an intelligence analyst synthesizing multiple articles from a single news feed into a consolidated briefing.

Analyze all articles to identify overarching themes, collective insights, and key individual findings.

FEED: {feed_title}

ARTICLES:
{articles_json}
"""
    contents = contents[:CONTEXT_WINDOW_SIZE - 100]
    
    try:
        client = get_instructor_client()
        result = get_structured_output(client, contents, MultiArticleSummary)
        return result
    except instructor.exceptions.InstructorRetryException as e:
        print(f"Instructor retry error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during summarization: {e}")
        raise


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
    
    # 2. Process each feed based on number of articles
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
    
    # 3. Assemble the final newsletter content
    newsletter = NewsletterContent(
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
        print("Categorized Content:")
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