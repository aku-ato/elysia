#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script for Weaviate aggregate query issues
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Set up local Weaviate connection
os.environ['WEAVIATE_IS_LOCAL'] = 'True'
os.environ['LOCAL_WEAVIATE_PORT'] = '8080'
os.environ['LOCAL_WEAVIATE_GRPC_PORT'] = '50051'

from weaviate.classes.query import Filter, Metrics
from elysia.util.client import ClientManager


def debug_aggregate_query():
    """Debug the aggregate query that's returning no results"""

    # Initialize Weaviate client for local instance
    client_manager = ClientManager()
    client = client_manager.get_client()

    print("=" * 80)
    print("WEAVIATE AGGREGATE QUERY DEBUG")
    print("=" * 80)

    # Get the collection - need to determine which one
    # Based on context, this seems to be a Twitter/social media collection
    collection_name = input("Enter collection name (e.g., 'ArabicTweets', 'SocialMedia'): ").strip()

    try:
        collection = client.collections.get(collection_name)
        print(f"\n[OK] Collection '{collection_name}' found")
    except Exception as e:
        print(f"\n[ERROR] Error getting collection: {e}")
        return

    # First, let's check what data exists
    print("\n" + "-" * 80)
    print("1. CHECKING COLLECTION DATA")
    print("-" * 80)

    # Check total count
    try:
        total_result = collection.aggregate.over_all(total_count=True)
        print(f"Total objects in collection: {total_result.total_count}")
    except Exception as e:
        print(f"[ERROR] Error getting total count: {e}")
        return

    # Check if author_id property exists and has data
    print("\n" + "-" * 80)
    print("2. CHECKING author_id PROPERTY")
    print("-" * 80)

    try:
        # Get some sample objects to see author_id values
        sample = collection.query.fetch_objects(limit=10)

        if sample.objects:
            print(f"\nFound {len(sample.objects)} sample objects")
            author_ids = []
            for i, obj in enumerate(sample.objects[:5]):
                author_id = obj.properties.get('author_id')
                print(f"  Object {i+1}: author_id = {author_id} (type: {type(author_id).__name__})")
                if author_id:
                    author_ids.append(author_id)

            if not author_ids:
                print("\n[WARNING] No author_id values found in sample objects!")
        else:
            print("\n[WARNING] No objects found in collection!")
    except Exception as e:
        print(f"[ERROR] Error fetching sample objects: {e}")

    # Check if the specific author_id exists
    print("\n" + "-" * 80)
    print("3. CHECKING SPECIFIC AUTHOR_ID: '3009116383'")
    print("-" * 80)

    try:
        # Try string match
        result_str = collection.query.fetch_objects(
            filters=Filter.by_property('author_id').equal('3009116383'),
            limit=5
        )
        print(f"String match ('3009116383'): {len(result_str.objects)} objects found")

        # Try integer match
        result_int = collection.query.fetch_objects(
            filters=Filter.by_property('author_id').equal(3009116383),
            limit=5
        )
        print(f"Integer match (3009116383): {len(result_int.objects)} objects found")

    except Exception as e:
        print(f"[ERROR] Error testing filters: {e}")

    # Now test the aggregate query
    print("\n" + "-" * 80)
    print("4. TESTING AGGREGATE QUERY")
    print("-" * 80)

    try:
        # Original query with string
        print("\nTesting with string filter...")
        result = collection.aggregate.over_all(
            total_count=True,
            filters=Filter.all_of([
                Filter.by_property('author_id').equal('3009116383')
            ]),
            return_metrics=[
                Metrics('retweets_count').integer(mean=True)
            ]
        )

        print(f"Total count: {result.total_count}")
        if hasattr(result, 'properties') and result.properties:
            print(f"Metrics: {result.properties}")
        else:
            print("No metrics returned")

    except Exception as e:
        print(f"[ERROR] Error with string filter: {e}")

    try:
        # Try with integer
        print("\nTesting with integer filter...")
        result = collection.aggregate.over_all(
            total_count=True,
            filters=Filter.all_of([
                Filter.by_property('author_id').equal(3009116383)
            ]),
            return_metrics=[
                Metrics('retweets_count').integer(mean=True)
            ]
        )

        print(f"Total count: {result.total_count}")
        if hasattr(result, 'properties') and result.properties:
            print(f"Metrics: {result.properties}")
        else:
            print("No metrics returned")

    except Exception as e:
        print(f"[ERROR] Error with integer filter: {e}")

    # Check if retweets_count property exists
    print("\n" + "-" * 80)
    print("5. CHECKING retweets_count PROPERTY")
    print("-" * 80)

    try:
        sample = collection.query.fetch_objects(limit=5)
        if sample.objects:
            for i, obj in enumerate(sample.objects):
                retweets = obj.properties.get('retweets_count')
                author = obj.properties.get('author_id')
                print(f"  Object {i+1}: author_id={author}, retweets_count={retweets} (type: {type(retweets).__name__ if retweets else 'None'})")
        else:
            print("No objects found")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    # Suggest fixes
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY & SUGGESTIONS")
    print("=" * 80)
    print("""
Possible issues:
1. Type mismatch: author_id stored as int but querying as string (or vice versa)
2. Property doesn't exist or has different name
3. Collection is empty or doesn't have matching data
4. retweets_count property missing or incorrect type

Try:
- Check the actual data type of author_id in your collection
- Verify the property names match exactly (case-sensitive)
- Use the correct type (string vs integer) in your filter
    """)

    client.close()


if __name__ == "__main__":
    debug_aggregate_query()
