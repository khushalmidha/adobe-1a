#!/usr/bin/env python3

import json

# Load both files
with open("test_outputs/file02.json", 'r', encoding='utf-8') as f:
    our_data = json.load(f)

with open("outputs/file02.json", 'r', encoding='utf-8') as f:
    expected_data = json.load(f)

print("=== TITLE COMPARISON ===")
print(f"Our title: '{our_data['title']}'")
print(f"Expected:  '{expected_data['title']}'")
print(f"Titles match: {our_data['title'] == expected_data['title']}")

print(f"\n=== OUTLINE COMPARISON ===")
print(f"Our outline count: {len(our_data['outline'])}")
print(f"Expected count: {len(expected_data['outline'])}")

print(f"\n=== FIRST 10 OUR HEADINGS ===")
for i, heading in enumerate(our_data['outline'][:10]):
    print(f"{i+1}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")

print(f"\n=== FIRST 10 EXPECTED HEADINGS ===")
for i, heading in enumerate(expected_data['outline'][:10]):
    print(f"{i+1}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")

# Check exact matches for first few
print(f"\n=== EXACT MATCH ANALYSIS ===")
our_headings = set()
expected_headings = set()

for heading in our_data['outline']:
    tuple_key = (heading['level'], heading['text'].strip(), heading['page'])
    our_headings.add(tuple_key)

for heading in expected_data['outline']:
    tuple_key = (heading['level'], heading['text'].strip(), heading['page'])
    expected_headings.add(tuple_key)

matches = our_headings & expected_headings
print(f"Exact matches: {len(matches)} out of {len(expected_headings)} expected")

if matches:
    print("Matching headings:")
    for match in sorted(matches):
        print(f"  {match[0]} | '{match[1]}' | Page {match[2]}")

mismatches = expected_headings - our_headings
if mismatches:
    print("\nMissing headings (first 5):")
    for miss in sorted(list(mismatches)[:5]):
        print(f"  {miss[0]} | '{miss[1]}' | Page {miss[2]}")
