🌐 MCP Internet Server
Internet Capability Layer for Local LLMs




[
]
[
]


A production-ready Model Context Protocol (MCP) server that gives local LLMs real-time internet capabilities — fully async, modular, and API-key free.

📌 Overview

Local LLMs are powerful — but static.

Without structured access to external data, they are limited to training-time knowledge.

MCP Internet Server extends local models (via LM Studio) with a real-time tool execution layer built on the Model Context Protocol (MCP). It enables LLMs to:

Perform live web searches

Fetch current weather

Retrieve news

Search GitHub

Extract webpage content

Convert currencies

And much more

All running locally.
No cloud LLM provider.
No API keys required.
No telemetry.

This project focuses on clean architecture, async execution, and modular extensibility.

🏗 Architecture
High-Level Flow

User sends a prompt in LM Studio

The LLM determines a tool is required

A structured MCP tool call is issued via STDIO

FastMCP dispatches the request

Tool executes async HTTP request

Result returned to the model

Model synthesizes final response

System Layers
1️⃣ Transport Layer

STDIO-based MCP communication

JSON tool call protocol

Strict stdout (protocol) / stderr (logging) separation

2️⃣ Execution Layer

FastMCP server

Decorator-based tool registration

Lazy-loaded imports for faster startup

3️⃣ Networking Layer

Async HTTP using httpx

Shared HTTP utilities

Browser-like headers

Timeout handling & structured error recovery

4️⃣ Parsing & Processing

BeautifulSoup + lxml

RSS feed parsing

Webpage content cleaning

Structured response formatting

5️⃣ Resilience Strategy

Fallback APIs

Graceful failure handling

Controlled output truncation

Input validation

🛠 Available Tools (22)
🔍 Search & Discovery

search_web

quick_lookup

search_site

📄 Content Extraction

read_webpage

read_pdf

📰 Media & Social

get_news

search_reddit

search_twitter

search_youtube

get_video_info

💻 Developer Tools

search_github

get_repo_info

🌤 Information Utilities

get_weather

get_current_time

translate_text

calculate

🌐 Network & URL Tools

shorten_url

get_my_ip

geolocate_ip

📦 Output & Automation

generate_qr

generate_wifi_qr

send_email

All tools operate using public/free endpoints wherever possible.

⚙️ Installation
Windows (Recommended: uv)
git clone https://github.com/yourusername/mcp-internet.git
cd mcp-internet
uv sync


Run manually for testing:

uv run mcp-internet

Linux (venv)
git clone https://github.com/yourusername/mcp-internet.git
cd mcp-internet

python -m venv .venv
source .venv/bin/activate

pip install -e .


Run manually:

python -m mcp_internet.server

🔧 LM Studio Configuration

Add to your mcp.json:

Using uv
{
  "mcpServers": {
    "mcp-internet": {
      "command": "uv",
      "args": ["run", "mcp-internet"],
      "cwd": "PATH_TO_PROJECT"
    }
  }
}

Using Python directly
{
  "mcpServers": {
    "mcp-internet": {
      "command": "python",
      "args": ["-m", "mcp_internet.server"],
      "cwd": "PATH_TO_PROJECT"
    }
  }
}


Restart LM Studio after configuration.

💡 Example Prompts
Search the web for Python async tutorials
What's the weather in Tokyo?
Get the latest technology news
Search GitHub for machine learning projects
Translate "Hello world" to Japanese
Read this webpage: https://example.com
Convert 100 USD to INR


The model will automatically call the appropriate tool.

📁 Project Structure
mcp-internet/
├── pyproject.toml
├── README.md
├── src/mcp_internet/
│   ├── server.py          # MCP server entry point
│   ├── tools/             # Tool implementations
│   └── utils/
│       └── http_client.py # Shared async HTTP utilities


Clear separation between:

Protocol layer

Tool implementations

Shared utilities

🧠 Design Principles
Async-First

All tools use non-blocking I/O for scalability and responsiveness.

Modular Architecture

Each tool is self-contained and registered via decorators.

Local-First

No model data is transmitted externally. Only tool-specific API calls are made.

Zero API Keys

Reduces friction and simplifies setup.

Graceful Failure

APIs fail → fallback logic triggers → structured error response returned.

🚀 Roadmap

 Tool result caching layer

 Rate limiting controls

 Docker container support

 Streaming tool responses

 Plugin-based tool discovery

 Observability & logging dashboard

🤝 Contributing

Contributions are welcome.

Focus areas:

New tools

Performance optimizations

Better fallback strategies

Streaming support

Cross-platform improvements

🔒 Privacy

This server does not:

Send prompts to external LLM providers

Log user queries externally

Store persistent user data

Only tool-specific API endpoints are contacted when required.

📄 License

MIT License.

✨ Final Note

This project explores what local AI becomes when given structured, controlled access to the internet.

It is not just a feature extension — it is an infrastructure layer for tool-augmented local intelligence.