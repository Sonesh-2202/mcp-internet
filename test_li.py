"""Test LinkedIn fetching."""
import asyncio
import httpx

async def test_li():
    url = "https://in.linkedin.com/in/sujaya-pon-gita-prabahar-singh-5723a2327"
    
    headers_bot = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    headers_normal = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(http2=True) as client:
        r1 = await client.get(url, headers=headers_bot, follow_redirects=True)
        print(f"Bot UA status: {r1.status_code}")
        
        r2 = await client.get(url, headers=headers_normal, follow_redirects=True)
        print(f"Normal UA status: {r2.status_code}")

asyncio.run(test_li())
