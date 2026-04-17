# 🌐 MCP Internet Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)

> **Give your local LLMs the power of the internet!** 🚀

An open-source Model Context Protocol (MCP) server providing **22 internet tools** for local Large Language Models. Equip platforms like LM Studio or Claude Desktop with web search, content reading, weather, news, YouTube integrations, and more—**no API keys required!** 

Seamlessly deployable and beautifully functional across **Windows, macOS, and Linux**.

---

## ✨ Key Features
- **Zero Configuration:** No API keys or external subscriptions needed.
- **22 Powerful Tools:** Search DuckDuckGo, fetch news, read PDFs, scrape web contents, translate text, and more.
- **Cross-Platform:** Out-of-the-box support for Windows, macOS, and practically all Linux distributions (Ubuntu, Fedora, Arch, Debian, etc).
- **Fast & Lightweight:** Built on modern Python standards using `mcp[cli]`, `httpx`, and asynchronous functions.
- **Local First:** Designed with privacy and local LLM execution in mind. Keep your data locally while bridging the gap to the public web.

---

## 🛠️ Available Tools (22 In Total)

| Category | Tools |
|----------|-------|
| 🔍 **Search** | `search_web`, `quick_lookup`, `search_site` |
| 📄 **Reading** | `read_webpage`, `read_pdf` |
| 📰 **News/Social** | `get_news`, `search_reddit`, `search_twitter` |
| 🎬 **YouTube** | `search_youtube`, `get_video_info` |
| 💻 **GitHub** | `search_github`, `get_repo_info` |
| 🌤️ **Info / Utils** | `get_weather`, `get_current_time`, `translate_text`, `calculate` |
| 🔗 **URLs/IP** | `shorten_url`, `get_my_ip`, `geolocate_ip` |
| 📱 **Generation** | `generate_qr`, `generate_wifi_qr`, `send_email` |

---

## 🚀 Quick Start (Universal)

The universally recommended setup tool is [uv](https://github.com/astral-sh/uv), a blazingly fast Python package manager.

```bash
# 1. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 2. Sync dependencies
uv sync
```

**MCP Client Configuration (e.g., LM Studio's `mcp.json`):**
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
*(Remember to replace `/absolute/path/to/mcp-internet` with your actual project path)*

### 📖 Detailed OS Guides
For complete, step-by-step instructions (including traditional `pip` & `venv` setups) for **Windows, macOS, Arch Linux, Ubuntu, Fedora, Debian, and other distributions**, please see the comprehensive 👉 **[Multi-Platform Usage Guide](MULTI_PLATFORM_GUIDE.md)**.

---

## 💡 Use Cases & Examples
Try asking your local LLM:
- *"Search the web for the latest Python 3.13 features."*
- *"What's the weather like in Tokyo right now?"*
- *"Get the latest headlines regarding Artificial Intelligence."*
- *"Search GitHub for open source agents, and read the README from the top result."*
- *"Can you translate this Japanese webpage to English for me?"*

---

## 📁 Project Architecture
```text
mcp-internet/
├── pyproject.toml         # Dependencies & Config
├── MULTI_PLATFORM_GUIDE.md# Extensive setup guidelines for all OS platforms
├── README.md              # Project overview
└── src/mcp_internet/
    ├── server.py          # Entry point & server logic
    └── tools/             # Modular tool implementations (web, reading, IP, etc.)
```

---

## 📄 License & Contributing
This project is licensed under the MIT License - See [LICENSE](LICENSE) for details. 

Contributions, bug reports, and feature requests are highly welcome! Let's build the ultimate internet-bridge for open-source AI together!

---
**Made with ❤️ for the Local Developer & LLM community**
