#!/usr/bin/env python3
"""
Test Arabic embedding quality and cross-language search.

This script tests:
1. Arabic text normalization impact on search quality
2. Cross-language semantic search (Arabic → English, etc.)
3. Query performance (latency, throughput)
4. Precision and recall for test queries
5. GPU acceleration effectiveness

Usage:
    # Run all tests
    python test_arabic_embedding.py
    
    # Run with custom queries
    python test_arabic_embedding.py --queries queries.json
    
    # Performance test only
    python test_arabic_embedding.py --performance-only
"""

import json
import os
import sys
import time
import requests
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from elysia.util.arabic import normalize_arabic_text
except ImportError:
    print("Warning: Could not import arabic utilities")
    normalize_arabic_text = lambda x: x

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("USER_ID", "default")
COLLECTION_NAME = "SocialMediaPosts"

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


# Test queries with expected topics
TEST_QUERIES = [
    {
        "query": "الذكاء الاصطناعي",
        "language": "ar",
        "expected_topics": ["Artificial Intelligence", "Technology"],
        "description": "Arabic AI query"
    },
    {
        "query": "artificial intelligence",
        "language": "en",
        "expected_topics": ["Artificial Intelligence", "Technology"],
        "description": "English AI query (should match Arabic content)"
    },
    {
        "query": "زيارة السلطان هيثم لبيلاروس",
        "language": "ar",
        "expected_topics": ["Belarus Visit", "Sultan Haitham"],
        "description": "Arabic Belarus visit query"
    },
    {
        "query": "sultan visit belarus",
        "language": "en",
        "expected_topics": ["Belarus Visit", "Sultan Haitham"],
        "description": "English Belarus query (cross-language)"
    },
    {
        "query": "السياسة والاقتصاد",
        "language": "ar",
        "expected_topics": ["Politics", "Economics"],
        "description": "Arabic politics/economics"
    },
    {
        "query": "التكنولوجيا الحديثة",
        "language": "ar",
        "expected_topics": ["Technology"],
        "description": "Arabic modern technology"
    },
]


def print_header(text: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"{CYAN}{text}{RESET}")
    print("=" * 70 + "\n")


def print_step(msg: str):
    print(f"{BLUE}▶ {msg}{RESET}")


def print_success(msg: str):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg: str):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg: str):
    print(f"{CYAN}ℹ {msg}{RESET}")


def query_collection(query: str, limit: int = 5) -> Tuple[List[Dict], float]:
    """
    Query the collection and measure response time.
    
    Returns:
        Tuple of (results, elapsed_time_ms)
    """
    url = f"{BACKEND_URL}/collections/{USER_ID}/query/{COLLECTION_NAME}"
    
    start = time.time()
    try:
        response = requests.post(
            url,
            json={"query": query, "limit": limit},
            timeout=30
        )
        elapsed_ms = (time.time() - start) * 1000
        
        if response.status_code == 200:
            return response.json(), elapsed_ms
        else:
            print_error(f"Query failed: HTTP {response.status_code}")
            return [], elapsed_ms
    except Exception as e:
        elapsed_ms = (time.time() - start) * 1000
        print_error(f"Query error: {e}")
        return [], elapsed_ms


def calculate_relevance(results: List[Dict], expected_topics: List[str]) -> Dict[str, float]:
    """
    Calculate precision and recall for query results.
    
    Args:
        results: Query results
        expected_topics: List of expected topics
    
    Returns:
        Dictionary with precision, recall, and f1 scores
    """
    if not results or not expected_topics:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Count how many results have expected topics
    relevant_count = 0
    for result in results:
        topic = result.get("topic", "")
        if any(exp_topic.lower() in topic.lower() for exp_topic in expected_topics):
            relevant_count += 1
    
    precision = relevant_count / len(results) if results else 0
    recall = relevant_count / len(expected_topics) if expected_topics else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "relevant_count": relevant_count,
        "total_count": len(results)
    }


