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
        query: The search query (person name, topic, question, etc.)
        num_results: Number of results to return (default: 10, max: 20)
        deep_search: Set to True to fetch and analyze content from top results
                     for more detailed information
    
    Returns:
        Search results with titles, URLs, and descriptions.
        If deep_search=True, also includes extracted content from top pages.
    """
    from .tools.search import search_web as _search
    return await _search(query, min(num_results, 20), deep_search)


@mcp.tool()
async def quick_lookup(query: str) -> str:
    """
    Quick lookup for a topic - ideal for finding info about people, places, or concepts.
    Searches the web and automatically fetches content from the most relevant result.
    
    Args:
        query: What to look up (e.g., "Sujaya Pon Gita", "Elon Musk", "Python programming")
    
    Returns:
        Search results plus detailed content from the most relevant page
    """
    from .tools.search import quick_lookup as _lookup
    return await _lookup(query)


@mcp.tool()
async def search_site(query: str, site: str) -> str:
    """
    Search within a specific website (LinkedIn, Instagram, GitHub, etc.)
    
    Args:
        query: What to search for
        site: Website domain (e.g., 'linkedin.com', 'instagram.com', 'github.com')
    
    Returns:
        Search results from that specific website only
    
    Examples:
        search_site("John Doe", "linkedin.com") - Find John Doe's LinkedIn
        search_site("sonesh_2202", "instagram.com") - Find Instagram profile
    """
    from .tools.search import search_site as _search_site
    return await _search_site(query, site)


# =============================================================================
# CONTENT READING TOOLS
# =============================================================================
@mcp.tool()
async def read_webpage(url: str, max_length: int = 5000) -> str:
    """
    Read and extract the main text content from a webpage.
    
    Args:
        url: The URL of the webpage to read
        max_length: Maximum characters to return (default: 5000)
    
    Returns:
        The main text content of the webpage
    """
    from .tools.webpage import read_webpage as _read
    return await _read(url, max_length)


@mcp.tool()
async def read_pdf(url: str, max_pages: int = 5, max_length: int = 5000) -> str:
    """
    Extract text content from a PDF URL.
    
    Args:
        url: URL of the PDF file
        max_pages: Maximum number of pages to extract (default: 5)
        max_length: Maximum characters to return (default: 5000)
    
    Returns:
        Extracted text from the PDF
    """
    from .tools.pdf_reader import read_pdf as _read_pdf
    return await _read_pdf(url, max_pages, max_length)


# =============================================================================
# NEWS & SOCIAL MEDIA TOOLS
# =============================================================================
@mcp.tool()
async def get_news(topic: str = "world", count: int = 5) -> str:
    """
    Get the latest news headlines from Google News.
    
    Args:
        topic: News topic - 'world', 'business', 'technology', 'science', 
               'health', 'sports', 'entertainment', or a search query
        count: Number of headlines to return (default: 5, max: 10)
    
    Returns:
        Latest news headlines with sources and links
    """
    from .tools.news import get_news as _news
    return await _news(topic, min(count, 10))


@mcp.tool()
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
        List of Reddit posts with titles, scores, and links
    """
    from .tools.reddit import search_reddit as _search_reddit
    return await _search_reddit(query, subreddit, min(num_results, 10), sort)


@mcp.tool()
async def get_subreddit_posts(subreddit: str, sort: str = "hot", num_results: int = 5) -> str:
    """
    Get top posts from a subreddit.
    
    Args:
        subreddit: Subreddit name (without r/)
        sort: Sort order - 'hot', 'new', 'top', 'rising'
        num_results: Number of posts to return (default: 5, max: 10)
    
    Returns:
        List of posts from the subreddit
    """
    from .tools.reddit import get_subreddit_posts as _get_subreddit
    return await _get_subreddit(subreddit, sort, min(num_results, 10))


