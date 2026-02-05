"""
Shared HTTP client utilities for making async requests.

Provides standardized HTTP fetching with proper error handling,
timeouts, and user-agent headers.
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Standard headers to appear as a regular browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def fetch_url(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
) -> str | None:
    """
    Fetch content from a URL and return as text.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects
        
    Returns:
        Response text content, or None if request failed
    """
    request_headers = {**DEFAULT_HEADERS, **(headers or {})}
    
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(timeout, connect=10.0),
        follow_redirects=follow_redirects,
    ) as client:
        try:
            response = await client.get(url, headers=request_headers)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching URL: {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for URL {url}: {e}")
            return None


async def fetch_json(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | list | None:
    """
    Fetch JSON data from a URL.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        params: Optional query parameters
        
    Returns:
        Parsed JSON data, or None if request failed
    """
    request_headers = {
        **DEFAULT_HEADERS,
        "Accept": "application/json",
        **(headers or {}),
    }
    
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(timeout, connect=10.0),
        follow_redirects=True,
    ) as client:
        try:
            response = await client.get(url, headers=request_headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching JSON from: {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for URL {url}: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error for URL {url}: {e}")
            return None