def test_query_quality():
    """Test query quality with predefined test queries."""
    print_header("🧪 QUERY QUALITY TESTS")
    
    results_summary = []
    total_precision = 0
    total_recall = 0
    total_f1 = 0
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n{MAGENTA}Test {i}/{len(TEST_QUERIES)}:{RESET} {test['description']}")
        print(f"  Query ({test['language']}): '{test['query']}'")
        print(f"  Expected topics: {test['expected_topics']}")
        
        # Execute query
        results, elapsed = query_collection(test['query'])
        
        if not results:
            print_error("  No results returned")
            continue
        
        # Calculate metrics
        metrics = calculate_relevance(results, test['expected_topics'])
        
        # Store results
        results_summary.append({
            "query": test['query'],
            "language": test['language'],
            "description": test['description'],
            "metrics": metrics,
            "elapsed_ms": elapsed
        })
        
        total_precision += metrics['precision']
        total_recall += metrics['recall']
        total_f1 += metrics['f1']
        
        # Print results
        print(f"  Results: {metrics['relevant_count']}/{metrics['total_count']} relevant")
        print(f"  Precision: {metrics['precision']:.1%}")
        print(f"  Recall: {metrics['recall']:.1%}")
        print(f"  F1 Score: {metrics['f1']:.3f}")
        print(f"  Time: {elapsed:.0f}ms")
        
        # Show top result
        if results:
            top = results[0]
            print(f"  Top result: {top.get('topic')} ({top.get('language')})")
            content_preview = top.get('content', '')[:60]
            print(f"             {content_preview}...")
    
    # Summary
    n = len(results_summary)
    if n > 0:
        print_header("📊 OVERALL METRICS")
        print(f"Average Precision: {total_precision/n:.1%}")
        print(f"Average Recall: {total_recall/n:.1%}")
        print(f"Average F1 Score: {total_f1/n:.3f}")
    
    return results_summary


def test_normalization_impact():
    """Test impact of Arabic normalization on search quality."""
    print_header("🔄 NORMALIZATION IMPACT TEST")
    
    # Test with diacritics vs normalized
    test_pairs = [
        {
            "with_diacritics": "مَرْحَباً بِكُمْ",
            "normalized": "مرحبا بكم",
            "description": "Greeting with/without diacritics"
        },
        {
            "with_diacritics": "الذِّكَاءُ الإصْطِنَاعِيّ",
            "normalized": "الذكاء الاصطناعي",
            "description": "AI with/without diacritics"
        },
    ]
    
    for pair in test_pairs:
        print(f"\n{MAGENTA}Testing:{RESET} {pair['description']}")
        print(f"  With diacritics: {pair['with_diacritics']}")
        print(f"  Normalized: {pair['normalized']}")
        
        # Query both versions
        results_diac, time_diac = query_collection(pair['with_diacritics'], limit=3)
        results_norm, time_norm = query_collection(pair['normalized'], limit=3)
        
        # Compare results
        if results_diac and results_norm:
            # Check if top results are similar
            top_diac_ids = [r.get('post_id') for r in results_diac[:3]]
            top_norm_ids = [r.get('post_id') for r in results_norm[:3]]
            
            overlap = len(set(top_diac_ids) & set(top_norm_ids))
            consistency = overlap / 3 * 100
            
            print(f"  Results consistency: {consistency:.0f}% ({overlap}/3 same)")
            print(f"  Time (diacritics): {time_diac:.0f}ms")
            print(f"  Time (normalized): {time_norm:.0f}ms")
            
            if consistency >= 66:
                print_success("  Good consistency - normalization working well")
            else:
                print_error("  Low consistency - normalization may need tuning")
        else:
            print_error("  No results to compare")


