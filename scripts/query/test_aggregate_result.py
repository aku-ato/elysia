#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test what the aggregate query actually returns
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Set up local Weaviate connection
os.environ['WEAVIATE_IS_LOCAL'] = 'True'
os.environ['LOCAL_WEAVIATE_PORT'] = '8080'
os.environ['LOCAL_WEAVIATE_GRPC_PORT'] = '50051'

from weaviate.classes.query import Filter, Metrics
from elysia.util.client import ClientManager
from elysia.util.parsing import format_aggregation_response
import json


def test_aggregate_result():
    """Test what the aggregate query returns and how it's formatted"""

    client_manager = ClientManager()
    client = client_manager.get_client()

    collection = client.collections.get('SocialMediaPosts')

    print("=" * 80)
    print("TESTING AGGREGATE QUERY RESULT")
    print("=" * 80)

    # Execute the query
    result = collection.aggregate.over_all(
        total_count=True,
        filters=Filter.all_of([
            Filter.by_property('author_id').equal('3009116383')
        ]),
        return_metrics=[
            Metrics('retweets_count').integer(count=True, mean=True)
        ]
    )

    print("\n1. RAW RESULT OBJECT")
    print("-" * 80)
    print(f"Type: {type(result)}")
    print(f"Result: {result}")

    print("\n2. RESULT ATTRIBUTES")
    print("-" * 80)
    print(f"total_count: {result.total_count}")
    print(f"properties: {result.properties}")

    if result.properties:
        for prop_name, prop_value in result.properties.items():
            print(f"\n  Property: {prop_name}")
            print(f"  Type: {type(prop_value)}")
            print(f"  Value: {prop_value}")

            # Check attributes
            if hasattr(prop_value, '__dict__'):
                for attr, val in prop_value.__dict__.items():
                    print(f"    {attr}: {val}")

    print("\n3. FORMATTED RESPONSE (format_aggregation_response)")
    print("-" * 80)
    formatted = format_aggregation_response(result)
    print(json.dumps(formatted, indent=2))

    print("\n4. CHECKING FOR NONE VALUES")
    print("-" * 80)
    if result.properties and 'retweets_count' in result.properties:
        retweets = result.properties['retweets_count']
        print(f"retweets_count mean: {retweets.mean}")
        print(f"retweets_count count: {retweets.count}")

        # Check if values are None or 0
        if retweets.mean is None:
            print("[WARNING] Mean is None!")
        if retweets.count is None:
            print("[WARNING] Count is None!")
        if retweets.mean == 0:
            print("[INFO] Mean is 0 (could be actual value or missing data)")

    print("\n5. ANALYSIS")
    print("-" * 80)

    if result.total_count == 0:
        print("[PROBLEM] No objects matched the filter!")
    elif result.total_count > 0:
        print(f"[OK] Found {result.total_count} matching objects")

        if not result.properties or 'retweets_count' not in result.properties:
            print("[PROBLEM] No retweets_count in properties!")
        else:
            retweets = result.properties['retweets_count']
            if retweets.count == 0:
                print("[PROBLEM] retweets_count.count is 0 - no values aggregated!")
                print("This likely means:")
                print("- retweets_count property is NULL/None for all matching objects")
                print("- or retweets_count doesn't exist on these objects")
            else:
                print(f"[OK] Successfully aggregated {retweets.count} retweets_count values")
                print(f"     Mean: {retweets.mean}")

    client.close()


if __name__ == "__main__":
    test_aggregate_result()
