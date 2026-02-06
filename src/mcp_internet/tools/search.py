"""
Web Search Tool - Search the internet using DuckDuckGo.

Uses ddgs library as primary with HTML scraping as fallback.
Includes retry logic to handle cold-start issues.
"""

import asyncio
import logging
import re
from urllib.parse import quote_plus, unquote

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)

# Global ddgs instance to avoid re-initialization
_ddgs_instance = None


def get_ddgs():
    """Get or create a reusable DDGS instance."""
    global _ddgs_instance
    if _ddgs_instance is None:
        from ddgs import DDGS
        _ddgs_instance = DDGS()
    return _ddgs_instance


async def warmup_search():
    """Pre-initialize the search components."""
    try:
        # Initialize ddgs instance
        get_ddgs()
        logger.info("Search module warmed up")
    except Exception as e:
        logger.warning(f"Search warmup failed: {e}")


async def fetch_page_content(url: str, max_length: int = 3000) -> str:
    """Fetch and extract main content from a URL."""
    try:
        from .webpage import read_webpage
        content = await read_webpage(url, max_length)
        return content
    except Exception as e:
        logger.error(f"Error fetching page content: {e}")
        return ""


def extract_url_from_ddg_redirect(ddg_url: str) -> str:
    """Extract the actual URL from a DuckDuckGo redirect link."""
    if "uddg=" in ddg_url:
        match = re.search(r'uddg=([^&]+)', ddg_url)
        if match:
            return unquote(match.group(1))
    return ddg_url


async def search_with_ddgs(query: str, num_results: int = 10, retries: int = 3) -> list[dict]:
    """
    Search using ddgs library with retry logic.
    
    The ddgs library can be slow on first call, so we retry if needed.
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            ddgs = get_ddgs()
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: list(ddgs.text(query, max_results=num_results))
            )
            if results:
                return results
            # If empty results, try again
            logger.warning(f"DDGS returned empty results (attempt {attempt + 1}/{retries})")
        except Exception as e:
            last_error = e
            logger.warning(f"DDGS search error (attempt {attempt + 1}/{retries}): {e}")
            # Reset instance on error
            global _ddgs_instance
            _ddgs_instance = None
            
        # Brief delay before retry
        if attempt < retries - 1:
            await asyncio.sleep(0.5)
    
    if last_error:
        logger.error(f"All DDGS attempts failed: {last_error}")
    return []


async def search_duckduckgo_html(query: str, num_results: int = 10) -> list[dict]:
    """
    Search using DuckDuckGo HTML interface as fallback.
    
    This method scrapes the HTML results page for comprehensive results
    including detailed snippets and proper URL extraction.
    """
    encoded_query = quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    html = await fetch_url(url)
    if not html:
        return []
    
    try:
        soup = BeautifulSoup(html, "lxml")
        results = []
        
        # Find all result divs
        for result_div in soup.find_all("div", class_="result"):
            if len(results) >= num_results:
                break
            
            # Extract title and link
            title_elem = result_div.find("a", class_="result__a")
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            raw_url = title_elem.get("href", "")
            result_url = extract_url_from_ddg_redirect(raw_url)
            
            # Extract snippet
            snippet_elem = result_div.find("a", class_="result__snippet")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
            
            if title and result_url:
                results.append({
                    "title": title,
                    "href": result_url,
                    "body": snippet
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error parsing DuckDuckGo HTML: {e}")
        return []


async def search_web(query: str, num_results: int = 10, deep_search: bool = False) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: The search query (person name, topic, question, etc.)
        num_results: Number of results to return (default: 10, max: 20)
        deep_search: If True, fetches content from top results for detailed info
        
    Returns:
        Formatted search results (with page content if deep_search is True)
    """
    if not query.strip():
        return "Error: Please provide a search query."
    
    num_results = min(num_results, 20)
    
    # Try DDGS library first (more reliable with retries)
    results = await search_with_ddgs(query, num_results, retries=3)
    
    # Fallback to HTML scraping if DDGS fails
    if not results:
        logger.info("DDGS failed, trying HTML scraping...")
        results = await search_duckduckgo_html(query, num_results)
    
    # Last resort: try exact match search
    if not results:
        logger.info("Trying exact match search...")
        results = await search_with_ddgs(f'"{query}"', num_results, retries=2)
    
    if not results:
        return f"No results found for: {query}. Please try again."
    
    # Format results
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        link = result.get("href", result.get("link", ""))
        snippet = result.get("body", result.get("snippet", "No description available"))
        
        formatted_results.append(
            f"\n{i}. {title}\n"
            f"   URL: {link}\n"
            f"   {snippet}\n"
        )
    
    header = f"🔍 Search Results for: '{query}'\n"
    header += "=" * 50
    formatted_output = header + "".join(formatted_results)
    
    # Deep search: Fetch content from top results
    if deep_search and results:
        formatted_output += "\n\n" + "=" * 50
        formatted_output += "\n📚 DEEP SEARCH - Detailed Content Analysis\n"
        formatted_output += "=" * 50
        
        for r in results[:3]:
            url = r.get("href", r.get("link", ""))
            title = r.get("title", "Unknown")
            if url:
                content = await fetch_page_content(url, 4000)
                if content and "Error" not in content[:20]:
                    formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{content[:3000]}"
                    if len(content) > 3000:
                        formatted_output += "\n[Content truncated...]"
    
    return formatted_output


async def quick_lookup(query: str) -> str:
    """
    Quick lookup for a topic - combines search + first result content.
    Best for finding info about people, places, or specific topics.
    
    Args:
        query: What to look up (person name, topic, etc.)
        
    Returns:
        Search results with content from the most relevant page
    """
    # Use DDGS with retries
    results = await search_with_ddgs(query, 5, retries=3)
    
    if not results:
        results = await search_duckduckgo_html(query, 5)
    
    if not results:
        return f"No results found for: {query}. Please try again."
    
    # Format basic results
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        link = result.get("href", result.get("link", ""))
        snippet = result.get("body", result.get("snippet", "No description available"))
        
        formatted_results.append(
            f"\n{i}. {title}\n"
            f"   URL: {link}\n"
            f"   {snippet}\n"
        )
    
    header = f"🔍 Search Results for: '{query}'\n"
    header += "=" * 50
    formatted = header + "".join(formatted_results)
    
    # Get content from the first result
    first_url = results[0].get("href", results[0].get("link", ""))
    if first_url:
        content = await fetch_page_content(first_url, 5000)
        if content and "Error" not in content[:20]:
            formatted += f"\n\n{'=' * 50}\n📖 Detailed Info:\n{'=' * 50}\n{content}"
    
    return formatted


async def search_site(query: str, site: str) -> str:
    """
    Search within a specific website.
    
    Args:
        query: Search query
        site: Website domain (e.g., 'linkedin.com', 'instagram.com', 'github.com')
        
    Returns:
        Search results from that specific site
    """
    site_query = f"site:{site} {query}"
    return await search_web(site_query, 10, False)
