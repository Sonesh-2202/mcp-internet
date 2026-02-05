"""
URL Tools - Shorten and expand URLs.

Uses free URL shortening services (no API keys required).
"""

import logging
import re
from urllib.parse import quote, urlparse

from ..utils.http_client import fetch_url, fetch_json

logger = logging.getLogger(__name__)


async def shorten_url(url: str) -> str:
    """
    Create a shortened URL.
    
    Args:
        url: The long URL to shorten
        
    Returns:
        Shortened URL
    """
    if not url.strip():
        return "❌ Error: Please provide a URL to shorten."
    
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return "❌ Error: Invalid URL format."
    except Exception:
        return "❌ Error: Invalid URL format."
    
    # Use is.gd API (free, no registration)
    encoded_url = quote(url, safe='')
    api_url = f"https://is.gd/create.php?format=simple&url={encoded_url}"
    
    short_url = await fetch_url(api_url)
    
    if short_url and short_url.startswith("http"):
        return f"""🔗 **URL Shortened Successfully**
{'=' * 40}

📌 Original: {url}
✂️ Short URL: {short_url.strip()}
"""
    else:
        # Fallback to TinyURL
        tinyurl_api = f"https://tinyurl.com/api-create.php?url={encoded_url}"
        short_url = await fetch_url(tinyurl_api)
        
        if short_url and short_url.startswith("http"):
            return f"""🔗 **URL Shortened Successfully**
{'=' * 40}

📌 Original: {url}
✂️ Short URL: {short_url.strip()}
"""
        
        return "❌ Error: Unable to shorten URL. The service may be temporarily unavailable."


async def expand_url(short_url: str) -> str:
    """
    Expand a shortened URL to reveal the destination.
    
    Args:
        short_url: The shortened URL to expand
        
    Returns:
        The original long URL
    """
    if not short_url.strip():
        return "❌ Error: Please provide a URL to expand."
    
    # Add protocol if missing  
    if not short_url.startswith(("http://", "https://")):
        short_url = "https://" + short_url
    
    try:
        import httpx
        
        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=10.0
        ) as client:
            # Follow redirects manually to find the final URL
            current_url = short_url
            redirect_chain = [current_url]
            
            for _ in range(10):  # Max 10 redirects
                response = await client.head(current_url, follow_redirects=False)
                
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location", "")
                    if location:
                        # Handle relative redirects
                        if location.startswith("/"):
                            parsed = urlparse(current_url)
                            location = f"{parsed.scheme}://{parsed.netloc}{location}"
                        current_url = location
                        redirect_chain.append(current_url)
                    else:
                        break
                else:
                    break
            
            final_url = redirect_chain[-1]
            
            output = f"""🔗 **URL Expanded**
{'=' * 40}

📌 Short URL: {short_url}
🎯 Destination: {final_url}
"""
            
            if len(redirect_chain) > 2:
                output += f"\n📍 Redirect chain ({len(redirect_chain)} hops):\n"
                for i, url in enumerate(redirect_chain):
                    output += f"   {i+1}. {url}\n"
            
            return output
            
    except Exception as e:
        logger.error(f"Error expanding URL: {e}")
        return f"❌ Error: Unable to expand URL. The URL may be invalid or the server is unreachable."
