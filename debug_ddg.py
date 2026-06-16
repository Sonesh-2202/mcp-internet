"""Check what DuckDuckGo HTML actually returns."""
import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def check():
    from mcp_internet.utils.http_client import fetch_url
    from urllib.parse import quote_plus
    
    query = "sujaya pon gita"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    
    html = await fetch_url(url, retries=2)
    if html:
        print(f"HTML length: {len(html)}")
        # Save to file for inspection
        with open("ddg_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved to ddg_debug.html")
        
        # Show key parts
        if "result" in html:
            print("Contains 'result'")
        if "captcha" in html.lower():
            print("⚠️ CAPTCHA detected!")
        if "Please try again" in html:
            print("⚠️ 'Please try again' message found")
        if "bot" in html.lower():
            print("⚠️ Bot detection possible")
        
        # Print the full HTML (it's small)
        print("\n--- Full HTML ---")
        print(html[:3000])
    else:
        print("Failed to fetch")

    # Also try with exact phrase in quotes
    print("\n\n--- Trying with quoted query ---")
    url2 = f'https://html.duckduckgo.com/html/?q={quote_plus(chr(34) + query + chr(34))}'
    html2 = await fetch_url(url2, retries=2)
    if html2:
        print(f"HTML length: {len(html2)}")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html2, "lxml")
        results = soup.find_all("div", class_="result")
        print(f"Results found: {len(results)}")
        for r in results[:5]:
            title = r.find("a", class_="result__a")
            if title:
                print(f"  - {title.get_text(strip=True)}")

    # Try Google search via ddgs
    print("\n\n--- DDGS with exact phrase ---")
    from ddgs import DDGS
    ddgs = DDGS()
    results = list(ddgs.text(f'"{query}"', max_results=10))
    print(f"DDGS exact phrase results: {len(results)}")
    for r in results[:5]:
        print(f"  - {r.get('title', 'N/A')}")
        print(f"    {r.get('href', r.get('link', 'N/A'))}")
        print(f"    {r.get('body', '')[:120]}")

asyncio.run(check())
