#!/usr/bin/env python3
"""
Load Arabic Twitter data from Elasticsearch JSON export into Weaviate.

This script:
1. Loads tweets from Elasticsearch JSON export (task_6552.json, task_6553.json, etc.)
2. Parses and extracts relevant fields from nested _source structure
3. Normalizes Arabic text for better semantic search
4. Maps sentiment from emotions array
5. Extracts topics from hashtags and content
6. Inserts tweets into Weaviate SocialMediaPosts collection in batches

Usage:
    # Dry-run to validate data
    python load_ar_tweets.py --file data/task_6552.json --dry-run --show-sample
    
    # Load first 100 tweets (test)
    python load_ar_tweets.py --file data/task_6552.json --limit 100
    
    # Load all tweets
    python load_ar_tweets.py --file data/task_6552.json
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Arabic normalization utility
try:
    from elysia.util.arabic import normalize_arabic_text, is_arabic_text
except ImportError:
    print("Warning: Could not import arabic utilities, using fallback")
    import re
    def normalize_arabic_text(text: str) -> str:
        """Fallback Arabic normalization."""
        if not text:
            return text
        arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
        text = arabic_diacritics.sub('', text)
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'[ؤئ]', 'ء', text)
        text = text.replace('\u0640', '')
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def is_arabic_text(text: str) -> bool:
        """Fallback Arabic detection."""
        return any('\u0600' <= c <= '\u06FF' for c in text) if text else False

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("USER_ID", "default")
COLLECTION_NAME = "SocialMediaPosts"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


def print_step(message: str):
    """Print step message in blue."""
    print(f"{BLUE}▶ {message}{RESET}")


def print_success(message: str):
    """Print success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{RED}✗ {message}{RESET}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠ {message}{RESET}")


def print_info(message: str):
    """Print info message in cyan."""
    print(f"{CYAN}ℹ {message}{RESET}")


