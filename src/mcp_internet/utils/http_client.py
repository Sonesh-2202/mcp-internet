"""
Shared HTTP client utilities for making async requests.

Provides standardized HTTP fetching with proper error handling,
timeouts, and user-agent headers.

Uses a persistent client connection to avoid cold-start issues.
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

# Timeout configuration - increased connect timeout for cold starts
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=15.0)

# Global client instance for connection reuse
_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """
    Get or create a shared async HTTP client.
    
    Using a shared client provides:
    - Connection pooling and reuse
    - Faster subsequent requests (no cold start)
    - Keep-alive connections
    """
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
            # HTTP/2 support for modern sites
            http2=True,
        )
    return _client


async def close_client() -> None:
    """Close the shared client (call on shutdown)."""
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
        _client = None


async def fetch_url(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
    retries: int = 2,
) -> str | None:
    """
    Fetch content from a URL and return as text.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects
        retries: Number of retry attempts on failure
        
    Returns:
        Response text content, or None if request failed
    """
    client = await get_client()
    request_headers = {**DEFAULT_HEADERS, **(headers or {})}
    
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = await client.get(
                url,
                headers=request_headers,
                timeout=httpx.Timeout(timeout, connect=15.0),
                follow_redirects=follow_redirects,
            )
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException as e:
            last_error = e
            logger.warning(f"Timeout fetching URL (attempt {attempt + 1}/{retries + 1}): {url}")
            if attempt < retries:
                continue  # Retry
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None  # Don't retry HTTP errors
        except httpx.RequestError as e:
            last_error = e
            logger.warning(f"Request error (attempt {attempt + 1}/{retries + 1}) for URL {url}: {e}")
            if attempt < retries:
                continue  # Retry
    
    if last_error:
        logger.error(f"All {retries + 1} attempts failed for URL: {url}")
    return None


async def fetch_json(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    params: dict[str, Any] | None = None,
    retries: int = 2,
) -> dict[str, Any] | list | None:
    """
    Fetch JSON data from a URL.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        params: Optional query parameters
        retries: Number of retry attempts on failure
        
    Returns:
        Parsed JSON data, or None if request failed
    """
    client = await get_client()
    request_headers = {
        **DEFAULT_HEADERS,
        "Accept": "application/json",
        **(headers or {}),
    }
    
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = await client.get(
                url,
                headers=request_headers,
                params=params,
                timeout=httpx.Timeout(timeout, connect=15.0),
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            last_error = e
            logger.warning(f"Timeout fetching JSON (attempt {attempt + 1}/{retries + 1}): {url}")
            if attempt < retries:
                continue
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
        except httpx.RequestError as e:
            last_error = e
            logger.warning(f"Request error (attempt {attempt + 1}/{retries + 1}) for URL {url}: {e}")
            if attempt < retries:
                continue
        except ValueError as e:
            logger.error(f"JSON decode error for URL {url}: {e}")
            return None
    
    if last_error:
        logger.error(f"All {retries + 1} attempts failed for URL: {url}")
    return None
