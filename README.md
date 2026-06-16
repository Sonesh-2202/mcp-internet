# 🌐 MCP Internet Server v3.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)

> **Give your local LLMs the power of the internet — with real data extraction, not just links!** 🚀

An open-source Model Context Protocol (MCP) server providing **25 internet tools** for local Large Language Models. The v3.0 upgrade adds **intelligent search with auto-extraction**, **multi-source aggregation**, **result caching**, and **structured output** — making your AI return actual data instead of raw links.

Seamlessly deployable across **Windows, macOS, and Linux**. **No API keys required!**

---

## 🆕 What's New in v3.0

| Feature | Before (v2.0) | After (v3.0) |
|---------|---------------|--------------|
| **Search Results** | Links + snippets only | Full data extraction from pages |
| **Tool Calls Needed** | 5-10+ per query | 1-2 per query |
| **Output Format** | Plain text | Markdown tables, bullet points |
| **Caching** | None | SQLite with TTL (30min-24h) |
| **Rate Limiting** | None | Per-domain throttling |
| **Multi-Source** | Manual per source | Auto-aggregation from top results |
| **Content Extraction** | Generic text only | Domain-aware (Wikipedia, IMDb, LinkedIn) |

### New Tools
- **`smart_search`** — 🌟 Searches + scrapes + extracts + formats in one call
- **`deep_search`** — Like smart_search but examines more sources
- **`clear_cache`** — Manage the result cache

---

## ✨ Key Features

- **🧠 Smart Search:** One tool call returns extracted data — movie lists, profiles, technical docs — not just links.
- **🔄 Auto-Extraction:** Automatically scrapes top results and extracts structured data (JSON-LD, tables, meta tags).
- **📊 Structured Output:** Results come as markdown tables, bullet points, and organized sections.
- **⚡ Cached Results:** Repeated queries are served from SQLite cache in milliseconds.
- **🛡️ Rate Limiting:** Per-domain request throttling prevents IP bans.
- **🔀 UA Rotation:** Pool of 7 browser user-agents for stealth.
- **🌐 Domain-Aware:** Special extractors for Wikipedia, IMDb, LinkedIn, and more.
- **🔒 Zero Config:** No API keys, no external subscriptions, no setup hassle.

---

## 🛠️ Available Tools (25 Total)

| Category | Tools |
|----------|-------|
| 🌟 **Smart Search** | `smart_search`, `deep_search` |
| 🔍 **Basic Search** | `search_web`, `quick_lookup`, `search_site` |
| 📄 **Reading** | `read_webpage`, `read_pdf` |
| 📰 **News/Social** | `get_news`, `search_reddit`, `search_twitter` |
| 🎬 **YouTube** | `search_youtube`, `get_video_info` |
| 💻 **GitHub** | `search_github`, `get_repo_info` |
| 🌤️ **Info / Utils** | `get_weather`, `get_current_time`, `translate_text`, `calculate` |
| 🔗 **URLs/IP** | `shorten_url`, `get_my_ip`, `geolocate_ip` |
| 📱 **Generation** | `generate_qr`, `generate_wifi_qr`, `send_email` |
| 🗄️ **Cache** | `clear_cache` |

---

## 🚀 Quick Start

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 2. Install dependencies
uv sync
```

### LM Studio Configuration

Add to your LM Studio `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": ["run", "mcp-internet"],
      "cwd": "/absolute/path/to/mcp-internet"
    }
  }
}
```

*(Replace `/absolute/path/to/mcp-internet` with your actual project path)*

### 📖 Detailed OS Guides
For complete, step-by-step instructions for **Windows, macOS, and Linux**, see the 👉 **[Multi-Platform Usage Guide](MULTI_PLATFORM_GUIDE.md)**.

---

## 💡 How It Works: smart_search vs search_web

### Before (v2.0): Multiple tool calls, manual scraping
```
User: "What are the upcoming Bollywood movies in 2026?"

Tool call 1: search_web("upcoming Bollywood movies 2026")
→ Returns 10 links with snippets

Tool call 2: read_webpage("https://www.imdb.com/...")
→ Returns raw text

