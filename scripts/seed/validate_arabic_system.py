#!/usr/bin/env python3
"""
Validate Arabic RAG system health and configuration.

This script checks:
- Docker services are running
- Weaviate is accessible
- Transformers service is ready
- Backend API is healthy
- Collection exists and is properly configured
- Sample query works (if data exists)
"""

import sys
import requests
import subprocess
from typing import Dict, List, Tuple

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"

# API Configuration
BACKEND_URL = "http://localhost:8000"
WEAVIATE_URL = "http://localhost:8080"
TRANSFORMERS_URL = "http://localhost:8081"
USER_ID = "default"
COLLECTION_NAME = "SocialMediaPosts"


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"{CYAN}{BOLD}{title}{RESET}")
    print("=" * 70)


def print_check(msg: str):
    """Print check message."""
    print(f"{BLUE}🔍 Checking: {msg}{RESET}")


def print_pass(msg: str):
    """Print success message."""
    print(f"{GREEN}✓ PASS: {msg}{RESET}")


def print_fail(msg: str):
    """Print failure message."""
    print(f"{RED}✗ FAIL: {msg}{RESET}")


def print_warn(msg: str):
    """Print warning message."""
    print(f"{YELLOW}⚠ WARN: {msg}{RESET}")


def print_info(msg: str):
    """Print info message."""
    print(f"{CYAN}ℹ INFO: {msg}{RESET}")


def check_docker_services() -> Tuple[bool, List[str]]:
    """Check if required Docker containers are running."""
    required_containers = [
        "elysia-weaviate",
        "elysia-transformers",
        "elysia-backend"
    ]

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )

        running_containers = result.stdout.strip().split("\n")
        missing = [c for c in required_containers if c not in running_containers]

        return len(missing) == 0, missing

    except subprocess.CalledProcessError:
        return False, required_containers
    except FileNotFoundError:
        return False, ["docker command not found"]


