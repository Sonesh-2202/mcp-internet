"""Live integration test — tests smart_search with real web data."""
import asyncio
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


async def test_live():
    from mcp_internet.tools.smart_search import smart_search
    from mcp_internet.utils.cache import cache_clear

    # Clear cache to force fresh results
    await cache_clear()

    print("=" * 60)
    print("LIVE INTEGRATION TEST - smart_search")
    print("=" * 60)

    # Test 1: General knowledge query
    print("\n📋 Test 1: General knowledge query")
    print("-" * 40)
    start = time.time()
    result = await smart_search("Python programming language", max_sources=2)
    elapsed = time.time() - start
    print(f"⏱️ Time: {elapsed:.1f}s")
    print(f"📏 Length: {len(result)} chars")
    has_content = len(result) > 500 and "Error" not in result[:50]
    print(f"{'✅' if has_content else '❌'} Has substantial content: {has_content}")
    # Show first 500 chars
    print(f"\n--- Preview ---\n{result[:500]}\n--- End ---\n")

    # Test 2: Cached response (should be instant)
    print("\n📋 Test 2: Cached response (same query)")
    print("-" * 40)
    start = time.time()
    result2 = await smart_search("Python programming language", max_sources=2)
    elapsed2 = time.time() - start
    print(f"⏱️ Time: {elapsed2:.3f}s (was {elapsed:.1f}s)")
    is_cached = elapsed2 < 0.5
    print(f"{'✅' if is_cached else '❌'} Cache working: {is_cached}")

    # Test 3: Query classification
    print("\n📋 Test 3: Query classification accuracy")
    print("-" * 40)
    from mcp_internet.tools.smart_search import classify_query
    tests = [
        ("upcoming movies 2026", "entertainment"),
        ("Sundar Pichai LinkedIn", "person"),
        ("latest AI news", "news"),
        ("GitHub Python library", "technical"),
        ("best pizza recipe", "general"),
    ]
    all_pass = True
    for query, expected in tests:
        actual = classify_query(query)
        passed = actual == expected
        if not passed:
            all_pass = False
        print(f"  {'✅' if passed else '❌'} '{query}' → {actual} (expected: {expected})")
    
    print(f"\n{'✅' if all_pass else '❌'} Classification: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    print("\n" + "=" * 60)
    print("LIVE TEST COMPLETE")
    print("=" * 60)


asyncio.run(test_live())