def test_cross_language_search():
    """Test cross-language semantic search."""
    print_header("🌍 CROSS-LANGUAGE SEARCH TEST")
    
    cross_lang_queries = [
        {
            "ar": "الذكاء الاصطناعي في الطب",
            "en": "artificial intelligence in medicine",
            "expected_topics": ["Artificial Intelligence", "Healthcare"]
        },
        {
            "ar": "التكنولوجيا الحديثة",
            "en": "modern technology",
            "expected_topics": ["Technology"]
        },
    ]
    
    for test in cross_lang_queries:
        print(f"\n{MAGENTA}Testing cross-language search:{RESET}")
        print(f"  Arabic: {test['ar']}")
        print(f"  English: {test['en']}")
        
        # Query both languages
        results_ar, time_ar = query_collection(test['ar'], limit=5)
        results_en, time_en = query_collection(test['en'], limit=5)
        
        if results_ar and results_en:
            # Check overlap
            ids_ar = set(r.get('post_id') for r in results_ar)
            ids_en = set(r.get('post_id') for r in results_en)
            overlap = len(ids_ar & ids_en)
            
            print(f"  Arabic results: {len(results_ar)}")
            print(f"  English results: {len(results_en)}")
            print(f"  Overlap: {overlap}/5 ({overlap/5*100:.0f}%)")
            
            if overlap >= 3:
                print_success("  Good cross-language semantic matching")
            elif overlap >= 2:
                print_info("  Moderate cross-language matching")
            else:
                print_error("  Poor cross-language matching")
        else:
            print_error("  No results to compare")


def test_performance(num_queries: int = 10):
    """Test query performance."""
    print_header("⚡ PERFORMANCE TEST")
    
    # Warm-up query
    print_step("Warming up model...")
    query_collection("مرحبا", limit=1)
    time.sleep(0.5)
    
    # Run multiple queries
    print_step(f"Running {num_queries} queries...")
    
    query = "الذكاء الاصطناعي"
    times = []
    
    for i in range(num_queries):
        _, elapsed = query_collection(query, limit=5)
        times.append(elapsed)
        print(f"  Query {i+1}/{num_queries}: {elapsed:.0f}ms", end='\r')
    
    print()
    
    # Calculate stats
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n{MAGENTA}Performance Results:{RESET}")
    print(f"  Average: {avg_time:.0f}ms")
    print(f"  Min: {min_time:.0f}ms")
    print(f"  Max: {max_time:.0f}ms")
    print(f"  Throughput: ~{1000/avg_time:.1f} queries/second")
    
    # Evaluate performance
    if avg_time < 100:
        print_success("  Excellent performance (GPU accelerated)")
    elif avg_time < 300:
        print_info("  Good performance")
    else:
        print_error("  Slow performance - check GPU acceleration")


def verify_collection_exists() -> bool:
    """Verify that the collection exists."""
    url = f"{BACKEND_URL}/collections/{USER_ID}/list"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            collections = response.json().get("collections", [])
            for coll in collections:
                if coll.get("name") == COLLECTION_NAME:
                    total = coll.get("total", 0)
                    print_success(f"Collection '{COLLECTION_NAME}' found ({total} objects)")
                    return total > 0
            print_error(f"Collection '{COLLECTION_NAME}' not found")
            return False
        else:
            print_error("Failed to list collections")
            return False
    except Exception as e:
        print_error(f"Error checking collection: {e}")
        return False


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Arabic embedding quality")
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run only performance tests"
    )
    parser.add_argument(
        "--num-queries",
        type=int,
        default=10,
        help="Number of queries for performance test (default: 10)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print(f"{CYAN}🧪 ARABIC EMBEDDING QUALITY TESTS{RESET}")
    print("=" * 70 + "\n")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Collection: {COLLECTION_NAME}")
    print()
    
    # Verify collection exists
    if not verify_collection_exists():
        print_error("\nCollection not found or empty. Load data first:")
        print_info("  python scripts/seed/load_ar_tweets.py --file data/task_6552.json")
        return 1
    
    print()
    
    # Run tests
    if args.performance_only:
        test_performance(args.num_queries)
    else:
        # Run all tests
        test_query_quality()
        test_normalization_impact()
        test_cross_language_search()
        test_performance(args.num_queries)
    
    print_header("✅ TESTS COMPLETE")
    print("Review the results above to assess embedding quality.\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
