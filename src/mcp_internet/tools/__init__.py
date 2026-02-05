"""Internet tools for MCP server."""

from .search import search_web
from .webpage import read_webpage
from .news import get_news
from .weather import get_weather
from .dictionary import get_definition
from .currency import get_currency_rate
from .time import get_current_time

__all__ = [
    "search_web",
    "read_webpage",
    "get_news",
    "get_weather",
    "get_definition",
    "get_currency_rate",
    "get_current_time",
]
