"""
Utility functions for Arabic text processing and normalization.

This module provides functions to normalize Arabic text for better semantic search
and embedding generation, particularly important for handling diacritics, 
character variants, and other Arabic-specific text processing needs.

Uses PyArabic when available for robust normalization, with regex fallback.
"""

import re
from typing import Optional

# Try to import PyArabic for advanced Arabic processing
try:
    import pyarabic.araby as araby
    PYARABIC_AVAILABLE = True
except ImportError:
    PYARABIC_AVAILABLE = False
    import warnings
    warnings.warn(
        "PyArabic not available. Using regex-based fallback for Arabic normalization. "
        "Install with: pip install pyarabic",
        UserWarning
    )

import re
from typing import Optional


def normalize_arabic_text(text: str) -> str:
    """
    Normalize Arabic text for better semantic search and embedding generation.
    
    Uses PyArabic when available for robust normalization, with regex fallback.
    
    This function performs several normalization steps:
    1. Removes Arabic diacritics (Tashkeel) - َ ُ ِ ً ٌ ٍ ْ ّ etc.
    2. Normalizes Alef variants (إ أ آ) to standard Alef (ا)
    3. Normalizes Hamza variants (ؤ ئ) to standard Hamza (ء)
    4. Removes Tatweel (Arabic elongation character ـ)
    5. Normalizes Lam-Alef ligatures (PyArabic only)
    6. Normalizes multiple whitespace to single spaces
    
    Args:
        text: Input Arabic text to normalize
        
    Returns:
        Normalized Arabic text suitable for embedding generation
        
    Example:
        >>> normalize_arabic_text("مَرْحَباً بِكُمْ")
        'مرحبا بكم'
        >>> normalize_arabic_text("الذكاء الإصطناعي")
        'الذكاء الاصطناعي'
    """
    if not text:
        return text
    
    # Check if text contains Arabic characters
    if not is_arabic_text(text):
        return text
    
    if PYARABIC_AVAILABLE:
        # Use PyArabic for robust normalization
        try:
            # Remove diacritics (Tashkeel)
            text = araby.strip_tashkeel(text)
            
            # Remove Tatweel (elongation character)
            text = araby.strip_tatweel(text)
            
            # Normalize Hamza variants
            text = araby.normalize_hamza(text)
            
            # Normalize Lam-Alef ligatures
            text = araby.normalize_lamalef(text)
            
            # Normalize Alef variants (additional step)
            text = normalize_alef_variants(text)
            
        except Exception as e:
            # Fallback to regex if PyArabic fails
            import warnings
            warnings.warn(f"PyArabic processing failed, using fallback: {e}")
            text = _normalize_arabic_fallback(text)
    else:
        # Use regex-based fallback
        text = _normalize_arabic_fallback(text)
    
    # Normalize multiple whitespace to single spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def _normalize_arabic_fallback(text: str) -> str:
    """
    Fallback Arabic normalization using regex when PyArabic is not available.
    
    Args:
        text: Input Arabic text
        
    Returns:
        Normalized text using regex patterns
    """
    # Remove Arabic diacritics
    text = remove_arabic_diacritics(text)
    
    # Normalize Alef variants
    text = normalize_alef_variants(text)
    
    # Normalize Hamza variants to standard Hamza
    text = re.sub(r'[ؤئ]', 'ء', text)
    
    # Remove Tatweel (Arabic elongation character)
    text = text.replace('\u0640', '')
    
    return text


def is_arabic_text(text: str, threshold: float = 0.3) -> bool:
    """
    Check if text contains significant Arabic content.
    
    Args:
        text: Text to check
        threshold: Minimum proportion of Arabic characters (0.0 to 1.0)
                  Default 0.3 means at least 30% Arabic characters
    
    Returns:
        True if text contains Arabic above threshold, False otherwise
        
    Examples:
        >>> is_arabic_text("مرحبا")
        True
        >>> is_arabic_text("Hello مرحبا World")
        True
        >>> is_arabic_text("Hello World")
        False
    """
    if not text:
        return False
    
    # Count Arabic characters (U+0600 to U+06FF)
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    
    # Count total non-whitespace characters
    total_chars = sum(1 for c in text if not c.isspace())
    
    if total_chars == 0:
        return False
    
    return (arabic_chars / total_chars) >= threshold