def check_weaviate_ready() -> Tuple[bool, str]:
    """Check if Weaviate is ready."""
    try:
        response = requests.get(f"{WEAVIATE_URL}/v1/.well-known/ready", timeout=5)
        return response.status_code == 200, "Ready"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_transformers_ready() -> Tuple[bool, str]:
    """Check if transformers service is ready."""
    try:
        response = requests.get(f"{TRANSFORMERS_URL}/.well-known/ready", timeout=5)
        return response.status_code == 204, "Ready"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_backend_healthy() -> Tuple[bool, str]:
    """Check if backend API is healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            return status == "healthy", status
        return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_collection_exists() -> Tuple[bool, str, Dict]:
    """Check if SocialMediaPosts collection exists."""
    try:
        response = requests.get(
            f"{WEAVIATE_URL}/v1/schema/{COLLECTION_NAME}",
            timeout=5
        )

        if response.status_code == 200:
            schema = response.json()
            vectorizer = schema.get("vectorizer", "unknown")
            properties = schema.get("properties", [])

            return True, vectorizer, schema
        elif response.status_code == 404:
            return False, "Collection not found", {}
        else:
            return False, f"HTTP {response.status_code}", {}

    except Exception as e:
        return False, str(e), {}


def get_collection_count() -> Tuple[bool, int]:
    """Get count of objects in collection."""
    graphql_query = """
    {
      Aggregate {
        SocialMediaPosts {
          meta {
            count
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
            count = data.get("data", {}).get("Aggregate", {}).get("SocialMediaPosts", [{}])[0].get("meta", {}).get("count", 0)
            return True, count
        else:
            return False, 0

    except Exception:
        return False, 0


def test_sample_query() -> Tuple[bool, str, int]:
    """Test a sample semantic search query."""
    graphql_query = """
    {
      Get {
        SocialMediaPosts(
          nearText: {
            concepts: ["السلطان"]
            certainty: 0.7
          }
          limit: 1
        ) {
          content
          _additional {
            certainty
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
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            # Check for errors
            if "errors" in data:
                return False, f"GraphQL error: {data['errors']}", 0

            posts = data.get("data", {}).get("Get", {}).get("SocialMediaPosts", [])

            if posts:
                certainty = posts[0].get("_additional", {}).get("certainty", 0)
                return True, f"Found result with certainty {certainty:.3f}", 1
            else:
                return True, "Query executed but no results (empty collection)", 0

        else:
            return False, f"HTTP {response.status_code}", 0

    except Exception as e:
        return False, str(e), 0


def check_offline_operation() -> Tuple[bool, str]:
    """Check if system is configured for offline operation."""
    try:
        # Check collection vectorizer instead of modules endpoint
        # (modules endpoint may not exist in newer versions)
        _, vectorizer, _ = check_collection_exists()

        if vectorizer == "text2vec-transformers":
            return True, "text2vec-transformers vectorizer (offline mode)"
        elif vectorizer == "text2vec-huggingface":
            return False, "text2vec-huggingface vectorizer (requires external API)"
        elif vectorizer:
            return False, f"Unknown vectorizer: {vectorizer}"
        else:
            return False, "Collection not found or no vectorizer"

    except Exception as e:
        return False, str(e)


def main():
    """Main validation routine."""
    print_header("🔍 ARABIC RAG SYSTEM VALIDATION")

    all_passed = True

    # Check 1: Docker services
    print_check("Docker services running")
    services_ok, missing = check_docker_services()
    if services_ok:
        print_pass("All required containers are running")
    else:
        print_fail(f"Missing containers: {', '.join(missing)}")
        print_info("Start with: cd /home/ppiccolo/projects/elysia/deploy && docker compose up -d")
        all_passed = False

    # Check 2: Weaviate
    print_check("Weaviate service")
    weaviate_ok, msg = check_weaviate_ready()
    if weaviate_ok:
        print_pass(f"Weaviate is ready at {WEAVIATE_URL}")
    else:
        print_fail(f"Weaviate not ready: {msg}")
        all_passed = False

    # Check 3: Transformers
    print_check("Transformers service")
    transformers_ok, msg = check_transformers_ready()
    if transformers_ok:
        print_pass(f"Transformers service is ready at {TRANSFORMERS_URL}")
    else:
        print_fail(f"Transformers service not ready: {msg}")
        all_passed = False

    # Check 4: Backend
    print_check("Backend API")
    backend_ok, msg = check_backend_healthy()
    if backend_ok:
        print_pass(f"Backend API is healthy at {BACKEND_URL}")
    else:
        print_fail(f"Backend API not healthy: {msg}")
        all_passed = False

    # Check 5: Collection exists
    print_check("SocialMediaPosts collection")
    collection_ok, vectorizer, schema = check_collection_exists()
    if collection_ok:
        print_pass(f"Collection exists with vectorizer: {vectorizer}")

        # Check vectorizer type
        if vectorizer == "text2vec-transformers":
            print_pass("Using text2vec-transformers (offline mode)")
        elif vectorizer == "text2vec-huggingface":
            print_warn("Using text2vec-huggingface (requires external API)")
            print_info("Consider switching to text2vec-transformers for offline operation")
        else:
            print_warn(f"Unknown vectorizer: {vectorizer}")

        # Check property count
        properties = schema.get("properties", [])
        if len(properties) >= 20:
            print_pass(f"Collection has {len(properties)} properties (expected 20)")
        else:
            print_warn(f"Collection has {len(properties)} properties (expected 20)")

    else:
        print_fail(f"Collection check failed: {vectorizer}")
        print_info("Create with: cd scripts/seed && make -f Makefile.arabic create-collection")
        all_passed = False

    # Check 6: Data count
    if collection_ok:
        print_check("Collection data")
        count_ok, count = get_collection_count()
        if count_ok:
            if count > 0:
                print_pass(f"Collection contains {count:,} posts")
            else:
                print_warn("Collection is empty (no data loaded)")
                print_info("Load data with: cd scripts/seed && make -f Makefile.arabic load-tweets")
        else:
            print_fail("Failed to get collection count")
            all_passed = False

    # Check 7: Offline operation
    print_check("Offline operation configuration")
    offline_ok, msg = check_offline_operation()
    if offline_ok:
        print_pass(msg)
    else:
        print_fail(msg)
        all_passed = False

    # Check 8: Sample query (only if data exists)
    if collection_ok and count_ok and count > 0:
        print_check("Sample semantic search query")
        query_ok, msg, result_count = test_sample_query()
        if query_ok:
            print_pass(f"Semantic search working: {msg}")
        else:
            print_fail(f"Semantic search failed: {msg}")
            all_passed = False

    # Final summary
    print_header("📊 VALIDATION SUMMARY")

    if all_passed:
        print(f"{GREEN}{BOLD}✅ ALL CHECKS PASSED{RESET}")
        print(f"{GREEN}System is ready for Arabic semantic search (fully offline){RESET}")
    else:
        print(f"{RED}{BOLD}❌ SOME CHECKS FAILED{RESET}")
        print(f"{YELLOW}Review the errors above and fix issues{RESET}")

    # Print quick start guide
    print_header("🚀 QUICK START")
    print("1. Query Arabic tweets:")
    print("   cd scripts/seed && python query_ar_tweets.py 'السلطان' --limit 5")
    print()
    print("2. Load more data:")
    print("   cd scripts/seed && make -f Makefile.arabic load-tweets")
    print()
    print("3. View statistics:")
    print("   cd scripts/seed && python query_ar_tweets.py --stats")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
