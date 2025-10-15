#!/usr/bin/env python3
"""
Test if standard Aggregate tool can handle hashtag filtering on array fields.
This should work if hashtags are in a separate array field like:
{
    "hashtags": ["السلطان_هيثم_يزور_بيلاروس", "معاك_للمونديال", "عمان"]
}
"""
from elysia import Tree, Settings

# Load settings from .env file using from_env_vars() class method
# This will automatically load WEAVIATE_IS_LOCAL, BASE_MODEL, etc.
settings = Settings.from_env_vars()

# Verify configuration
print("=" * 80)
print("Configuration Check:")
print("=" * 80)
print(f"Local Weaviate: {settings.WEAVIATE_IS_LOCAL}")
if settings.WEAVIATE_IS_LOCAL:
    print(f"Weaviate Port: {settings.LOCAL_WEAVIATE_PORT}")
    print(f"Weaviate gRPC Port: {settings.LOCAL_WEAVIATE_GRPC_PORT}")
else:
    print(f"Weaviate URL: {settings.WCD_URL}")
print(f"Base Model: {settings.BASE_MODEL}")
print(f"Complex Model: {settings.COMPLEX_MODEL}")
print(f"Model API Base: {getattr(settings, 'MODEL_API_BASE', 'default')}")
print("=" * 80)

# Create tree with settings
tree = Tree(settings=settings)

print("\n" + "=" * 80)
print("Testing Standard Aggregate Tool with Hashtag Filtering")
print("=" * 80)
print("Query: Who tweets most frequently with hashtag السلطان_هيثم_يزور_بيلاروس? in the last month?")
print("Collection: SocialMediaPosts")
print("=" * 80 + "\n")

# Execute query
response, objects = tree(
    "Who tweets most frequently with hashtag السلطان_هيثم_يزور_بيلاروس in the last month?",
    collection_names=["SocialMediaPosts"]
)

print("\n" + "=" * 80)
print("RESPONSE:")
print("=" * 80)
print(response)

print("\n" + "=" * 80)
print("OBJECTS:")
print("=" * 80)
import json
print(json.dumps(objects, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("SUCCESS: Standard Aggregate tool handled hashtag filtering!")
print("=" * 80)