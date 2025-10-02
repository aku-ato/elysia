#!/usr/bin/env python3
"""
Seed script to populate Elysia with example multilingual collections for testing cross-collection correlation.

Creates two collections:
1. SocialMediaPosts - Multilingual tweets (Arabic, English, Italian)
2. AudioTranscriptions - Multilingual audio transcripts (Arabic, English, Italian)

Both collections share common metadata fields for correlation testing.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
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


def create_collection(collection_data: Dict[str, Any]) -> bool:
    """Create a collection using the Elysia API."""
    url = f"{BACKEND_URL}/collections/{USER_ID}/create"

    try:
        response = requests.post(url, json=collection_data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("error"):
            print_error(f"API error: {result['error']}")
            return False

        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def insert_objects(collection_name: str, objects: List[Dict[str, Any]]) -> bool:
    """Insert objects into a collection using the Elysia API."""
    url = f"{BACKEND_URL}/collections/{USER_ID}/insert/{collection_name}"
    data = {"objects": objects}

    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("error"):
            print_error(f"API error: {result['error']}")
            return False

        inserted = result.get("inserted_count", 0)
        failed = result.get("failed_count", 0)
        print_success(f"Inserted {inserted} objects, {failed} failed")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def generate_social_media_posts() -> List[Dict[str, Any]]:
    """Generate sample social media posts in multiple languages."""
    base_time = datetime(2025, 1, 15, 9, 0, 0)

    posts = [
        # Arabic posts
        {
            "post_id": "tw_001",
            "content": "مؤتمر التكنولوجيا كان رائعاً! تعلمت الكثير عن الذكاء الاصطناعي",
            "language": "ar",
            "timestamp": (base_time + timedelta(hours=1, minutes=30)).isoformat() + "Z",
            "author_id": "user_ahmed",
            "topic": "AI Conference",
            "sentiment": "positive",
            "hashtags": ["#AI", "#TechConf2025"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_002",
            "content": "الجلسة النقاشية عن التعلم الآلي في الطب كانت ملهمة جداً",
            "language": "ar",
            "timestamp": (base_time + timedelta(hours=2, minutes=15)).isoformat() + "Z",
            "author_id": "user_fatima",
            "topic": "ML in Medicine",
            "sentiment": "positive",
            "hashtags": ["#MachineLearning", "#Healthcare"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_003",
            "content": "ورشة العمل الأساسية كانت مملة للأسف، لا توجد معلومات جديدة",
            "language": "ar",
            "timestamp": (base_time + timedelta(hours=5, minutes=30)).isoformat() + "Z",
            "author_id": "user_omar",
            "topic": "ML Basics",
            "sentiment": "negative",
            "hashtags": ["#Workshop", "#Boring"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },

        # English posts
        {
            "post_id": "tw_004",
            "content": "The AI conference was amazing! Learned so much about machine learning applications",
            "language": "en",
            "timestamp": (base_time + timedelta(hours=2, minutes=45)).isoformat() + "Z",
            "author_id": "user_sarah",
            "topic": "AI Conference",
            "sentiment": "positive",
            "hashtags": ["#AI", "#MachineLearning"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_005",
            "content": "Great panel discussion on ML in healthcare. The future of diagnostics looks promising!",
            "language": "en",
            "timestamp": (base_time + timedelta(hours=2, minutes=20)).isoformat() + "Z",
            "author_id": "user_john",
            "topic": "ML in Medicine",
            "sentiment": "positive",
            "hashtags": ["#Healthcare", "#Innovation"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_006",
            "content": "The basics workshop was disappointing. Too elementary for experienced developers.",
            "language": "en",
            "timestamp": (base_time + timedelta(hours=5, minutes=45)).isoformat() + "Z",
            "author_id": "user_emily",
            "topic": "ML Basics",
            "sentiment": "negative",
            "hashtags": ["#Workshop", "#TooBasic"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_007",
            "content": "Keynote speaker Ahmed gave an excellent overview of AI applications!",
            "language": "en",
            "timestamp": (base_time + timedelta(hours=0, minutes=45)).isoformat() + "Z",
            "author_id": "user_sarah",
            "topic": "AI in Healthcare",
            "sentiment": "positive",
            "hashtags": ["#Keynote", "#AI"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },

        # Italian posts
        {
            "post_id": "tw_008",
            "content": "Il convegno sull'intelligenza artificiale è stato fantastico! Ho imparato moltissimo",
            "language": "it",
            "timestamp": (base_time + timedelta(hours=1, minutes=20)).isoformat() + "Z",
            "author_id": "user_marco",
            "topic": "AI Conference",
            "sentiment": "positive",
            "hashtags": ["#AI", "#Tecnologia"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_009",
            "content": "La discussione sul machine learning nella medicina è stata illuminante!",
            "language": "it",
            "timestamp": (base_time + timedelta(hours=2, minutes=30)).isoformat() + "Z",
            "author_id": "user_giulia",
            "topic": "ML in Medicine",
            "sentiment": "positive",
            "hashtags": ["#MachineLearning", "#Medicina"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_010",
            "content": "Il workshop di base è stato deludente, troppe nozioni elementari",
            "language": "it",
            "timestamp": (base_time + timedelta(hours=5, minutes=20)).isoformat() + "Z",
            "author_id": "user_marco",
            "topic": "ML Basics",
            "sentiment": "negative",
            "hashtags": ["#Workshop", "#Deludente"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_011",
            "content": "La keynote di Ahmed sulle applicazioni dell'AI è stata eccellente!",
            "language": "it",
            "timestamp": (base_time + timedelta(hours=0, minutes=50)).isoformat() + "Z",
            "author_id": "user_giulia",
            "topic": "AI in Healthcare",
            "sentiment": "positive",
            "hashtags": ["#Keynote", "#IA"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },

        # Cross-language interactions
        {
            "post_id": "tw_012",
            "content": "شكراً لسارة على المشاركة الرائعة في النقاش!",
            "language": "ar",
            "timestamp": (base_time + timedelta(hours=2, minutes=50)).isoformat() + "Z",
            "author_id": "user_ahmed",
            "topic": "ML in Medicine",
            "sentiment": "positive",
            "hashtags": ["#Collaboration"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        },
        {
            "post_id": "tw_013",
            "content": "Grazie Marco per le domande interessanti durante il workshop!",
            "language": "it",
            "timestamp": (base_time + timedelta(hours=6, minutes=0)).isoformat() + "Z",
            "author_id": "user_sarah",
            "topic": "ML Basics",
            "sentiment": "positive",
            "hashtags": ["#QA", "#Learning"],
            "event_id": "tech_conf_2025",
            "location": "Dubai"
        }
    ]

    return posts


def generate_audio_transcriptions() -> List[Dict[str, Any]]:
    """Generate sample audio transcriptions in multiple languages."""
    base_time = datetime(2025, 1, 15, 9, 0, 0)

    transcriptions = [
        # Arabic transcriptions
        {
            "transcription_id": "aud_001",
            "transcript": "مرحباً بكم في المؤتمر التقني لعام 2025. سنتحدث اليوم عن تطبيقات الذكاء الاصطناعي في الرعاية الصحية. التقدم في هذا المجال مذهل حقاً.",
            "language": "ar",
            "duration_seconds": 1800,
            "timestamp": (base_time + timedelta(hours=0)).isoformat() + "Z",
            "speaker_id": "user_ahmed",
            "topic": "AI in Healthcare",
            "audio_quality": "high",
            "keywords": ["AI", "Healthcare", "Applications", "Technology"],
            "event_id": "tech_conf_2025",
            "session_type": "keynote"
        },
        {
            "transcription_id": "aud_002",
            "transcript": "في هذه الجلسة سنناقش كيفية استخدام التعلم الآلي في تشخيص الأمراض. النتائج التي حققناها مبهرة للغاية.",
            "language": "ar",
            "duration_seconds": 2400,
            "timestamp": (base_time + timedelta(hours=2)).isoformat() + "Z",
            "speaker_id": "user_fatima",
            "topic": "ML in Medicine",
            "audio_quality": "high",
            "keywords": ["Machine Learning", "Medical", "Diagnostics", "Results"],
            "event_id": "tech_conf_2025",
            "session_type": "panel"
        },

        # English transcriptions
        {
            "transcription_id": "aud_003",
            "transcript": "Today we'll discuss how machine learning is transforming medical diagnostics. The accuracy improvements are remarkable, with some systems achieving over 95% accuracy in early disease detection.",
            "language": "en",
            "duration_seconds": 2400,
            "timestamp": (base_time + timedelta(hours=2)).isoformat() + "Z",
            "speaker_id": "user_sarah",
            "topic": "ML in Medicine",
            "audio_quality": "high",
            "keywords": ["Machine Learning", "Medical", "Diagnostics", "Accuracy"],
            "event_id": "tech_conf_2025",
            "session_type": "panel"
        },
        {
            "transcription_id": "aud_004",
            "transcript": "This workshop will cover the fundamentals of machine learning. We'll start with linear regression and work our way up to more complex algorithms. Let's begin with the basics.",
            "language": "en",
            "duration_seconds": 3600,
            "timestamp": (base_time + timedelta(hours=5)).isoformat() + "Z",
            "speaker_id": "user_john",
            "topic": "ML Basics",
            "audio_quality": "medium",
            "keywords": ["Machine Learning", "Regression", "Basics", "Algorithms"],
            "event_id": "tech_conf_2025",
            "session_type": "workshop"
        },
        {
            "transcription_id": "aud_005",
            "transcript": "Welcome everyone to the Tech Conference 2025. I'm honored to present the keynote on AI applications in healthcare. This field is evolving rapidly.",
            "language": "en",
            "duration_seconds": 1800,
            "timestamp": (base_time + timedelta(hours=0)).isoformat() + "Z",
            "speaker_id": "user_ahmed",
            "topic": "AI in Healthcare",
            "audio_quality": "high",
            "keywords": ["AI", "Healthcare", "Keynote", "Innovation"],
            "event_id": "tech_conf_2025",
            "session_type": "keynote"
        },

        # Italian transcriptions
        {
            "transcription_id": "aud_006",
            "transcript": "Oggi discuteremo come il machine learning sta trasformando la diagnostica medica. I miglioramenti nell'accuratezza sono davvero notevoli.",
            "language": "it",
            "duration_seconds": 2400,
            "timestamp": (base_time + timedelta(hours=2)).isoformat() + "Z",
            "speaker_id": "user_giulia",
            "topic": "ML in Medicine",
            "audio_quality": "high",
            "keywords": ["Machine Learning", "Medicina", "Diagnostica", "Accuratezza"],
            "event_id": "tech_conf_2025",
            "session_type": "panel"
        },
        {
            "transcription_id": "aud_007",
            "transcript": "Il workshop di oggi coprirà le basi del machine learning. Inizieremo con la regressione lineare e poi passeremo ad algoritmi più complessi.",
            "language": "it",
            "duration_seconds": 3600,
            "timestamp": (base_time + timedelta(hours=5)).isoformat() + "Z",
            "speaker_id": "user_marco",
            "topic": "ML Basics",
            "audio_quality": "medium",
            "keywords": ["Machine Learning", "Regressione", "Basi", "Algoritmi"],
            "event_id": "tech_conf_2025",
            "session_type": "workshop"
        },
        {
            "transcription_id": "aud_008",
            "transcript": "Benvenuti a tutti al Convegno Tecnologico 2025. Sono onorato di presentare la keynote sulle applicazioni dell'intelligenza artificiale nella sanità.",
            "language": "it",
            "duration_seconds": 1800,
            "timestamp": (base_time + timedelta(hours=0)).isoformat() + "Z",
            "speaker_id": "user_ahmed",
            "topic": "AI in Healthcare",
            "audio_quality": "high",
            "keywords": ["IA", "Sanità", "Keynote", "Tecnologia"],
            "event_id": "tech_conf_2025",
            "session_type": "keynote"
        },

        # Q&A sessions
        {
            "transcription_id": "aud_009",
            "transcript": "Thank you for that question. Yes, the AI models we discussed can be adapted for multiple languages including Arabic and Italian.",
            "language": "en",
            "duration_seconds": 300,
            "timestamp": (base_time + timedelta(hours=1, minutes=30)).isoformat() + "Z",
            "speaker_id": "user_ahmed",
            "topic": "AI in Healthcare",
            "audio_quality": "high",
            "keywords": ["Q&A", "Multilingual", "AI"],
            "event_id": "tech_conf_2025",
            "session_type": "keynote"
        },
        {
            "transcription_id": "aud_010",
            "transcript": "La domanda di Marco è molto pertinente. Sì, possiamo applicare questi concetti anche a dataset più piccoli.",
            "language": "it",
            "duration_seconds": 240,
            "timestamp": (base_time + timedelta(hours=6, minutes=15)).isoformat() + "Z",
            "speaker_id": "user_sarah",
            "topic": "ML Basics",
            "audio_quality": "medium",
            "keywords": ["Q&A", "Dataset", "Small Data"],
            "event_id": "tech_conf_2025",
            "session_type": "workshop"
        }
    ]

    return transcriptions


def create_social_media_posts_collection():
    """Create the SocialMediaPosts collection."""
    print_step("Creating SocialMediaPosts collection...")

    collection_data = {
        "collection_name": "SocialMediaPosts",
        "description": "Multilingual social media posts (tweets) from tech conference",
        "properties": [
            {"name": "post_id", "data_type": "text"},
            {"name": "content", "data_type": "text"},
            {"name": "language", "data_type": "text"},
            {"name": "timestamp", "data_type": "date"},
            {"name": "author_id", "data_type": "text"},
            {"name": "topic", "data_type": "text"},
            {"name": "sentiment", "data_type": "text"},
            {"name": "hashtags", "data_type": "text[]"},
            {"name": "event_id", "data_type": "text"},
            {"name": "location", "data_type": "text"}
        ],
        "vectorizer_config": {
            "type": "text2vec-openai",
            "model": "text-embedding-3-small"
        }
    }

    if create_collection(collection_data):
        print_success("SocialMediaPosts collection created")
        return True
    return False


def create_audio_transcriptions_collection():
    """Create the AudioTranscriptions collection."""
    print_step("Creating AudioTranscriptions collection...")

    collection_data = {
        "collection_name": "AudioTranscriptions",
        "description": "Multilingual audio transcriptions from tech conference sessions",
        "properties": [
            {"name": "transcription_id", "data_type": "text"},
            {"name": "transcript", "data_type": "text"},
            {"name": "language", "data_type": "text"},
            {"name": "duration_seconds", "data_type": "int"},
            {"name": "timestamp", "data_type": "date"},
            {"name": "speaker_id", "data_type": "text"},
            {"name": "topic", "data_type": "text"},
            {"name": "audio_quality", "data_type": "text"},
            {"name": "keywords", "data_type": "text[]"},
            {"name": "event_id", "data_type": "text"},
            {"name": "session_type", "data_type": "text"}
        ],
        "vectorizer_config": {
            "type": "text2vec-openai",
            "model": "text-embedding-3-small"
        }
    }

    if create_collection(collection_data):
        print_success("AudioTranscriptions collection created")
        return True
    return False


def main():
    """Main execution flow."""
    print(f"\n{BLUE}{'='*60}")
    print("  Elysia Cross-Collection Correlation Seed Script")
    print(f"{'='*60}{RESET}\n")

    print(f"Backend URL: {BACKEND_URL}")
    print(f"User ID: {USER_ID}\n")

    # Step 1: Create collections
    print_step("Step 1: Creating collections...")
    if not create_social_media_posts_collection():
        print_error("Failed to create SocialMediaPosts collection")
        sys.exit(1)

    if not create_audio_transcriptions_collection():
        print_error("Failed to create AudioTranscriptions collection")
        sys.exit(1)

    print_success("All collections created successfully\n")

    # Step 2: Insert social media posts
    print_step("Step 2: Inserting social media posts...")
    posts = generate_social_media_posts()
    if not insert_objects("SocialMediaPosts", posts):
        print_error("Failed to insert social media posts")
        sys.exit(1)
    print()

    # Step 3: Insert audio transcriptions
    print_step("Step 3: Inserting audio transcriptions...")
    transcriptions = generate_audio_transcriptions()
    if not insert_objects("AudioTranscriptions", transcriptions):
        print_error("Failed to insert audio transcriptions")
        sys.exit(1)
    print()

    # Summary
    print(f"{GREEN}{'='*60}")
    print("  ✓ Seed completed successfully!")
    print(f"{'='*60}{RESET}\n")

    print("Summary:")
    print(f"  • SocialMediaPosts: {len(posts)} posts inserted")
    print(f"  • AudioTranscriptions: {len(transcriptions)} transcripts inserted")
    print(f"  • Total records: {len(posts) + len(transcriptions)}")
    print(f"\n{YELLOW}Next steps:{RESET}")
    print("  1. Analyze collections in the Elysia frontend")
    print("  2. Test cross-collection queries")
    print("  3. Explore multilingual correlation\n")


if __name__ == "__main__":
    main()