Tool call 3: read_webpage("https://www.wikipedia.org/...")
→ Returns raw text

AI must manually piece together the answer from raw text.
```

### After (v3.0): One tool call, structured data
```
User: "What are the upcoming Bollywood movies in 2026?"

Tool call 1: smart_search("upcoming Bollywood movies 2026")
→ Returns:
  - Extracted movie list with titles, dates, genres
  - Markdown tables with ratings
  - Data from multiple sources combined
  - All in one response, ready to present
```

---

## 🏗️ Architecture

```
mcp-internet/
├── pyproject.toml              # Dependencies & Config
├── README.md                   # This file
├── MULTI_PLATFORM_GUIDE.md     # OS-specific setup guide
└── src/mcp_internet/
    ├── server.py               # Entry point — 25 MCP tools
    ├── tools/
    │   ├── smart_search.py     # 🌟 Intelligent search + extraction
    │   ├── search.py           # Basic DuckDuckGo search
    │   ├── webpage.py          # Page reader with structured extraction
    │   ├── news.py             # News headlines
    │   ├── youtube.py          # YouTube search & video info
    │   ├── github.py           # GitHub repos & users
    │   ├── reddit.py           # Reddit search
    │   ├── twitter.py          # Twitter/X via Nitter
    │   └── ...                 # weather, time, translate, math, etc.
    └── utils/
        ├── http_client.py      # Async HTTP with UA rotation & rate limiting
        ├── cache.py            # SQLite TTL cache
        └── extractors.py       # Domain-specific data extractors
```

### Data Flow

```
User Query → smart_search
    ├── 1. Check cache (return if fresh)
    ├── 2. Optimize query & classify (person/movie/news/tech/general)
    ├── 3. Search DuckDuckGo (HTML scraping + ddgs fallback)
    ├── 4. Prioritize results by domain authority
    ├── 5. Scrape top 3 pages in parallel (asyncio.gather)
    ├── 6. Apply domain-specific extractors
    │       ├── Wikipedia → infobox, summary, key facts
    │       ├── IMDb → titles, ratings, cast, genres
    │       ├── LinkedIn → name, role, skills, experience
    │       └── Generic → JSON-LD, OpenGraph, tables
    ├── 7. Aggregate & format as structured markdown
    ├── 8. Cache result
    └── 9. Return comprehensive response
```

---

## 🔧 Supported Data Sources

| Source | What's Extracted | Extractor Type |
|--------|-----------------|----------------|
| **Wikipedia** | Infobox, summary, key facts | Domain-specific |
| **IMDb** | Movie/show details, ratings, cast, genres | Domain-specific (JSON-LD) |
| **LinkedIn** | Name, role, skills, experience, education | Domain-specific (Googlebot UA) |
| **GitHub** | Repos, stars, forks, languages, topics | API-based |
| **Reddit** | Posts, scores, comments, subreddit info | JSON API |
| **YouTube** | Video titles, channels, views, duration | HTML parsing |
| **Any website** | JSON-LD, OpenGraph, HTML tables, main text | Generic fallback |

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Cache hit** | < 50ms |
| **Simple search** | 1-3 seconds |
| **Smart search (3 sources)** | 3-8 seconds |
| **Deep search (5+ sources)** | 5-15 seconds |
| **Rate limiting** | 2 req/sec per domain |
| **UA rotation** | 7 browser user-agents |

---

## 🧪 Testing

```bash
# Run the integration test suite
uv run python test_v3.py
```

### Recommended LM Studio Test Queries:
1. **`"What are the upcoming Bollywood movies in 2026?"`** — Should return movie lists
2. **`"Search the web for Sundar Pichai"`** — Should return profile data
3. **`"Latest albums by Taylor Swift"`** — Should return music data
4. **`"Python asyncio tutorial"`** — Should return technical content

---

## 📄 License & Contributing
This project is licensed under the MIT License - See [LICENSE](LICENSE) for details.

Contributions, bug reports, and feature requests are highly welcome!

---
**Made with ❤️ for the Local Developer & LLM community**
