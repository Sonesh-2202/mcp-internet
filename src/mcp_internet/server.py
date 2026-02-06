"""
MCP Internet Server - Main Entry Point

This server provides internet access tools for local LLMs in LM Studio.
Run with: uv run python -m mcp_internet.server
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (important for MCP STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Initialize FastMCP server
mcp = FastMCP("mcp-internet")


# =============================================================================
# SEARCH TOOLS
# =============================================================================
@mcp.tool()
async def search_web(query: str, num_results: int = 10, deep_search: bool = False) -> str:
    """
    Search the internet using DuckDuckGo.
    
    Args:
        query: The search query
        num_results: Number of results (default: 10, max: 20)
        deep_search: Fetch content from top results for details
    """
    from .tools.search import search_web as _search
    return await _search(query, min(num_results, 20), deep_search)


@mcp.tool()
async def quick_lookup(query: str) -> str:
    """
    Quick info lookup - searches and fetches content from top result.
    
    Args:
        query: What to look up (person, topic, etc.)
    """
    from .tools.search import quick_lookup as _lookup
    return await _lookup(query)


@mcp.tool()
async def search_site(query: str, site: str) -> str:
    """
    Search within a specific website.
    
    Args:
        query: What to search for
        site: Website domain (e.g., 'linkedin.com', 'instagram.com')
    """
    from .tools.search import search_site as _search_site
    return await _search_site(query, site)


# =============================================================================
# CONTENT READING
# =============================================================================
@mcp.tool()
async def read_webpage(url: str, max_length: int = 5000) -> str:
    """
    Extract text content from a webpage.
    
    Args:
        url: The URL to read
        max_length: Maximum characters (default: 5000)
    """
    from .tools.webpage import read_webpage as _read
    return await _read(url, max_length)


@mcp.tool()
async def read_pdf(url: str, max_pages: int = 5) -> str:
    """
    Extract text from a PDF URL.
    
    Args:
        url: URL of the PDF file
        max_pages: Maximum pages to extract (default: 5)
    """
    from .tools.pdf_reader import read_pdf as _read_pdf
    return await _read_pdf(url, max_pages, 5000)


# =============================================================================
# NEWS & SOCIAL
# =============================================================================
@mcp.tool()
async def get_news(topic: str = "world", count: int = 5) -> str:
    """
    Get latest news headlines.
    
    Args:
        topic: 'world', 'technology', 'business', etc. or search query
        count: Number of headlines (default: 5)
    """
    from .tools.news import get_news as _news
    return await _news(topic, min(count, 10))


@mcp.tool()
async def search_reddit(query: str, subreddit: str = "", num_results: int = 5) -> str:
    """
    Search Reddit for posts.
    
    Args:
        query: Search query
        subreddit: Optional subreddit to search within
        num_results: Number of results (default: 5)
    """
    from .tools.reddit import search_reddit as _search_reddit
    return await _search_reddit(query, subreddit, min(num_results, 10), "relevance")


@mcp.tool()
async def search_twitter(query: str, num_results: int = 5) -> str:
    """
    Search Twitter/X for tweets.
    
    Args:
        query: Search query
        num_results: Number of tweets (default: 5)
    """
    from .tools.twitter import search_twitter as _search_twitter
    return await _search_twitter(query, min(num_results, 10))


# =============================================================================
# YOUTUBE
# =============================================================================
@mcp.tool()
async def search_youtube(query: str, num_results: int = 5) -> str:
    """
    Search YouTube for videos.
    
    Args:
        query: Search query
        num_results: Number of results (default: 5)
    """
    from .tools.youtube import search_youtube as _search_yt
    return await _search_yt(query, min(num_results, 10))


@mcp.tool()
async def get_video_info(url: str) -> str:
    """
    Get YouTube video information.
    
    Args:
        url: YouTube video URL or video ID
    """
    from .tools.youtube import get_video_info as _get_video
    return await _get_video(url)


# =============================================================================
# GITHUB
# =============================================================================
@mcp.tool()
async def search_github(query: str, num_results: int = 5, language: str = "") -> str:
    """
    Search GitHub repositories.
    
    Args:
        query: Search query
        num_results: Number of results (default: 5)
        language: Filter by language (e.g., 'python')
    """
    from .tools.github import search_github as _search_gh
    return await _search_gh(query, min(num_results, 10), language, "stars")


@mcp.tool()
async def get_repo_info(repo: str) -> str:
    """
    Get GitHub repository information.
    
    Args:
        repo: Repository as 'owner/repo' (e.g., 'microsoft/vscode')
    """
    from .tools.github import get_repo_info as _get_repo
    return await _get_repo(repo)


# =============================================================================
# WEATHER & TIME
# =============================================================================
@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get weather forecast for a location.
    
    Args:
        location: City name (e.g., "Tokyo", "New York")
    """
    from .tools.weather import get_weather as _weather
    return await _weather(location)


