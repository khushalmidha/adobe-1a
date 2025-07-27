#!/usr/bin/env python3
"""Check if file01 is being filtered by invitation detection."""

# Test the invitation filter
all_text = "Application form for grant of LTC advance"
filter_phrases = [
    'hope to see', 'pigeon forge', 'rsvp', 'party', 'event', 
    'invitation', 'please visit', 'waiver', 'topjump'
]

print(f"Testing text: '{all_text}'")
print(f"Text (lowercase): '{all_text.lower()}'")
print()

for phrase in filter_phrases:
    if phrase in all_text.lower():
        print(f"MATCH FOUND: '{phrase}' is in the text!")
    else:
        print(f"'{phrase}' - not found")

print()
print(f"Any phrase match: {any(phrase in all_text.lower() for phrase in filter_phrases)}")
