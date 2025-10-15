"""
Hashtag Aggregation Example for Elysia

This example demonstrates how to use the HashtagAggregate tool to find which author
tweets most frequently with a specific hashtag.

Usage:
    python examples/hashtag_aggregation_example.py

Requirements:
    - Weaviate connection configured
    - A collection with tweet data (with 'author' and 'text' properties)
"""

import asyncio
from elysia import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate


async def example_basic_usage():
    """
    Basic example: Find top author for a specific hashtag
    """
    print("=" * 60)
    print("Example 1: Basic Hashtag Aggregation")
    print("=" * 60)

    # Initialize tree with the custom tool
    tree = Tree()
    hashtag_tool = HashtagAggregate()
    tree.tools.append(hashtag_tool)

    # Query for tweets with specific hashtag
    response, objects = tree(
        "Who tweets most frequently with the hashtag #السلطان_هيثم_يزور_بيلاروس?",
        collection_names=["ArabicTweets"]
    )

    print("\nResponse:", response)
    if objects:
        print("\nTop Authors:")
        for obj in objects:
            if 'collections' in obj:
                for collection_data in obj['collections']:
                    for collection_name, data in collection_data.items():
                        if 'authors' in data:
                            for author_data in data['authors'][:5]:  # Top 5
                                print(f"  - {author_data['author']}: {author_data['count']} tweets")


async def example_with_custom_properties():
    """
    Advanced example: Custom property names
    """
    print("\n" + "=" * 60)
    print("Example 2: Custom Property Names")
    print("=" * 60)

    tree = Tree()
    hashtag_tool = HashtagAggregate()
    tree.tools.append(hashtag_tool)

    # If your collection uses different property names
    response, objects = tree(
        "Count tweets by user for hashtag #example",
        collection_names=["CustomTweets"],
        # These would be passed through if the tool detects them:
        # author_property="user_name",
        # text_property="content"
    )

    print("\nResponse:", response)


async def example_programmatic_usage():
    """
    Direct programmatic usage without natural language
    """
    print("\n" + "=" * 60)
    print("Example 3: Direct Programmatic Usage")
    print("=" * 60)

    from elysia.config import Settings
    from elysia.tree.objects import TreeData
    from elysia.util.client import ClientManager
    import dspy

    # Setup
    settings = Settings()
    client_manager = ClientManager(settings)
    tree_data = TreeData(
        user_prompt="Direct hashtag query",
        collection_names=["ArabicTweets"],
        settings=settings
    )

    # Initialize tool and call directly
    hashtag_tool = HashtagAggregate()

    base_lm = dspy.LM(
        model=f"{settings.BASE_PROVIDER}/{settings.BASE_MODEL}",
        api_key=settings.get_api_key(settings.BASE_PROVIDER),
    )
    complex_lm = dspy.LM(
        model=f"{settings.COMPLEX_PROVIDER}/{settings.COMPLEX_MODEL}",
        api_key=settings.get_api_key(settings.COMPLEX_PROVIDER),
    )

    inputs = {
        "hashtag": "#السلطان_هيثم_يزور_بيلاروس",
        "collection_name": "ArabicTweets",
        "author_property": "author",
        "text_property": "text",
        "limit": 1000
    }

    print(f"\nQuerying for hashtag: {inputs['hashtag']}")
    print(f"Collection: {inputs['collection_name']}")
    print(f"Limit: {inputs['limit']}\n")

    async for result in hashtag_tool(
        tree_data=tree_data,
        inputs=inputs,
        client_manager=client_manager,
        base_lm=base_lm,
        complex_lm=complex_lm
    ):
        if hasattr(result, 'text'):
            print(f"Status: {result.text}")
        elif hasattr(result, 'error_message'):
            print(f"Error: {result.error_message}")
        elif hasattr(result, 'metadata'):
            print(f"\nResults:")
            print(f"  Total tweets: {result.metadata.get('total_tweets', 0)}")
            print(f"  Unique authors: {result.metadata.get('unique_authors', 0)}")
            if result.metadata.get('top_author'):
                author, count = result.metadata['top_author']
                print(f"  Top author: {author} ({count} tweets)")


async def example_comparison_with_standard_aggregate():
    """
    Compare results with standard aggregate tool
    """
    print("\n" + "=" * 60)
    print("Example 4: Comparison with Standard Aggregate")
    print("=" * 60)

    tree = Tree()

    # Standard aggregate (no hashtag filter)
    print("\n1. Standard aggregate (all tweets by author):")
    response1, objects1 = tree(
        "Count total tweets by author in ArabicTweets",
        collection_names=["ArabicTweets"]
    )
    print("Response:", response1)

    # Hashtag-filtered aggregate
    hashtag_tool = HashtagAggregate()
    tree.tools.append(hashtag_tool)

    print("\n2. Hashtag-filtered aggregate (specific hashtag):")
    response2, objects2 = tree(
        "Count tweets by author with hashtag #السلطان_هيثم_يزور_بيلاروس",
        collection_names=["ArabicTweets"]
    )
    print("Response:", response2)

    print("\nNotice the difference:")
    print("- Standard aggregate counts ALL tweets")
    print("- Hashtag aggregate counts ONLY tweets with specific hashtag")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("ELYSIA HASHTAG AGGREGATION EXAMPLES")
    print("=" * 60 + "\n")

    try:
        # Run basic example
        await example_basic_usage()

        # Uncomment to run additional examples:
        # await example_with_custom_properties()
        # await example_programmatic_usage()
        # await example_comparison_with_standard_aggregate()

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("\nMake sure you have:")
        print("1. Configured Weaviate connection (WCD_URL, WCD_API_KEY)")
        print("2. A collection with tweet data")
        print("3. LLM API keys configured")


if __name__ == "__main__":
    asyncio.run(main())
