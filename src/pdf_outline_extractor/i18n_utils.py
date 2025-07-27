"""Internationalization utilities for multilingual text processing.

This module handles language detection, Unicode normalization, and 
text processing for various scripts including RTL and CJK languages.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any
try:
    import unicodedata2
    # Use unicodedata2 for better Unicode support if available
    unicodedata = unicodedata2
except ImportError:
    pass

try:
    from langdetect import detect, detect_langs, LangDetectException
except ImportError:
    # Fallback if langdetect is not available
    def detect(text: str) -> str:
        return 'en'
    
    def detect_langs(text: str) -> List[Any]:
        return []
    
    class LangDetectException(Exception):
        pass


class TextNormalizer:
    """Handles text normalization and language detection for multilingual PDFs."""
    
    def __init__(self, default_language: str = 'en'):
        """Initialize text normalizer.
        
        Args:
            default_language: Default language code to use when detection fails
        """
        self.default_language = default_language
        
        # Script ranges for different writing systems
        self.script_ranges = {
            'latin': [(0x0000, 0x024F), (0x1E00, 0x1EFF)],
            'arabic': [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)],
            'hebrew': [(0x0590, 0x05FF)],
            'cyrillic': [(0x0400, 0x04FF), (0x0500, 0x052F)],
            'greek': [(0x0370, 0x03FF)],
            'cjk': [
                (0x4E00, 0x9FFF),  # CJK Unified Ideographs
                (0x3400, 0x4DBF),  # CJK Extension A
                (0x3040, 0x309F),  # Hiragana
                (0x30A0, 0x30FF),  # Katakana
                (0xAC00, 0xD7AF),  # Hangul
            ],
            'devanagari': [(0x0900, 0x097F)],
            'thai': [(0x0E00, 0x0E7F)],
        }
        
        # RTL language codes
        self.rtl_languages = {
            'ar', 'he', 'fa', 'ur', 'ps', 'sd', 'ku', 'dv'
        }
        
        # Common abbreviations and stopwords for better language detection
        self.language_markers = {
            'en': ['the', 'and', 'of', 'to', 'in', 'for', 'with', 'on'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das'],
            'it': ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un'],
            'pt': ['o', 'de', 'que', 'e', 'do', 'da', 'em', 'um'],
            'ru': ['в', 'и', 'не', 'на', 'с', 'то', 'что', 'он'],
            'zh': ['的', '是', '在', '有', '我', '他', '这', '了'],
            'ja': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て'],
            'ar': ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي'],
            'he': ['של', 'את', 'על', 'אל', 'זה', 'זו', 'הוא', 'היא'],
        }

    def normalize_text(self, text: str) -> str:
        """Normalize Unicode text using NFC normalization.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text with preserved formatting characters
        """
        if not text:
            return text
            
        # Apply NFC normalization
        normalized = unicodedata.normalize('NFC', text)
        
        # Preserve important whitespace and control characters
        # Replace multiple spaces with single space, but preserve tabs and newlines
        normalized = re.sub(r'[ ]+', ' ', normalized)
        
        return normalized

    def detect_language(self, text: str, min_length: int = 10) -> Tuple[str, float]:
        """Detect the language of a text span.
        
        Args:
            text: Text to analyze
            min_length: Minimum text length for reliable detection
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text or len(text.strip()) < min_length:
            return self.default_language, 0.0
        
        # Clean text for language detection
        clean_text = self._clean_for_detection(text)
        
        if len(clean_text) < min_length:
            return self.default_language, 0.0
        
        try:
            # Use langdetect for primary detection
            detected_lang = detect(clean_text)
            
            # Get confidence scores
            lang_probs = detect_langs(clean_text)
            confidence = 0.0
            
            for lang_prob in lang_probs:
                if lang_prob.lang == detected_lang:
                    confidence = lang_prob.prob
                    break
            
            # Verify with script analysis
            script_lang = self._detect_by_script(text)
            if script_lang and script_lang != detected_lang:
                # If script suggests different language, lower confidence
                confidence *= 0.7
            
            return detected_lang, confidence
            
        except (LangDetectException, Exception):
            # Fallback to script-based detection
            script_lang = self._detect_by_script(text)
            if script_lang:
                return script_lang, 0.5
            
            # Final fallback using language markers
            marker_lang = self._detect_by_markers(clean_text)
            return marker_lang, 0.3

    def _clean_for_detection(self, text: str) -> str:
        """Clean text for better language detection.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text suitable for language detection
        """
        # Remove URLs, emails, and numbers
        clean = re.sub(r'https?://\S+|www\.\S+', '', text)
        clean = re.sub(r'\b\w+@\w+\.\w+\b', '', clean)
        clean = re.sub(r'\b\d+\b', '', clean)
        
        # Remove excessive punctuation but keep sentence structure
        clean = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', ' ', clean, flags=re.UNICODE)
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()

    def _detect_by_script(self, text: str) -> Optional[str]:
        """Detect language based on Unicode script ranges.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code or None if detection fails
        """
        char_counts = {}
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                script = self._get_char_script(ord(char))
                if script:
                    char_counts[script] = char_counts.get(script, 0) + 1
        
        if total_chars == 0:
            return None
        
        # Find dominant script
        dominant_script = max(char_counts.items(), key=lambda x: x[1], default=(None, 0))[0]
        
        # Map script to language
        script_to_lang = {
            'arabic': 'ar',
            'hebrew': 'he',
            'cyrillic': 'ru',
            'greek': 'el',
            'cjk': 'zh',  # Default to Chinese for CJK
            'devanagari': 'hi',
            'thai': 'th',
        }
        
        return script_to_lang.get(dominant_script)

    def _get_char_script(self, codepoint: int) -> Optional[str]:
        """Get the script for a Unicode codepoint.
        
        Args:
            codepoint: Unicode codepoint
            
        Returns:
            Script name or None
        """
        for script, ranges in self.script_ranges.items():
            for start, end in ranges:
                if start <= codepoint <= end:
                    return script
        return None

    def _detect_by_markers(self, text: str) -> str:
        """Detect language using common word markers.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (defaults to default_language)
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        scores = {}
        for lang, markers in self.language_markers.items():
            score = sum(1 for marker in markers if marker in words)
            if score > 0:
                scores[lang] = score / len(markers)
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return self.default_language

    def is_rtl_language(self, language_code: str) -> bool:
        """Check if a language uses right-to-left writing.
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if language is RTL
        """
        return language_code in self.rtl_languages

    def detect_text_direction(self, text: str) -> str:
        """Detect text direction based on content.
        
        Args:
            text: Text to analyze
            
        Returns:
            'rtl', 'ltr', or 'mixed'
        """
        rtl_chars = 0
        ltr_chars = 0
        
        for char in text:
            if char.isalpha():
                script = self._get_char_script(ord(char))
                if script in ['arabic', 'hebrew']:
                    rtl_chars += 1
                else:
                    ltr_chars += 1
        
        total_chars = rtl_chars + ltr_chars
        if total_chars == 0:
            return 'ltr'
        
        rtl_ratio = rtl_chars / total_chars
        
        if rtl_ratio > 0.7:
            return 'rtl'
        elif rtl_ratio > 0.3:
            return 'mixed'
        else:
            return 'ltr'

    def process_multilingual_text(self, text: str) -> Dict[str, Any]:
        """Process text with full multilingual analysis.
        
        Args:
            text: Text to process
            
        Returns:
            Dictionary with normalized text and language information
        """
        if not text:
            return {
                'normalized': '',
                'language': self.default_language,
                'confidence': 0.0,
                'direction': 'ltr',
                'script': 'latin',
                'length': 0
            }
        
        normalized = self.normalize_text(text)
        language, confidence = self.detect_language(normalized)
        direction = self.detect_text_direction(normalized)
        
        # Determine dominant script
        script_counts = {}
        for char in normalized:
            if char.isalpha():
                script = self._get_char_script(ord(char))
                if script:
                    script_counts[script] = script_counts.get(script, 0) + 1
        
        dominant_script = 'latin'  # default
        if script_counts:
            dominant_script = max(script_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'normalized': normalized,
            'language': language,
            'confidence': confidence,
            'direction': direction,
            'script': dominant_script,
            'length': len(normalized),
            'is_rtl': self.is_rtl_language(language)
        }

    def extract_clean_heading_text(self, text: str) -> str:
        """Extract clean heading text, removing numbering and bullets.
        
        Args:
            text: Raw heading text
            
        Returns:
            Cleaned heading text
        """
        # Normalize first
        clean_text = self.normalize_text(text)
        
        # Remove common numbering patterns
        patterns_to_remove = [
            r'^\s*\d+\.?\s*',  # 1. or 1
            r'^\s*\d+\.\d+\.?\s*',  # 1.1. or 1.1
            r'^\s*\d+\.\d+\.\d+\.?\s*',  # 1.1.1. or 1.1.1
            r'^\s*[a-zA-Z]\.?\s*',  # a. or A.
            r'^\s*[ivxlcdm]+\.?\s*',  # roman numerals
            r'^\s*[IVXLCDM]+\.?\s*',  # roman numerals uppercase
            r'^\s*[-•‣⁃▪▫◦‰‱\*\+»]\s*',  # bullets
        ]
        
        for pattern in patterns_to_remove:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE | re.UNICODE)
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
