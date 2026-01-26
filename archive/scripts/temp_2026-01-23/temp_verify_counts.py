#!/usr/bin/env python3
"""Verify library counts against CLAUDE.md expected values."""

import csv
from scripts.voynich import Transcript

tx = Transcript()

# Count with defaults (excluding labels and uncertain)
default_a = sum(1 for _ in tx.currier_a())
default_b = sum(1 for _ in tx.currier_b())

# Count including labels
with_labels_a = sum(1 for _ in tx.currier_a(exclude_labels=False))
with_labels_b = sum(1 for _ in tx.currier_b(exclude_labels=False))

# Count including uncertain
with_uncertain_a = sum(1 for _ in tx.currier_a(exclude_uncertain=False))
with_uncertain_b = sum(1 for _ in tx.currier_b(exclude_uncertain=False))

# Count including both
with_both_a = sum(1 for _ in tx.currier_a(exclude_labels=False, exclude_uncertain=False))
with_both_b = sum(1 for _ in tx.currier_b(exclude_labels=False, exclude_uncertain=False))

print("Currier A counts:")
print(f"  Default (no labels, no uncertain): {default_a}")
print(f"  With labels: {with_labels_a}")
print(f"  With uncertain: {with_uncertain_a}")
print(f"  With both: {with_both_a}")
print(f"  Expected (CLAUDE.md): 11,415")

print("\nCurrier B counts:")
print(f"  Default (no labels, no uncertain): {default_b}")
print(f"  With labels: {with_labels_b}")
print(f"  With uncertain: {with_uncertain_b}")
print(f"  With both: {with_both_b}")
print(f"  Expected (CLAUDE.md): 23,243")

# Check raw counts
print("\n" + "="*50)
print("Raw CSV counts (H-only):")
a_raw = 0
b_raw = 0
a_empty = 0
b_empty = 0
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        lang = row.get('language', '').strip()
        word = row.get('word', '').strip()
        if lang == 'A':
            a_raw += 1
            if not word:
                a_empty += 1
        elif lang == 'B':
            b_raw += 1
            if not word:
                b_empty += 1

print(f"  Currier A raw: {a_raw} (empty: {a_empty})")
print(f"  Currier B raw: {b_raw} (empty: {b_empty})")
print(f"  B discrepancy: {b_raw} - {with_both_b} = {b_raw - with_both_b}")
