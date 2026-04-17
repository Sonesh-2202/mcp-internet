# 🌍 Multi-Platform Usage Guide

This guide provides comprehensive, step-by-step instructions for deploying and using the **MCP Internet Server** across any major operating system.

Whether you're running Windows, macOS, or any flavor of Linux, you can effortlessly supercharge your local LLMs!

---

## 📋 Table of Contents
1. [General Prerequisites](#-general-prerequisites)
2. [Method 1: The Universal Way (Using uv - Recommended)](#-method-1-the-universal-way-using-uv---recommended)
3. [Method 2: OS-Specific Native Setups (Using venv/pip)](#-method-2-os-specific-native-setups-using-venvpip)
    - [Windows](#windows)
    - [macOS](#macos)
    - [Debian / Ubuntu](#debian--ubuntu-based-linux)
    - [Fedora / RHEL](#fedora--rhel-based-linux)
    - [Arch Linux](#arch-linux)
4. [Connecting to LLM Clients](#-connecting-to-llm-clients)
    - [LM Studio](#lm-studio)
    - [Claude Desktop](#claude-desktop)
5. [Troubleshooting](#-troubleshooting)

---

## 🛠️ General Prerequisites

Before you begin, ensure you have:
1. **Python 3.10 or higher** installed. ([Python Downloads](https://www.python.org/downloads/))
2. **Git** installed to clone the repository.
3. Access to your preferred terminal/command-line interface.

---

## 🚀 Method 1: The Universal Way (Using uv - Recommended)

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package manager written in Rust. It abstracts away virtual environment complexities seamlessly on **every** platform.

**1. Install uv** (if you don't have it):
- **macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows:** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

**2. Setup Project:**
```bash
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet
uv sync
```
*That's it! Your setup is complete.*

---

## 🖥️ Method 2: OS-Specific Native Setups (Using venv/pip)

If you prefer using standard Python tools, here is how to set up natively on different operating systems.

### Windows

```powershell
# 1. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.\.venv\Scripts\activate

# 4. Install dependencies
pip install -e .
```

### macOS

macOS includes Python 3 by default, or you can install it via Homebrew (`brew install python`).

```bash
# 1. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -e .
```

### Debian / Ubuntu Based Linux
*(e.g., Ubuntu, Linux Mint, Pop!_OS)*

```bash
# 1. Install prerequisites (Python venv and Git)
sudo apt update
sudo apt install python3-venv python3-pip git -y

# 2. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -e .
```

### Fedora / RHEL Based Linux
*(e.g., Fedora, CentOS, Rocky Linux)*

```bash
# 1. Install prerequisites
sudo dnf install python3-pip git -y

# 2. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -e .
```

### Arch Linux
*(e.g., Arch Linux, Manjaro, EndeavourOS)*

```bash
# 1. Install prerequisites
sudo pacman -S python python-pip git base-devel

# 2. Clone the repository
git clone https://github.com/Sonesh-2202/mcp-internet.git
cd mcp-internet

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -e .
```
---

## 🔌 Connecting to LLM Clients

MCP servers must be configured within an MCP-compatible client. Here are the instructions for the two most popular applications.

### LM Studio

Navigate to the **Program** tab in LM Studio, and locate the `mcp.json` file configuration settings.
Add the following entry:

**If you used setup Method 1 (`uv`):**
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": ["run", "mcp-internet"],
      "cwd": "/absolute/path/to/your/mcp-internet"
    }
  }
}
```

**If you used setup Method 2 (Virtual Env - macOS/Linux):**
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "/absolute/path/to/mcp-internet/.venv/bin/python",
      "args": ["-m", "mcp_internet.server"],
      "cwd": "/absolute/path/to/mcp-internet"
    }
  }
}
```

**If you used setup Method 2 (Virtual Env - Windows):**
```json
{
  "mcpServers": {
    "mcp-internet": {
      "command": "C:\\absolute\\path\\to\\mcp-internet\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_internet.server"],
      "cwd": "C:\\absolute\\path\\to\\mcp-internet"
    }
  }
}
```
*Tip: On Windows paths, remember to escape the backslashes (`\\`), or simply use forward slashes (`/`).*

### Claude Desktop

Locate your Claude Desktop Configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the same JSON payload shown for LM Studio into your config file, and restart the Claude Desktop application.

---

## 🔧 Troubleshooting

- **Python not found error (Linux/macOS):**
  Ensure you are using `python3` instead of `python` in your terminal commands if `python` is not aliased.
- **Permission errors parsing HTML (Debian/Ubuntu):**
  If packages like `lxml` fail to install during `pip install`, you might lack system C-libraries. Install them via:
  `sudo apt install libxml2-dev libxslt-dev python3-dev` natively, or simply rely on `uv` to pull pre-compiled wheels.
- **Server fails to boot in LM Studio:**
  Examine the `cwd` (Current Working Directory). It **must** point precisely to the folder containing the `pyproject.toml` file.

---
*Happy exploring the web with your local models!*
