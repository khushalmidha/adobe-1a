"""PDF Outline Extractor - Pure Python implementation.

A library for extracting structured outlines from PDF documents using
font size analysis and layout heuristics without ML dependencies.
"""

__version__ = "1.0.0"
__author__ = "Adobe Hackathon Team"
__email__ = "team@example.com"

from .extractor_new import PDFOutlineExtractor
from .json_writer_new import OutlineWriter
from .layout_utils_new import LayoutAnalyzer
from .i18n_utils_new import normalize_text, detect_language

__all__ = [
    "PDFOutlineExtractor",
    "OutlineWriter", 
    "LayoutAnalyzer",
    "normalize_text",
    "detect_language",
]
