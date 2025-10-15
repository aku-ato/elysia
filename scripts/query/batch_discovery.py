#!/usr/bin/env python3
"""
Batch discovery script - tests critical query patterns one by one
"""
from elysia import Tree, Settings
import json
from datetime import datetime

# Test queries ordered by priority (most likely to need custom tools)
TESTS = [
    {
        "name": "hashtag_cooccurrence",
        "query": "What other hashtags appear most frequently with #السلطان_هيثم_يزور_بيلاروس?",
        "expected_tool": "CUSTOM (requires array intersection analysis)",
        "priority": "HIGH"
    },
    {
        "name": "trending_hashtags",
        "query": "Which hashtags are trending this week compared to last week?",
        "expected_tool": "CUSTOM (requires time comparison)",
        "priority": "HIGH"
    },
    {
        "name": "author_posting_pattern",
        "query": "When does user mahas1012 typically post? Show hourly distribution.",
        "expected_tool": "aggregate OR CUSTOM (time-based grouping)",
        "priority": "MEDIUM"
    },
    {
        "name": "multiple_hashtags_and",
        "query": "Find posts that contain both #السلطان_هيثم_يزور_بيلاروس AND #عمان",
        "expected_tool": "aggregate (CONTAINS_ALL filter)",
        "priority": "LOW"
    },
    {
        "name": "hashtag_by_time",
        "query": "How many posts with #السلطان_هيثم_يزور_بيلاروس were made per day?",
        "expected_tool": "aggregate (group by date + filter)",
        "priority": "LOW"
    }
]

settings = Settings.from_env_vars()
results = []

print("=" * 80)
print("🔬 BATCH TOOL DISCOVERY")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total tests: {len(TESTS)}")
print("=" * 80 + "\n")

for i, test in enumerate(TESTS, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST {i}/{len(TESTS)}: {test['name'].upper()}")
    print(f"Priority: {test['priority']}")
    print("=" * 80)
    print(f"Query: {test['query']}")
    print(f"Expected: {test['expected_tool']}")
    print("-" * 80)

    try:
        tree = Tree(settings=settings)
        start = datetime.now()

        response, objects = tree(
            test['query'],
            collection_names=["SocialMediaPosts"]
        )

        duration = (datetime.now() - start).total_seconds()

        result = {
            "name": test['name'],
            "priority": test['priority'],
            "query": test['query'],
            "expected_tool": test['expected_tool'],
            "status": "success",
            "duration_seconds": duration,
            "response_preview": response[:200] if response else None,
            "objects_count": len(objects) if objects else 0
        }

        print(f"\n✅ SUCCESS ({duration:.2f}s)")
        print(f"Response preview: {response[:150]}...")
        print(f"Objects returned: {len(objects) if objects else 0}")

    except Exception as e:
        result = {
            "name": test['name'],
            "priority": test['priority'],
            "query": test['query'],
            "expected_tool": test['expected_tool'],
            "status": "failed",
            "error": f"{type(e).__name__}: {str(e)}"
        }

        print(f"\n❌ FAILED")
        print(f"Error: {type(e).__name__}: {str(e)}")

    results.append(result)

# Summary
print(f"\n\n{'=' * 80}")
print("📊 DISCOVERY SUMMARY")
print("=" * 80)

success_count = sum(1 for r in results if r['status'] == 'success')
failed_count = sum(1 for r in results if r['status'] == 'failed')

print(f"✅ Successful: {success_count}/{len(TESTS)}")
print(f"❌ Failed: {failed_count}/{len(TESTS)}")

print(f"\n{'-' * 80}")
print("HIGH PRIORITY TESTS:")
print("-" * 80)
for r in results:
    if r['priority'] == 'HIGH':
        status_icon = "✅" if r['status'] == 'success' else "❌"
        print(f"{status_icon} {r['name']}: {r['status']}")

# Save results
output_file = "batch_discovery_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'=' * 80}")
print(f"📁 Full results saved to: {output_file}")
print("=" * 80)
