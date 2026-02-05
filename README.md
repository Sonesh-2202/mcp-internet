# 🌐 MCP Internet Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)
[![Tools](https://img.shields.io/badge/Tools-33-orange.svg)](#-available-tools)

> **Give your local LLMs the power of the internet!** 🚀

An MCP (Model Context Protocol) server that provides **33 internet access tools** for local LLMs running in LM Studio. Search the web, read articles, get weather, fetch news, check stocks, and much more - all without requiring API keys!

## ✨ Features at a Glance

| Category | Tools |
|----------|-------|
| 🔍 **Search** | Web search, quick lookup, site-specific search |
| 📰 **News & Social** | News, Reddit, Hacker News, Twitter/X |
| 🎬 **Media** | YouTube search & video info |
| 💻 **Developer** | GitHub repos/users, code paste sharing |
| 💰 **Finance** | Stocks, crypto, currency conversion |
| 🌤️ **Info** | Weather, time zones, definitions, translation |
| 🔗 **URLs** | Shorten, expand, QR codes, WHOIS |
| 🛠️ **Utilities** | Calculator, IP lookup, PDF reader, email |

**🆓 No API keys required!** All tools use free, open APIs.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- [LM Studio](https://lmstudio.ai/) 0.3.17+

### Installation

```bash
# Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .

# Optional: For PDF support
pip install pdfplumber
```

### Configure LM Studio

1. Open **LM Studio**
2. Go to the **Program** tab (terminal icon in sidebar)
3. Click **Install > Edit mcp.json**
4. Add the following configuration:

```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": [
        "run",
        "mcp-internet"
      ],
      "cwd": "E:\\Coding projects\\MCP-Internet"
    }
  }
}
```

> **Note:** Replace the `cwd` path with your actual project location.

5. **Restart LM Studio** to load the server

## 🛠️ Available Tools

### 🔍 Search Tools

| Tool | Description |
|------|-------------|
| `search_web` | Search the internet using DuckDuckGo (with deep search option) |
| `quick_lookup` | Quick info lookup for people, topics, concepts |
| `search_site` | Search within specific sites (LinkedIn, Instagram, etc.) |

### 📄 Content Reading

| Tool | Description |
|------|-------------|
| `read_webpage` | Extract clean text from any URL |
| `read_pdf` | Extract text from PDF URLs |

### 📰 News & Social Media

| Tool | Description |
|------|-------------|
| `get_news` | Latest headlines from Google News |
| `search_reddit` | Search Reddit posts and discussions |
| `get_subreddit_posts` | Get top posts from a subreddit |
| `get_hackernews` | Get top/new/best stories from HN |
| `search_hackernews` | Search Hacker News via Algolia |
| `search_twitter` | Search Twitter/X via Nitter |
| `get_user_tweets` | Get recent tweets from a user |

### 🎬 YouTube

| Tool | Description |
|------|-------------|
| `search_youtube` | Search YouTube videos |
| `get_video_info` | Get video details (title, views, description) |

### 💻 GitHub

| Tool | Description |
|------|-------------|
| `search_github` | Search GitHub repositories |
| `get_repo_info` | Get detailed repo information |
| `get_github_user` | Get user/org profile info |

### 💰 Finance

| Tool | Description |
|------|-------------|
| `get_stock_price` | Stock prices via Yahoo Finance |
| `get_crypto_price` | Crypto prices via CoinGecko |
| `get_currency_rate` | Live exchange rates |

### 🌤️ Information

| Tool | Description |
|------|-------------|
| `get_weather` | Weather forecasts via Open-Meteo |
| `get_current_time` | World timezone clock |
| `get_definition` | Wikipedia summaries & dictionary |
| `translate_text` | Translate between 30+ languages |
| `detect_language` | Detect text language |
| `calculate` | Safe math expression evaluator |

### 🔗 URL & Network Tools

| Tool | Description |
|------|-------------|
| `shorten_url` | Create short URLs |
| `expand_url` | Reveal destination of short URLs |
| `get_my_ip` | Get your public IP address |
| `geolocate_ip` | Get location info for any IP |
| `whois_lookup` | Domain registration info |

### 📱 QR Codes

| Tool | Description |
|------|-------------|
| `generate_qr` | Generate QR code for text/URL |
| `generate_wifi_qr` | Generate WiFi network QR code |

### 📤 Sharing

| Tool | Description |
|------|-------------|
| `create_paste` | Share code snippets via pastebin |
| `send_email` | Send emails via SMTP |

## 💡 Usage Examples

Try asking your LLM:

```
"Search the web for Python async tutorials"
"What's the weather in Tokyo?"
"Get the latest tech news"
"What's the price of Bitcoin?"
"Search Reddit for machine learning discussions"
"Find trending repos on GitHub for Rust"
"What's on the front page of Hacker News?"
"Translate 'Hello world' to Japanese"
"Calculate 15% of 2500"
"Create a QR code for my website"
"Get stock price for AAPL"
"Search YouTube for coding tutorials"
```

## 🧪 Testing

### Using MCP Inspector

```bash
cd "e:\Coding projects\MCP-Internet"
uv run mcp dev src/mcp_internet/server.py
```

This opens an interactive browser interface to test all tools.

### Direct Testing

```bash
# Test search
uv run python -c "import asyncio; from src.mcp_internet.tools.search import search_web; print(asyncio.run(search_web('Python programming')))"

# Test stock price
uv run python -c "import asyncio; from src.mcp_internet.tools.stocks import get_stock_price; print(asyncio.run(get_stock_price('AAPL')))"

# Test crypto
uv run python -c "import asyncio; from src.mcp_internet.tools.stocks import get_crypto_price; print(asyncio.run(get_crypto_price('bitcoin')))"
```

## 📁 Project Structure

```
MCP-Internet/
├── src/mcp_internet/
│   ├── __init__.py
│   ├── server.py              # Main MCP server (33 tools)
│   ├── tools/
│   │   ├── search.py          # Web search, quick_lookup, search_site
│   │   ├── webpage.py         # Content extraction
│   │   ├── news.py            # News headlines
│   │   ├── weather.py         # Weather data
│   │   ├── dictionary.py      # Definitions
│   │   ├── currency.py        # Currency rates
│   │   ├── time.py            # World time
│   │   ├── youtube.py         # YouTube search & info
│   │   ├── reddit.py          # Reddit search
│   │   ├── hackernews.py      # Hacker News
│   │   ├── stocks.py          # Stock & crypto prices
│   │   ├── github.py          # GitHub search & info
│   │   ├── translator.py      # Translation
│   │   ├── twitter.py         # Twitter/X search
│   │   ├── urls.py            # URL shortener/expander
│   │   ├── ip_tools.py        # IP geolocation
│   │   ├── math_tools.py      # Calculator
│   │   ├── qr_code.py         # QR code generator
│   │   ├── pdf_reader.py      # PDF text extraction
│   │   ├── pastebin.py        # Code sharing
│   │   ├── email_sender.py    # SMTP email
│   │   └── whois.py           # Domain lookup
│   └── utils/
│       └── http_client.py     # HTTP utilities
├── pyproject.toml
├── README.md
└── LICENSE
```

## ⚙️ Configuration

### Email Setup (Optional)

To use the `send_email` tool, set these environment variables:

```bash
MCP_SMTP_SERVER=smtp.gmail.com
MCP_SMTP_PORT=587
MCP_SMTP_EMAIL=your-email@gmail.com
MCP_SMTP_PASSWORD=your-app-password
```

For Gmail, use an [App Password](https://myaccount.google.com/apppasswords).

## 🔧 Troubleshooting

### Server not appearing in LM Studio
- Ensure `mcp.json` path is correct for your system
- Restart LM Studio after editing config
- Check that Python 3.10+ and uv are installed

### Tool execution errors
- Check your internet connection
- Some APIs may be temporarily unavailable
- View logs in LM Studio's Program tab

### "Module not found" errors
```bash
uv sync --reinstall
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new tools
- Submit pull requests

## 📄 License

MIT License - feel free to use this in your projects!

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The open standard
- [LM Studio](https://lmstudio.ai/) - Local LLM inference
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [Open-Meteo](https://open-meteo.com/) - Free weather API
- [CoinGecko](https://www.coingecko.com/) - Crypto prices
- [Wikipedia](https://www.wikipedia.org/) - Knowledge base

---

<p align="center">
  Made with ❤️ for the local AI community<br>
  <b>Version 2.0 - 33 Tools!</b>
</p>