def safe_get(data: Dict, path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value using dot notation.
    
    Args:
        data: Dictionary to query
        path: Dot-separated path (e.g., "searchable.text.text_ar")
        default: Default value if path not found
    
    Returns:
        Value at path or default
        
    Examples:
        >>> data = {"searchable": {"text": {"text_ar": "مرحبا"}}}
        >>> safe_get(data, "searchable.text.text_ar")
        'مرحبا'
        >>> safe_get(data, "missing.path", "default")
        'default'
    """
    keys = path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        elif isinstance(value, list) and key.isdigit():
            idx = int(key)
            value = value[idx] if idx < len(value) else default
        else:
            return default
            
        if value is None:
            return default
    
    return value


def extract_topic_from_text(text: str, hashtags: List[str]) -> str:
    """
    Extract topic from text and hashtags.
    
    Uses simple keyword matching. Can be improved with NLP/LLM.
    
    Args:
        text: Tweet text content
        hashtags: List of hashtags in tweet
    
    Returns:
        Extracted topic string
    """
    text_lower = text.lower()
    
    # Check hashtags first (more reliable)
    if any(h for h in hashtags if 'بيلاروس' in h or 'belarus' in h.lower()):
        return "Belarus Visit"
    elif any(h for h in hashtags if 'سلطان' in h or 'هيثم' in h):
        return "Sultan Haitham"
    
    # Check text content
    if any(word in text_lower for word in ['الذكاء', 'ai', 'intelligence', 'ذكاء']):
        return "Artificial Intelligence"
    elif any(word in text_lower for word in ['صحة', 'طب', 'health', 'medicine', 'medical']):
        return "Healthcare"
    elif any(word in text_lower for word in ['تقنية', 'تكنولوجيا', 'tech', 'technology']):
        return "Technology"
    elif any(word in text_lower for word in ['سياسة', 'politics', 'political']):
        return "Politics"
    elif any(word in text_lower for word in ['اقتصاد', 'economy', 'economic']):
        return "Economics"
    else:
        return "General"


def map_sentiment(emotions: List[str]) -> str:
    """
    Map emotions array to simple sentiment classification.
    
    Args:
        emotions: List of emotions (e.g., ["positivism", "neutrality"])
    
    Returns:
        Sentiment: "positive", "negative", or "neutral"
    """
    if not emotions:
        return "neutral"
    
    # First emotion is usually the dominant one
    emotion = emotions[0].lower() if emotions else ""
    
    if emotion in ['positivism', 'positive', 'joy', 'happiness', 'optimism']:
        return "positive"
    elif emotion in ['negativism', 'negative', 'anger', 'sadness', 'fear']:
        return "negative"
    else:
        return "neutral"


def extract_post_from_es_doc(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and transform Elasticsearch document to Weaviate post format.
    
    Args:
        doc: Elasticsearch document with _source, _id, _type, etc.
        
    Returns:
        Dictionary ready for Weaviate insertion or None if invalid
    """
    try:
        source = doc.get("_source", {})
        searchable = source.get("searchable", {})
        
        # Extract text (prefer text_ar from searchable)
        text_raw = safe_get(searchable, "text.text_ar", "")
        if not text_raw:
            text_raw = safe_get(source, "original.text.content", "")
        
        if not text_raw:
            return None
        
        # Extract author info from searchable.actors.sender[0]
        sender = safe_get(searchable, "actors.sender.0", {})
        if not sender:
            # Fallback: try parsing from original.document JSON string
            doc_str = safe_get(source, "original.document", "")
            if isinstance(doc_str, str) and doc_str:
                try:
                    parsed_doc = json.loads(doc_str)
                    sender_list = safe_get(parsed_doc, "post.postInfo.sender", [])
                    sender = sender_list[0] if sender_list else {}
                except:
                    sender = {}
        
        # Extract hashtags (clean format without #)
        hashtags_raw = safe_get(searchable, "hashtags", [])
        hashtags = []
        for h in hashtags_raw:
            if isinstance(h, str):
                h_clean = h.replace('#', '').strip()
                if h_clean:
                    hashtags.append(h_clean)
        
        # Extract engagement metrics
        views_count = source.get("views_count", 0) or 0
        likes_count = source.get("favorites_count", 0) or 0
        retweets_count = source.get("retweets_count", 0) or 0
        replies_count = source.get("replies_count", 0) or 0
        
        # Check if it's a reply
        parent_id = source.get("parent_id", "") or ""
        doc_type = doc.get("_type", "")
        is_reply = bool(parent_id) or "reply" in doc_type.lower()
        
        # Extract timestamp
        timestamp = safe_get(searchable, "timestamp", "")
        if not timestamp:
            timestamp = source.get("dt_created", datetime.now().isoformat() + "Z")
        
        # Normalize Arabic text for embedding
        text_normalized = normalize_arabic_text(text_raw)
        
        # Detect language (default to ar for this dataset)
        language = "ar" if is_arabic_text(text_normalized) else "en"
        
        # Extract URLs
        urls = safe_get(searchable, "urls", []) or []
        
        # Build the post
        post = {
            "post_id": doc.get("_id", ""),
            "content": text_normalized,
            "language": language,
            "timestamp": timestamp,
            "author_id": sender.get("user_id", "") or sender.get("id", "") or "unknown",
            "author_username": sender.get("username", "") or "",
            "author_name": sender.get("name", "") or "",
            "topic": extract_topic_from_text(text_raw, hashtags),
            "sentiment": map_sentiment(safe_get(searchable, "emotions", [])),
            "hashtags": hashtags,
            "event_id": str(source.get("task_id", "6552")),
            "location": sender.get("address", "") or "",
            "urls": urls if isinstance(urls, list) else [],
            "post_type": doc_type.replace("twitter_", "").replace("_v1", ""),
            "views_count": int(views_count),
            "likes_count": int(likes_count),
            "retweets_count": int(retweets_count),
            "replies_count": int(replies_count),
            "reply_to_post_id": parent_id,
            "is_reply": is_reply,
        }

        # Validate post before returning
        is_valid, error_msg = validate_post(post)
        if not is_valid:
            print_warning(f"Invalid post {post.get('post_id', 'unknown')}: {error_msg}")
            return None

        return post
        
    except Exception as e:
        print_error(f"Error extracting post from doc {doc.get('_id', 'unknown')}: {e}")
        return None


def validate_post(post: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate post data before insertion.

    Checks for required fields, data integrity, and reasonable limits.

    Args:
        post: Post dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    # Required fields check
    if not post.get("post_id"):
        return False, "Missing post_id"

    if not post.get("content"):
        return False, "Missing content"

    # Content length validation (Weaviate limits + embedding model limits)
    content = post.get("content", "")
    if len(content) > 10000:
        return False, f"Content too long: {len(content)} chars (max 10000)"

    if len(content) < 1:
        return False, "Content is empty"

    # Timestamp validation
    timestamp = post.get("timestamp", "")
    try:
        datetime.fromisoformat(timestamp.replace("Z", ""))
    except (ValueError, AttributeError, TypeError):
        return False, f"Invalid timestamp format: {timestamp}"

    # URL validation (basic - check count)
    urls = post.get("urls", [])
    if urls and len(urls) > 50:
        return False, f"Too many URLs: {len(urls)} (max 50)"

    # Hashtags validation
    hashtags = post.get("hashtags", [])
    if hashtags and len(hashtags) > 100:
        return False, f"Too many hashtags: {len(hashtags)} (max 100)"

    # Engagement metrics should be non-negative
    for metric in ["views_count", "likes_count", "retweets_count", "replies_count"]:
        value = post.get(metric, 0)
        if not isinstance(value, int) or value < 0:
            return False, f"Invalid {metric}: {value} (must be non-negative integer)"

    return True, ""


def load_tweets_from_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Load tweets from Elasticsearch JSON export.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        List of Elasticsearch documents
    """
    print_step(f"Loading tweets from: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if "hits" in data:
            hits = data["hits"].get("hits", [])
            total = data["hits"].get("total", len(hits))
            if isinstance(total, dict):
                total = total.get("value", len(hits))
        else:
            # Assume it's a list of documents
            hits = data if isinstance(data, list) else [data]
            total = len(hits)
        
        print_success(f"Loaded {len(hits)} tweets from file (total: {total})")
        
        return hits
        
    except FileNotFoundError:
        print_error(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return []
    except Exception as e:
        print_error(f"Error loading file: {e}")
        return []


def insert_posts_one_by_one(posts: List[Dict[str, Any]]) -> tuple[int, int]:
    """
    Insert posts into Weaviate one at a time (fallback for batch issues).

    Args:
        posts: List of post dictionaries

    Returns:
        Tuple of (successful_count, failed_count)
    """
    url = f"{BACKEND_URL}/collections/{USER_ID}/insert/{COLLECTION_NAME}"

    successful = 0
    failed = 0
    total = len(posts)

    print(f"  Inserting {total} posts one-by-one...")

    for i, post in enumerate(posts, 1):
        try:
            response = requests.post(url, json={"objects": [post]}, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if result.get("inserted_count", 0) > 0:
                    successful += 1
                    if i % 10 == 0 or i == total:
                        print(f"  Progress: {i}/{total} - ✓ {successful} inserted, ✗ {failed} failed")
                else:
                    failed += 1
                    errors = result.get("errors", [])
                    if i <= 3:  # Show first 3 errors
                        print(f"  ✗ Post {i} failed: {errors[0] if errors else 'Unknown error'}")
            else:
                failed += 1
                if i <= 3:
                    print(f"  ✗ Post {i} HTTP {response.status_code}: {response.text[:100]}")

        except Exception as e:
            failed += 1
            if i <= 3:
                print(f"  ✗ Post {i} exception: {e}")

    return successful, failed


def insert_posts_batch(posts: List[Dict[str, Any]], batch_size: int = 50, fallback_one_by_one: bool = True) -> tuple[int, int]:
    """
    Insert posts into Weaviate in batches, with optional one-by-one fallback.

    Args:
        posts: List of post dictionaries
        batch_size: Number of posts per batch (default 50)
        fallback_one_by_one: If True, fall back to one-by-one insertion on total failure

    Returns:
        Tuple of (successful_count, failed_count)
    """
    url = f"{BACKEND_URL}/collections/{USER_ID}/insert/{COLLECTION_NAME}"

    successful = 0
    failed = 0
    total_batches = (len(posts) + batch_size - 1) // batch_size

    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        batch_num = i // batch_size + 1

        try:
            response = requests.post(url, json={"objects": batch}, timeout=60)

            if response.status_code == 200:
                result = response.json()
                batch_success = result.get("inserted_count", 0)
                batch_failed = result.get("failed_count", 0)
                errors = result.get("errors", [])

                successful += batch_success
                failed += batch_failed

                status = "✓" if batch_failed == 0 else "⚠"
                print(f"  {status} Batch {batch_num}/{total_batches}: "
                      f"Inserted {batch_success}, Failed {batch_failed}")

                # Print error details if there are failures
                if errors and batch_failed > 0:
                    print(f"      First error: {errors[0] if isinstance(errors, list) else errors}")
            else:
                print_error(f"Batch {batch_num} failed: HTTP {response.status_code}")
                error_detail = response.text[:200]
                print_error(f"Response: {error_detail}")
                failed += len(batch)

        except requests.exceptions.Timeout:
            print_error(f"Batch {batch_num} timeout")
            failed += len(batch)
        except Exception as e:
            print_error(f"Error inserting batch {batch_num}: {e}")
            failed += len(batch)

    # If all batches failed and fallback is enabled, try one-by-one
    if fallback_one_by_one and successful == 0 and failed > 0:
        print_warning(f"\n  All batch insertions failed. Trying one-by-one insertion...")
        return insert_posts_one_by_one(posts)

    return successful, failed


def print_statistics(tweets: List[Dict], posts: List[Dict]):
    """Print detailed statistics about the data."""
    print("\n" + "=" * 70)
    print(f"{CYAN}📊 DATA STATISTICS{RESET}")
    print("=" * 70)
    
    # Document types
    types = {}
    for tweet in tweets:
        doc_type = tweet.get("_type", "unknown")
        types[doc_type] = types.get(doc_type, 0) + 1
    
    print(f"\n{MAGENTA}📄 Document Types:{RESET}")
    for dtype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dtype}: {count}")
    
    # Sentiment distribution
    sentiments = {}
    for post in posts:
        sentiment = post.get("sentiment", "unknown")
        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
    
    print(f"\n{MAGENTA}😊 Sentiment Distribution:{RESET}")
    for sentiment, count in sorted(sentiments.items(), key=lambda x: x[1], reverse=True):
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "❓")
        print(f"  {emoji} {sentiment}: {count}")
    
    # Topic distribution
    topics = {}
    for post in posts:
        topic = post.get("topic", "unknown")
        topics[topic] = topics.get(topic, 0) + 1
    
    print(f"\n{MAGENTA}🏷️  Topic Distribution:{RESET}")
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {topic}: {count}")
    
    # Engagement stats
    total_views = sum(p.get("views_count", 0) for p in posts)
    total_likes = sum(p.get("likes_count", 0) for p in posts)
    total_retweets = sum(p.get("retweets_count", 0) for p in posts)
    
    print(f"\n{MAGENTA}📈 Engagement Metrics:{RESET}")
    print(f"  Total Views: {total_views:,}")
    print(f"  Total Likes: {total_likes:,}")
    print(f"  Total Retweets: {total_retweets:,}")
    if posts:
        print(f"  Avg Views per post: {total_views // len(posts):,}")
    
    # Reply stats
    replies = sum(1 for p in posts if p.get("is_reply"))
    print(f"\n{MAGENTA}💬 Reply Statistics:{RESET}")
    print(f"  Total Replies: {replies}")
    print(f"  Regular Tweets: {len(posts) - replies}")
    
    # Top hashtags
    hashtag_counts = {}
    for post in posts:
        for tag in post.get("hashtags", []):
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    
    print(f"\n{MAGENTA}🔥 Top Hashtags:{RESET}")
    for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  #{tag}: {count}")
    
    print("=" * 70 + "\n")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Load Arabic tweets from Elasticsearch JSON into Weaviate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to validate data
  python load_ar_tweets.py --file data/task_6552.json --dry-run --show-sample
  
  # Load first 100 tweets (test)
  python load_ar_tweets.py --file data/task_6552.json --limit 100
  
  # Load all tweets
  python load_ar_tweets.py --file data/task_6552.json
        """
    )
    
    parser.add_argument(
        "--file",
        required=True,
        help="Path to Elasticsearch JSON file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without inserting into Weaviate"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of tweets to process"
    )
    parser.add_argument(
        "--show-sample",
        action="store_true",
        help="Show sample posts after parsing"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for insertion (default: 50)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print(f"{CYAN}📥 ARABIC TWEETS LOADER{RESET}")
    print("=" * 70 + "\n")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"User ID: {USER_ID}")
    print_info(f"Collection: {COLLECTION_NAME}")
    print_info(f"File: {args.file}")
    if args.limit:
        print_info(f"Limit: {args.limit} tweets")
    if args.dry_run:
        print_warning("DRY RUN MODE - No data will be inserted")
    print()
    
    # Load tweets
    tweets = load_tweets_from_file(args.file)
    
    if not tweets:
        print_error("No tweets loaded. Exiting.")
        return 1
    
    # Apply limit if specified
    if args.limit:
        tweets = tweets[:args.limit]
        print_warning(f"Limited to {args.limit} tweets\n")
    
    # Parse tweets
    print_step(f"Parsing {len(tweets)} tweets...")
    posts = []
    skipped = 0
    
    for i, tweet in enumerate(tweets, 1):
        if i % 100 == 0:
            print(f"  Processing: {i}/{len(tweets)}...", end='\r')
        
        post = extract_post_from_es_doc(tweet)
        if post:
            posts.append(post)
        else:
            skipped += 1
    
    print(f"  Processing: {len(tweets)}/{len(tweets)} - Done!          ")
    print_success(f"Parsed {len(posts)} posts ({skipped} skipped)\n")
    
    if not posts:
        print_error("No valid posts to insert. Exiting.")
        return 1
    
    # Show statistics
    print_statistics(tweets, posts)
    
    # Show sample if requested
    if args.show_sample and posts:
        print("=" * 70)
        print(f"{CYAN}📝 SAMPLE POSTS{RESET}")
        print("=" * 70 + "\n")
        
        for i, post in enumerate(posts[:3], 1):
            print(f"{MAGENTA}Post {i}:{RESET}")
            print(f"  ID: {post['post_id']}")
            print(f"  Author: {post['author_name']} (@{post['author_username']})")
            print(f"  Type: {post['post_type']}")
            print(f"  Topic: {post['topic']}")
            print(f"  Sentiment: {post['sentiment']}")
            content_preview = post['content'][:100] + "..." if len(post['content']) > 100 else post['content']
            print(f"  Content: {content_preview}")
            print(f"  Hashtags: {post['hashtags']}")
            print(f"  Engagement: {post['views_count']} views, {post['likes_count']} likes")
            print()
    
    # Insert or dry-run
    if args.dry_run:
        print("=" * 70)
        print_warning("🏃 DRY RUN - No data will be inserted into Weaviate")
        print(f"Would insert {len(posts)} posts")
        print("=" * 70 + "\n")
        return 0
    
    else:
        print("=" * 70)
        print_step(f"📤 Inserting {len(posts)} posts into Weaviate...")
        print("=" * 70 + "\n")
        
        successful, failed = insert_posts_batch(posts, batch_size=args.batch_size)
        
        print("\n" + "=" * 70)
        print(f"{CYAN}📊 INSERTION RESULTS{RESET}")
        print("=" * 70)
        print(f"{GREEN}✅ Inserted: {successful}{RESET}")
        print(f"{RED}❌ Failed: {failed}{RESET}")
        print(f"📊 Total: {len(posts)}")
        
        success_rate = (successful / len(posts) * 100) if posts else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("=" * 70 + "\n")
        
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