@mcp.tool()
async def get_hackernews(category: str = "top", num_results: int = 10) -> str:
    """
    Get stories from Hacker News.
    
    Args:
        category: Type of stories - 'top', 'new', 'best', 'ask', 'show', 'job'
        num_results: Number of stories to return (default: 10, max: 20)
    
    Returns:
        List of Hacker News stories with scores and links
    """
    from .tools.hackernews import get_hackernews as _get_hn
    return await _get_hn(category, min(num_results, 20))


@mcp.tool()
async def search_hackernews(query: str, num_results: int = 10, search_type: str = "story") -> str:
    """
    Search Hacker News using Algolia API.
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 10, max: 20)
        search_type: Type to search - 'story', 'comment', 'all'
    
    Returns:
        Search results from Hacker News
    """
    from .tools.hackernews import search_hackernews as _search_hn
    return await _search_hn(query, min(num_results, 20), search_type)


@mcp.tool()
async def search_twitter(query: str, num_results: int = 5) -> str:
    """
    Search Twitter/X for tweets.
    
    Args:
        query: Search query
        num_results: Number of tweets to return (default: 5, max: 10)
    
    Returns:
        List of tweets with authors and content
    
    Note: Uses Nitter (open-source Twitter frontend). Results may vary.
    """
    from .tools.twitter import search_twitter as _search_twitter
    return await _search_twitter(query, min(num_results, 10))


@mcp.tool()
async def get_user_tweets(username: str, num_results: int = 5) -> str:
    """
    Get recent tweets from a Twitter user.
    
    Args:
        username: Twitter username (without @)
        num_results: Number of tweets to return (default: 5, max: 10)
    
    Returns:
        Recent tweets from the user
    """
    from .tools.twitter import get_user_tweets as _get_tweets
    return await _get_tweets(username, min(num_results, 10))


# =============================================================================
# YOUTUBE TOOLS
# =============================================================================
@mcp.tool()
async def search_youtube(query: str, num_results: int = 5) -> str:
    """
    Search YouTube for videos.
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 5, max: 10)
    
    Returns:
        List of YouTube videos with titles and URLs
    """
    from .tools.youtube import search_youtube as _search_yt
    return await _search_yt(query, min(num_results, 10))


@mcp.tool()
async def get_video_info(url: str) -> str:
    """
    Get information about a YouTube video.
    
    Args:
        url: YouTube video URL or video ID
    
    Returns:
        Video information including title, description, views, etc.
    """
    from .tools.youtube import get_video_info as _get_video
    return await _get_video(url)


# =============================================================================
# GITHUB TOOLS
# =============================================================================
@mcp.tool()
async def search_github(
    query: str,
    num_results: int = 5,
    language: str = "",
    sort: str = "stars"
) -> str:
    """
    Search GitHub repositories.
    
    Args:
        query: Search query (keywords, topics, etc.)
        num_results: Number of results to return (default: 5, max: 10)
        language: Filter by programming language (e.g., 'python', 'javascript')
        sort: Sort by - 'stars', 'forks', 'updated', 'help-wanted-issues'
    
    Returns:
        List of matching GitHub repositories
    """
    from .tools.github import search_github as _search_gh
    return await _search_gh(query, min(num_results, 10), language, sort)


@mcp.tool()
async def get_repo_info(repo: str) -> str:
    """
    Get detailed information about a GitHub repository.
    
    Args:
        repo: Repository in format 'owner/repo' (e.g., 'microsoft/vscode')
    
    Returns:
        Detailed repository information
    """
    from .tools.github import get_repo_info as _get_repo
    return await _get_repo(repo)


@mcp.tool()
async def get_github_user(username: str) -> str:
    """
    Get information about a GitHub user or organization.
    
    Args:
        username: GitHub username
    
    Returns:
        User/organization profile information
    """
    from .tools.github import get_github_user as _get_user
    return await _get_user(username)


