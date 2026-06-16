"""
Webpage Reader Tool - Extract clean text content from any URL.

Uses BeautifulSoup to parse HTML and extract the main readable content,
stripping navigation, ads, scripts, and other non-content elements.

v3.0 Upgrades:
- JSON-LD structured data extraction
- HTML table → markdown table conversion
- Domain-aware extraction using extractor registry
- OpenGraph meta tag extraction
- Result caching
"""

import logging
import re

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url
from ..utils.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# Elements to remove (navigation, ads, scripts, etc.)
REMOVE_TAGS = [
    "script", "style", "nav", "header", "footer", "aside",
    "form", "button", "iframe", "noscript", "svg", "canvas",
    "advertisement", "ad", "sidebar", "menu", "popup",
]

# Classes/IDs that typically contain non-content
REMOVE_PATTERNS = [
    r"nav", r"menu", r"sidebar", r"footer", r"header", r"ad[-_]?",
    r"advertisement", r"social", r"share", r"comment", r"related",
    r"popup", r"modal", r"cookie", r"banner", r"promo",
]


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_main_content(soup: BeautifulSoup, url: str = "") -> str:
    """Extract the main readable content from parsed HTML."""
    
    is_linkedin = "linkedin.com" in url.lower()

    if is_linkedin:
        # LinkedIn public profiles have a <main> tag containing the entire profile
        main_content = soup.find("main")
        if main_content:
            for tag in ["script", "style", "nav", "svg", "button", "iframe", "noscript"]:
                for element in main_content.find_all(tag):
                    try:
                        element.decompose()
                    except:
                        pass
            return main_content.get_text(separator='\n', strip=True)

    # Remove unwanted elements
    for tag in REMOVE_TAGS:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove elements with common non-content classes/IDs
    pattern = re.compile('|'.join(REMOVE_PATTERNS), re.IGNORECASE)
    for element in soup.find_all(class_=pattern):
        element.decompose()
    for element in soup.find_all(id=pattern):
        element.decompose()
    
    # Try to find main content containers
    main_content = None
    for tag in ["main", "article", '[role="main"]']:
        main_content = soup.find(tag) if not tag.startswith('[') else soup.select_one(tag)
        if main_content:
            break
    
    # If no main container found, try content divs
    if not main_content:
        for class_name in ["content", "post", "entry", "article", "body"]:
            main_content = soup.find(class_=re.compile(class_name, re.IGNORECASE))
            if main_content:
                break
    
    # Fall back to body
    if not main_content:
        main_content = soup.find("body") or soup
    
    return main_content.get_text(separator='\n', strip=True)


async def read_webpage(url: str, max_length: int = 5000) -> str:
    """
    Read and extract text content from a webpage.
    
    Automatically extracts structured data (JSON-LD, tables, meta tags)
    when available, in addition to the main text content.
    
    Args:
        url: The URL to read
        max_length: Maximum characters to return
        
    Returns:
        Extracted text content with any structured data found
    """
    if not url.strip():
        return "❌ Error: Please provide a URL."
    
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Check cache
    cached = await cache_get("page", f"read:{url}", max_length=max_length)
    if cached:
        return cached
    
    html = await fetch_url(url)
    if not html:
        return f"❌ Error: Unable to fetch content from {url}. The page may be unavailable or blocking requests."
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Get title
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else "Unknown Page"
        
        # Get meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content", "") if meta_desc else ""
        
        # Try structured extraction first
        structured_section = ""
        try:
            from ..utils.extractors import extract_structured_data, format_extracted_data
            data = extract_structured_data(html, url)
            formatted = format_extracted_data(data)
            if formatted.strip() and len(formatted) > 50:
                structured_section = f"\n📊 **Structured Data:**\n{formatted}\n"
        except Exception as e:
            logger.debug(f"Structured extraction failed for {url}: {e}")
        
        # Extract HTML tables as markdown
        tables_section = ""
        try:
            from ..utils.extractors import extract_html_tables, tables_to_markdown
            tables = extract_html_tables(soup)
            if tables:
                md_tables = tables_to_markdown(tables)
                if md_tables.strip():
                    tables_section = f"\n📋 **Tables Found:**\n{md_tables}\n"
        except Exception:
            pass
        
        # Extract main content
        content = extract_main_content(soup, url)
        content = clean_text(content)
        
        # Calculate available space for content
        overhead = len(structured_section) + len(tables_section) + 200
        content_max = max(max_length - overhead, 1000)
        
        # Truncate if needed
        if len(content) > content_max:
            content = content[:content_max] + "...\n\n[Content truncated]"
        
        # Format output
        output = f"""📄 **{title_text}**
🔗 {url}
"""
        if description:
            output += f"📝 {description}\n"
        
        if structured_section:
            output += structured_section
        
        if tables_section:
            output += tables_section
        
        output += f"""
{'=' * 50}

{content}
"""
        # Cache the result
        await cache_set("page", f"read:{url}", output, max_length=max_length)
        
        return output
        
    except Exception as e:
        logger.error(f"Error parsing webpage: {e}")
        return f"❌ Error: Unable to parse content from {url}. The page format may not be supported."
