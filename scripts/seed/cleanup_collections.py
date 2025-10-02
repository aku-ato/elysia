#!/usr/bin/env python3
"""
Cleanup script to remove the test collections created by seed_correlation_collections.py

Removes:
- SocialMediaPosts collection
- AudioTranscriptions collection
"""

import os
import sys
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
RESET = "\033[0m"

COLLECTIONS_TO_DELETE = ["SocialMediaPosts", "AudioTranscriptions"]


def print_step(message: str):
    """Print a step message in blue."""
    print(f"{BLUE}▶ {message}{RESET}")


def print_success(message: str):
    """Print a success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print an error message in red."""
    print(f"{RED}✗ {message}{RESET}")


def print_warning(message: str):
    """Print a warning message in yellow."""
    print(f"{YELLOW}⚠ {message}{RESET}")


def delete_collection(collection_name: str) -> bool:
    """Delete a collection using the Elysia API."""
    url = f"{BACKEND_URL}/collections/{USER_ID}/delete/{collection_name}"
    data = {"collection_name": collection_name, "confirm": True}

    try:
        response = requests.delete(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("error"):
            print_error(f"API error: {result['error']}")
            return False

        if result.get("deleted"):
            return True
        return False
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def main():
    """Main execution flow."""
    print(f"\n{YELLOW}{'='*60}")
    print("  Elysia Test Collections Cleanup Script")
    print(f"{'='*60}{RESET}\n")

    print(f"Backend URL: {BACKEND_URL}")
    print(f"User ID: {USER_ID}\n")

    print_warning("This will delete the following collections:")
    for collection in COLLECTIONS_TO_DELETE:
        print(f"  • {collection}")
    print()

    # Confirm deletion
    try:
        confirm = input(f"{YELLOW}Are you sure you want to continue? (yes/no): {RESET}").strip().lower()
        if confirm not in ["yes", "y"]:
            print_warning("Cleanup cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Cleanup cancelled by user{RESET}")
        sys.exit(0)

    print()

    # Delete collections
    success_count = 0
    fail_count = 0

    for collection_name in COLLECTIONS_TO_DELETE:
        print_step(f"Deleting {collection_name}...")
        if delete_collection(collection_name):
            print_success(f"{collection_name} deleted successfully")
            success_count += 1
        else:
            print_error(f"Failed to delete {collection_name}")
            fail_count += 1
        print()

    # Summary
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"  Cleanup Summary")
    print(f"{BLUE}{'='*60}{RESET}\n")
    print(f"  • Deleted: {GREEN}{success_count}{RESET} collections")
    if fail_count > 0:
        print(f"  • Failed: {RED}{fail_count}{RESET} collections")
    print()

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
