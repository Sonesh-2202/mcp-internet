"""
Web Search Tool - Search the internet using DuckDuckGo.

Uses HTML scraping as primary (most reliable) with ddgs library as fallback.

v3.0 Upgrades:
- Caching for repeated queries
- Improved deep_search that auto-extracts content
- Better formatting with structured data extraction
"""

import asyncio
import logging
import re
from urllib.parse import quote_plus, unquote

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url
from ..utils.cache import cache_get, cache_set

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


async def search_duckduckgo_html(query: str, num_results: int = 10, retries: int = 3) -> list[dict]:
    """
    Search using DuckDuckGo HTML interface - PRIMARY METHOD.
    
    This method scrapes the HTML results page and is the most reliable
    approach. Uses fetch_url which has built-in retry logic.
    """
    encoded_query = quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    for attempt in range(retries):
        html = await fetch_url(url, retries=2)
        if not html:
            logger.warning(f"HTML fetch failed (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                await asyncio.sleep(0.3)
            continue
        
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
            
            if results:
                return results
            
            logger.warning(f"No results parsed from HTML (attempt {attempt + 1}/{retries})")
            
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo HTML: {e}")
        
        if attempt < retries - 1:
            await asyncio.sleep(0.3)
    
    return []


async def search_with_ddgs(query: str, num_results: int = 10) -> list[dict]:
    """Fallback search using ddgs library."""
    try:
        from ddgs import DDGS
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def do_search():
            ddgs = DDGS()
            return list(ddgs.text(query, max_results=num_results))
        
        results = await loop.run_in_executor(None, do_search)
        return results if results else []
    except Exception as e:
        logger.error(f"DDGS fallback error: {e}")
        return []


async def search_web(query: str, num_results: int = 10, deep_search: bool = False) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: The search query (person name, topic, question, etc.)
        num_results: Number of results to return (default: 10, max: 20)
        deep_search: If True, automatically scrapes and extracts content from top results
        
    Returns:
        Formatted search results (with extracted page content if deep_search is True)
    """
    if not query.strip():
        return "Error: Please provide a search query."
    
    num_results = min(num_results, 20)
    
    # Check cache
    cache_params = {"num_results": num_results, "deep": deep_search}
    cached = await cache_get("search", query, **cache_params)
    if cached:
        logger.info(f"Cache HIT for search_web: {query[:50]}")
        return cached
    
    # Try HTML scraping first - most reliable with built-in retries
    results = await search_duckduckgo_html(query, num_results, retries=3)
    
    # Fallback to ddgs library
    if not results:
        logger.info("HTML scraping failed, trying ddgs library...")
        results = await search_with_ddgs(query, num_results)
    
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
    
    # Deep search: Fetch and extract content from top results
    if deep_search and results:
        formatted_output += "\n\n" + "=" * 50
        formatted_output += "\n📚 DEEP SEARCH - Detailed Content Analysis\n"
        formatted_output += "=" * 50
        
        # Scrape top results in parallel for speed
        urls_to_scrape = []
        for r in results[:3]:
            url = r.get("href", r.get("link", ""))
            if url and not any(skip in url.lower() for skip in [".pdf", ".zip", "youtube.com/watch"]):
                urls_to_scrape.append(url)
        
        # Extract structured data from each
        for url in urls_to_scrape:
            title = next(
                (r.get("title", "Unknown") for r in results 
                 if r.get("href", r.get("link", "")) == url),
                "Unknown"
            )
            
            try:
                from ..utils.extractors import extract_structured_data, format_extracted_data
                
                html = await fetch_url(url, timeout=15.0, retries=1)
                if html:
                    # Try structured extraction first
                    data = extract_structured_data(html, url)
                    formatted = format_extracted_data(data)
                    
                    if formatted.strip() and len(formatted) > 50:
                        formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{formatted[:3000]}"
                    else:
                        # Fallback to basic content
                        content = await fetch_page_content(url, 4000)
                        if content and "Error" not in content[:20]:
                            formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{content[:3000]}"
                    
                    if len(formatted) > 3000:
                        formatted_output += "\n[Content truncated...]"
            except Exception as e:
                logger.error(f"Deep search extraction error for {url}: {e}")
                # Fallback to basic fetch
                content = await fetch_page_content(url, 4000)
                if content and "Error" not in content[:20]:
                    formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{content[:3000]}"
    
    # Cache the result
    await cache_set("search", query, formatted_output, **cache_params)
    
    return formatted_output


async def quick_lookup(query: str) -> str:
    """
    Quick lookup for a topic - combines search + structured content extraction.
    """
    # Check cache
    cached = await cache_get("search", f"quick:{query}")
    if cached:
        return cached
    
    results = await search_duckduckgo_html(query, 5, retries=3)
    
    if not results:
        results = await search_with_ddgs(query, 5)
    
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
    
    # Get structured content from first result
    first_url = results[0].get("href", results[0].get("link", ""))
    if first_url:
        try:
            from ..utils.extractors import extract_structured_data, format_extracted_data
            
            html = await fetch_url(first_url, timeout=15.0, retries=1)
            if html:
                data = extract_structured_data(html, first_url)
                extracted = format_extracted_data(data)
                
                if extracted.strip() and len(extracted) > 50:
                    formatted += f"\n\n{'=' * 50}\n📖 Detailed Info:\n{'=' * 50}\n{extracted}"
                else:
                    content = await fetch_page_content(first_url, 5000)
                    if content and "Error" not in content[:20]:
                        formatted += f"\n\n{'=' * 50}\n📖 Detailed Info:\n{'=' * 50}\n{content}"
        except Exception:
            content = await fetch_page_content(first_url, 5000)
            if content and "Error" not in content[:20]:
                formatted += f"\n\n{'=' * 50}\n📖 Detailed Info:\n{'=' * 50}\n{content}"
    
    # Cache
    await cache_set("search", f"quick:{query}", formatted)
    
    return formatted


async def search_site(query: str, site: str) -> str:
    """Search within a specific website."""
    site_query = f"site:{site} {query}"
    return await search_web(site_query, 10, False)


async def deep_search(query: str, num_sources: int = 5) -> str:
    """
    Deep web search — searches and scrapes multiple pages for comprehensive results.
    
    Runs a search, then fetches and extracts content from the top results
    to provide detailed, in-depth information from multiple sources.
    
    Args:
        query: The search query (person, topic, question, anything)
        num_sources: Number of pages to scrape for details (1-8, default: 5)
        
    Returns:
        Formatted search results with extracted page content from multiple sources
    """
    if not query.strip():
        return "Error: Please provide a search query."
    
    num_sources = max(1, min(num_sources, 8))
    
    # Check cache
    cache_params = {"num_sources": num_sources, "deep": True}
    cached = await cache_get("search", f"deep:{query}", **cache_params)
    if cached:
        logger.info(f"Cache HIT for deep_search: {query[:50]}")
        return cached
    
    # Search with more results to have a bigger pool to scrape from
    num_results = max(num_sources + 5, 15)
    results = await search_duckduckgo_html(query, num_results, retries=3)
    
    if not results:
        logger.info("HTML scraping failed, trying ddgs library...")
        results = await search_with_ddgs(query, num_results)
    
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
    
    header = f"🔍 Deep Search Results for: '{query}'\n"
    header += "=" * 50
    formatted_output = header + "".join(formatted_results)
    
    # Scrape top results for detailed content
    formatted_output += "\n\n" + "=" * 50
    formatted_output += "\n📚 DEEP SEARCH - Detailed Content Analysis\n"
    formatted_output += "=" * 50
    
    urls_to_scrape = []
    for r in results[:num_sources + 2]:  # Extra buffer in case some fail
        url = r.get("href", r.get("link", ""))
        if url and not any(skip in url.lower() for skip in [".pdf", ".zip", ".exe", "youtube.com/watch", "youtu.be/"]):
            urls_to_scrape.append(url)
        if len(urls_to_scrape) >= num_sources:
            break
    
    for url in urls_to_scrape:
        title = next(
            (r.get("title", "Unknown") for r in results
             if r.get("href", r.get("link", "")) == url),
            "Unknown"
        )
        
        try:
            from ..utils.extractors import extract_structured_data, format_extracted_data
            
            html = await fetch_url(url, timeout=15.0, retries=1)
            if html:
                data = extract_structured_data(html, url)
                formatted = format_extracted_data(data)
                
                if formatted.strip() and len(formatted) > 50:
                    formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{formatted[:4000]}"
                else:
                    content = await fetch_page_content(url, 4000)
                    if content and "Error" not in content[:20]:
                        formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{content[:4000]}"
                
                if len(formatted) > 4000:
                    formatted_output += "\n[Content truncated...]"
        except Exception as e:
            logger.error(f"Deep search extraction error for {url}: {e}")
            content = await fetch_page_content(url, 4000)
            if content and "Error" not in content[:20]:
                formatted_output += f"\n\n📄 From: {title}\n{'-' * 40}\n{content[:4000]}"
    
    # Cache result
    await cache_set("search", f"deep:{query}", formatted_output, **cache_params)
    
    return formatted_output
