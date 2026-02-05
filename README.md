# 🌐 MCP Internet Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)

> **Give your local LLMs the power to access the internet!** 🚀

An MCP (Model Context Protocol) server that provides internet access tools for local LLMs running in LM Studio. Search the web, read articles, get weather, fetch news, and more - all without requiring API keys!

## ✨ Features

| Tool | Description |
|------|-------------|
| 🔍 **search_web** | Search the internet using DuckDuckGo (with optional deep search) |
| 🎯 **quick_lookup** | Quick info lookup for people, topics, concepts |
| 🌐 **search_site** | Search within specific sites (LinkedIn, Instagram, GitHub, etc.) |
| 📄 **read_webpage** | Extract clean text from any URL |
| 📰 **get_news** | Latest headlines from Google News |
| 🌤️ **get_weather** | Weather forecasts via Open-Meteo |
| 📖 **get_definition** | Wikipedia summaries & dictionary |
| 💱 **get_currency_rate** | Live exchange rates |
| 🕐 **get_current_time** | World timezone clock |

**🆓 No API keys required!** All tools use free, open APIs.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- [LM Studio](https://lmstudio.ai/) 0.3.17+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-internet.git
cd mcp-internet

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
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

### Verify Installation

The tools should now appear in LM Studio. Try asking your LLM:

> "Search the web for Sujaya Pon Gita"

> "Find sonesh_2202 on Instagram"

> "What's the weather in Tokyo?"

## 🛠️ Available Tools

### 🔍 search_web
Search the internet using DuckDuckGo. Now with **deep search** option!

```
Query: "Python programming" or "Elon Musk"
Results: 10 (default), max 20
Deep Search: Set to true for detailed content analysis
```

**Examples:**
- Basic: "Search for AI news"
- Deep: "Do a deep search for quantum computing"

### 🎯 quick_lookup (NEW!)
Quick info lookup - perfect for finding info about **people, places, or topics**.

```
Query: "Sujaya Pon Gita" or "sonesh_2202"
```
Automatically fetches and shows content from the most relevant result!

### 🌐 search_site (NEW!)
Search within a **specific website** - great for finding social profiles!

```
Query: "John Doe"
Site: "linkedin.com" or "instagram.com" or "github.com"
```

**Examples:**
- "Search for John Doe on LinkedIn"
- "Find sonesh_2202 on Instagram"

### 📄 read_webpage
Extract the main content from any webpage.

```
URL: "https://example.com/article"
Max Length: 5000 characters (default)
```

### 📰 get_news
Fetch latest news headlines.

```
Topics: world, business, technology, science, health, sports, entertainment
... or any search query
```

### 🌤️ get_weather
Get current weather and 3-day forecast.

```
Location: "Tokyo", "New York, USA", "Paris, France"
```

### 📖 get_definition
Look up definitions and Wikipedia summaries.

```
Term: "quantum computing", "Python", "artificial intelligence"
```

### 💱 get_currency_rate
Convert currencies with live rates.

```
From: "USD"
To: "EUR"
Amount: 100
```

### 🕐 get_current_time
Get current time for any timezone.

```
Location: "Tokyo", "America/New_York", "UTC"
```

## 🧪 Testing

### Using MCP Inspector

```bash
cd "e:\Coding projects\MCP-Internet"
uv run mcp dev src/mcp_internet/server.py
```

This opens an interactive browser interface where you can test all tools.

### Direct Testing

```bash
# Test search
uv run python -c "import asyncio; from src.mcp_internet.tools.search import search_web; print(asyncio.run(search_web('Python programming')))"

# Test quick lookup
uv run python -c "import asyncio; from src.mcp_internet.tools.search import quick_lookup; print(asyncio.run(quick_lookup('Elon Musk')))"
```

## 📁 Project Structure

```
MCP-Internet/
├── src/mcp_internet/
│   ├── __init__.py
│   ├── server.py           # Main MCP server (9 tools)
│   ├── tools/
│   │   ├── search.py       # Web search, quick_lookup, search_site
│   │   ├── webpage.py      # Content extraction
│   │   ├── news.py         # News headlines
│   │   ├── weather.py      # Weather data
│   │   ├── dictionary.py   # Definitions
│   │   ├── currency.py     # Currency rates
│   │   └── time.py         # World time
│   └── utils/
│       └── http_client.py  # HTTP utilities
├── pyproject.toml
├── README.md
└── LICENSE
```

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
# Reinstall dependencies
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
- [Wikipedia](https://www.wikipedia.org/) - Knowledge base

---

<p align="center">
  Made with ❤️ for the local AI community
</p>
