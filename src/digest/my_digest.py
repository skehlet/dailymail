import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dailymail_shared.my_gemini import call_gemini_with_structured_outputs

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
    
    contents = f"""
# ROLE
You are an expert intelligence analyst and senior editor. Your task is to synthesize multiple articles from a single news feed into a single, consolidated briefing.

# TASK
You will be given a feed title and a list of articles. Your task is to analyze all articles to identify the overarching themes, notable collective insights, and key individual findings. Based on your synthesis, you will populate the fields of the required structured output.

# INSTRUCTIONS FOR CONTENT

Overall Summary (for the summary field):

Write a 3-4 sentence narrative that synthesizes the most important developments and recurring themes from all articles combined.

This should provide a high-level, integrated overview of the topic as presented in the feed, as if you were briefing a busy executive.

Collective Insights (for the notable_aspects field):

In 1-2 flowing prose sentences, describe what is most notable, unexpected, or important about this collection of articles when viewed as a group.

Focus on new trends, contradictions between reports, surprising data points, or the broader implications of the combined information. Do not simply repeat points from the summary.

Individual Source Highlights (for the sources list):

For each article provided in the input, you must generate a corresponding item in the output list.

Each item must include the original title and url.

For the highlight of each source, write a unique 1-2 sentence summary that captures the single most important or interesting finding from that specific article, setting it apart from the others.

# OUTPUT REQUIREMENTS

Deliver only the requested content. Do not include any introductions, pleasantries, apologies, or notes about the process.

# ARTICLES TO ANALYZE

Feed Title: "{feed_title}"

Articles:
{articles_json}
"""

    # Make the API call using the OpenAI structured outputs method
    result = call_gemini_with_structured_outputs(contents, MultiArticleSummary)
    return result


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
    
    contents = f"""
# ROLE
You are a senior editor writing the opening paragraph for a prestigious daily news briefing for informed professionals.

# TASK
Your task is to write a single, compelling introductory paragraph (2-3 sentences) that acts as a "hook" for the entire newsletter. You will achieve this by synthesizing the most significant details from the provided story summaries into a concise and cohesive narrative.

# GUIDELINES FOR THE PARAGRAPH

Synthesize, Don't List: Instead of just listing categories (e.g., "In tech, finance, and politics..."), you must seamlessly weave specific, interesting details from 3-5 of the most important stories into your narrative.

Hook with Substance: Grab the reader's attention with concrete facts and key developments from the provided summaries. Prioritize substance over sensationalism or vague, clickbait-style claims.

Professional Tone: The tone must be professional, direct, and informative.

# EXAMPLE OF TONE AND STYLE
"Today, the tech world saw a major breakthrough in AI that exceeds human performance on cognitive tasks, while the finance sector showed resilience despite ongoing inflation concerns."

# OUTPUT REQUIREMENTS
Your response must be the paragraph text ONLY. Do not include any greetings ("Hello,"), closings, titles (like "Newsletter Opening:"), or any other conversational text or markdown formatting.

# STORIES TO HIGHLIGHT
Here is the information about the stories to highlight:

{feed_info_json}
"""

    result = call_gemini_with_structured_outputs(contents, OpeningParagraph)
    return result.text

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