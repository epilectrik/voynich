#!/usr/bin/env python3
"""
Test 19: RI vs HT Classification

Are the Rosettes "RI-like" labels actually:
- RI (Registry Items): First-line tokens from A that appear in B
- HT (Herbal Terms): A vocabulary that stays in herbal sections

Key test: Do these tokens appear in Currier B?
If yes -> RI (they pass through to execution)
If no -> HT (they're A-only vocabulary)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# The C2 "RI-like" tokens from T18
C2_TOKENS = ['okees', 'otchdo', 'otedar', 'otees', 'otody',
             'air', 'am', 'ar', 'ol', 'or', 'ochar', 'ochedy', 'olchedy']

# All label tokens from Rosettes
rosettes_labels = defaultdict(list)

# Track where tokens appear
token_in_a = defaultdict(list)  # token -> list of (folio, section, line)
token_in_b = defaultdict(list)
token_in_a_first_line = defaultdict(list)  # First line appearances
token_in_a_herbal = defaultdict(list)  # Herbal section appearances

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                if placement in ['C', 'C1', 'C2', 'Q', 'T']:
                    rosettes_labels[placement].append(token)
            elif currier == 'A':
                token_in_a[token].append((folio, section, line_num))
                if line_num == '1':
                    token_in_a_first_line[token].append((folio, section))
                if section == 'H':
                    token_in_a_herbal[token].append((folio, line_num))
            elif currier == 'B':
                token_in_b[token].append((folio, section, line_num))

print("=" * 70)
print("TEST 19: RI vs HT CLASSIFICATION")
print("=" * 70)
print()

# 1. Check C2 tokens specifically
print("1. C2 'RI-LIKE' TOKENS ANALYSIS")
print("-" * 50)

c2_unique = set(rosettes_labels.get('C2', []))
print(f"C2 unique tokens: {len(c2_unique)}")
print()

print(f"{'Token':<12} {'In A':<6} {'In B':<6} {'A Line1':<8} {'A Herbal':<8} {'Classification'}")
print("-" * 60)

for token in sorted(c2_unique):
    in_a = len(token_in_a[token])
    in_b = len(token_in_b[token])
    in_a_l1 = len(token_in_a_first_line[token])
    in_a_h = len(token_in_a_herbal[token])

    if in_b > 0:
        if in_a_l1 > 0:
            classification = "RI (in B, A-line1)"
        else:
            classification = "RI (in B)"
    elif in_a > 0:
        if in_a_h > 0:
            classification = "HT (A-only, herbal)"
        else:
            classification = "A-only (not herbal)"
    else:
        classification = "UNIQUE"

    print(f"{token:<12} {in_a:<6} {in_b:<6} {in_a_l1:<8} {in_a_h:<8} {classification}")

print()

# 2. Check ALL label tokens
print("2. ALL ROSETTES LABEL TOKENS")
print("-" * 50)

all_label_tokens = set()
for placement in ['C', 'C1', 'C2', 'Q', 'T']:
    all_label_tokens.update(rosettes_labels.get(placement, []))

in_b_count = 0
in_a_only = 0
in_a_l1_count = 0
in_a_herbal_count = 0
unique_count = 0

for token in all_label_tokens:
    in_a = len(token_in_a[token])
    in_b = len(token_in_b[token])

    if in_b > 0:
        in_b_count += 1
        if len(token_in_a_first_line[token]) > 0:
            in_a_l1_count += 1
    elif in_a > 0:
        in_a_only += 1
        if len(token_in_a_herbal[token]) > 0:
            in_a_herbal_count += 1
    else:
        unique_count += 1

print(f"Total unique label tokens: {len(all_label_tokens)}")
print()
print(f"Appears in Currier B: {in_b_count} ({in_b_count/len(all_label_tokens)*100:.1f}%) -> RI candidates")
print(f"  - Also in A first-line: {in_a_l1_count}")
print(f"Appears in A only: {in_a_only} ({in_a_only/len(all_label_tokens)*100:.1f}%) -> HT candidates")
print(f"  - In A herbal section: {in_a_herbal_count}")
print(f"Unique to Rosettes: {unique_count} ({unique_count/len(all_label_tokens)*100:.1f}%)")
print()

# 3. Breakdown by placement
print("3. CLASSIFICATION BY PLACEMENT")
print("-" * 50)

print(f"{'Placement':<10} {'Total':<8} {'In B (RI)':<12} {'A-only (HT)':<12} {'Unique':<10}")
print("-" * 52)

for placement in ['C', 'C1', 'C2', 'Q', 'T']:
    tokens = set(rosettes_labels.get(placement, []))
    if not tokens:
        continue

    in_b = sum(1 for t in tokens if len(token_in_b[t]) > 0)
    a_only = sum(1 for t in tokens if len(token_in_b[t]) == 0 and len(token_in_a[t]) > 0)
    unique = sum(1 for t in tokens if len(token_in_b[t]) == 0 and len(token_in_a[t]) == 0)

    in_b_pct = in_b / len(tokens) * 100
    a_only_pct = a_only / len(tokens) * 100

    print(f"{placement:<10} {len(tokens):<8} {in_b} ({in_b_pct:>4.1f}%)    {a_only} ({a_only_pct:>4.1f}%)    {unique}")

print()

# 4. First-line analysis
print("4. FIRST-LINE (RI) TOKENS IN ROSETTES LABELS")
print("-" * 50)

first_line_tokens = []
for token in all_label_tokens:
    if len(token_in_a_first_line[token]) > 0 and len(token_in_b[token]) > 0:
        first_line_tokens.append(token)

print(f"Tokens appearing in A first-line AND in B: {len(first_line_tokens)}")
print(f"These are definite RI (registry items that pass to B)")
print()

if first_line_tokens:
    print("Examples:")
    for token in sorted(first_line_tokens)[:20]:
        a_l1 = len(token_in_a_first_line[token])
        b_count = len(token_in_b[token])
        print(f"  {token}: {a_l1} A-line1 occurrences, {b_count} B occurrences")

print()

# 5. Summary
print("=" * 70)
print("CONCLUSION")
print("=" * 70)

print(f"""
ROSETTES LABEL VOCABULARY CLASSIFICATION:

1. Tokens appearing in Currier B: {in_b_count} ({in_b_count/len(all_label_tokens)*100:.1f}%)
   -> These are RI (Registry Items) that pass from A to B
   -> They're procedural vocabulary used in execution

2. Tokens appearing in A only: {in_a_only} ({in_a_only/len(all_label_tokens)*100:.1f}%)
   -> These COULD be HT (Herbal Terms) if herbal-specific
   -> Of these, {in_a_herbal_count} appear in herbal sections

3. Tokens unique to Rosettes: {unique_count} ({unique_count/len(all_label_tokens)*100:.1f}%)
   -> Rosettes-specific vocabulary
""")

if in_b_count > in_a_only:
    print("VERDICT: Rosettes labels are predominantly RI (appear in B)")
    print("They use execution vocabulary, not herbal-specific terms.")
else:
    print("VERDICT: Rosettes labels include significant HT (A-only) vocabulary")
    print("Some labels reference herbal/botanical material.")
