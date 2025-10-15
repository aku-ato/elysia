#!/usr/bin/env python3
"""
Test script for HashtagAggregate tool

This script validates the hashtag aggregation tool with the ArabicTweets collection
to answer: "Who tweets most frequently with #السلطان_هيثم_يزور_بيلاروس?"

Usage:
    python scripts/test_hashtag_tool.py

Requirements:
    - Configured Weaviate connection
    - ArabicTweets collection with data
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from elysia.config import Settings
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
import dspy


async def test_hashtag_tool():
    """Test the HashtagAggregate tool with Arabic tweets"""

    print("=" * 70)
    print("HASHTAG AGGREGATION TOOL TEST")
    print("=" * 70)

    # Initialize settings and connections
    print("\n1. Initializing Elysia settings...")
    try:
        settings = Settings()
        print(f"   ✓ Settings loaded")
        print(f"   - Base model: {settings.BASE_MODEL}")
        print(f"   - Complex model: {settings.COMPLEX_MODEL}")
    except Exception as e:
        print(f"   ✗ Failed to load settings: {str(e)}")
        return False

    # Setup client manager
    print("\n2. Connecting to Weaviate...")
    try:
        client_manager = ClientManager(settings)
        if not client_manager.is_client:
            print("   ✗ Weaviate connection not available")
            print("   Make sure WCD_URL and WCD_API_KEY are set")
            return False
        print(f"   ✓ Connected to Weaviate")
    except Exception as e:
        print(f"   ✗ Connection failed: {str(e)}")
        return False

    # Setup LLMs
    print("\n3. Initializing language models...")
    try:
        base_lm = dspy.LM(
            model=f"{settings.BASE_PROVIDER}/{settings.BASE_MODEL}",
            api_key=settings.get_api_key(settings.BASE_PROVIDER),
        )
        complex_lm = dspy.LM(
            model=f"{settings.COMPLEX_PROVIDER}/{settings.COMPLEX_MODEL}",
            api_key=settings.get_api_key(settings.COMPLEX_PROVIDER),
        )
        print(f"   ✓ Language models initialized")
    except Exception as e:
        print(f"   ✗ LLM initialization failed: {str(e)}")
        return False

    # Verify collection exists
    print("\n4. Verifying ArabicTweets collection...")
    try:
        async with client_manager.connect_to_async_client() as client:
            collections = client.collections.list_all()
            collection_names = [c.name for c in collections]
            if "ArabicTweets" not in collection_names:
                print(f"   ✗ ArabicTweets collection not found")
                print(f"   Available collections: {', '.join(collection_names)}")
                return False
            print(f"   ✓ ArabicTweets collection found")
    except Exception as e:
        print(f"   ✗ Collection verification failed: {str(e)}")
        return False

    # Initialize the tool
    print("\n5. Initializing HashtagAggregate tool...")
    try:
        hashtag_tool = HashtagAggregate(logger=None)
        print(f"   ✓ Tool initialized")
        print(f"   - Name: {hashtag_tool.name}")
        print(f"   - Description: {hashtag_tool.description[:80]}...")
    except Exception as e:
        print(f"   ✗ Tool initialization failed: {str(e)}")
        return False

    # Setup tree data
    print("\n6. Preparing query...")
    hashtag = "#السلطان_هيثم_يزور_بيلاروس"
    print(f"   - Target hashtag: {hashtag}")
    print(f"   - Collection: ArabicTweets")

    tree_data = TreeData(
        user_prompt=f"Who tweets most frequently with {hashtag}?",
        collection_names=["ArabicTweets"],
        settings=settings
    )

    inputs = {
        "hashtag": hashtag,
        "collection_name": "ArabicTweets",
        "author_property": "author",
        "text_property": "text",
        "limit": 1000
    }

    # Execute the tool
    print("\n7. Executing hashtag aggregation...")
    print("-" * 70)

    results = {
        "responses": [],
        "aggregations": [],
        "errors": [],
        "texts": []
    }

    try:
        async for result in hashtag_tool(
            tree_data=tree_data,
            inputs=inputs,
            client_manager=client_manager,
            base_lm=base_lm,
            complex_lm=complex_lm
        ):
            # Categorize results
            result_type = type(result).__name__

            if hasattr(result, 'text'):
                print(f"   [{result_type}] {result.text}")
                results["responses"].append(result.text)

            elif hasattr(result, 'error_message'):
                print(f"   [ERROR] {result.error_message}")
                results["errors"].append(result.error_message)

            elif hasattr(result, 'metadata'):
                print(f"   [Aggregation] Processing results...")
                results["aggregations"].append(result)

                # Display detailed results
                metadata = result.metadata
                print(f"\n   Results Summary:")
                print(f"   ├─ Total tweets: {metadata.get('total_tweets', 0)}")
                print(f"   ├─ Unique authors: {metadata.get('unique_authors', 0)}")

                if metadata.get('top_author'):
                    author, count = metadata['top_author']
                    print(f"   └─ Top author: {author} ({count} tweets)")

                # Display top 10 authors
                if 'author_counts' in metadata:
                    print(f"\n   Top 10 Authors:")
                    author_counts = metadata['author_counts']
                    for i, (author, count) in enumerate(list(author_counts.items())[:10], 1):
                        print(f"   {i:2d}. {author}: {count} tweets")

            else:
                print(f"   [{result_type}] {result}")

    except Exception as e:
        print(f"\n   ✗ Execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("-" * 70)

    # Validate results
    print("\n8. Validating results...")
    success = True

    if results["errors"]:
        print(f"   ✗ Errors encountered: {len(results['errors'])}")
        success = False
    else:
        print(f"   ✓ No errors")

    if results["aggregations"]:
        print(f"   ✓ Aggregation completed: {len(results['aggregations'])} result(s)")

        # Check if we got the expected result
        agg = results["aggregations"][0]
        if agg.metadata.get('total_tweets', 0) > 0:
            print(f"   ✓ Found tweets with hashtag")
            top_author = agg.metadata.get('top_author')
            if top_author:
                author, count = top_author
                print(f"   ✓ Top author identified: {author} ({count} tweets)")
        else:
            print(f"   ⚠ No tweets found with hashtag (this may be expected)")
    else:
        print(f"   ✗ No aggregation results returned")
        success = False

    # Final summary
    print("\n" + "=" * 70)
    if success:
        print("TEST RESULT: ✓ SUCCESS")
        print("\nThe HashtagAggregate tool is working correctly!")

        if results["aggregations"]:
            agg = results["aggregations"][0]
            top_author = agg.metadata.get('top_author')
            if top_author:
                author, count = top_author
                print(f"\nAnswer: {author} tweets most frequently with {hashtag}")
                print(f"        ({count} tweets out of {agg.metadata.get('total_tweets')} total)")
    else:
        print("TEST RESULT: ✗ FAILED")
        print("\nThe tool encountered issues. Check the logs above for details.")

    print("=" * 70)

    return success


async def main():
    """Main entry point"""
    try:
        success = await test_hashtag_tool()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
