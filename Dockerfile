# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir "mcp[cli]>=1.2.0" httpx beautifulsoup4 lxml

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src

# Run the MCP server
CMD ["python", "-m", "mcp_internet.server"]
