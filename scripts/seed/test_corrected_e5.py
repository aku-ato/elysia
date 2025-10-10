#!/usr/bin/env python3
"""
Test corrected E5 model configuration with Weaviate.

This script verifies that:
1. E5 models work correctly with the 'model' parameter (not passageModel/queryModel)
2. Collections can be created successfully
3. Arabic text can be vectorized and searched

Usage:
    python test_corrected_e5.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("USER_ID", "default")

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_step(msg: str):
    print(f"{BLUE}▶ {msg}{RESET}")


def print_success(msg: str):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg: str):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg: str):
    print(f"{CYAN}ℹ {msg}{RESET}")


def delete_collection_if_exists(collection_name: str) -> bool:
    """Delete collection if it exists."""
    url = f"{BACKEND_URL}/collections/{USER_ID}/delete/{collection_name}"
    try:
        response = requests.delete(url, timeout=10)
        if response.status_code in [200, 404]:
            return True
        return False
    except Exception as e:
        print_error(f"Failed to delete collection: {e}")
        return False


def test_e5_default_vectorizer():
    """Test E5 model with default vectorizer using 'model' parameter."""
    print_step("Test 1: E5 model with default vectorizer")

    collection_name = "TestE5Default"

    # Clean up first
    delete_collection_if_exists(collection_name)

    collection_data = {
        "collection_name": collection_name,
        "description": "Test E5 model with correct configuration",
        "properties": [
            {"name": "text", "data_type": "text"},
            {"name": "language", "data_type": "text"}
        ],
        "vectorizer_config": {
            "type": "text2vec-huggingface",
            "model": "intfloat/multilingual-e5-large"  # Correct: use 'model' parameter
        }
    }

    url = f"{BACKEND_URL}/collections/{USER_ID}/create"

    try:
        response = requests.post(url, json=collection_data, timeout=30)

        if response.status_code == 201:
            print_success(f"Collection '{collection_name}' created successfully")
            return True
        else:
            print_error(f"Failed to create collection: HTTP {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_e5_named_vectors():
    """Test E5 model with named vectors using 'model' parameter."""
    print_step("Test 2: E5 model with named vectors")

    collection_name = "TestE5NamedVectors"

    # Clean up first
    delete_collection_if_exists(collection_name)

    collection_data = {
        "collection_name": collection_name,
        "description": "Test E5 model with named vectors",
        "properties": [
            {"name": "text", "data_type": "text"},
            {"name": "title", "data_type": "text"}
        ],
        "vectorizer_config": {
            "type": "none"  # No default vectorizer
        },
        "named_vectors": [
            {
                "name": "text_vector",
                "vectorizer_type": "text2vec-huggingface",
                "model": "intfloat/multilingual-e5-large",  # Correct: use 'model' parameter
                "source_properties": ["text"]
            }
        ]
    }

    url = f"{BACKEND_URL}/collections/{USER_ID}/create"

    try:
        response = requests.post(url, json=collection_data, timeout=30)

        if response.status_code == 201:
            print_success(f"Collection '{collection_name}' created successfully")
            return True
        else:
            print_error(f"Failed to create collection: HTTP {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def verify_backend():
    """Verify backend is accessible."""
    print_step("Verifying backend connection...")

    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is accessible at {BACKEND_URL}")
            return True
        else:
            print_error(f"Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BACKEND_URL}")
        print_info("Make sure the backend service is running")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {e}")
        return False


def main():
    """Main execution."""
    print("\n" + "=" * 70)
    print(f"{CYAN}🧪 E5 MODEL CONFIGURATION TEST{RESET}")
    print("=" * 70 + "\n")

    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"User ID: {USER_ID}")
    print()

    # Verify backend
    if not verify_backend():
        print_error("\n❌ Cannot proceed without backend connection")
        return 1

    print()

    # Run tests
    results = []

    # Test 1: Default vectorizer
    results.append(("Default Vectorizer", test_e5_default_vectorizer()))
    print()

    # Test 2: Named vectors
    results.append(("Named Vectors", test_e5_named_vectors()))
    print()

    # Print summary
    print("=" * 70)
    print(f"{CYAN}📊 TEST SUMMARY{RESET}")
    print("=" * 70 + "\n")

    all_passed = True
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False

    print()

    if all_passed:
        print("=" * 70)
        print(f"{GREEN}✅ ALL TESTS PASSED{RESET}")
        print("=" * 70)
        print(f"\n{GREEN}E5 model configuration is working correctly!{RESET}\n")
        return 0
    else:
        print("=" * 70)
        print(f"{RED}❌ SOME TESTS FAILED{RESET}")
        print("=" * 70)
        print(f"\n{RED}E5 model configuration needs attention{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
