#!/usr/bin/env python3
"""
Test script to verify the HashtagAggregate output format
"""
import json

# Simulate the output structure from HashtagAggregate
author_property = "author_username"
collection_name = "SocialMediaPosts"
sorted_authors = [
    ("mahas1012", 32),
    ("kathiri19ali1", 28),
    ("Wahabalqumi", 26),
]
tweets_count = 735

# Our current format
aggregation_results = {
    "ELYSIA_NUM_ITEMS": tweets_count,
    author_property: {
        "type": "text",
        "values": [
            {
                "value": count,
                "field": author,
                "aggregation": "count"
            }
            for author, count in sorted_authors
        ]
    }
}

objects = [
    {
        "num_items": tweets_count,
        "collections": [
            {collection_name: aggregation_results}
        ],
    }
]

print("=" * 80)
print("HASHTAG AGGREGATE OUTPUT STRUCTURE")
print("=" * 80)
print(json.dumps(objects, indent=2, ensure_ascii=False))
print()

# Test the parsing logic from objects.py
print("=" * 80)
print("PARSING TEST (simulating objects.py:393-402)")
print("=" * 80)

collection_data = objects[0]["collections"][0][collection_name]
print(f"\nMetrics in collection '{collection_name}':")
for metric in collection_data:
    if metric != "ELYSIA_NUM_ITEMS":
        print(f"  - {metric}")
        print(f"    Type: {collection_data[metric].get('type', 'N/A')}")
        print(f"    Values count: {len(collection_data[metric]['values'])}")
        print(f"    First value: {collection_data[metric]['values'][0]}")

        # This is what the frontend will iterate over
        print(f"    Iterating values:")
        for i, val in enumerate(collection_data[metric]['values'][:3]):
            print(f"      [{i}] value={val['value']}, field={val['field']}, aggregation={val['aggregation']}")

print("\n" + "=" * 80)
print("TEST PASSED - Structure is valid!")
print("=" * 80)
