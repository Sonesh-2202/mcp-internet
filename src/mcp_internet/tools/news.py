"""
News Tool - Fetch latest news headlines.

Uses ddgs library for reliable and fresh news results.
Falls back to Google News RSS if needed.
"""

import logging
from datetime import datetime
from html import unescape
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from ddgs import DDGS

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)

# Google News RSS topic mappings (fallback)
TOPIC_URLS = {
    "world": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "health": "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-US&gl=US&ceid=US:en",
    "sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
}


def get_news_ddgs(topic: str, count: int = 5) -> str | None:
    """Get news using ddgs library (primary method)."""
    try:
        ddgs = DDGS()
        
        # Use ddgs news search for fresh results
        results = list(ddgs.news(
            topic,
            max_results=count,
            timelimit="d"  # Last day for most recent news
        ))
        
        if not results:
            # Try with weekly timelimit
            results = list(ddgs.news(topic, max_results=count, timelimit="w"))
        
        if not results:
            return None
        
        output = f"Latest News: {topic}\n"
        output += "=" * 50 + "\n"
        
        for i, news in enumerate(results, 1):
            title = news.get("title", "No title")
            source = news.get("source", "Unknown")
            date = news.get("date", "")
            url = news.get("url", news.get("link", ""))
            body = news.get("body", news.get("excerpt", ""))[:200]
            
            output += f"\n{i}. {title}\n"
            output += f"   Source: {source}"
            if date:
                output += f" | {date}"
            output += f"\n   URL: {url}\n"
            if body:
                output += f"   {body}...\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error fetching news via ddgs: {e}")
        return None


def parse_google_news_item(item: BeautifulSoup) -> dict | None:
    """Parse a single news item from Google News RSS."""
    try:
        title_elem = item.find("title")
        link_elem = item.find("link")
        pub_date_elem = item.find("pubDate")
        source_elem = item.find("source")
        
        if not title_elem or not link_elem:
            return None
        
        title = unescape(title_elem.get_text(strip=True))
        link = link_elem.get_text(strip=True)
        source = source_elem.get_text(strip=True) if source_elem else "Unknown"
        
        # Parse date
        pub_date = ""
        if pub_date_elem:
            try:
                dt = datetime.strptime(
                    pub_date_elem.get_text(strip=True),
                    "%a, %d %b %Y %H:%M:%S %Z"
                )
                pub_date = dt.strftime("%b %d, %Y %H:%M")
            except ValueError:
                pub_date = pub_date_elem.get_text(strip=True)[:20]
        
        return {
            "title": title,
            "link": link,
            "source": source,
            "date": pub_date,
        }
    except Exception as e:
        logger.error(f"Error parsing news item: {e}")
        return None


async def get_news_rss(topic: str, count: int = 5) -> str | None:
    """Get news from Google News RSS (fallback method)."""
    topic_lower = topic.lower().strip()
    
    # Get RSS URL
    if topic_lower in TOPIC_URLS:
        rss_url = TOPIC_URLS[topic_lower]
        display_topic = topic_lower.capitalize()
    else:
        encoded = quote_plus(topic)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        display_topic = topic
    
    rss_content = await fetch_url(rss_url)
    if not rss_content:
        return None
    
    try:
        soup = BeautifulSoup(rss_content, "lxml-xml")
        items = soup.find_all("item")
        
        if not items:
            return None
        
        news_items = []
        for item in items[:count]:
            parsed = parse_google_news_item(item)
            if parsed:
                news_items.append(parsed)
        
        if not news_items:
            return None
        
        # Format output
        output = f"Latest {display_topic} News\n"
        output += "=" * 50 + "\n"
        
        for i, news in enumerate(news_items, 1):
            output += f"\n{i}. {news['title']}\n"
            output += f"   Source: {news['source']} | {news['date']}\n"
            output += f"   URL: {news['link']}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error parsing news feed: {e}")
        return None


async def get_news(topic: str = "world", count: int = 5) -> str:
    """
    Get latest news headlines.
    
    Uses ddgs library for fresh news, falls back to Google News RSS.
    
    Args:
        topic: News topic or search query
        count: Number of headlines to return
        
    Returns:
        Formatted news headlines
    """
    # Try ddgs first (more reliable for fresh news)
    result = get_news_ddgs(topic, count)
    if result:
        return result
    
    # Fallback to Google News RSS
    result = await get_news_rss(topic, count)
    if result:
        return result
    
    return f"Error: Unable to fetch news for '{topic}'. Please try again later."
