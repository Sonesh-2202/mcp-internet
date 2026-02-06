# 🌐 MCP Internet Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-ready-purple.svg)](https://lmstudio.ai/)

> **Give your local LLMs the power of the internet!** 🚀

An MCP server providing **22 internet tools** for local LLMs in LM Studio. Search the web, read articles, get weather, news, and more - **no API keys required!**

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
  - [Windows](#windows-using-uv)
  - [Arch Linux](#arch-linux-using-venv)
- [Available Tools](#️-available-tools-22)
- [Configuration](#-configuration)
  - [Windows Configuration](#windows-configuration)
  - [Arch Linux Configuration](#arch-linux-configuration)
- [Dependencies](#-dependencies)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## 🚀 Quick Start

### Windows (using uv)

```bash
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet
uv sync
```

### Arch Linux (using venv)

```bash
# Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# Install Python if not already installed
sudo pacman -S python python-pip

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Or install with pip directly
pip install mcp[cli] httpx beautifulsoup4 lxml ddgs
```

**For PDF support (optional):**
```bash
pip install pdfplumber
# Or install all optional dependencies
pip install -e ".[all]"
```

---

## ⚙️ Configuration

### Windows Configuration

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

### Arch Linux Configuration

Add to LM Studio's `mcp.json` (typically at `~/.config/lmstudio/mcp.json`):

**Option 1: Using venv directly**
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "/path/to/mcp-internet/.venv/bin/python",
      "args": ["-m", "mcp_internet.server"],
      "cwd": "/path/to/mcp-internet"
    }
  }
}
```

**Option 2: Using a shell wrapper script**

Create a shell script `~/.local/bin/run-mcp-internet.sh`:
```bash
#!/bin/bash
cd /path/to/mcp-internet
source .venv/bin/activate
python -m mcp_internet.server
```

Then in `mcp.json`:
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "/home/youruser/.local/bin/run-mcp-internet.sh",
      "args": []
    }
  }
}
```

**Option 3: Using uv on Arch Linux**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then use the same configuration as Windows
```

```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": ["run", "mcp-internet"],
      "cwd": "/path/to/mcp-internet"
    }
  }
}
```

---

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

---

## 📦 Dependencies

### Core Dependencies (Required)
| Package | Version | Purpose |
|---------|---------|---------|
| `mcp[cli]` | >=1.2.0 | MCP server framework |
| `httpx` | >=0.27.0 | Async HTTP client |
| `beautifulsoup4` | >=4.12.0 | HTML parsing |
| `lxml` | >=5.0.0 | Fast XML/HTML parser |
| `ddgs` | >=9.0.0 | DuckDuckGo search |

### Optional Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `pdfplumber` | >=0.10.0 | PDF reading support |

### Manual Installation (Arch Linux)

```bash
# Activate your venv first
source .venv/bin/activate

# Install core dependencies
pip install "mcp[cli]>=1.2.0" "httpx>=0.27.0" "beautifulsoup4>=4.12.0" "lxml>=5.0.0" "ddgs>=9.0.0"

# Optional: PDF support
pip install "pdfplumber>=0.10.0"
```

---

## 💡 Try These

```
"Search the web for Python tutorials"
"What's the weather in Tokyo?"
"Get the latest tech news"
"Search YouTube for coding tutorials"
"Search GitHub for machine learning projects"
"Translate 'Hello' to Japanese"
```

---

## 🔧 Troubleshooting

### Common Issues on Arch Linux

**1. Python command not found**
```bash
# Arch uses python3 by default
sudo pacman -S python
# Or create an alias
alias python=python3
```

**2. Module not found errors**
```bash
# Ensure venv is activated
source .venv/bin/activate

# Reinstall the package in editable mode
pip install -e .
```

**3. Permission denied on script**
```bash
chmod +x ~/.local/bin/run-mcp-internet.sh
```

**4. SSL/Certificate errors**
```bash
# Install CA certificates
sudo pacman -S ca-certificates
pip install --upgrade certifi
```

**5. lxml build fails**
```bash
# Install required system libraries
sudo pacman -S libxml2 libxslt
pip install lxml
```

### Common Issues on Windows

**1. Unicode/Emoji errors**
The server automatically handles this, but ensure your terminal supports UTF-8.

**2. Path issues in mcp.json**
Use double backslashes (`\\`) or forward slashes (`/`) in paths.

---

## 📁 Project Structure

```
mcp-internet/
├── pyproject.toml         # Project configuration & dependencies
├── README.md              # This file
├── src/mcp_internet/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── tools/             # Tool implementations
│   │   ├── search.py      # Web search (DuckDuckGo)
│   │   ├── webpage.py     # Content extraction
│   │   ├── news.py        # News headlines
│   │   ├── weather.py     # Weather data
│   │   ├── youtube.py     # YouTube search
│   │   ├── reddit.py      # Reddit search
│   │   ├── twitter.py     # Twitter search
│   │   ├── github.py      # GitHub search
│   │   ├── translator.py  # Translation
│   │   ├── math_tools.py  # Calculator
│   │   ├── urls.py        # URL tools
│   │   ├── ip_tools.py    # IP lookup
│   │   ├── qr_code.py     # QR codes
│   │   ├── pdf_reader.py  # PDF reading
│   │   ├── email_sender.py# Email
│   │   └── time.py        # Time zones
│   └── utils/
│       └── http_client.py # HTTP utilities
└── .venv/                 # Virtual environment (created by you)
```

---

## 🔄 Updating

### Windows
```bash
cd mcp-internet
git pull
uv sync
```

### Arch Linux
```bash
cd mcp-internet
git pull
source .venv/bin/activate
pip install -e .
```

---

## 🧪 Running Manually (Testing)

### Windows
```bash
uv run mcp-internet
```

### Arch Linux
```bash
source .venv/bin/activate
python -m mcp_internet.server
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for the local LLM community**
