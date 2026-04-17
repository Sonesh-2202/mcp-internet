"""
Reddit Search Tool - Search Reddit posts and discussions.

Uses Reddit's JSON API (no authentication required for public content).
"""

import logging
from urllib.parse import quote_plus

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)


async def search_reddit(
    query: str,
    subreddit: str = "",
    num_results: int = 5,
    sort: str = "relevance"
) -> str:
    """
    Search Reddit for posts and discussions.
    
    Args:
        query: Search query
        subreddit: Optional subreddit to search within (e.g., 'python', 'programming')
        num_results: Number of results to return (default: 5, max: 10)
        sort: Sort order - 'relevance', 'hot', 'top', 'new', 'comments'
        
    Returns:
        Formatted list of Reddit posts with titles, subreddits, and URLs
    """
    if not query.strip():
        return "❌ Error: Please provide a search query."
    
    num_results = min(num_results, 10)
    encoded_query = quote_plus(query)
    
    # Build URL
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={encoded_query}&restrict_sr=1&sort={sort}&limit={num_results}"
    else:
        url = f"https://www.reddit.com/search.json?q={encoded_query}&sort={sort}&limit={num_results}"
    
    data = await fetch_json(url)
    
    if not data or "data" not in data:
        return f"❌ Error: Unable to search Reddit for '{query}'."
    
    posts = data.get("data", {}).get("children", [])
    
    if not posts:
        return f"No Reddit posts found for: {query}"
    
    # Format output
    output = f"🤖 Reddit Search Results for: '{query}'"
    if subreddit:
        output += f" in r/{subreddit}"
    output += "\n" + "=" * 50 + "\n"
    
    for i, post in enumerate(posts, 1):
        post_data = post.get("data", {})
        
        title = post_data.get("title", "No title")
        subreddit_name = post_data.get("subreddit", "unknown")
        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)
        permalink = post_data.get("permalink", "")
        selftext = post_data.get("selftext", "")[:200]
        
        post_url = f"https://reddit.com{permalink}" if permalink else ""
        
        output += f"\n{i}. {title}\n"
        output += f"   📍 r/{subreddit_name} | ⬆️ {score} | 💬 {num_comments} comments\n"
        output += f"   🔗 {post_url}\n"
        
        if selftext:
            # Clean up the text preview
            preview = selftext.replace('\n', ' ').strip()
            output += f"   📝 {preview}...\n"
    
    return output


async def get_subreddit_posts(
    subreddit: str,
    sort: str = "hot",
    num_results: int = 5
) -> str:
    """
    Get top posts from a subreddit.
    
    Args:
        subreddit: Subreddit name (without r/)
        sort: Sort order - 'hot', 'new', 'top', 'rising'
        num_results: Number of posts to return (default: 5, max: 10)
        
    Returns:
        Formatted list of posts from the subreddit
    """
    if not subreddit.strip():
        return "❌ Error: Please provide a subreddit name."
    
    # Remove r/ prefix if provided
    subreddit = subreddit.replace("r/", "").strip()
    num_results = min(num_results, 10)
    
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={num_results}"
    
    data = await fetch_json(url)
    
    if not data or "data" not in data:
        return f"❌ Error: Unable to fetch posts from r/{subreddit}. The subreddit may not exist or is private."
    
    posts = data.get("data", {}).get("children", [])
    
    if not posts:
        return f"No posts found in r/{subreddit}"
    
    # Format output
    output = f"🤖 Top Posts from r/{subreddit} ({sort})\n"
    output += "=" * 50 + "\n"
    
    for i, post in enumerate(posts, 1):
        post_data = post.get("data", {})
        
        title = post_data.get("title", "No title")
        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)
        permalink = post_data.get("permalink", "")
        author = post_data.get("author", "unknown")
        
        post_url = f"https://reddit.com{permalink}" if permalink else ""
        
        output += f"\n{i}. {title}\n"
        output += f"   👤 u/{author} | ⬆️ {score} | 💬 {num_comments} comments\n"
        output += f"   🔗 {post_url}\n"
    
    return output
