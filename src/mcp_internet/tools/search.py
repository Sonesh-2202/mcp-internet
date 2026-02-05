"""
Web Search Tool - Search the internet using DuckDuckGo.

Uses both HTML scraping (for best results) and ddgs library (as fallback).
Includes deep search and site-specific search features.
"""

import logging
import re
from urllib.parse import quote_plus, unquote

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)


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


async def search_duckduckgo_html(query: str, num_results: int = 10) -> list[dict]:
    """
    Search using DuckDuckGo HTML interface - THE ORIGINAL METHOD THAT WORKS BEST.
    
    This method scrapes the HTML results page for more comprehensive results
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
            url = extract_url_from_ddg_redirect(raw_url)
            
            # Extract snippet
            snippet_elem = result_div.find("a", class_="result__snippet")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
            
            if title and url:
                results.append({
                    "title": title,
                    "href": url,
                    "body": snippet
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error parsing DuckDuckGo HTML: {e}")
        return []


async def search_with_ddgs(query: str, num_results: int = 10) -> list[dict]:
    """Fallback search using ddgs library."""
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=num_results))
        return results
    except Exception as e:
        logger.error(f"Error with ddgs search: {e}")
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
    
    # Try HTML scraping first (best results) - THIS IS THE ORIGINAL METHOD
    results = await search_duckduckgo_html(query, num_results)
    
    # Fallback to ddgs library if HTML scraping fails
    if not results:
        logger.info("HTML scraping returned no results, trying ddgs library...")
        results = await search_with_ddgs(query, num_results)
    
    if not results:
        # Try exact match search
        results = await search_duckduckgo_html(f'"{query}"', num_results)
    
    if not results:
        return f"No results found for: {query}"
    
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
    # Use HTML scraping for best results
    results = await search_duckduckgo_html(query, 5)
    
    if not results:
        results = await search_with_ddgs(query, 5)
    
    if not results:
        return f"No results found for: {query}"
    
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
