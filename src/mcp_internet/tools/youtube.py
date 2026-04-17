"""
YouTube Search Tool - Search YouTube videos and get video info.

Uses YouTube's public search page for video discovery.
No API key required!
"""

import logging
import re
from urllib.parse import quote_plus, unquote, parse_qs, urlparse

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url, fetch_json

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str | None:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def search_youtube(query: str, num_results: int = 5) -> str:
    """
    Search YouTube for videos.
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 5, max: 10)
        
    Returns:
        Formatted list of YouTube videos with titles, URLs, and descriptions
    """
    if not query.strip():
        return "❌ Error: Please provide a search query."
    
    num_results = min(num_results, 10)
    encoded_query = quote_plus(query)
    
    # Use YouTube's search page
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    html = await fetch_url(url)
    if not html:
        return f"❌ Error: Unable to search YouTube for '{query}'."
    
    try:
        # Extract video data from the page
        # YouTube embeds JSON data in the page
        results = []
        
        # Find video IDs and titles in the HTML/JSON
        video_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
        title_pattern = r'"title":\{"runs":\[\{"text":"([^"]+)"\}\]'
        
        video_ids = re.findall(video_pattern, html)
        titles = re.findall(title_pattern, html)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_videos = []
        for vid in video_ids:
            if vid not in seen:
                seen.add(vid)
                unique_videos.append(vid)
        
        # Match videos with titles
        for i, video_id in enumerate(unique_videos[:num_results]):
            title = titles[i] if i < len(titles) else "Unknown Title"
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            results.append({
                "title": title,
                "url": video_url,
                "video_id": video_id
            })
        
        if not results:
            return f"No videos found for: {query}"
        
        # Format output
        output = f"🎬 YouTube Search Results for: '{query}'\n"
        output += "=" * 50 + "\n"
        
        for i, video in enumerate(results, 1):
            output += f"\n{i}. {video['title']}\n"
            output += f"   🔗 {video['url']}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error parsing YouTube results: {e}")
        return f"❌ Error: Unable to parse YouTube search results."


async def get_video_info(url: str) -> str:
    """
    Get information about a YouTube video.
    
    Args:
        url: YouTube video URL or video ID
        
    Returns:
        Video information including title, description, views, etc.
    """
    # Extract video ID
    video_id = url if len(url) == 11 else extract_video_id(url)
    
    if not video_id:
        return "❌ Error: Invalid YouTube URL or video ID."
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    html = await fetch_url(video_url)
    if not html:
        return f"❌ Error: Unable to fetch video info for {video_id}."
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Get title
        title_match = re.search(r'"title":"([^"]+)"', html)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # Get description
        desc_match = re.search(r'"shortDescription":"([^"]*)"', html)
        description = desc_match.group(1) if desc_match else "No description"
        description = description.replace('\\n', '\n')[:500]
        
        # Get view count
        views_match = re.search(r'"viewCount":"(\d+)"', html)
        views = views_match.group(1) if views_match else "Unknown"
        if views.isdigit():
            views = f"{int(views):,}"
        
        # Get channel name
        channel_match = re.search(r'"ownerChannelName":"([^"]+)"', html)
        channel = channel_match.group(1) if channel_match else "Unknown Channel"
        
        # Get duration
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if duration_match:
            seconds = int(duration_match.group(1))
            minutes, secs = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                duration = f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                duration = f"{minutes}:{secs:02d}"
        else:
            duration = "Unknown"
        
        output = f"""🎬 **{title}**
🔗 {video_url}

📺 Channel: {channel}
👁️ Views: {views}
⏱️ Duration: {duration}

📝 Description:
{description}
"""
        return output
        
    except Exception as e:
        logger.error(f"Error parsing video info: {e}")
        return f"❌ Error: Unable to parse video information."
