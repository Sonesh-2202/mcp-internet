"""Debug script to diagnose search issues with 'sujaya pon gita'."""
import asyncio
import sys
import logging

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr,
                    format="%(name)s - %(levelname)s - %(message)s")


async def debug():
    query = "sujaya pon gita"

    # Step 1: Test DuckDuckGo HTML scraping directly
    print("=" * 60)
    print(f"DEBUG: Searching for '{query}'")
    print("=" * 60)

    print("\n--- Step 1: DuckDuckGo HTML Scraping ---")
    from mcp_internet.tools.search import search_duckduckgo_html
    results = await search_duckduckgo_html(query, 10, retries=3)
    print(f"HTML scraping returned {len(results)} results")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r.get('title', 'N/A')}")
        print(f"     URL: {r.get('href', 'N/A')}")
        print(f"     Snippet: {r.get('body', 'N/A')[:100]}")

    # Step 2: Test ddgs fallback
    if not results:
        print("\n--- Step 2: DDGS Library Fallback ---")
        from mcp_internet.tools.search import search_with_ddgs
        results = await search_with_ddgs(query, 10)
        print(f"DDGS returned {len(results)} results")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r.get('title', 'N/A')}")
            print(f"     URL: {r.get('href', r.get('link', 'N/A'))}")
            print(f"     Snippet: {r.get('body', r.get('snippet', 'N/A'))[:100]}")

    # Step 3: Test the raw HTML fetch to see what DuckDuckGo returns
    print("\n--- Step 3: Raw HTML inspection ---")
    from mcp_internet.utils.http_client import fetch_url
    from urllib.parse import quote_plus
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    html = await fetch_url(url, retries=2)
    if html:
        print(f"HTML length: {len(html)} chars")
        # Check for result markers
        if "result__a" in html:
            print("✅ Found 'result__a' class (results present)")
        else:
            print("❌ No 'result__a' class found")
        if "No results" in html or "no results" in html.lower():
            print("⚠️ Page says 'No results'")
        # Check for bot detection
        if "captcha" in html.lower() or "robot" in html.lower():
            print("⚠️ Possible bot detection (captcha/robot mention found)")
        # Show a snippet of the HTML around results
        idx = html.find("result")
        if idx > 0:
            print(f"First 'result' mention at char {idx}:")
            print(html[max(0, idx-50):idx+200])
    else:
        print("❌ Failed to fetch HTML from DuckDuckGo")

    # Step 4: Test smart_search
    print("\n--- Step 4: smart_search output ---")
    from mcp_internet.utils.cache import cache_clear
    await cache_clear()  # Clear cache for fresh results
    
    from mcp_internet.tools.smart_search import smart_search
    result = await smart_search(query, max_sources=3)
    print(f"smart_search output length: {len(result)} chars")
    print(f"\n{result[:2000]}")


asyncio.run(debug())
