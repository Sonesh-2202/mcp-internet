"""Utility modules for MCP Internet Server."""

from .http_client import fetch_url, fetch_json, fetch_multiple
from .cache import cache_get, cache_set, cache_clear

__all__ = [
    "fetch_url",
    "fetch_json",
    "fetch_multiple",
    "cache_get",
    "cache_set",
    "cache_clear",
]
