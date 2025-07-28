"""PDF Outline Extractor - Pure Python implementation.

A library for extracting structured outlines from PDF documents using
font size analysis and layout heuristics without ML dependencies.
"""

__version__ = "1.0.0"
__author__ = "Adobe Hackathon Team"
__email__ = "team@example.com"

from .extractor_new import PDFOutlineExtractor

__all__ = [
    "PDFOutlineExtractor",
]
