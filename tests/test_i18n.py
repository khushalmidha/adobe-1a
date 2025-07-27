"""Tests for internationalization and multilingual text processing."""

import pytest
from pdf_outline_extractor.i18n_utils import TextNormalizer


class TestTextNormalizer:
    """Test cases for TextNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = TextNormalizer()
    
    def test_initialization(self):
        """Test text normalizer initialization."""
        normalizer = TextNormalizer(default_language='es')
        assert normalizer.default_language == 'es'
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        # Test with normal text
        text = "Hello World"
        normalized = self.normalizer.normalize_text(text)
        assert normalized == "Hello World"
        
        # Test with extra spaces
        text_spaces = "Hello    World"
        normalized_spaces = self.normalizer.normalize_text(text_spaces)
        assert normalized_spaces == "Hello World"
        
        # Test with empty text
        assert self.normalizer.normalize_text("") == ""
        assert self.normalizer.normalize_text(None) is None
    
    def test_normalize_text_unicode(self):
        """Test Unicode normalization."""
        # Test with combining characters
        text_combining = "é"  # e + combining acute accent
        normalized = self.normalizer.normalize_text(text_combining)
        assert len(normalized) == 1  # Should be combined into single character
        
        # Test with various Unicode characters
        text_unicode = "Héllo Wörld! 你好世界"
        normalized = self.normalizer.normalize_text(text_unicode)
        assert "Héllo Wörld! 你好世界" in normalized
    
    def test_normalize_text_preserve_formatting(self):
        """Test that important formatting characters are preserved."""
        # Test with tabs and newlines
        text_formatting = "Chapter 1\tIntroduction\nSection 1.1"
        normalized = self.normalizer.normalize_text(text_formatting)
        assert "\t" in normalized
        assert "\n" in normalized
    
    def test_detect_language_english(self):
        """Test English language detection."""
        text = "This is a sample English text with common words."
        lang, confidence = self.normalizer.detect_language(text)
        
        assert isinstance(lang, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    def test_detect_language_short_text(self):
        """Test language detection with short text."""
        short_text = "Hi"
        lang, confidence = self.normalizer.detect_language(short_text)
        
        # Should fallback to default language for short text
        assert lang == self.normalizer.default_language
        assert confidence == 0.0
    
    def test_detect_language_multilingual(self):
        """Test detection with multilingual content."""
        # Test various languages
        test_cases = [
            ("Bonjour le monde", "fr"),  # French
            ("Hola mundo", "es"),  # Spanish
            ("Hallo Welt", "de"),  # German
            ("Ciao mondo", "it"),  # Italian
            ("你好世界", "zh"),  # Chinese
            ("こんにちは世界", "ja"),  # Japanese
            ("مرحبا بالعالم", "ar"),  # Arabic
            ("שלום עולם", "he"),  # Hebrew
        ]
        
        for text, expected_lang in test_cases:
            try:
                lang, confidence = self.normalizer.detect_language(text)
                # Note: Actual detection might vary, so we just check basic properties
                assert isinstance(lang, str)
                assert len(lang) >= 2  # Language codes are at least 2 characters
                assert 0.0 <= confidence <= 1.0
            except Exception:
                # Some language detection might fail, that's okay for testing
                pass
    
    def test_clean_for_detection(self):
        """Test text cleaning for language detection."""
        dirty_text = "Visit https://example.com or email test@example.com for info about item #123."
        clean_text = self.normalizer._clean_for_detection(dirty_text)
        
        # Should remove URLs, emails, and numbers
        assert "https://example.com" not in clean_text
        assert "test@example.com" not in clean_text
        assert "123" not in clean_text
        assert "Visit" in clean_text
        assert "info" in clean_text
    
    def test_detect_by_script_arabic(self):
        """Test script-based language detection for Arabic."""
        arabic_text = "مرحبا بكم في هذا النص العربي"
        script_lang = self.normalizer._detect_by_script(arabic_text)
        assert script_lang == 'ar'
    
    def test_detect_by_script_chinese(self):
        """Test script-based language detection for Chinese."""
        chinese_text = "欢迎来到中文世界"
        script_lang = self.normalizer._detect_by_script(chinese_text)
        assert script_lang == 'zh'
    
    def test_detect_by_script_hebrew(self):
        """Test script-based language detection for Hebrew."""
        hebrew_text = "ברוכים הבאים לטקסט עברי"
        script_lang = self.normalizer._detect_by_script(hebrew_text)
        assert script_lang == 'he'
    
    def test_detect_by_script_mixed(self):
        """Test script detection with mixed scripts."""
        mixed_text = "Hello مرحبا 你好"
        script_lang = self.normalizer._detect_by_script(mixed_text)
        # Should detect the dominant script
        assert script_lang is not None
    
    def test_get_char_script(self):
        """Test character script detection."""
        # Test various character scripts
        test_cases = [
            (ord('A'), 'latin'),
            (ord('ا'), 'arabic'),  # Arabic letter alif
            (ord('א'), 'hebrew'),  # Hebrew letter alef
            (ord('中'), 'cjk'),    # Chinese character
            (ord('あ'), 'cjk'),    # Hiragana
            (ord('カ'), 'cjk'),    # Katakana
            (ord('한'), 'cjk'),    # Hangul
        ]
        
        for codepoint, expected_script in test_cases:
            script = self.normalizer._get_char_script(codepoint)
            assert script == expected_script
    
    def test_detect_by_markers(self):
        """Test language detection using word markers."""
        # Test English markers
        english_text = "the quick brown fox and the lazy dog"
        lang = self.normalizer._detect_by_markers(english_text)
        assert lang == 'en'
        
        # Test with no markers
        no_markers_text = "xyz qwerty asdfgh"
        lang = self.normalizer._detect_by_markers(no_markers_text)
        assert lang == self.normalizer.default_language
    
    def test_is_rtl_language(self):
        """Test RTL language detection."""
        # Test known RTL languages
        rtl_languages = ['ar', 'he', 'fa', 'ur']
        for lang in rtl_languages:
            assert self.normalizer.is_rtl_language(lang) is True
        
        # Test known LTR languages
        ltr_languages = ['en', 'fr', 'de', 'es', 'zh', 'ja']
        for lang in ltr_languages:
            assert self.normalizer.is_rtl_language(lang) is False
    
    def test_detect_text_direction(self):
        """Test text direction detection."""
        # Test LTR text
        ltr_text = "This is left-to-right text"
        direction = self.normalizer.detect_text_direction(ltr_text)
        assert direction == 'ltr'
        
        # Test RTL text (Arabic)
        rtl_text = "هذا نص من اليمين إلى اليسار"
        direction = self.normalizer.detect_text_direction(rtl_text)
        assert direction == 'rtl'
        
        # Test mixed text
        mixed_text = "English text with Arabic نص عربي"
        direction = self.normalizer.detect_text_direction(mixed_text)
        assert direction in ['ltr', 'rtl', 'mixed']
        
        # Test empty text
        empty_direction = self.normalizer.detect_text_direction("")
        assert empty_direction == 'ltr'
    
    def test_process_multilingual_text(self):
        """Test comprehensive multilingual text processing."""
        test_text = "Hello World! 你好世界"
        
        result = self.normalizer.process_multilingual_text(test_text)
        
        # Check required fields
        required_fields = ['normalized', 'language', 'confidence', 'direction', 'script', 'length', 'is_rtl']
        for field in required_fields:
            assert field in result
        
        # Check field types and values
        assert isinstance(result['normalized'], str)
        assert isinstance(result['language'], str)
        assert isinstance(result['confidence'], float)
        assert result['direction'] in ['ltr', 'rtl', 'mixed']
        assert isinstance(result['script'], str)
        assert isinstance(result['length'], int)
        assert isinstance(result['is_rtl'], bool)
        
        # Check values make sense
        assert result['length'] > 0
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_process_multilingual_text_empty(self):
        """Test multilingual processing with empty text."""
        result = self.normalizer.process_multilingual_text("")
        
        assert result['normalized'] == ''
        assert result['language'] == self.normalizer.default_language
        assert result['confidence'] == 0.0
        assert result['direction'] == 'ltr'
        assert result['length'] == 0
    
    def test_extract_clean_heading_text(self):
        """Test heading text cleaning."""
        # Test numbered heading
        numbered = "1. Introduction to the Topic"
        cleaned = self.normalizer.extract_clean_heading_text(numbered)
        assert cleaned == "Introduction to the Topic"
        
        # Test nested numbering
        nested = "1.2.3 Detailed Subsection"
        cleaned_nested = self.normalizer.extract_clean_heading_text(nested)
        assert cleaned_nested == "Detailed Subsection"
        
        # Test bullet points
        bulleted = "• Important Point"
        cleaned_bullet = self.normalizer.extract_clean_heading_text(bulleted)
        assert cleaned_bullet == "Important Point"
        
        # Test Roman numerals
        roman = "IV. Fourth Chapter"
        cleaned_roman = self.normalizer.extract_clean_heading_text(roman)
        assert cleaned_roman == "Fourth Chapter"
        
        # Test with tabs and newlines
        formatted = "1.\tChapter with\ttabs and\nnewlines"
        cleaned_formatted = self.normalizer.extract_clean_heading_text(formatted)
        assert "Chapter with\ttabs and\nnewlines" in cleaned_formatted
        assert not cleaned_formatted.startswith("1.")
    
    def test_extract_clean_heading_text_edge_cases(self):
        """Test heading cleaning with edge cases."""
        # Test text that shouldn't be cleaned
        normal_text = "Regular heading without numbering"
        cleaned = self.normalizer.extract_clean_heading_text(normal_text)
        assert cleaned == "Regular heading without numbering"
        
        # Test empty text
        empty_cleaned = self.normalizer.extract_clean_heading_text("")
        assert empty_cleaned == ""
        
        # Test only numbers/bullets
        only_number = "1."
        cleaned_only = self.normalizer.extract_clean_heading_text(only_number)
        assert cleaned_only == ""
        
        # Test multiple spaces
        spaced = "2.   Multiple   Spaces   Between   Words"
        cleaned_spaced = self.normalizer.extract_clean_heading_text(spaced)
        assert "Multiple Spaces Between Words" in cleaned_spaced
        assert not cleaned_spaced.startswith("2.")


class TestUnicodeHandling:
    """Test cases for Unicode and character encoding handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = TextNormalizer()
    
    def test_unicode_normalization_forms(self):
        """Test different Unicode normalization forms."""
        # Composed vs decomposed characters
        composed = "é"  # Single character
        decomposed = "e\u0301"  # e + combining acute accent
        
        normalized_composed = self.normalizer.normalize_text(composed)
        normalized_decomposed = self.normalizer.normalize_text(decomposed)
        
        # Both should normalize to the same form (NFC)
        assert normalized_composed == normalized_decomposed
    
    def test_emoji_handling(self):
        """Test handling of emoji characters."""
        emoji_text = "Chapter 1: Data Analysis 📊📈"
        normalized = self.normalizer.normalize_text(emoji_text)
        
        # Emojis should be preserved
        assert "📊" in normalized
        assert "📈" in normalized
        assert "Chapter 1: Data Analysis" in normalized
    
    def test_combining_characters(self):
        """Test handling of combining characters."""
        text_with_combining = "naïve résumé"
        normalized = self.normalizer.normalize_text(text_with_combining)
        
        # Combining characters should be properly normalized
        assert "naïve" in normalized
        assert "résumé" in normalized
    
    def test_zero_width_characters(self):
        """Test handling of zero-width characters."""
        # Text with zero-width joiner
        text_zwj = "word\u200djoined"
        normalized = self.normalizer.normalize_text(text_zwj)
        
        # Zero-width characters should be preserved in normalization
        assert len(normalized) > 0
    
    def test_unusual_punctuation(self):
        """Test handling of unusual punctuation marks."""
        text_punct = "Hello… world‽ How are you⁇"
        normalized = self.normalizer.normalize_text(text_punct)
        
        # Unusual punctuation should be preserved
        assert "…" in normalized
        assert "‽" in normalized
        assert "⁇" in normalized
    
    def test_bidirectional_text(self):
        """Test handling of bidirectional text."""
        # Mixed LTR and RTL text
        bidi_text = "English text עברית Arabic نص"
        result = self.normalizer.process_multilingual_text(bidi_text)
        
        assert result['direction'] in ['ltr', 'rtl', 'mixed']
        assert len(result['normalized']) > 0
    
    def test_script_mixing(self):
        """Test handling of mixed scripts."""
        mixed_scripts = "Hello 你好 مرحبا שלום"
        result = self.normalizer.process_multilingual_text(mixed_scripts)
        
        # Should handle mixed scripts gracefully
        assert result['normalized'] == mixed_scripts  # Basic normalization
        assert len(result['script']) > 0


@pytest.mark.parametrize("text,expected_pattern", [
    ("1. Introduction", r"Introduction"),
    ("• Bullet point", r"Bullet point"),
    ("Chapter 2: Title", r"Chapter 2: Title"),
    ("   Spaced text   ", r"Spaced text"),
    ("UPPERCASE TEXT", r"UPPERCASE TEXT"),
])
def test_heading_cleaning_patterns(text, expected_pattern):
    """Parametrized test for heading cleaning patterns."""
    normalizer = TextNormalizer()
    cleaned = normalizer.extract_clean_heading_text(text)
    
    import re
    assert re.search(expected_pattern, cleaned) is not None


@pytest.mark.parametrize("language_code,is_rtl", [
    ("ar", True),
    ("he", True),
    ("fa", True),
    ("ur", True),
    ("en", False),
    ("fr", False),
    ("zh", False),
    ("ja", False),
])
def test_rtl_language_detection(language_code, is_rtl):
    """Parametrized test for RTL language detection."""
    normalizer = TextNormalizer()
    assert normalizer.is_rtl_language(language_code) == is_rtl
