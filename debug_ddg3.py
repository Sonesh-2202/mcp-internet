"""Test duckduckgo fetching using requests or without custom headers."""
import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def check():
    import httpx
    from urllib.parse import quote_plus
    
    query = "sujaya pon gita"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers)
        html = response.text
        if html:
            print(f"HTML length: {len(html)}")
            if "result__a" in html:
                print("✅ Found 'result__a' class")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                results = soup.find_all("div", class_="result")
                print(f"Results: {len(results)}")
            else:
                print("❌ No results found. Output snippet:")
                print(html[:500])

asyncio.run(check())
