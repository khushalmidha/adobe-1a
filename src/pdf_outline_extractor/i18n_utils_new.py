"""
Internationalization utilities for multilingual text processing.
Pure Python implementation without ML dependencies.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any


def normalize_text(text: str) -> str:
    """
    Normalize text using Unicode NFC normalization while preserving
    tabs, newlines, and control characters as literal parts.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Normalize Unicode to NFC form
    normalized = unicodedata.normalize('NFC', text)
    
    # Preserve whitespace characters as they are part of the text
    # Don't strip or modify tabs, newlines, etc.
    return normalized


def detect_language(text: str) -> str:
    """
    Simple language detection based on character sets.
    Fallback implementation without ML dependencies.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code (ISO 639-1)
    """
    if not text or len(text.strip()) < 3:
        return "en"  # Default to English
    
    # Character set analysis
    char_counts = {
        'latin': 0,
        'arabic': 0,
        'hebrew': 0,
        'cyrillic': 0,
        'cjk': 0,
        'greek': 0,
        'total': 0
    }
    
    for char in text:
        code_point = ord(char)
        char_counts['total'] += 1
        
        # Latin scripts (including extended)
        if (0x0000 <= code_point <= 0x024F) or (0x1E00 <= code_point <= 0x1EFF):
            char_counts['latin'] += 1
        # Arabic
        elif (0x0600 <= code_point <= 0x06FF) or (0x0750 <= code_point <= 0x077F):
            char_counts['arabic'] += 1
        # Hebrew
        elif 0x0590 <= code_point <= 0x05FF:
            char_counts['hebrew'] += 1
        # Cyrillic
        elif 0x0400 <= code_point <= 0x04FF:
            char_counts['cyrillic'] += 1
        # CJK
        elif (0x4E00 <= code_point <= 0x9FFF) or (0x3400 <= code_point <= 0x4DBF):
            char_counts['cjk'] += 1
        # Greek
        elif 0x0370 <= code_point <= 0x03FF:
            char_counts['greek'] += 1
    
    if char_counts['total'] == 0:
        return "en"
    
    # Determine dominant script
    script_ratios = {
        script: count / char_counts['total'] 
        for script, count in char_counts.items() 
        if script != 'total'
    }
    
    # Find dominant script
    dominant_script = max(script_ratios.items(), key=lambda x: x[1])
    
    # Map script to language
    if dominant_script[1] > 0.3:  # At least 30% of characters
        script_to_lang = {
            'arabic': 'ar',
            'hebrew': 'he',
            'cyrillic': 'ru',
            'cjk': 'zh',  # Default to Chinese for CJK
            'greek': 'el',
            'latin': 'en'  # Default to English for Latin
        }
        return script_to_lang.get(dominant_script[0], 'en')
    
    return "en"  # Default to English


def is_rtl_language(lang_code: str) -> bool:
    """
    Check if a language uses right-to-left writing.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        True if language is RTL
    """
    rtl_languages = {'ar', 'he', 'fa', 'ur', 'yi', 'ji'}
    return lang_code.lower() in rtl_languages


def clean_text_for_analysis(text: str) -> str:
    """
    Clean text for analysis while preserving intentional formatting.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize Unicode
    cleaned = normalize_text(text)
    
    # Remove zero-width characters but preserve other whitespace
    cleaned = re.sub(r'[\u200B-\u200D\uFEFF]', '', cleaned)
    
    # Normalize excessive whitespace (but preserve single tabs/newlines)
    cleaned = re.sub(r'  +', ' ', cleaned)  # Multiple spaces to single
    
    return cleaned


def extract_text_features(text: str) -> Dict[str, Any]:
    """
    Extract features from text for analysis.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of text features
    """
    if not text:
        return {
            'length': 0,
            'char_count': 0,
            'word_count': 0,
            'has_digits': False,
            'has_punctuation': False,
            'is_caps': False,
            'is_title_case': False,
            'language': 'en',
            'is_rtl': False
        }
    
    # Basic metrics
    length = len(text)
    char_count = len(text.strip())
    words = text.split()
    word_count = len(words)
    
    # Content analysis
    has_digits = bool(re.search(r'\d', text))
    has_punctuation = bool(re.search(r'[^\w\s]', text))
    is_caps = text.isupper() and char_count > 3
    is_title_case = text.istitle()
    
    # Language detection
    language = detect_language(text)
    is_rtl = is_rtl_language(language)
    
    return {
        'length': length,
        'char_count': char_count,
        'word_count': word_count,
        'has_digits': has_digits,
        'has_punctuation': has_punctuation,
        'is_caps': is_caps,
        'is_title_case': is_title_case,
        'language': language,
        'is_rtl': is_rtl
    }


def handle_special_characters(text: str) -> str:
    """
    Handle special characters including diacritics, combining characters,
    emoji, and unusual punctuation.
    
    Args:
        text: Input text with special characters
        
    Returns:
        Processed text
    """
    if not text:
        return ""
    
    # Normalize to ensure proper combining character handling
    normalized = unicodedata.normalize('NFC', text)
    
    # Handle different character categories
    processed_chars = []
    
    for char in normalized:
        category = unicodedata.category(char)
        
        # Keep most characters as-is
        if category.startswith('L'):  # Letters
            processed_chars.append(char)
        elif category.startswith('N'):  # Numbers
            processed_chars.append(char)
        elif category.startswith('P'):  # Punctuation
            processed_chars.append(char)
        elif category.startswith('S'):  # Symbols (including emoji)
            processed_chars.append(char)
        elif category.startswith('Z'):  # Separators (spaces, etc.)
            processed_chars.append(char)
        elif category.startswith('M'):  # Marks (combining characters)
            processed_chars.append(char)
        elif category.startswith('C'):  # Control characters
            # Preserve tabs, newlines as they might be intentional
            if char in '\t\n\r':
                processed_chars.append(char)
            else:
                # Skip other control characters
                continue
        else:
            # Keep other characters
            processed_chars.append(char)
    
    return ''.join(processed_chars)


def validate_heading_text(text: str, min_length: int = 2, max_length: int = 200) -> bool:
    """
    Validate if text is suitable for a heading.
    
    Args:
        text: Text to validate
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length
        
    Returns:
        True if text is valid for heading
    """
    if not text:
        return False
    
    cleaned = text.strip()
    
    # Length check
    if len(cleaned) < min_length or len(cleaned) > max_length:
        return False
    
    # Content check - should have some alphanumeric content
    if not re.search(r'[a-zA-Z0-9\u00C0-\u024F\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u4E00-\u9FFF]', cleaned):
        return False
    
    # Reject if mostly punctuation or whitespace
    alphanumeric_count = len(re.findall(r'[a-zA-Z0-9\u00C0-\u024F\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u4E00-\u9FFF]', cleaned))
    if alphanumeric_count < len(cleaned) * 0.3:  # At least 30% alphanumeric
        return False
    
    return True


def normalize_heading_text(text: str) -> str:
    """
    Normalize heading text for consistent processing.
    
    Args:
        text: Raw heading text
        
    Returns:
        Normalized heading text
    """
    if not text:
        return ""
    
    # Apply all normalization steps
    normalized = normalize_text(text)
    normalized = handle_special_characters(normalized)
    normalized = clean_text_for_analysis(normalized)
    
    # Final cleanup
    normalized = normalized.strip()
    
    return normalized
