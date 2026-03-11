"""Internet tools for MCP server."""

from .search import search_web
from .webpage import read_webpage
from .news import get_news
from .weather import get_weather
from .time import get_current_time

__all__ = [
    "search_web",
    "read_webpage",
    "get_news",
    "get_weather",
    "get_current_time",
]
