"""
Webpage Reader Tool - Extract clean text content from any URL.

Uses BeautifulSoup to parse HTML and extract the main readable content,
stripping navigation, ads, scripts, and other non-content elements.
"""

import logging
import re

from bs4 import BeautifulSoup

from ..utils.http_client import fetch_url

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
    
    Args:
        url: The URL to read
        max_length: Maximum characters to return
        
    Returns:
        Extracted text content
    """
    if not url.strip():
        return "❌ Error: Please provide a URL."
    
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
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
        
        # Extract main content
        content = extract_main_content(soup, url)
        content = clean_text(content)
        
        # Truncate if needed
        if len(content) > max_length:
            content = content[:max_length] + "...\n\n[Content truncated]"
        
        # Format output
        output = f"""📄 **{title_text}**
🔗 {url}
"""
        if description:
            output += f"📝 {description}\n"
        
        output += f"""
{'=' * 50}

{content}
"""
        return output
        
    except Exception as e:
        logger.error(f"Error parsing webpage: {e}")
        return f"❌ Error: Unable to parse content from {url}. The page format may not be supported."