# =============================================================================
# FINANCE TOOLS
# =============================================================================
@mcp.tool()
async def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price and market data.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
    
    Returns:
        Current stock price, change, and market data
    """
    from .tools.stocks import get_stock_price as _get_stock
    return await _get_stock(symbol)


@mcp.tool()
async def get_crypto_price(coin: str, currency: str = "usd") -> str:
    """
    Get the current cryptocurrency price.
    
    Args:
        coin: Cryptocurrency name or ID (e.g., 'bitcoin', 'ethereum', 'dogecoin')
        currency: Fiat currency for price (default: 'usd')
    
    Returns:
        Current crypto price and market data
    """
    from .tools.stocks import get_crypto_price as _get_crypto
    return await _get_crypto(coin, currency)


@mcp.tool()
async def get_currency_rate(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> str:
    """
    Get currency exchange rate and convert an amount.
    
    Args:
        from_currency: Source currency code (e.g., "USD", "EUR", "INR")
        to_currency: Target currency code (e.g., "JPY", "GBP", "INR")
        amount: Amount to convert (default: 1.0)
    
    Returns:
        Exchange rate and converted amount
    """
    from .tools.currency import get_currency_rate as _currency
    return await _currency(from_currency.upper(), to_currency.upper(), amount)


# =============================================================================
# WEATHER & TIME TOOLS
# =============================================================================
@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get current weather and forecast for a location.
    
    Args:
        location: City name, address, or coordinates (e.g., "Tokyo", "New York, USA")
    
    Returns:
        Current weather conditions and 3-day forecast
    """
    from .tools.weather import get_weather as _weather
    return await _weather(location)


@mcp.tool()
async def get_current_time(location: str = "UTC") -> str:
    """
    Get the current time for a timezone or city.
    
    Args:
        location: Timezone name (e.g., "America/New_York"), city name (e.g., "Tokyo"), 
                  or UTC offset (e.g., "UTC+5:30")
    
    Returns:
        Current date and time for the specified location
    """
    from .tools.time import get_current_time as _time
    return await _time(location)


# =============================================================================
# KNOWLEDGE TOOLS
# =============================================================================
@mcp.tool()
async def get_definition(term: str) -> str:
    """
    Get the definition or Wikipedia summary for a term.
    
    Args:
        term: The word or topic to define/lookup
    
    Returns:
        Definition, summary, and related information
    """
    from .tools.dictionary import get_definition as _define
    return await _define(term)


@mcp.tool()
async def translate_text(
    text: str,
    to_language: str = "english",
    from_language: str = "auto"
) -> str:
    """
    Translate text between languages.
    
    Args:
        text: The text to translate
        to_language: Target language (name or code, e.g., 'spanish', 'es')
        from_language: Source language (default: 'auto' for auto-detect)
    
    Returns:
        Translated text with language information
    """
    from .tools.translator import translate_text as _translate
    return await _translate(text, to_language, from_language)


@mcp.tool()
async def detect_language(text: str) -> str:
    """
    Detect the language of a text.
    
    Args:
        text: The text to analyze
    
    Returns:
        Detected language information
    """
    from .tools.translator import detect_language as _detect
    return await _detect(text)


