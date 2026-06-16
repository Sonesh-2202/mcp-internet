"""Check DuckDuckGo HTML without Accept-Encoding header."""
import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def check():
    from mcp_internet.utils.http_client import get_client
    from urllib.parse import quote_plus
    
    query = "sujaya pon gita"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    
    client = await get_client()
    headers = dict(client.headers)
    if "accept-encoding" in headers:
        del headers["accept-encoding"]
    
    response = await client.get(url, headers=headers)
    html = response.text
    if html:
        print(f"HTML length: {len(html)}")
        if "result" in html:
            print("Contains 'result'")
        if "result__a" in html:
            print("✅ Found 'result__a' class (results present)")
        else:
            print("❌ No 'result__a' class found")
        print("\n--- Snippet ---")
        idx = html.find("result__a")
        if idx > 0:
            print(html[max(0, idx-100):idx+200])
        else:
            print(html[:500])

asyncio.run(check())
