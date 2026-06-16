"""Quick integration test for MCP Internet v3.0 upgrades."""
import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


async def test():
    # Test 1: Cache system
    from mcp_internet.utils.cache import cache_get, cache_set, cache_clear
    await cache_set("search", "test_query", "test_value")
    result = await cache_get("search", "test_query")
    assert result == "test_value", f"Cache failed: got {result}"
    await cache_clear("search")
    result = await cache_get("search", "test_query")
    assert result is None, "Cache clear failed"
    print("✅ Cache system: PASS")
    
    # Test 2: Extractors
    from mcp_internet.utils.extractors import extract_structured_data
    html = (
        '<html><head><title>Test Page</title>'
        '<meta property="og:title" content="OG Title"/></head>'
        '<body><table><tr><th>Name</th><th>Value</th></tr>'
        '<tr><td>A</td><td>1</td></tr></table></body></html>'
    )
    data = extract_structured_data(html, "https://example.com")
    assert "title" in data, f"Extraction failed: {data}"
    print(f"✅ Extractors: PASS (extracted keys: {list(data.keys())})")
    
    # Test 3: HTTP client upgrades
    from mcp_internet.utils.http_client import _get_default_headers, _USER_AGENTS
    h1 = _get_default_headers()
    assert "User-Agent" in h1
    assert len(_USER_AGENTS) >= 5
    print(f"✅ HTTP client: PASS ({len(_USER_AGENTS)} UAs, rate limiter ready)")
    
    # Test 4: Query optimization
    from mcp_internet.tools.smart_search import optimize_query, classify_query
    assert optimize_query("search for upcoming movies") == "upcoming movies"
    assert classify_query("upcoming Bollywood movies 2026") == "entertainment"
    assert classify_query("LinkedIn profile of Sundar Pichai") == "person"
    assert classify_query("latest news about AI") == "news"
    print("✅ Query intelligence: PASS")
    
    # Test 5: Table formatting
    from mcp_internet.utils.extractors import tables_to_markdown
    tables = [{"headers": ["Movie", "Rating"], "rows": [["Movie A", "8.5"], ["Movie B", "7.2"]]}]
    md = tables_to_markdown(tables)
    assert "| Movie | Rating |" in md
    assert "| Movie A | 8.5 |" in md
    print("✅ Table formatting: PASS")
    
    print("\n🎉 All unit tests passed!")


asyncio.run(test())
