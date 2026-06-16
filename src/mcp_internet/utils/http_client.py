"""
Shared HTTP client utilities for making async requests.

Provides standardized HTTP fetching with proper error handling,
timeouts, and user-agent headers.

v3.0 Upgrades:
- User-agent rotation (pool of realistic browser UAs)
- Per-domain rate limiting (prevents IP bans)
- Persistent client connection for connection reuse
"""

import asyncio
import logging
import random
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Pool of realistic browser User-Agent strings for rotation
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

# GoogleBot headers to bypass certain authwalls (e.g., LinkedIn)
GOOGLEBOT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _get_default_headers() -> dict[str, str]:
    """Get default headers with a randomly selected User-Agent."""
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


# Standard headers (for backward compat)
DEFAULT_HEADERS = _get_default_headers()

# Timeout configuration - increased connect timeout for cold starts
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=15.0)

# Global client instance for connection reuse
_client: httpx.AsyncClient | None = None


# =============================================================================
# RATE LIMITER
# =============================================================================

class DomainRateLimiter:
    """
    Simple per-domain rate limiter.
    
    Ensures we don't make more than `max_per_second` requests per domain per second.
    Tracks last request time per domain and enforces minimum delay.
    """
    
    def __init__(self, max_per_second: float = 2.0):
        self._min_interval = 1.0 / max_per_second
        self._last_request: dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return "unknown"
    
    async def wait(self, url: str) -> None:
        """Wait if necessary to respect rate limits for this domain."""
        domain = self._extract_domain(url)
        
        async with self._lock:
            now = time.monotonic()
            last = self._last_request.get(domain, 0)
            elapsed = now - last
            
            if elapsed < self._min_interval:
                delay = self._min_interval - elapsed
                await asyncio.sleep(delay)
            
            self._last_request[domain] = time.monotonic()


# Global rate limiter instance
_rate_limiter = DomainRateLimiter(max_per_second=2.0)


# =============================================================================
# CLIENT MANAGEMENT
# =============================================================================

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
            headers=_get_default_headers(),
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


# =============================================================================
# FETCH FUNCTIONS
# =============================================================================

async def fetch_url(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
    retries: int = 2,
    rate_limit: bool = True,
) -> str | None:
    """
    Fetch content from a URL and return as text.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects
        retries: Number of retry attempts on failure
        rate_limit: Whether to apply rate limiting (default: True)
        
    Returns:
        Response text content, or None if request failed
    """
    if rate_limit:
        await _rate_limiter.wait(url)
    
    client = await get_client()
    
    # Use Googlebot for LinkedIn, rotated UA for others
    if "linkedin.com" in url.lower():
        base_headers = GOOGLEBOT_HEADERS.copy()
    else:
        base_headers = _get_default_headers()
    
    request_headers = {**base_headers, **(headers or {})}
    
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
                await asyncio.sleep(0.5 * (attempt + 1))
                continue  # Retry with backoff
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error(f"HTTP error {status} for URL: {url}")
            
            # Retry on 429 (rate limited) and 5xx (server errors)
            if status == 429 or status >= 500:
                if attempt < retries:
                    delay = 2.0 * (attempt + 1)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
            
            return None  # Don't retry other HTTP errors
        except httpx.RequestError as e:
            last_error = e
            logger.warning(f"Request error (attempt {attempt + 1}/{retries + 1}) for URL {url}: {e}")
            if attempt < retries:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue  # Retry with backoff
    
    if last_error:
        logger.error(f"All {retries + 1} attempts failed for URL: {url}")
    return None


async def fetch_json(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    params: dict[str, Any] | None = None,
    retries: int = 2,
    rate_limit: bool = True,
) -> dict[str, Any] | list | None:
    """
    Fetch JSON data from a URL.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (merged with defaults)
        timeout: Request timeout in seconds
        params: Optional query parameters
        retries: Number of retry attempts on failure
        rate_limit: Whether to apply rate limiting (default: True)
        
    Returns:
        Parsed JSON data, or None if request failed
    """
    if rate_limit:
        await _rate_limiter.wait(url)
    
    client = await get_client()
    
    if "linkedin.com" in url.lower():
        base_headers = GOOGLEBOT_HEADERS.copy()
    else:
        base_headers = _get_default_headers()
    
    request_headers = {
        **base_headers,
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
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error(f"HTTP error {status} for URL: {url}")
            
            if status == 429 or status >= 500:
                if attempt < retries:
                    delay = 2.0 * (attempt + 1)
                    await asyncio.sleep(delay)
                    continue
            
            return None
        except httpx.RequestError as e:
            last_error = e
            logger.warning(f"Request error (attempt {attempt + 1}/{retries + 1}) for URL {url}: {e}")
            if attempt < retries:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        except ValueError as e:
            logger.error(f"JSON decode error for URL {url}: {e}")
            return None
    
    if last_error:
        logger.error(f"All {retries + 1} attempts failed for URL: {url}")
    return None


async def fetch_multiple(
    urls: list[str],
    max_concurrent: int = 5,
    timeout: float = 20.0,
    retries: int = 1,
) -> dict[str, str | None]:
    """
    Fetch multiple URLs concurrently with controlled parallelism.
    
    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum concurrent requests
        timeout: Per-request timeout
        retries: Retry count per request
        
    Returns:
        Dict mapping URL → response text (None for failures)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results: dict[str, str | None] = {}
    
    async def _fetch_one(url: str):
        async with semaphore:
            result = await fetch_url(url, timeout=timeout, retries=retries)
            results[url] = result
    
    tasks = [_fetch_one(url) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
