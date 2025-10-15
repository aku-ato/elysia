#!/usr/bin/env python3
"""
Simulate exactly what the frontend receives after to_frontend() serialization
"""
import json
from elysia.util.parsing import format_dict_to_serialisable

# Simulate the exact structure from HashtagAggregate
author_property = "author_username"
collection_name = "SocialMediaPosts"

sorted_authors = [
    ("mahas1012", 32),
    ("kathiri19ali1", 28),
    ("Wahabalqumi", 26),
]
tweets_count = 735

# Step 1: Our aggregation_results
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

# Step 2: Objects structure
objects = [
    {
        "num_items": tweets_count,
        "collections": [
            {collection_name: aggregation_results}
        ],
    }
]

print("=" * 80)
print("BEFORE format_dict_to_serialisable")
print("=" * 80)
print(json.dumps(objects, indent=2, ensure_ascii=False))

# Step 3: Apply format_dict_to_serialisable (what to_json does)
for obj in objects:
    format_dict_to_serialisable(obj)

print("\n" + "=" * 80)
print("AFTER format_dict_to_serialisable")
print("=" * 80)
print(json.dumps(objects, indent=2, ensure_ascii=False))

# Step 4: Simulate frontend access pattern
print("\n" + "=" * 80)
print("FRONTEND ACCESS SIMULATION")
print("=" * 80)

# Frontend receives: payload.objects[0].collections[0][collectionName]
collection_data = objects[0]["collections"][0][collection_name]
print(f"\nCollection data: {json.dumps(collection_data, indent=2, ensure_ascii=False)}")

# Frontend iterates over fields
for field_name in collection_data:
    if field_name != "ELYSIA_NUM_ITEMS":
        field = collection_data[field_name]
        print(f"\nField '{field_name}':")
        print(f"  field = {field}")
        print(f"  type(field) = {type(field)}")
        print(f"  'values' in field = {('values' in field)}")

        if 'values' in field:
            values = field['values']
            print(f"  type(field['values']) = {type(values)}")
            print(f"  field['values'] = {values}")

            # This is line 92 in AggregationDisplay.tsx
            try:
                print("\n  Testing: for (const aggValue of field.values)")
                for aggValue in values:
                    print(f"    ✅ aggValue = {aggValue}")
                    break
            except TypeError as e:
                print(f"    ❌ ERROR: {e}")
        else:
            print("  ❌ NO 'values' KEY IN FIELD!")
            print(f"  Available keys: {list(field.keys()) if isinstance(field, dict) else 'N/A'}")

print("\n" + "=" * 80)
print("DATA TYPE VERIFICATION")
print("=" * 80)
print(f"Is values a list? {isinstance(field['values'], list)}")
print(f"Is values iterable? {hasattr(field['values'], '__iter__')}")
print(f"Values length: {len(field['values'])}")
