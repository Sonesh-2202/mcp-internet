"""
Twitter/X Search Tool - Search tweets using Nitter instances.

Nitter is an open-source Twitter frontend that allows scraping without auth.
"""

import logging
import re
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)

# List of Nitter instances (some may be down)
NITTER_INSTANCES = [
    "nitter.privacydev.net",
    "nitter.poast.org",
    "nitter.1d4.us",
]


async def search_twitter(query: str, num_results: int = 5) -> str:
    """
    Search Twitter/X for tweets.
    
    Args:
        query: Search query
        num_results: Number of tweets to return (default: 5, max: 10)
        
    Returns:
        List of matching tweets with authors and content
        
    Note:
        Uses Nitter (open-source Twitter frontend). 
        Results may be limited depending on instance availability.
    """
    if not query.strip():
        return "❌ Error: Please provide a search query."
    
    num_results = min(num_results, 10)
    encoded_query = quote_plus(query)
    
    # Try each Nitter instance
    html = None
    working_instance = None
    
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/search?f=tweets&q={encoded_query}"
        html = await fetch_url(url)
        if html and "timeline-item" in html:
            working_instance = instance
            break
    
    if not html or not working_instance:
        return f"""❌ Unable to search Twitter for '{query}'.

Nitter instances may be temporarily unavailable. 
You can try searching directly at: https://twitter.com/search?q={encoded_query}
"""
    
    try:
        soup = BeautifulSoup(html, "lxml")
        tweets = []
        
        for tweet_div in soup.select(".timeline-item")[:num_results]:
            # Get author info
            author_elem = tweet_div.select_one(".username")
            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
            
            fullname_elem = tweet_div.select_one(".fullname")
            fullname = fullname_elem.get_text(strip=True) if fullname_elem else author
            
            # Get tweet content
            content_elem = tweet_div.select_one(".tweet-content")
            content = content_elem.get_text(strip=True) if content_elem else "No content"
            
            # Get stats
            stats_elem = tweet_div.select(".tweet-stat")
            stats = {}
            for stat in stats_elem:
                text = stat.get_text(strip=True)
                if "retweet" in stat.get("title", "").lower():
                    stats["retweets"] = text
                elif "like" in stat.get("title", "").lower():
                    stats["likes"] = text
                elif "quote" in stat.get("title", "").lower():
                    stats["quotes"] = text
            
            # Get tweet link
            link_elem = tweet_div.select_one(".tweet-link")
            tweet_path = link_elem.get("href", "") if link_elem else ""
            tweet_url = f"https://twitter.com{tweet_path}" if tweet_path else ""
            
            tweets.append({
                "author": author,
                "fullname": fullname,
                "content": content[:280],
                "retweets": stats.get("retweets", "0"),
                "likes": stats.get("likes", "0"),
                "url": tweet_url
            })
        
        if not tweets:
            return f"No tweets found for: {query}"
        
        # Format output
        output = f"🐦 Twitter Search: '{query}'\n"
        output += "=" * 50 + "\n"
        
        for i, tweet in enumerate(tweets, 1):
            output += f"\n{i}. **{tweet['fullname']}** {tweet['author']}\n"
            output += f"   {tweet['content']}\n"
            output += f"   🔁 {tweet['retweets']} | ❤️ {tweet['likes']}\n"
            if tweet['url']:
                output += f"   🔗 {tweet['url']}\n"
        
        output += f"\n💡 Results via Nitter ({working_instance})"
        
        return output
        
    except Exception as e:
        logger.error(f"Error parsing Twitter results: {e}")
        return f"❌ Error: Unable to parse Twitter search results."


async def get_user_tweets(username: str, num_results: int = 5) -> str:
    """
    Get recent tweets from a Twitter user.
    
    Args:
        username: Twitter username (without @)
        num_results: Number of tweets to return (default: 5, max: 10)
        
    Returns:
        Recent tweets from the user
    """
    if not username.strip():
        return "❌ Error: Please provide a Twitter username."
    
    username = username.strip().lstrip("@")
    num_results = min(num_results, 10)
    
    # Try each Nitter instance
    html = None
    working_instance = None
    
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/{username}"
        html = await fetch_url(url)
        if html and "timeline-item" in html:
            working_instance = instance
            break
    
    if not html or not working_instance:
        return f"""❌ Unable to fetch tweets from @{username}.

The user may not exist, or Nitter instances are temporarily unavailable.
Try visiting: https://twitter.com/{username}
"""
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Get user info
        profile_name = soup.select_one(".profile-card-fullname")
        profile_bio = soup.select_one(".profile-bio")
        
        name = profile_name.get_text(strip=True) if profile_name else username
        bio = profile_bio.get_text(strip=True) if profile_bio else ""
        
        tweets = []
        for tweet_div in soup.select(".timeline-item")[:num_results]:
            content_elem = tweet_div.select_one(".tweet-content")
            content = content_elem.get_text(strip=True) if content_elem else "No content"
            
            date_elem = tweet_div.select_one(".tweet-date a")
            date = date_elem.get("title", "") if date_elem else ""
            
            tweets.append({
                "content": content[:280],
                "date": date
            })
        
        if not tweets:
            return f"No tweets found from @{username}"
        
        # Format output
        output = f"🐦 **{name}** (@{username})\n"
        if bio:
            output += f"📝 {bio[:150]}{'...' if len(bio) > 150 else ''}\n"
        output += "=" * 50 + "\n"
        
        for i, tweet in enumerate(tweets, 1):
            output += f"\n{i}. {tweet['content']}\n"
            if tweet['date']:
                output += f"   📅 {tweet['date']}\n"
        
        output += f"\n🔗 https://twitter.com/{username}"
        
        return output
        
    except Exception as e:
        logger.error(f"Error parsing user tweets: {e}")
        return f"❌ Error: Unable to fetch tweets from @{username}."
