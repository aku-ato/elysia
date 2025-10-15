#!/usr/bin/env python3
"""
Tool Discovery Script: Test various investigative queries to identify gaps in standard tools.

This script tests different social media analysis patterns to discover which ones:
1. ✅ Work perfectly with standard Aggregate/Query tools
2. ⚠️  Work but are slow/inefficient
3. ❌ Fail or require workarounds (candidates for custom tools)

Test Categories:
- Hashtag-based aggregations
- Time-based analysis
- Cross-collection correlations
- Author behavior patterns
- Content analysis
- Network analysis
"""
from elysia import Tree, Settings
import json
from datetime import datetime

# Load settings
settings = Settings.from_env_vars()

# Create tree
tree = Tree(settings=settings)

# Test queries organized by category
test_queries = {
    "hashtag_analysis": [
        {
            "name": "Top authors for hashtag",
            "query": "Who are the top 5 authors posting with hashtag #السلطان_هيثم_يزور_بيلاروس?",
            "expected_tool": "aggregate (with CONTAINS_ANY filter)",
            "test_standard": True
        },
        {
            "name": "Multiple hashtag correlation",
            "query": "Which authors post with both #السلطان_هيثم_يزور_بيلاروس AND #عمان?",
            "expected_tool": "aggregate (with AND filters)",
            "test_standard": True
        },
        {
            "name": "Hashtag co-occurrence",
            "query": "What other hashtags appear most frequently with #السلطان_هيثم_يزور_بيلاروس?",
            "expected_tool": "custom? (requires array intersection)",
            "test_standard": True
        }
    ],

    "temporal_analysis": [
        {
            "name": "Posts per day",
            "query": "How many posts are there per day for the last week?",
            "expected_tool": "aggregate (group by date)",
            "test_standard": True
        },
        {
            "name": "Peak posting hours",
            "query": "What hour of the day has the most tweets?",
            "expected_tool": "aggregate (extract hour from timestamp)",
            "test_standard": True
        },
        {
            "name": "Trending hashtags over time",
            "query": "Which hashtags are trending this week vs last week?",
            "expected_tool": "custom? (requires time-based comparison)",
            "test_standard": True
        }
    ],

    "author_behavior": [
        {
            "name": "Most active authors",
            "query": "Who are the top 10 most active authors overall?",
            "expected_tool": "aggregate (group by author, count)",
            "test_standard": True
        },
        {
            "name": "Authors by average engagement",
            "query": "Which authors have the highest average likes per post?",
            "expected_tool": "aggregate (group by author, average likes)",
            "test_standard": True
        },
        {
            "name": "Author posting patterns",
            "query": "Show me posting frequency distribution for author @mahas1012",
            "expected_tool": "query + custom analysis?",
            "test_standard": True
        }
    ],

    "content_analysis": [
        {
            "name": "Most common words in tweets",
            "query": "What are the most common words in tweets about #السلطان_هيثم_يزور_بيلاروس?",
            "expected_tool": "custom (requires NLP/text processing)",
            "test_standard": False  # Likely to fail
        },
        {
            "name": "Sentiment analysis",
            "query": "What's the sentiment distribution for posts with #السلطان_هيثم_يزور_بيلاروس?",
            "expected_tool": "custom (requires sentiment model)",
            "test_standard": False  # Requires ML
        }
    ],

    "cross_collection": [
        {
            "name": "Authors posting across topics",
            "query": "Which authors post about both politics and sports?",
            "expected_tool": "cross-collection query (if categories exist)",
            "test_standard": True
        }
    ],

    "network_analysis": [
        {
            "name": "Reply/mention network",
            "query": "Who does @mahas1012 mention most frequently?",
            "expected_tool": "query + custom analysis (graph)",
            "test_standard": False  # Complex
        }
    ]
}

def run_test(category, test_case):
    """Run a single test query and capture results."""
    print("\n" + "=" * 100)
    print(f"📊 CATEGORY: {category.upper()}")
    print(f"🧪 TEST: {test_case['name']}")
    print("=" * 100)
    print(f"Query: {test_case['query']}")
    print(f"Expected Tool: {test_case['expected_tool']}")
    print(f"Testing with standard tools: {test_case['test_standard']}")
    print("-" * 100)

    if not test_case['test_standard']:
        print("⏭️  SKIPPED - Requires custom implementation")
        return {
            "category": category,
            "name": test_case['name'],
            "query": test_case['query'],
            "status": "skipped",
            "reason": "Requires custom tool",
            "expected_tool": test_case['expected_tool']
        }

    try:
        start_time = datetime.now()

        response, objects = tree(
            test_case['query'],
            collection_names=["SocialMediaPosts"]
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n✅ SUCCESS")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📄 Response: {response[:200]}..." if len(response) > 200 else f"📄 Response: {response}")
        print(f"📦 Objects returned: {len(objects)}")

        return {
            "category": category,
            "name": test_case['name'],
            "query": test_case['query'],
            "status": "success",
            "duration_seconds": duration,
            "response_preview": response[:200],
            "num_objects": len(objects),
            "expected_tool": test_case['expected_tool']
        }

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return {
            "category": category,
            "name": test_case['name'],
            "query": test_case['query'],
            "status": "failed",
            "error": str(e),
            "expected_tool": test_case['expected_tool']
        }

def main():
    """Run all test queries and generate report."""
    print("=" * 100)
    print("🔬 TOOL DISCOVERY: Testing Investigative Query Patterns")
    print("=" * 100)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    all_results = []

    # Run tests by category
    for category, tests in test_queries.items():
        for test_case in tests:
            result = run_test(category, test_case)
            all_results.append(result)

            # Brief pause between tests
            import time
            time.sleep(2)

    # Generate summary report
    print("\n\n" + "=" * 100)
    print("📊 DISCOVERY REPORT")
    print("=" * 100)

    # Group results by status
    succeeded = [r for r in all_results if r['status'] == 'success']
    failed = [r for r in all_results if r['status'] == 'failed']
    skipped = [r for r in all_results if r['status'] == 'skipped']

    print(f"\n✅ Succeeded: {len(succeeded)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏭️  Skipped: {len(skipped)}")

    if failed:
        print("\n" + "=" * 100)
        print("❌ FAILED QUERIES (Candidates for Custom Tools)")
        print("=" * 100)
        for result in failed:
            print(f"\n📌 {result['name']}")
            print(f"   Category: {result['category']}")
            print(f"   Query: {result['query']}")
            print(f"   Expected: {result['expected_tool']}")
            print(f"   Error: {result['error'][:100]}...")

    if skipped:
        print("\n" + "=" * 100)
        print("⏭️  SKIPPED QUERIES (Known Custom Tool Requirements)")
        print("=" * 100)
        for result in skipped:
            print(f"\n📌 {result['name']}")
            print(f"   Category: {result['category']}")
            print(f"   Expected: {result['expected_tool']}")

    # Save detailed results
    with open('tool_discovery_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 100)
    print("💾 Detailed results saved to: tool_discovery_results.json")
    print("=" * 100)

if __name__ == "__main__":
    main()