@mcp.tool()
async def get_current_time(location: str = "UTC") -> str:
    """
    Get current time for a timezone or city.
    
    Args:
        location: Timezone or city name (e.g., "Tokyo", "America/New_York")
    """
    from .tools.time import get_current_time as _time
    return await _time(location)


# =============================================================================
# TRANSLATION & MATH
# =============================================================================
@mcp.tool()
async def translate_text(text: str, to_language: str = "english") -> str:
    """
    Translate text to another language.
    
    Args:
        text: Text to translate
        to_language: Target language (e.g., 'spanish', 'japanese')
    """
    from .tools.translator import translate_text as _translate
    return await _translate(text, to_language, "auto")


@mcp.tool()
async def calculate(expression: str) -> str:
    """
    Evaluate a math expression safely.
    
    Args:
        expression: Math expression (e.g., "sqrt(16)", "15% of 200")
    """
    from .tools.math_tools import calculate as _calc
    return await _calc(expression)


# =============================================================================
# URL & IP TOOLS
# =============================================================================
@mcp.tool()
async def shorten_url(url: str) -> str:
    """
    Create a shortened URL.
    
    Args:
        url: The long URL to shorten
    """
    from .tools.urls import shorten_url as _shorten
    return await _shorten(url)


@mcp.tool()
async def get_my_ip() -> str:
    """Get your public IP address with location info."""
    from .tools.ip_tools import get_my_ip as _my_ip
    return await _my_ip()


@mcp.tool()
async def geolocate_ip(ip: str) -> str:
    """
    Get location info for an IP address.
    
    Args:
        ip: IP address to look up
    """
    from .tools.ip_tools import geolocate_ip as _geolocate
    return await _geolocate(ip)


# =============================================================================
# QR CODES
# =============================================================================
@mcp.tool()
async def generate_qr(content: str, size: int = 200) -> str:
    """
    Generate a QR code for text or URL.
    
    Args:
        content: Text or URL to encode
        size: Size in pixels (default: 200)
    """
    from .tools.qr_code import generate_qr as _gen_qr
    return await _gen_qr(content, size)


@mcp.tool()
async def generate_wifi_qr(ssid: str, password: str, security: str = "WPA") -> str:
    """
    Generate a WiFi QR code.
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        security: 'WPA', 'WEP', or 'nopass'
    """
    from .tools.qr_code import generate_wifi_qr as _wifi_qr
    return await _wifi_qr(ssid, password, security, False)


# =============================================================================
# EMAIL
# =============================================================================
@mcp.tool()
async def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Send an email (requires SMTP config via env vars).
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body text
    """
    from .tools.email_sender import send_email as _send_email
    return await _send_email(to_email, subject, body, "", 587, "", "")


# =============================================================================
# Server Entry Point
# =============================================================================
async def warmup():
    """Pre-initialize components to avoid cold-start delays."""
    try:
        # Warmup HTTP client
        from .utils.http_client import get_client
        await get_client()
        logger.info("HTTP client warmed up")
    except Exception as e:
        logger.warning(f"Warmup failed (non-critical): {e}")


def main():
    """Run the MCP server using STDIO transport."""
    import asyncio
    
    logger.info("Starting MCP Internet Server...")
    
    # Warmup components
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(warmup())
    except Exception as e:
        logger.warning(f"Warmup error: {e}")
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
