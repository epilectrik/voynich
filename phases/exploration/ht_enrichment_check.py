#!/usr/bin/env python3
"""Check HT enrichment at line-initial properly."""

import sys
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token

# HT prefixes (from C347)
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do'}
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}

def is_ht(token):
    token_lower = token.lower()
    result = parse_currier_a_token(token)

    # Skip DA
    if result.prefix in DA_PREFIXES or token_lower.startswith('da'):
        return False

    # Check HT prefix
    for ht_pf in HT_PREFIXES:
        if token_lower.startswith(ht_pf) and not result.is_prefix_legal:
            return True
    return False

# Count
initial_total = 0
initial_ht = 0
all_total = 0
all_ht = 0

with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 15:
            transcriber = parts[12].strip('"') if len(parts) > 12 else ''
            if transcriber != 'H':
                continue
            lang = parts[6].strip('"')
            if lang == 'A':
                word = parts[0].strip('"')
                li = parts[13].strip('"')

                all_total += 1
                if is_ht(word):
                    all_ht += 1

                if li == '1':
                    initial_total += 1
                    if is_ht(word):
                        initial_ht += 1

print(f"All A tokens: {all_total}")
print(f"All HT tokens: {all_ht} ({100*all_ht/all_total:.2f}%)")
print()
print(f"Line-initial tokens: {initial_total}")
print(f"Line-initial HT: {initial_ht} ({100*initial_ht/initial_total:.2f}%)")
print()
print(f"Overall HT rate: {100*all_ht/all_total:.2f}%")
print(f"Line-initial HT rate: {100*initial_ht/initial_total:.2f}%")
print(f"Enrichment ratio: {(initial_ht/initial_total) / (all_ht/all_total):.2f}x")