@mcp.tool()
async def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression to evaluate
                   Supports: +, -, *, /, //, %, **
                   Functions: sqrt, sin, cos, tan, log, exp, floor, ceil, abs, factorial
                   Constants: pi, e
    
    Returns:
        The result of the calculation
    
    Examples:
        calculate("2 + 2") -> 4
        calculate("sqrt(16)") -> 4.0
        calculate("15% of 200") -> 30.0
    """
    from .tools.math_tools import calculate as _calc
    return await _calc(expression)


# =============================================================================
# URL TOOLS
# =============================================================================
@mcp.tool()
async def shorten_url(url: str) -> str:
    """
    Create a shortened URL.
    
    Args:
        url: The long URL to shorten
    
    Returns:
        Shortened URL
    """
    from .tools.urls import shorten_url as _shorten
    return await _shorten(url)


@mcp.tool()
async def expand_url(short_url: str) -> str:
    """
    Expand a shortened URL to reveal the destination.
    
    Args:
        short_url: The shortened URL to expand
    
    Returns:
        The original long URL
    """
    from .tools.urls import expand_url as _expand
    return await _expand(short_url)


# =============================================================================
# IP & NETWORK TOOLS
# =============================================================================
@mcp.tool()
async def get_my_ip() -> str:
    """
    Get your public IP address.
    
    Returns:
        Your public IP address with location info
    """
    from .tools.ip_tools import get_my_ip as _my_ip
    return await _my_ip()


@mcp.tool()
async def geolocate_ip(ip: str) -> str:
    """
    Get geolocation information for an IP address.
    
    Args:
        ip: The IP address to look up (IPv4 or IPv6)
    
    Returns:
        Location and network information for the IP
    """
    from .tools.ip_tools import geolocate_ip as _geolocate
    return await _geolocate(ip)


@mcp.tool()
async def whois_lookup(domain: str) -> str:
    """
    Look up WHOIS registration information for a domain.
    
    Args:
        domain: Domain name (e.g., 'example.com', 'github.com')
    
    Returns:
        Domain registration information
    """
    from .tools.whois import whois_lookup as _whois
    return await _whois(domain)


# =============================================================================
# QR CODE TOOLS
# =============================================================================
@mcp.tool()
async def generate_qr(content: str, size: int = 200) -> str:
    """
    Generate a QR code for text or URL.
    
    Args:
        content: The text, URL, or data to encode
        size: Size in pixels (default: 200, range: 50-500)
    
    Returns:
        URL to the generated QR code image
    """
    from .tools.qr_code import generate_qr as _gen_qr
    return await _gen_qr(content, size)


@mcp.tool()
async def generate_wifi_qr(
    ssid: str,
    password: str,
    security: str = "WPA",
    hidden: bool = False
) -> str:
    """
    Generate a QR code for WiFi network credentials.
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        security: Security type - 'WPA', 'WEP', or 'nopass' (default: 'WPA')
        hidden: Whether the network is hidden (default: False)
    
    Returns:
        URL to the QR code that connects to WiFi when scanned
    """
    from .tools.qr_code import generate_wifi_qr as _wifi_qr
    return await _wifi_qr(ssid, password, security, hidden)


# =============================================================================
# SHARING TOOLS
# =============================================================================
@mcp.tool()
async def create_paste(
    content: str,
    title: str = "",
    syntax: str = "text",
    expiry_days: int = 7
) -> str:
    """
    Create a paste/code snippet to share.
    
    Args:
        content: The text or code to paste
        title: Optional title for the paste
        syntax: Syntax highlighting (e.g., 'python', 'javascript', 'text')
        expiry_days: Days until paste expires (default: 7, max: 365)
    
    Returns:
        URL to the created paste
    """
    from .tools.pastebin import create_paste as _paste
    return await _paste(content, title, syntax, expiry_days)


@mcp.tool()
async def send_email(
    to_email: str,
    subject: str,
    body: str,
    smtp_server: str = "",
    smtp_port: int = 587,
    sender_email: str = "",
    sender_password: str = ""
) -> str:
    """
    Send an email via SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body text
        smtp_server: SMTP server (default: from env MCP_SMTP_SERVER)
        smtp_port: SMTP port (default: 587)
        sender_email: Sender email (default: from env MCP_SMTP_EMAIL)
        sender_password: Sender password (default: from env MCP_SMTP_PASSWORD)
    
    Returns:
        Success or error message
    
    Note: Requires SMTP configuration via parameters or environment variables.
    """
    from .tools.email_sender import send_email as _send_email
    return await _send_email(to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password)


# =============================================================================
# Server Entry Point
# =============================================================================
def main():
    """Run the MCP server using STDIO transport."""
    logger.info("Starting MCP Internet Server with 33 tools...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
