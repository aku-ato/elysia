#!/usr/bin/env python3
"""
Convenience script to query for top authors by hashtag.
Automatically registers the HashtagAggregate tool.

Usage:
    python scripts/query_hashtag_author.py "#السلطان_هيثم_يزور_بيلاروس"
    python scripts/query_hashtag_author.py "#example" --collection Tweets
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from elysia import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate


def create_tree_with_hashtag_tool():
    """
    Create a Tree instance with the HashtagAggregate tool registered.

    Returns:
        Tree: Configured tree with hashtag tool available
    """
    # Create tree with default configuration
    tree = Tree()

    # Register the HashtagAggregate tool in the "search" branch
    tree.add_tool(
        tool=HashtagAggregate,
        branch_id="search"
    )

    print("✅ Tree initialized with HashtagAggregate tool")
    print(f"   Available tools: {list(tree.tools.keys())}")

    return tree


def query_hashtag_author(hashtag: str, collection: str = "ArabicTweets"):
    """
    Query for the top author by hashtag.

    Args:
        hashtag: The hashtag to search for (with or without #)
        collection: The Weaviate collection name

    Returns:
        tuple: (response, objects) from the tree query
    """
    # Ensure hashtag has # prefix
    if not hashtag.startswith('#'):
        hashtag = f'#{hashtag}'

    print(f"\n📊 Querying for top authors with hashtag: {hashtag}")
    print(f"   Collection: {collection}\n")

    # Create tree with hashtag tool
    tree = create_tree_with_hashtag_tool()

    # Execute query
    response, objects = tree(
        f"Who tweets most frequently with the hashtag {hashtag}?",
        collection_names=[collection]
    )

    return response, objects


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/query_hashtag_author.py <hashtag> [collection]")
        print("\nExamples:")
        print('  python scripts/query_hashtag_author.py "#السلطان_هيثم_يزور_بيلاروس"')
        print('  python scripts/query_hashtag_author.py "#example" ArabicTweets')
        sys.exit(1)

    hashtag = sys.argv[1]
    collection = sys.argv[2] if len(sys.argv) > 2 else "ArabicTweets"

    try:
        response, objects = query_hashtag_author(hashtag, collection)

        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"\n{response}\n")

        if objects:
            print("\nDetailed Results:")
            for obj in objects:
                if 'collections' in obj:
                    for collection_data in obj['collections']:
                        for coll_name, data in collection_data.items():
                            if 'authors' in data:
                                print(f"\nTop 10 authors in {coll_name}:")
                                for i, author_data in enumerate(data['authors'][:10], 1):
                                    print(f"  {i:2d}. {author_data['author']}: {author_data['count']} tweets")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
