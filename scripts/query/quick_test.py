#!/usr/bin/env python3
"""
Quick test script for exploring single queries.
Usage: Edit the QUERY variable below and run.
"""
from elysia import Tree, Settings
import json

# Load settings
settings = Settings.from_env_vars()
tree = Tree(settings=settings)

# ========================================
# EDIT THIS QUERY TO TEST
# ========================================
QUERY = "What other hashtags appear most frequently with #السلطان_هيثم_يزور_بيلاروس?"

COLLECTION = "SocialMediaPosts"
# ========================================

print("=" * 80)
print("🧪 Quick Query Test")
print("=" * 80)
print(f"Query: {QUERY}")
print(f"Collection: {COLLECTION}")
print("=" * 80 + "\n")

try:
    response, objects = tree(QUERY, collection_names=[COLLECTION])

    print("\n" + "=" * 80)
    print("✅ RESPONSE:")
    print("=" * 80)
    print(response)

    print("\n" + "=" * 80)
    print("📦 OBJECTS:")
    print("=" * 80)
    print(json.dumps(objects, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print(f"✅ SUCCESS - {len(objects)} objects returned")
    print("=" * 80)

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR:")
    print("=" * 80)
    print(f"{type(e).__name__}: {str(e)}")
    print("=" * 80)