def preprocess_for_embedding(
    text: str, 
    language: Optional[str] = None,
    auto_detect: bool = True
) -> str:
    """
    Preprocess text for embedding generation.
    
    Applies language-specific normalization:
    - For Arabic: applies normalize_arabic_text
    - For other languages: returns text as-is
    
    Args:
        text: Text to preprocess
        language: ISO 639-1 language code (e.g., 'ar', 'en', 'it')
                 If None, will auto-detect if auto_detect=True
        auto_detect: If True and language is None, auto-detects Arabic
    
    Returns:
        Preprocessed text ready for embedding
        
    Examples:
        >>> preprocess_for_embedding("مَرْحَباً", language="ar")
        'مرحبا'
        >>> preprocess_for_embedding("Hello", language="en")
        'Hello'
        >>> preprocess_for_embedding("مَرْحَباً")  # auto-detect
        'مرحبا'
    """
    if not text:
        return text
    
    # Auto-detect Arabic if requested
    if language is None and auto_detect:
        if is_arabic_text(text):
            language = "ar"
    
    # Apply Arabic normalization
    if language == "ar":
        return normalize_arabic_text(text)
    
    # For other languages, return as-is
    return text


def get_normalization_stats(original: str, normalized: str) -> dict:
    """
    Get statistics about text normalization.
    
    Useful for debugging and understanding what changed during normalization.
    
    Args:
        original: Original text before normalization
        normalized: Text after normalization
    
    Returns:
        Dictionary with normalization statistics:
        - chars_removed: Number of characters removed
        - chars_changed: Number of characters changed
        - length_before: Original length
        - length_after: Normalized length
        - reduction_percent: Percentage of characters removed
        
    Examples:
        >>> original = "مَرْحَباً"
        >>> normalized = normalize_arabic_text(original)
        >>> stats = get_normalization_stats(original, normalized)
        >>> stats['chars_removed']
        3
    """
    chars_removed = len(original) - len(normalized)
    length_before = len(original)
    length_after = len(normalized)
    
    # Calculate how many characters were changed (not just removed)
    min_len = min(length_before, length_after)
    chars_changed = sum(1 for i in range(min_len) if original[i] != normalized[i])
    
    reduction_percent = (chars_removed / length_before * 100) if length_before > 0 else 0
    
    return {
        "chars_removed": chars_removed,
        "chars_changed": chars_changed,
        "length_before": length_before,
        "length_after": length_after,
        "reduction_percent": round(reduction_percent, 2)
    }


def remove_arabic_diacritics(text: str) -> str:
    """
    Remove Arabic diacritics (Tashkeel) from text.

    Removes vowel marks and other diacritical marks used in Arabic script.

    Args:
        text: Input text with potential diacritics

    Returns:
        Text with diacritics removed

    Examples:
        >>> remove_arabic_diacritics("مَرْحَباً")
        'مرحبا'
    """
    if not text:
        return text

    # Unicode range for Arabic diacritics (Tashkeel)
    # U+064B to U+065F: Diacritical marks
    # U+0670: Alef Superscript
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    return arabic_diacritics.sub('', text)


def normalize_alef_variants(text: str) -> str:
    """
    Normalize different Alef variants to standard Alef.

    Arabic has multiple Alef forms that should be normalized for
    consistent text matching and embedding generation.

    Normalizes:
    - إ (Alef with Hamza below) → ا
    - أ (Alef with Hamza above) → ا
    - آ (Alef with Madda) → ا

    Args:
        text: Input text with potential Alef variants

    Returns:
        Text with normalized Alef characters

    Examples:
        >>> normalize_alef_variants("الإسلام")
        'الاسلام'
        >>> normalize_alef_variants("أحمد")
        'احمد'
    """
    if not text:
        return text

    # Normalize all Alef variants to standard Alef (U+0627)
    # U+0625: Alef with Hamza below (إ)
    # U+0623: Alef with Hamza above (أ)
    # U+0622: Alef with Madda above (آ)
    return re.sub(r'[إأآا]', 'ا', text)


def clean_for_display(text: str) -> str:
    """
    Clean Arabic text for display purposes.

    Unlike normalize_arabic_text(), this preserves diacritics for readability
    but removes only the Tatweel (elongation character) which is purely decorative.

    Use this when you want to clean text for display while maintaining
    original pronunciation marks.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text suitable for display

    Examples:
        >>> clean_for_display("مَرْحَـــباً")  # Note elongation
        'مَرْحَباً'
        >>> clean_for_display("الـــذكاء")
        'الذكاء'
    """
    if not text:
        return text

    # Remove only Tatweel (U+0640) - the elongation character
    # Preserve all diacritics for proper pronunciation
    text = text.replace('\u0640', '')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text
