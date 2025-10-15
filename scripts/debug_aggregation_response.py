#!/usr/bin/env python3
"""
Debug script to show exactly what the HashtagAggregate tool sends
"""
import json

# Simulate exactly what HashtagAggregate sends
author_property = "author_username"
collection_name = "SocialMediaPosts"
hashtag = "#السلطان_هيثم_يزور_بيلاروس"

sorted_authors = [
    ("mahas1012", 32),
    ("kathiri19ali1", 28),
    ("Wahabalqumi", 26),
]
tweets_count = 735
author_counts = {"mahas1012": 32, "kathiri19ali1": 28}

# This is EXACTLY what we create in hashtag_aggregate.py
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

metadata = {
    "collection_name": collection_name,
    "hashtag": hashtag,
    "total_items": tweets_count,
    "unique_authors": len(author_counts),
    "top_author": sorted_authors[0] if sorted_authors else None,
    "author_counts": dict(sorted_authors),
}

# Full Aggregation object structure
aggregation_payload = {
    "objects": objects,
    "metadata": metadata
}

print("=" * 80)
print("COMPLETE AGGREGATION PAYLOAD")
print("=" * 80)
print(json.dumps(aggregation_payload, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("CHECKING SPECIFIC PATHS THE FRONTEND WILL ACCESS")
print("=" * 80)

# Simulate frontend access pattern
collection_data = objects[0]["collections"][0][collection_name]
print(f"\n1. Collection data keys: {list(collection_data.keys())}")

for key in collection_data:
    if key != "ELYSIA_NUM_ITEMS":
        field = collection_data[key]
        print(f"\n2. Field '{key}':")
        print(f"   - Has 'type': {('type' in field)}")
        print(f"   - Has 'values': {('values' in field)}")
        if 'values' in field:
            print(f"   - values is list: {isinstance(field['values'], list)}")
            print(f"   - values is iterable: {hasattr(field['values'], '__iter__')}")
            print(f"   - values length: {len(field['values'])}")
            print(f"   - First value: {field['values'][0]}")

            # This is what line 92 of AggregationDisplay.tsx tries to do
            try:
                for aggValue in field['values']:
                    print(f"   - Iteration works! aggValue = {aggValue}")
                    break  # Just test first iteration
                print("   ✅ Iteration successful!")
            except TypeError as e:
                print(f"   ❌ Iteration failed: {e}")

print("\n" + "=" * 80)
print("TYPE CHECKING")
print("=" * 80)
print(f"collection_data type: {type(collection_data)}")
print(f"field type: {type(field)}")
print(f"field['values'] type: {type(field['values'])}")
print(f"field['values'] value: {field['values']}")
