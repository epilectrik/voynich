#!/usr/bin/env python3
"""Generate character mapping from our transcription encoding to EVA font."""
import re
import json
from collections import Counter

# Read both files
with open('data/transcriptions/voynich_eva.txt', 'r', encoding='utf-8', errors='replace') as f:
    ours = f.read()
with open('data/transcriptions/reference/ZL_official.txt', 'r', encoding='utf-8', errors='replace') as f:
    zl = f.read()

# Find aligned word pairs
word_pairs = []
for m in re.finditer(r'<(\d+[rv]\d*)\.(\d+)>([^<]+)', ours):
    folio, line, text = m.groups()
    our_words = [w for w in re.split(r'[.\s,]+', text) if w and len(w) > 1]
    
    zl_match = re.search(rf'<f{folio}\.{line}[^>]*>([^<]+)', zl)
    if zl_match:
        zl_text = re.sub(r'<%>', '', zl_match.group(1))
        zl_text = re.sub(r'<[^>]+>', '', zl_text)
        zl_text = re.sub(r'\[[^\]]+\]', '', zl_text)
        zl_text = re.sub(r'\{[^}]+\}', '', zl_text)
        zl_words = [w for w in re.split(r'[.\s,]+', zl_text) if w and len(w) > 1]
        
        if len(our_words) == len(zl_words):
            for ow, zw in zip(our_words, zl_words):
                if len(ow) == len(zw):
                    word_pairs.append((ow, zw))

# Build character mapping with confidence scores
char_map = {}
for our_word, zl_word in word_pairs:
    for oc, zc in zip(our_word, zl_word):
        if oc not in char_map:
            char_map[oc] = Counter()
        char_map[oc][zc] += 1

# Generate final mapping (only include high-confidence mappings)
final_map = {}
print("Character Mapping (Our Encoding -> EVA Font)")
print("=" * 50)

for oc in sorted(char_map.keys()):
    counts = char_map[oc]
    total = sum(counts.values())
    best_char, best_count = counts.most_common(1)[0]
    confidence = 100 * best_count / total
    
    # Only include if different from identity and reasonably confident
    if confidence >= 50:
        if oc != best_char:  # Only non-identity mappings
            final_map[oc] = best_char
            print(f"  '{oc}' -> '{best_char}'  ({confidence:.0f}% of {total} samples)")
        else:
            print(f"  '{oc}' -> '{best_char}'  (identity, {confidence:.0f}%)")

# Save the mapping
with open('vee/app/eva_font_mapping.json', 'w') as f:
    json.dump(final_map, f, indent=2)

print()
print(f"Saved {len(final_map)} non-identity mappings to vee/app/eva_font_mapping.json")
print()
print("Final mapping dict:")
print(json.dumps(final_map, indent=2))
