"""
Hacker News Tool - Fetch top stories and search Hacker News.

Uses the official Hacker News API and Algolia HN Search API.
No API key required!
"""

import logging
from urllib.parse import quote_plus

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

# Hacker News API endpoints
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA_API = "https://hn.algolia.com/api/v1"


async def get_hackernews(
    category: str = "top",
    num_results: int = 10
) -> str:
    """
    Get stories from Hacker News.
    
    Args:
        category: Type of stories - 'top', 'new', 'best', 'ask', 'show', 'job'
        num_results: Number of stories to return (default: 10, max: 20)
        
    Returns:
        Formatted list of Hacker News stories
    """
    valid_categories = ["top", "new", "best", "ask", "show", "job"]
    
    if category.lower() not in valid_categories:
        return f"❌ Error: Invalid category '{category}'. Valid options: {', '.join(valid_categories)}"
    
    num_results = min(num_results, 20)
    
    # Get story IDs
    url = f"{HN_API_BASE}/{category.lower()}stories.json"
    story_ids = await fetch_json(url)
    
    if not story_ids:
        return f"❌ Error: Unable to fetch {category} stories from Hacker News."
    
    # Fetch individual stories
    stories = []
    for story_id in story_ids[:num_results]:
        story_url = f"{HN_API_BASE}/item/{story_id}.json"
        story = await fetch_json(story_url)
        if story:
            stories.append(story)
    
    if not stories:
        return f"No {category} stories found on Hacker News."
    
    # Format output
    category_emoji = {
        "top": "🔥",
        "new": "🆕",
        "best": "⭐",
        "ask": "❓",
        "show": "📺",
        "job": "💼"
    }
    
    output = f"{category_emoji.get(category, '📰')} Hacker News - {category.capitalize()} Stories\n"
    output += "=" * 50 + "\n"
    
    for i, story in enumerate(stories, 1):
        title = story.get("title", "No title")
        url = story.get("url", "")
        score = story.get("score", 0)
        by = story.get("by", "unknown")
        descendants = story.get("descendants", 0)  # comment count
        story_id = story.get("id", "")
        
        hn_link = f"https://news.ycombinator.com/item?id={story_id}"
        
        output += f"\n{i}. {title}\n"
        output += f"   ⬆️ {score} points | 👤 {by} | 💬 {descendants} comments\n"
        
        if url:
            output += f"   🔗 {url}\n"
        output += f"   📰 {hn_link}\n"
    
    return output


async def search_hackernews(
    query: str,
    num_results: int = 10,
    search_type: str = "story"
) -> str:
    """
    Search Hacker News using Algolia API.
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 10, max: 20)
        search_type: Type to search - 'story', 'comment', 'all'
        
    Returns:
        Formatted search results from Hacker News
    """
    if not query.strip():
        return "❌ Error: Please provide a search query."
    
    num_results = min(num_results, 20)
    encoded_query = quote_plus(query)
    
    # Build search URL
    tag_filter = ""
    if search_type == "story":
        tag_filter = "&tags=story"
    elif search_type == "comment":
        tag_filter = "&tags=comment"
    
    url = f"{HN_ALGOLIA_API}/search?query={encoded_query}&hitsPerPage={num_results}{tag_filter}"
    
    data = await fetch_json(url)
    
    if not data or "hits" not in data:
        return f"❌ Error: Unable to search Hacker News for '{query}'."
    
    hits = data.get("hits", [])
    
    if not hits:
        return f"No Hacker News results found for: {query}"
    
    # Format output
    output = f"🔍 Hacker News Search: '{query}'\n"
    output += "=" * 50 + "\n"
    
    for i, hit in enumerate(hits, 1):
        title = hit.get("title") or hit.get("story_title", "No title")
        url = hit.get("url", "")
        points = hit.get("points", 0)
        author = hit.get("author", "unknown")
        num_comments = hit.get("num_comments", 0)
        object_id = hit.get("objectID", "")
        
        hn_link = f"https://news.ycombinator.com/item?id={object_id}"
        
        output += f"\n{i}. {title}\n"
        
        if points is not None:
            output += f"   ⬆️ {points} points | 👤 {author}"
            if num_comments is not None:
                output += f" | 💬 {num_comments} comments"
            output += "\n"
        
        if url:
            output += f"   🔗 {url}\n"
        output += f"   📰 {hn_link}\n"
    
    return output
