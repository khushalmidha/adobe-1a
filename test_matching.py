#!/usr/bin/env python3
"""Simple test to check exact text matching."""

test_text = "Ontario's Digital Library"
test_lower = test_text.lower()

keywords = ["ontario", "digital library", "critical component"]

print(f"Text: '{test_text}'")
print(f"Lower: '{test_lower}'")
print(f"Keywords: {keywords}")

for keyword in keywords:
    if keyword in test_lower:
        print(f"✅ MATCH: '{keyword}' found in text")
    else:
        print(f"❌ NO MATCH: '{keyword}' not found in text")
