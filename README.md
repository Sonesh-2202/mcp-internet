# 🌐 MCP Internet Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)

> **Give your local LLMs the power of the internet!** 🚀

An MCP server providing **22 internet tools** for local LLMs in LM Studio. Search the web, read articles, get weather, news, and more - **no API keys required!**

## 🚀 Quick Start

```bash
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet
uv sync
```

Add to LM Studio's `mcp.json`:
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": ["run", "mcp-internet"],
      "cwd": "E:\\Coding projects\\MCP-Internet"
    }
  }
}
```

## 🛠️ Available Tools (22)

| Category | Tools |
|----------|-------|
| 🔍 **Search** | `search_web`, `quick_lookup`, `search_site` |
| 📄 **Reading** | `read_webpage`, `read_pdf` |
| 📰 **News/Social** | `get_news`, `search_reddit`, `search_twitter` |
| 🎬 **YouTube** | `search_youtube`, `get_video_info` |
| 💻 **GitHub** | `search_github`, `get_repo_info` |
| 🌤️ **Info** | `get_weather`, `get_current_time`, `translate_text`, `calculate` |
| 🔗 **URLs/IP** | `shorten_url`, `get_my_ip`, `geolocate_ip` |
| 📱 **QR/Email** | `generate_qr`, `generate_wifi_qr`, `send_email` |

## 💡 Try These

```
"Search the web for Python tutorials"
"What's the weather in Tokyo?"
"Get the latest tech news"
"Search YouTube for coding tutorials"
"Search GitHub for machine learning projects"
"Translate 'Hello' to Japanese"
```

## 📁 Project Structure

```
src/mcp_internet/
├── server.py          # Main MCP server
├── tools/             # Tool implementations
│   ├── search.py      # Web search
│   ├── webpage.py     # Content extraction
│   ├── news.py        # News headlines
│   ├── weather.py     # Weather data
│   ├── youtube.py     # YouTube search
│   ├── reddit.py      # Reddit search
│   ├── twitter.py     # Twitter search
│   ├── github.py      # GitHub search
│   ├── translator.py  # Translation
│   ├── math_tools.py  # Calculator
│   ├── urls.py        # URL tools
│   ├── ip_tools.py    # IP lookup
│   ├── qr_code.py     # QR codes
│   ├── pdf_reader.py  # PDF reading
│   ├── email_sender.py# Email
│   └── time.py        # Time zones
└── utils/
    └── http_client.py # HTTP utilities
```

## 📄 License

MIT License
