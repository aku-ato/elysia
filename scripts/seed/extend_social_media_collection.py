#!/usr/bin/env python3
"""
Create extended SocialMediaPosts collection with Twitter-specific fields.

This script creates a collection optimized for Twitter/social media data with:
- Basic post fields (content, language, timestamp, author, etc.)
- Twitter-specific fields (username, post_type, URLs, etc.)
- Engagement metrics (views, likes, retweets, replies)
- Reply chain tracking (parent post references)
- Hugging Face multilingual-e5-large vectorizer for Arabic support

Usage:
    python extend_social_media_collection.py [--yes]

    --yes: Skip confirmation prompt and create collection automatically
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("USER_ID", "default")

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


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


def create_extended_social_media_collection() -> bool:
    """
    Create SocialMediaPosts collection with extended Twitter fields.
    
    Returns:
        True if collection created successfully, False otherwise
    """
    print_step("Creating extended SocialMediaPosts collection...")
    
    collection_data = {
        "collection_name": "SocialMediaPosts",
        "description": "Multilingual social media posts with engagement metrics and reply chains",
        "properties": [
            # Original fields
            {"name": "post_id", "data_type": "text"},
            {"name": "content", "data_type": "text"},
            {"name": "language", "data_type": "text"},
            {"name": "timestamp", "data_type": "date"},
            {"name": "author_id", "data_type": "text"},
            {"name": "topic", "data_type": "text"},
            {"name": "sentiment", "data_type": "text"},
            {"name": "hashtags", "data_type": "text[]"},
            {"name": "event_id", "data_type": "text"},
            {"name": "location", "data_type": "text"},
            
            # Extended fields for Twitter
            {"name": "author_username", "data_type": "text"},
            {"name": "author_name", "data_type": "text"},
            {"name": "urls", "data_type": "text[]"},
            {"name": "post_type", "data_type": "text"},  # tweet, reply, first, etc.
            
            # Engagement metrics
            {"name": "views_count", "data_type": "int"},
            {"name": "likes_count", "data_type": "int"},
            {"name": "retweets_count", "data_type": "int"},
            {"name": "replies_count", "data_type": "int"},
            
            # Reply chain tracking
            {"name": "reply_to_post_id", "data_type": "text"},
            {"name": "is_reply", "data_type": "bool"},
        ],
        "vectorizer_config": {
            "type": "text2vec-huggingface",
            "model": "intfloat/multilingual-e5-large"
            # NOTE: source_properties only works with named vectors, not default vectorizer
            # All properties will be vectorized by default
        }
    }
    
    url = f"{BACKEND_URL}/collections/{USER_ID}/create"
    
    try:
        print_info(f"Sending request to: {url}")
        response = requests.post(url, json=collection_data, timeout=30)
        
        if response.status_code == 201:
            print_success(f"Collection 'SocialMediaPosts' created successfully")
            print_info(f"Vectorizer: text2vec-huggingface (multilingual-e5-large)")
            print_info(f"Total properties: {len(collection_data['properties'])}")
            return True
        elif response.status_code == 400:
            error_msg = response.json().get("error", response.text)
            if "already exists" in error_msg.lower():
                print_warning(f"Collection 'SocialMediaPosts' already exists")
                print_info("Delete it first if you want to recreate:")
                print_info(f"  curl -X DELETE {BACKEND_URL}/collections/{USER_ID}/delete/SocialMediaPosts")
            else:
                print_error(f"Bad request: {error_msg}")
            return False
        else:
            print_error(f"Request failed: HTTP {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BACKEND_URL}")
        print_info("Make sure the backend service is running:")
        print_info("  cd /home/ppiccolo/projects/elysia/deploy")
        print_info("  docker-compose up -d backend")
        return False
    except requests.exceptions.Timeout:
        print_error("Request timeout after 30 seconds")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_collection_schema():
    """Print the collection schema in a nice format."""
    print("\n" + "=" * 70)
    print(f"{CYAN}📋 COLLECTION SCHEMA: SocialMediaPosts{RESET}")
    print("=" * 70 + "\n")
    
    print(f"{BLUE}Basic Fields:{RESET}")
    print("  • post_id (text) - Unique post identifier")
    print("  • content (text) - Post content (normalized for Arabic)")
    print("  • language (text) - ISO 639-1 language code (ar, en, it, etc.)")
    print("  • timestamp (date) - Post creation timestamp")
    print("  • author_id (text) - Author user ID")
    print("  • topic (text) - Extracted/assigned topic")
    print("  • sentiment (text) - positive, negative, or neutral")
    print("  • hashtags (text[]) - Array of hashtags")
    print("  • event_id (text) - Related event/task ID")
    print("  • location (text) - Geographic location")
    
    print(f"\n{BLUE}Twitter-Specific Fields:{RESET}")
    print("  • author_username (text) - Twitter @username")
    print("  • author_name (text) - Display name")
    print("  • urls (text[]) - Array of URLs in post")
    print("  • post_type (text) - tweet, reply, first, etc.")
    
    print(f"\n{BLUE}Engagement Metrics:{RESET}")
    print("  • views_count (int) - Number of views")
    print("  • likes_count (int) - Number of likes/favorites")
    print("  • retweets_count (int) - Number of retweets")
    print("  • replies_count (int) - Number of replies")
    
    print(f"\n{BLUE}Reply Chain:{RESET}")
    print("  • reply_to_post_id (text) - Parent post ID if this is a reply")
    print("  • is_reply (boolean) - True if this post is a reply")
    
    print(f"\n{BLUE}Vectorizer:{RESET}")
    print("  • Type: text2vec-huggingface")
    print("  • Model: intfloat/multilingual-e5-large")
    print("  • Vectorized fields: content, topic (optimized for performance)")
    print("  • Optimized for: Arabic, English, Italian, and 100+ languages")
    print("  • GPU-accelerated via t2v-transformers service")
    
    print("\n" + "=" * 70 + "\n")


def verify_backend_connection() -> bool:
    """
    Verify that backend is accessible.
    
    Returns:
        True if backend is accessible, False otherwise
    """
    print_step("Verifying backend connection...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is accessible at {BACKEND_URL}")
            return True
        else:
            print_warning(f"Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BACKEND_URL}")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {e}")
        return False


def main():
    """Main execution."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create extended SocialMediaPosts collection")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print(f"{CYAN}🔧 EXTENDED SOCIAL MEDIA COLLECTION CREATOR{RESET}")
    print("=" * 70 + "\n")

    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"User ID: {USER_ID}")
    print()

    # Verify backend connection
    if not verify_backend_connection():
        print_error("\n❌ Cannot proceed without backend connection")
        print_info("Start the backend service first:")
        print_info("  cd /home/ppiccolo/projects/elysia/deploy")
        print_info("  docker-compose up -d")
        return 1

    print()

    # Show what will be created
    print_collection_schema()

    # Confirm creation (unless --yes flag is provided)
    if not args.yes:
        try:
            response = input(f"{CYAN}Create this collection? [Y/n]: {RESET}").strip().lower()
            if response and response != 'y' and response != 'yes':
                print_warning("Collection creation cancelled")
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\n")
            print_warning("Collection creation cancelled")
            return 0

    print()
    
    # Create collection
    success = create_extended_social_media_collection()
    
    if success:
        print("\n" + "=" * 70)
        print(f"{GREEN}✅ SUCCESS{RESET}")
        print("=" * 70)
        print("\n" + f"{GREEN}Collection 'SocialMediaPosts' is ready for data!{RESET}\n")
        print("Next steps:")
        print(f"  1. Load Arabic tweets:")
        print(f"     python scripts/seed/load_ar_tweets.py --file scripts/seed/data/task_6552.json")
        print(f"\n  2. Query the collection:")
        print(f"     curl -X POST {BACKEND_URL}/collections/{USER_ID}/query/SocialMediaPosts \\")
        print(f'          -H "Content-Type: application/json" \\')
        print(f'          -d \'{{"query": "الذكاء الاصطناعي", "limit": 5}}\'')
        print()
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"{RED}❌ FAILED{RESET}")
        print("=" * 70)
        print("\nCollection creation failed. Check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
