# 🌐 MCP Internet Server - Complete Technical Documentation

> **Comprehensive guide covering every aspect of the project: architecture, code, APIs, execution, and troubleshooting.**

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [How It Works](#-how-it-works)
3. [Complete Architecture](#-complete-architecture)
4. [Installation & Setup](#-installation--setup)
5. [Execution Methods](#-execution-methods)
6. [Tool Deep Dives](#-tool-deep-dives)
7. [Code Walkthrough](#-code-walkthrough)
8. [API Reference](#-api-reference)
9. [Troubleshooting Guide](#-troubleshooting-guide)
10. [Best Practices](#-best-practices)

---

## 🎯 Project Overview

### What is MCP Internet Server?

MCP Internet Server is a **Model Context Protocol (MCP)** server that provides internet access capabilities to local Large Language Models (LLMs) running in LM Studio. It allows your AI to:

- 🔍 Search the web (with deep search option)
- 🎯 Quick lookup for people, topics, concepts
- 🌐 Search within specific sites (LinkedIn, Instagram, etc.)
- 📰 Fetch latest news
- 🌤️ Get weather forecasts
- 📄 Read webpage content
- 📖 Look up definitions
- 💱 Convert currencies
- 🕐 Get world time

### What is MCP?

**MCP (Model Context Protocol)** is an open protocol that enables LLMs to interact with external tools and data sources. Think of it as a standardized way for AI models to "call functions" in the real world.

### What is LM Studio?

**LM Studio** is an application that lets you run LLMs locally on your computer. It supports MCP servers, meaning your local AI can use the tools provided by this server.

### Key Benefits

| Feature | Benefit |
|---------|---------|
| **No API Keys** | All tools use free, open APIs |
| **Privacy** | Runs locally, your data stays on your machine |
| **9 Tools** | Comprehensive internet access without rate limits |
| **Easy Setup** | Just configure and restart LM Studio |

---

## 🔄 How It Works

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LM STUDIO                                │
│                                                                  │
│  ┌───────────────┐    ┌─────────────────────────────────────┐  │
│  │   Your LLM    │───▶│  "What's the weather in Tokyo?"    │  │
│  │  (Qwen, etc)  │    └─────────────────────────────────────┘  │
│  └───────┬───────┘                                               │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MCP INTERNET SERVER                         │    │
│  │                                                          │    │
│  │   server.py  ◀──────────────────────────────────────▶   │    │
│  │       │                                                  │    │
│  │       ├── get_weather("Tokyo")                          │    │
│  │       │       │                                          │    │
│  │       │       ▼                                          │    │
│  │       │   ┌─────────────────────────────────┐           │    │
│  │       │   │  1. Geocode "Tokyo" to lat/lon  │           │    │
│  │       │   │  2. Fetch from Open-Meteo API    │           │    │
│  │       │   │  3. Format and return response   │           │    │
│  │       │   └─────────────────────────────────┘           │    │
│  │       │                                                  │    │
│  │       └──▶ Returns formatted weather data               │    │
│  └─────────────────────────────────────────────────────────┘    │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ "The weather in Tokyo is 15°C, partly cloudy with..."      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

1. **User asks a question** in LM Studio chat
2. **LM Studio starts the MCP server** (if not already running)
3. **LLM decides to use a tool** based on the question
4. **MCP server receives the tool call** via STDIO
5. **Tool function executes** (fetches data from internet)
6. **Result returned to LLM** which formats the response
7. **User sees the answer** in the chat

### Communication Protocol

The MCP server uses **STDIO (Standard Input/Output)** transport:
- LM Studio writes JSON requests to the server's stdin
- Server writes JSON responses to stdout
- All logs go to stderr (so they don't interfere with MCP communication)

---

## 🏗️ Complete Architecture

### Directory Structure

```
MCP-Internet/
│
├── 📄 pyproject.toml          # Project metadata & dependencies
├── 📄 README.md               # User-facing documentation
├── 📄 LICENSE                 # MIT License
├── 📄 .gitignore              # Git ignore rules
│
└── 📁 src/
    └── 📁 mcp_internet/
        │
        ├── 📄 __init__.py     # Package marker
        ├── 📄 server.py       # Main MCP server (entry point)
        │
        ├── 📁 tools/          # Individual tool implementations
        │   ├── 📄 search.py   # Web search (DuckDuckGo)
        │   ├── 📄 webpage.py  # Content extraction
        │   ├── 📄 news.py     # News headlines (Google News)
        │   ├── 📄 weather.py  # Weather data (Open-Meteo)
        │   ├── 📄 dictionary.py # Definitions (Wikipedia + Dictionary)
        │   ├── 📄 currency.py # Exchange rates
        │   └── 📄 time.py     # World time
        │
        └── 📁 utils/
            └── 📄 http_client.py  # Shared HTTP utilities
```

### Dependency Graph

```
server.py (Main Entry Point)
    │
    ├── mcp.server.fastmcp.FastMCP  # MCP framework
    │
    └── tools/
        ├── search.py ──────▶ utils/http_client.py
        │                     (fetch_url)
        │
        ├── webpage.py ─────▶ utils/http_client.py
        │                     (fetch_url)
        │
        ├── news.py ────────▶ utils/http_client.py
        │                     (fetch_url)
        │
        ├── weather.py ─────▶ utils/http_client.py
        │                     (fetch_json)
        │
        ├── dictionary.py ──▶ utils/http_client.py
        │                     (fetch_json)
        │
        ├── currency.py ────▶ utils/http_client.py
        │                     (fetch_json)
        │
        └── time.py ────────▶ utils/http_client.py
                              (fetch_json)
```

### Dependencies (from pyproject.toml)

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp[cli]` | ≥1.2.0 | MCP framework with CLI tools |
| `httpx` | ≥0.27.0 | Async HTTP client |
| `beautifulsoup4` | ≥4.12.0 | HTML parsing |
| `lxml` | ≥5.0.0 | Fast XML/HTML parser |

---

## ⚙️ Installation & Setup

### Prerequisites

1. **Python 3.10+** - Required for modern type hints
2. **uv package manager** - Recommended (or pip)
3. **LM Studio 0.3.17+** - With MCP support

### Step 1: Clone/Download the Project

```bash
git clone https://github.com/yourusername/mcp-internet.git
cd mcp-internet
```

### Step 2: Install Dependencies

**Using uv (Recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
```

### Step 3: Configure LM Studio

1. Open **LM Studio**
2. Go to the **Program** tab (terminal icon in sidebar)
3. Click **Install > Edit mcp.json**
4. Add this configuration:

```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "python",
      "args": ["-m", "mcp_internet.server"],
      "cwd": "e:\\Coding projects\\MCP-Internet\\src"
    }
  }
}
```

> **Important:** The `cwd` must point to the `src` folder so Python can find the `mcp_internet` module.

### Step 4: Restart LM Studio

Close and reopen LM Studio. The tools should now appear in the chat.

---

## 🚀 Execution Methods

### Method 1: LM Studio (Primary Use)

This is how the server is **meant to be used**:

1. Configure `mcp.json` (see above)
2. Restart LM Studio
3. Start a chat with any model
4. Ask questions like:
   - *"What's the weather in Mumbai?"*
   - *"Search for recent AI news"*
   - *"What time is it in Tokyo?"*

**What happens behind the scenes:**
- LM Studio automatically starts `python -m mcp_internet.server`
- The server runs continuously, waiting for tool calls
- When you ask a question, the LLM decides which tool to call
- The server executes the tool and returns the result

### Method 2: MCP Inspector (Development/Testing)

For testing tools without LM Studio:

```bash
cd "e:\Coding projects\MCP-Internet"
uv run mcp dev src/mcp_internet/server.py
```

This opens a browser interface where you can:
- See all available tools
- Test each tool with custom parameters
- View the raw JSON responses

### Method 3: Direct Python Testing

Test individual functions directly:

**Test Weather:**
```bash
uv run python -c "import asyncio; from src.mcp_internet.tools.weather import get_weather; print(asyncio.run(get_weather('Mumbai')))"
```

**Test Search:**
```bash
uv run python -c "import asyncio; from src.mcp_internet.tools.search import search_web; print(asyncio.run(search_web('Python programming')))"
```

**Test News:**
```bash
uv run python -c "import asyncio; from src.mcp_internet.tools.news import get_news; print(asyncio.run(get_news('technology')))"
```

**Test Currency:**
```bash
uv run python -c "import asyncio; from src.mcp_internet.tools.currency import get_currency_rate; print(asyncio.run(get_currency_rate('USD', 'INR', 100)))"
```

**Test Time:**
```bash
uv run python -c "import asyncio; from src.mcp_internet.tools.time import get_current_time; print(asyncio.run(get_current_time('Mumbai')))"
```

---

## 🛠️ Tool Deep Dives

### 1. 🔍 search_web

**Purpose:** Search the internet using DuckDuckGo

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `num_results` | int | 10 | Max results (1-20) |
| `deep_search` | bool | False | If True, fetches content from top results |

**How it works:**
1. Uses the `ddgs` library for reliable DuckDuckGo search
2. Returns results with titles, URLs, and snippets
3. If `deep_search=True`, fetches content from top 2-3 URLs
4. Returns formatted results with detailed page content

**API Used:** DuckDuckGo via `ddgs` library (no API key needed)

---

### 1.5 🎯 quick_lookup (NEW)

**Purpose:** Quick info lookup for people, places, or topics

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | What to look up |

**How it works:**
1. Performs a web search
2. Automatically fetches content from the most relevant result
3. Returns search results + detailed content from top page

**Best for:** Finding info about people, concepts, or specific topics

---

### 1.6 🌐 search_site (NEW)

**Purpose:** Search within a specific website

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `site` | string | required | Website domain (e.g., "linkedin.com") |

**How it works:**
1. Uses `site:domain` DuckDuckGo operator
2. Returns only results from that specific website

**Best for:** Finding social profiles (LinkedIn, Instagram, GitHub, etc.)

---

### 2. 📄 read_webpage

**Purpose:** Extract clean text from any URL

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to read |
| `max_length` | int | 5000 | Max characters to return |

**How it works:**
1. Adds `https://` if missing
2. Fetches HTML content
3. Removes non-content elements (nav, ads, scripts, etc.)
4. Finds main content container (`<main>`, `<article>`, etc.)
5. Extracts clean text
6. Truncates if exceeds max_length

**Removed Elements:**
- `script`, `style`, `nav`, `header`, `footer`, `aside`
- Elements with classes/IDs matching: nav, menu, sidebar, ad, social, etc.

---

### 3. 📰 get_news

**Purpose:** Fetch latest news headlines

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | string | "world" | Topic or search query |
| `count` | int | 5 | Number of headlines (1-10) |

**Supported Topics:**
- `world`, `business`, `technology`, `science`
- `health`, `sports`, `entertainment`
- Any custom search query

**How it works:**
1. Maps topic to Google News RSS URL
2. For custom queries, uses search RSS endpoint
3. Parses RSS XML with BeautifulSoup
4. Extracts title, source, date, and link

**API Used:** Google News RSS (free, no key)

---

### 4. 🌤️ get_weather

**Purpose:** Get current weather and 3-day forecast

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | string | required | City name or address |

**How it works:**
1. **Geocoding:** Converts location name to coordinates using Open-Meteo Geocoding API
2. **Weather Fetch:** Gets current conditions + forecast from Open-Meteo API
3. **Processing:** Converts weather codes to human-readable descriptions with emojis
4. **Formatting:** Returns current temp, feels like, humidity, wind, and 3-day forecast

**Weather Code Examples:**
- 0 → ☀️ Clear sky
- 3 → ☁️ Overcast
- 61 → 🌧️ Slight rain
- 95 → ⛈️ Thunderstorm

**API Used:** Open-Meteo (free, no key, European quality data)

---

### 5. 📖 get_definition

**Purpose:** Get definitions and Wikipedia summaries

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `term` | string | required | Word or topic to define |

**How it works:**
1. **First:** Tries Wikipedia REST API for summaries (good for topics, concepts)
2. **Fallback:** For single words, tries Free Dictionary API
3. Returns formatted definition with phonetics, parts of speech, examples, synonyms

**APIs Used:**
- Wikipedia REST API: `https://en.wikipedia.org/api/rest_v1/page/summary/`
- Free Dictionary API: `https://api.dictionaryapi.dev/api/v2/entries/en/`

---

### 6. 💱 get_currency_rate

**Purpose:** Convert currencies with live rates

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from_currency` | string | required | Source currency code (e.g., "USD") |
| `to_currency` | string | required | Target currency code (e.g., "INR") |
| `amount` | float | 1.0 | Amount to convert |

**How it works:**
1. **Primary:** Tries Frankfurter API (European Central Bank data)
2. **Fallback:** Tries ExchangeRate-API
3. Calculates conversion and returns formatted result

**APIs Used:**
- Frankfurter: `https://api.frankfurter.app/latest`
- ExchangeRate: `https://open.er-api.com/v6/latest`

**Supported Currencies:** USD, EUR, GBP, JPY, INR, CNY, AUD, CAD, CHF, and 50+ more

---

### 7. 🕐 get_current_time

**Purpose:** Get current time for any timezone or city

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | string | "UTC" | City name or timezone |

**How it works:**
1. **City Lookup:** Maps common city names to timezones (e.g., "Mumbai" → "Asia/Kolkata")
2. **Timezone Check:** Validates against Python's `available_timezones()`
3. **API Call:** Fetches accurate time from WorldTimeAPI
4. **Fallback:** Uses Python's `datetime` with `ZoneInfo` if API fails

**Supported Cities:** New York, LA, London, Paris, Tokyo, Mumbai, Delhi, Sydney, Dubai, Singapore, and many more

**API Used:** WorldTimeAPI: `https://worldtimeapi.org/api/timezone/`

---

## 💻 Code Walkthrough

### server.py - The Main Entry Point

```python
# Initialize FastMCP server with name "mcp-internet"
mcp = FastMCP("mcp-internet")

# Each tool is decorated with @mcp.tool()
@mcp.tool()
async def search_web(query: str, num_results: int = 5) -> str:
    """Docstring becomes the tool description for LLM"""
    from .tools.search import search_web as _search
    return await _search(query, min(num_results, 10))

# Entry point uses STDIO transport
def main():
    logger.info("Starting MCP Internet Server...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

**Key Points:**
- Tools are lazy-loaded (imported only when called) for faster startup
- All tools are async for non-blocking I/O
- Logging goes to stderr to not interfere with STDIO communication

### http_client.py - Shared HTTP Utilities

```python
# Browser-like headers to avoid being blocked
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Accept": "text/html,application/xhtml+xml,...",
    "Accept-Language": "en-US,en;q=0.5",
}

# Two main functions:
async def fetch_url(url: str, ...) -> str | None:
    """Fetch HTML content as text"""

async def fetch_json(url: str, ...) -> dict | list | None:
    """Fetch and parse JSON response"""
```

**Error Handling:**
- Timeout errors: Returns `None` with log
- HTTP errors: Returns `None` with status code logged
- Request errors: Returns `None` with error logged

---

## 📚 API Reference

### External APIs Used

| API | Endpoint | Purpose | Rate Limit | Auth |
|-----|----------|---------|------------|------|
| DuckDuckGo HTML | `html.duckduckgo.com/html/` | Web search | None | None |
| Open-Meteo Geocoding | `geocoding-api.open-meteo.com` | Location to coords | None | None |
| Open-Meteo Weather | `api.open-meteo.com` | Weather data | None | None |
| Google News RSS | `news.google.com/rss` | News headlines | None | None |
| Wikipedia REST | `en.wikipedia.org/api/rest_v1` | Summaries | None | None |
| Free Dictionary | `api.dictionaryapi.dev` | Word definitions | None | None |
| Frankfurter | `api.frankfurter.app` | Currency (ECB) | None | None |
| ExchangeRate-API | `open.er-api.com` | Currency (backup) | None | None |
| WorldTimeAPI | `worldtimeapi.org/api` | Current time | None | None |

---

## 🔧 Troubleshooting Guide

### Issue: Server Not Appearing in LM Studio

**Solutions:**
1. Verify `mcp.json` path is correct:
   ```json
   "cwd": "e:\\Coding projects\\MCP-Internet\\src"
   ```
2. Restart LM Studio completely (close and reopen)
3. Check Python is in PATH: Run `python --version` in terminal
4. Verify dependencies: Run `uv sync` or `pip install -e .`

### Issue: "Module not found" Error

**Solutions:**
```bash
# Reinstall dependencies
uv sync --reinstall

# Or with pip
pip install -e . --force-reinstall
```

### Issue: Tool Returns "Unable to fetch" Errors

**Causes & Solutions:**
1. **No internet connection** - Check your connection
2. **API temporarily down** - Wait and retry
3. **Firewall blocking** - Check firewall settings
4. **VPN issues** - Try disabling VPN

### Issue: Weather Location Not Found

**Solutions:**
- Use more specific location: "Mumbai, India" instead of just "Mumbai"
- Use English names for cities
- Try alternative spellings

### Issue: Currency Not Supported

**Solutions:**
- Use 3-letter ISO codes: USD, EUR, GBP, INR, JPY
- Some exotic currencies may not be supported by free APIs

### Viewing Server Logs

In LM Studio:
1. Go to the **Program** tab
2. Click on **mcp-internet** server
3. View logs in the output panel

Logs include:
- Server startup confirmation
- HTTP errors with status codes
- Parsing errors

---

## ✅ Best Practices

### For Users

1. **Be specific with locations** - "New York, USA" works better than "NY"
2. **Use English** - APIs work best with English queries
3. **Check tool availability** - Ask your LLM what tools it has access to
4. **Combine tools** - "Search for XYZ, then read the first result"

### For Developers

1. **Always use async** - All HTTP calls should be async
2. **Handle errors gracefully** - Return user-friendly error messages
3. **Log to stderr** - Never print to stdout (breaks STDIO transport)
4. **Validate inputs** - Check for empty strings, invalid formats
5. **Set timeouts** - Avoid hanging on slow APIs
6. **Use fallback APIs** - Primary API fails → try backup

---

## 📜 License

MIT License - Free for personal and commercial use.

---

## 🙏 Credits

- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **LM Studio**: [lmstudio.ai](https://lmstudio.ai/)
- **Open-Meteo**: Free weather API
- **DuckDuckGo**: Privacy-focused search
- **Wikipedia**: Knowledge base

---

*Last Updated: February 5, 2026*
