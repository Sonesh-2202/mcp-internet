"""
Pastebin Tool - Share code snippets and text.

Uses dpaste.org (no registration required).
"""

import logging
from urllib.parse import urlencode

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)


async def create_paste(
    content: str,
    title: str = "",
    syntax: str = "text",
    expiry_days: int = 7
) -> str:
    """
    Create a paste/code snippet to share.
    
    Args:
        content: The text or code to paste
        title: Optional title for the paste
        syntax: Syntax highlighting (e.g., 'python', 'javascript', 'text')
        expiry_days: Days until paste expires (default: 7, max: 365)
        
    Returns:
        URL to the created paste
        
    Supported syntax options:
        python, javascript, java, c, cpp, csharp, ruby, go, rust, php,
        html, css, sql, bash, json, yaml, xml, markdown, text
    """
    if not content.strip():
        return "❌ Error: Please provide content to paste."
    
    # Validate expiry
    expiry_days = max(1, min(expiry_days, 365))
    
    try:
        import httpx
        
        # Use dpaste.org API
        url = "https://dpaste.org/api/"
        
        # Map common syntax names
        syntax_map = {
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "rb": "ruby",
            "sh": "bash",
            "yml": "yaml",
            "md": "markdown",
            "txt": "text",
            "c++": "cpp",
            "c#": "csharp",
        }
        
        syntax = syntax_map.get(syntax.lower(), syntax.lower())
        
        # dpaste uses different expiry format
        expiry_map = {
            1: "onetime",
            7: "604800",  # 7 days in seconds
            30: "2592000",  # 30 days in seconds
            365: "31536000",  # 1 year in seconds
        }
        
        # Find closest expiry
        closest_expiry = min(expiry_map.keys(), key=lambda x: abs(x - expiry_days))
        expiry = expiry_map[closest_expiry]
        
        data = {
            "content": content,
            "syntax": syntax,
            "expiry_days": str(expiry_days),
        }
        
        if title:
            data["title"] = title
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                paste_url = response.text.strip()
                
                return f"""📋 **Paste Created Successfully**
{'=' * 40}

🔗 URL: {paste_url}

📝 Title: {title or '(untitled)'}
💻 Syntax: {syntax}
⏰ Expires: {expiry_days} day{'s' if expiry_days != 1 else ''}

📄 Preview:
{content[:200]}{'...' if len(content) > 200 else ''}
"""
            else:
                logger.error(f"Paste creation failed: {response.status_code} - {response.text}")
                return f"❌ Error: Failed to create paste. Status: {response.status_code}"
        
    except ImportError:
        return "❌ Error: httpx module not available."
    except Exception as e:
        logger.error(f"Paste creation error: {e}")
        return f"❌ Error: {str(e)}"
