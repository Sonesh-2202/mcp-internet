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
# Tool: Web Search
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


# =============================================================================
# Tool: Quick Lookup (Find info about people, topics, etc.)
# =============================================================================
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


# =============================================================================
# Tool: Search Site (Search within a specific website)
# =============================================================================
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
# Tool: Read Webpage
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


# =============================================================================
# Tool: Get News
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


# =============================================================================
# Tool: Get Weather
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


# =============================================================================
# Tool: Get Definition
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


# =============================================================================
# Tool: Get Currency Rate
# =============================================================================
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
# Tool: Get Current Time
# =============================================================================
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
# Server Entry Point
# =============================================================================
def main():
    """Run the MCP server using STDIO transport."""
    logger.info("Starting MCP Internet Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
