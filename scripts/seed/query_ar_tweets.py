#!/usr/bin/env python3
"""
Query Arabic tweets using semantic search.

This script performs semantic search on the SocialMediaPosts collection
using the self-hosted multilingual E5 model (fully offline).
"""

import sys
import argparse
import requests
from typing import List, Dict, Any, Optional

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

# API Configuration
BACKEND_URL = "http://localhost:8000"
WEAVIATE_URL = "http://localhost:8080"
USER_ID = "default"
COLLECTION_NAME = "SocialMediaPosts"


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"{CYAN}{BOLD}{title}{RESET}")
    print("=" * 70 + "\n")


def print_step(msg: str):
    """Print step message in blue."""
    print(f"{BLUE}▶ {msg}{RESET}")


def print_success(msg: str):
    """Print success message in green."""
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠ {msg}{RESET}")


def print_info(msg: str):
    """Print info message in cyan."""
    print(f"{CYAN}ℹ {msg}{RESET}")


def semantic_search(
    query: str,
    limit: int = 5,
    certainty: float = 0.7,
    language: Optional[str] = None,
    topic: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform semantic search using Weaviate GraphQL API.

    Args:
        query: Search query (can be Arabic or English)
        limit: Maximum number of results
        certainty: Minimum certainty threshold (0.0-1.0)
        language: Optional language filter (e.g., 'ar', 'en')
        topic: Optional topic filter

    Returns:
        List of matching posts with metadata
    """
    # Build GraphQL query with optional filters
    where_clause = ""
    if language or topic:
        conditions = []
        if language:
            conditions.append(f'{{path: ["language"], operator: Equal, valueText: "{language}"}}')
        if topic:
            conditions.append(f'{{path: ["topic"], operator: Equal, valueText: "{topic}"}}')

        if len(conditions) == 1:
            where_clause = f'where: {{{conditions[0]}}}'
        else:
            where_clause = f'where: {{operator: And, operands: [{", ".join(conditions)}]}}'

    graphql_query = f"""
    {{
      Get {{
        SocialMediaPosts(
          nearText: {{
            concepts: ["{query}"]
            certainty: {certainty}
          }}
          {where_clause}
          limit: {limit}
        ) {{
          post_id
          content
          topic
          language
          timestamp
          author_id
          author_username
          author_name
          sentiment
          hashtags
          post_type
          views_count
          likes_count
          retweets_count
          replies_count
          is_reply
          reply_to_post_id
          _additional {{
            certainty
            distance
          }}
        }}
      }}
    }}
    """

    try:
        response = requests.post(
            f"{WEAVIATE_URL}/v1/graphql",
            json={"query": graphql_query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                print_error(f"GraphQL errors: {data['errors']}")
                return []

            posts = data.get("data", {}).get("Get", {}).get("SocialMediaPosts", [])
            return posts
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return []

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Weaviate")
        print_info("Make sure Weaviate is running:")
        print_info("  cd /home/ppiccolo/projects/elysia/deploy")
        print_info("  docker-compose up -d weaviate")
        return []
    except requests.exceptions.Timeout:
        print_error("Request timeout after 30 seconds")
        return []
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []


def print_result(post: Dict[str, Any], index: int):
    """Print a single search result in a nice format."""
    additional = post.get("_additional", {})
    certainty = additional.get("certainty", 0.0)
    distance = additional.get("distance", 0.0)

    print(f"\n{MAGENTA}{BOLD}Result #{index}{RESET}")
    print(f"{CYAN}Relevance: {certainty:.3f} (distance: {distance:.4f}){RESET}")
    print("-" * 70)

    # Basic info
    print(f"{BLUE}Author:{RESET} {post.get('author_name', 'N/A')} (@{post.get('author_username', 'N/A')})")
    print(f"{BLUE}Language:{RESET} {post.get('language', 'N/A').upper()}")
    print(f"{BLUE}Topic:{RESET} {post.get('topic', 'N/A')}")
    print(f"{BLUE}Sentiment:{RESET} {post.get('sentiment', 'N/A')}")
    print(f"{BLUE}Type:{RESET} {post.get('post_type', 'N/A')}")

    # Content
    content = post.get("content", "")
    print(f"\n{BLUE}Content:{RESET}")
    print(f"  {content}")

    # Hashtags
    hashtags = post.get("hashtags", [])
    if hashtags:
        print(f"\n{BLUE}Hashtags:{RESET} {' '.join(hashtags)}")

    # Engagement metrics
    views = post.get("views_count", 0)
    likes = post.get("likes_count", 0)
    retweets = post.get("retweets_count", 0)
    replies = post.get("replies_count", 0)

    print(f"\n{BLUE}Engagement:{RESET}")
    print(f"  👁️  Views: {views:,}")
    print(f"  ❤️  Likes: {likes:,}")
    print(f"  🔄 Retweets: {retweets:,}")
    print(f"  💬 Replies: {replies:,}")

    # Reply info
    if post.get("is_reply"):
        print(f"\n{BLUE}Reply to:{RESET} {post.get('reply_to_post_id', 'N/A')}")

    print("-" * 70)


def get_collection_stats() -> Dict[str, Any]:
    """Get collection statistics."""
    graphql_query = """
    {
      Aggregate {
        SocialMediaPosts {
          meta {
            count
          }
          language {
            count
            topOccurrences(limit: 10) {
              value
              occurs
            }
          }
          topic {
            topOccurrences(limit: 5) {
              value
              occurs
            }
          }
          sentiment {
            topOccurrences(limit: 3) {
              value
              occurs
            }
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            f"{WEAVIATE_URL}/v1/graphql",
            json={"query": graphql_query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("Aggregate", {}).get("SocialMediaPosts", [{}])[0]
        else:
            return {}
    except Exception:
        return {}


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Query Arabic tweets using semantic search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for posts about the Sultan
  python query_ar_tweets.py "السلطان"

  # Search with more results
  python query_ar_tweets.py "زيارة بيلاروس" --limit 10

  # Filter by language
  python query_ar_tweets.py "visit" --language ar

  # Filter by topic
  python query_ar_tweets.py "السلطان" --topic "Belarus Visit"

  # Show collection statistics
  python query_ar_tweets.py --stats
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (Arabic or English)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results (default: 5)"
    )
    parser.add_argument(
        "--certainty",
        type=float,
        default=0.7,
        help="Minimum certainty threshold 0.0-1.0 (default: 0.7)"
    )
    parser.add_argument(
        "--language",
        choices=["ar", "en", "it"],
        help="Filter by language code"
    )
    parser.add_argument(
        "--topic",
        help="Filter by topic"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show collection statistics instead of searching"
    )

    args = parser.parse_args()

    # Print header
    print_header("🔍 ARABIC TWEETS SEMANTIC SEARCH")

    print_info(f"Weaviate URL: {WEAVIATE_URL}")
    print_info(f"Collection: {COLLECTION_NAME}")
    print_info(f"User ID: {USER_ID}")

    # Show stats if requested
    if args.stats:
        print_step("Fetching collection statistics...")
        stats = get_collection_stats()

        if stats:
            meta = stats.get("meta", {})
            total = meta.get("count", 0)

            print_header("📊 COLLECTION STATISTICS")

            print(f"{BLUE}Total Posts:{RESET} {total:,}")

            # Languages
            language_data = stats.get("language", {})
            if language_data and "topOccurrences" in language_data:
                print(f"\n{BLUE}Languages:{RESET}")
                for item in language_data.get("topOccurrences", []):
                    lang = item.get("value", "N/A")
                    count = item.get("occurs", 0)
                    print(f"  {lang}: {count:,}")

            # Topics
            topic_data = stats.get("topic", {})
            if topic_data and "topOccurrences" in topic_data:
                print(f"\n{BLUE}Topics:{RESET}")
                for item in topic_data.get("topOccurrences", []):
                    topic = item.get("value", "N/A")
                    count = item.get("occurs", 0)
                    print(f"  {topic}: {count:,}")

            # Sentiments
            sentiment_data = stats.get("sentiment", {})
            if sentiment_data and "topOccurrences" in sentiment_data:
                print(f"\n{BLUE}Sentiment Distribution:{RESET}")
                sentiment_icons = {
                    "positive": "😊",
                    "negative": "😞",
                    "neutral": "😐"
                }
                for item in sentiment_data.get("topOccurrences", []):
                    sent = item.get("value", "N/A")
                    count = item.get("occurs", 0)
                    icon = sentiment_icons.get(sent, "")
                    print(f"  {icon} {sent}: {count:,}")
        else:
            print_error("Failed to fetch statistics")

        return 0

    # Require query if not showing stats
    if not args.query:
        parser.print_help()
        return 1

    # Build filter description
    filters = []
    if args.language:
        filters.append(f"language={args.language}")
    if args.topic:
        filters.append(f"topic={args.topic}")
    filter_desc = f" (filters: {', '.join(filters)})" if filters else ""

    print_step(f"Searching for: '{args.query}'{filter_desc}")
    print_info(f"Limit: {args.limit} results")
    print_info(f"Minimum certainty: {args.certainty}")

    # Perform search
    results = semantic_search(
        query=args.query,
        limit=args.limit,
        certainty=args.certainty,
        language=args.language,
        topic=args.topic
    )

    if not results:
        print_warning("No results found")
        print_info("Try:")
        print_info("  - Lowering the certainty threshold (--certainty 0.5)")
        print_info("  - Using different search terms")
        print_info("  - Removing filters")
        return 0

    print_success(f"Found {len(results)} results")

    # Print results
    print_header("📋 SEARCH RESULTS")

    for i, post in enumerate(results, 1):
        print_result(post, i)

    # Summary
    print_header("✅ SEARCH COMPLETE")
    print_info(f"Query: '{args.query}'")
    print_info(f"Results: {len(results)}")

    if results:
        avg_certainty = sum(r.get("_additional", {}).get("certainty", 0) for r in results) / len(results)
        print_info(f"Average certainty: {avg_certainty:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
