"""Test fixtures and sample data for PDF outline extraction tests."""

import json
from pathlib import Path

# Sample JSON outline for testing
SAMPLE_OUTLINE = {
    "title": "Sample Document Title",
    "outline": [
        {"level": "H1", "text": "Chapter 1: Introduction", "page": 0},
        {"level": "H2", "text": "1.1 Background", "page": 1},
        {"level": "H3", "text": "1.1.1 Historical Context", "page": 1},
        {"level": "H2", "text": "1.2 Objectives", "page": 2},
        {"level": "H1", "text": "Chapter 2: Methodology", "page": 3},
        {"level": "H2", "text": "2.1 Data Collection", "page": 4},
        {"level": "H3", "text": "2.1.1 Survey Design", "page": 4},
        {"level": "H3", "text": "2.1.2 Sampling Strategy", "page": 5},
        {"level": "H2", "text": "2.2 Analysis Framework", "page": 6},
        {"level": "H1", "text": "Chapter 3: Results", "page": 7}
    ]
}

# Sample outline with multilingual content
MULTILINGUAL_OUTLINE = {
    "title": "多语言文档 / Multilingual Document",
    "outline": [
        {"level": "H1", "text": "第一章：介绍", "page": 0},
        {"level": "H2", "text": "1.1 Background Information", "page": 1},
        {"level": "H1", "text": "الفصل الثاني: المنهجية", "page": 2},
        {"level": "H2", "text": "2.1 جمع البيانات", "page": 3},
        {"level": "H1", "text": "Chapter 3: Résultats", "page": 4},
        {"level": "H2", "text": "3.1 Analyse des données", "page": 5}
    ]
}

# Sample outline with edge cases
EDGE_CASE_OUTLINE = {
    "title": "Document with\tTabs and\nNewlines",
    "outline": [
        {"level": "H1", "text": "Section with\ttabs", "page": 0},
        {"level": "H2", "text": "Subsection with\nnewlines", "page": 1},
        {"level": "H3", "text": "Sub-subsection with émojis 📊", "page": 2},
        {"level": "H1", "text": "SECTION IN ALL CAPS", "page": 3},
        {"level": "H2", "text": "section in lowercase", "page": 4}
    ]
}

# Empty outline for PDFs without clear structure
EMPTY_OUTLINE = {
    "title": "",
    "outline": []
}


def create_sample_json_file(fixture_dir: Path, filename: str, outline_data: dict) -> Path:
    """Create a sample JSON file for testing.
    
    Args:
        fixture_dir: Directory to create the file in
        filename: Name of the JSON file
        outline_data: Outline data to write
        
    Returns:
        Path to created file
    """
    file_path = fixture_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(outline_data, f, ensure_ascii=False, indent=2)
    
    return file_path


def setup_test_fixtures(fixture_dir: Path) -> dict:
    """Set up all test fixtures in the given directory.
    
    Args:
        fixture_dir: Directory to create fixtures in
        
    Returns:
        Dictionary mapping fixture names to file paths
    """
    fixtures = {}
    
    # Create sample JSON files
    fixtures['sample'] = create_sample_json_file(
        fixture_dir, 'sample.json', SAMPLE_OUTLINE
    )
    
    fixtures['multilingual'] = create_sample_json_file(
        fixture_dir, 'multilingual.json', MULTILINGUAL_OUTLINE
    )
    
    fixtures['edge_cases'] = create_sample_json_file(
        fixture_dir, 'edge_cases.json', EDGE_CASE_OUTLINE
    )
    
    fixtures['empty'] = create_sample_json_file(
        fixture_dir, 'empty.json', EMPTY_OUTLINE
    )
    
    return fixtures
