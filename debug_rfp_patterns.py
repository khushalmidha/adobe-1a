#!/usr/bin/env python3
"""Debug specific RFP pattern matching."""

import re

def test_patterns():
    # Test phase patterns
    test_texts = [
        "Phase I: Business Planning",
        "Phase II: Implementing and Transitioning", 
        "Phase III: Operating and Growing the ODL",
        "1. Preamble",
        "2. Terms of Reference",
        "Milestones",
        "Guidance and Advice:",
        "For the Ontario government it could mean:"
    ]
    
    print("=== TESTING RFP PATTERNS ===")
    
    for text in test_texts:
        text_lower = text.lower()
        print(f"\nTesting: '{text}'")
        
        # Test phase pattern
        if re.match(r'^phase [ivx]+:', text_lower):
            print("  ✓ Matches phase pattern")
        else:
            print("  ✗ No phase pattern match")
        
        # Test numbered pattern for page >= 10
        if re.match(r'^\d+\.\s+', text):
            print("  ✓ Matches numbered pattern")
        else:
            print("  ✗ No numbered pattern match")
        
        # Test colon endings
        if text.endswith(':'):
            print("  ✓ Ends with colon")
        else:
            print("  ✗ No colon ending")
        
        # Test H3 keywords
        rfp_h3_keywords = [
            'timeline', 'access', 'governance', 'funding', 'decision-making',
            'accountability', 'structure', 'equitable', 'shared', 'local',
            'guidance', 'advice', 'training', 'purchasing', 'licensing', 
            'technological', 'support', 'milestones', 'business planning', 
            'implementing', 'transitioning', 'operating', 'growing', 'preamble', 
            'membership', 'appointment', 'criteria', 'process', 'term', 'chair', 
            'meetings', 'lines', 'communication', 'financial', 'administrative', 
            'policies', 'phase', 'what could', 'really mean'
        ]
        
        matches = [kw for kw in rfp_h3_keywords if kw in text_lower]
        if matches:
            print(f"  ✓ Matches H3 keywords: {matches}")
        else:
            print("  ✗ No H3 keyword matches")

if __name__ == "__main__":
    test_patterns()
