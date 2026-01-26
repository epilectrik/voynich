#!/usr/bin/env python3
"""
Statistical test for -ol/-ar suffix divergence between PREFIX-REQ and PREFIX-FORB.

Run Fisher's exact test to determine if the divergence is significant.
Also check alternative explanations (material class, phonotactics, length).
"""

import csv
import json
from collections import Counter, defaultdict
from scipy import stats

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])
pp_middles = set(data['a_shared_middles'])

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_full(token):
    if not token:
        return None, None, None
    working = token
    prefix = None
    suffix = None
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break
    return prefix, working if working else None, suffix

# First classify MIDDLEs into prefix-required/forbidden
appears_with_prefix = set()
appears_without_prefix = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue
        prefix, middle, suffix = extract_full(word)
        if middle and middle in ri_middles:
            if prefix:
                appears_with_prefix.add(middle)
            else:
                appears_without_prefix.add(middle)

prefix_required = appears_with_prefix - appears_without_prefix
prefix_forbidden = appears_without_prefix - appears_with_prefix

print("="*70)
print("STATISTICAL TESTS: SUFFIX DIVERGENCE")
print("="*70)
print(f"\nPREFIX-REQUIRED MIDDLEs: {len(prefix_required)}")
print(f"PREFIX-FORBIDDEN MIDDLEs: {len(prefix_forbidden)}")

# Collect suffix data for each token
req_tokens = []  # list of (middle, suffix, has_ol, has_ar)
forb_tokens = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_full(word)
        if middle and middle in ri_middles:
            if middle in prefix_required and prefix:
                req_tokens.append({'middle': middle, 'suffix': suffix})
            elif middle in prefix_forbidden and not prefix:
                forb_tokens.append({'middle': middle, 'suffix': suffix})

print(f"\nPREFIX-REQUIRED tokens: {len(req_tokens)}")
print(f"PREFIX-FORBIDDEN tokens: {len(forb_tokens)}")

# Build contingency tables
# For -ol suffix
req_with_ol = sum(1 for t in req_tokens if t['suffix'] == 'ol')
req_without_ol = len(req_tokens) - req_with_ol
forb_with_ol = sum(1 for t in forb_tokens if t['suffix'] == 'ol')
forb_without_ol = len(forb_tokens) - forb_with_ol

print("\n" + "="*70)
print("TEST 1: -ol SUFFIX")
print("="*70)

print(f"\nContingency table:")
print(f"                    -ol    not -ol")
print(f"  PREFIX-REQUIRED   {req_with_ol:>4}    {req_without_ol:>4}")
print(f"  PREFIX-FORBIDDEN  {forb_with_ol:>4}    {forb_without_ol:>4}")

# Fisher's exact test
table_ol = [[req_with_ol, req_without_ol], [forb_with_ol, forb_without_ol]]
odds_ol, p_ol = stats.fisher_exact(table_ol)
print(f"\nFisher's exact test:")
print(f"  Odds ratio: {odds_ol:.2f}")
print(f"  p-value: {p_ol:.4f}")
if p_ol < 0.01:
    print(f"  --> SIGNIFICANT at p < 0.01")
elif p_ol < 0.05:
    print(f"  --> Significant at p < 0.05 (marginal)")
else:
    print(f"  --> NOT significant")

# For -ar suffix
req_with_ar = sum(1 for t in req_tokens if t['suffix'] == 'ar')
req_without_ar = len(req_tokens) - req_with_ar
forb_with_ar = sum(1 for t in forb_tokens if t['suffix'] == 'ar')
forb_without_ar = len(forb_tokens) - forb_with_ar

print("\n" + "="*70)
print("TEST 2: -ar SUFFIX")
print("="*70)

print(f"\nContingency table:")
print(f"                    -ar    not -ar")
print(f"  PREFIX-REQUIRED   {req_with_ar:>4}    {req_without_ar:>4}")
print(f"  PREFIX-FORBIDDEN  {forb_with_ar:>4}    {forb_without_ar:>4}")

table_ar = [[req_with_ar, req_without_ar], [forb_with_ar, forb_without_ar]]
odds_ar, p_ar = stats.fisher_exact(table_ar)
print(f"\nFisher's exact test:")
print(f"  Odds ratio: {odds_ar:.2f}")
print(f"  p-value: {p_ar:.4f}")
if p_ar < 0.01:
    print(f"  --> SIGNIFICANT at p < 0.01")
elif p_ar < 0.05:
    print(f"  --> Significant at p < 0.05 (marginal)")
else:
    print(f"  --> NOT significant")

# Alternative explanation checks
print("\n" + "="*70)
print("ALTERNATIVE EXPLANATION CHECKS")
print("="*70)

# Check 1: MIDDLE length difference
req_lengths = [len(t['middle']) for t in req_tokens]
forb_lengths = [len(t['middle']) for t in forb_tokens]

avg_req_len = sum(req_lengths) / len(req_lengths)
avg_forb_len = sum(forb_lengths) / len(forb_lengths)

print(f"\n1. MIDDLE LENGTH:")
print(f"   PREFIX-REQUIRED avg length: {avg_req_len:.2f}")
print(f"   PREFIX-FORBIDDEN avg length: {avg_forb_len:.2f}")

# t-test for length difference
t_stat, p_len = stats.ttest_ind(req_lengths, forb_lengths)
print(f"   t-test p-value: {p_len:.4f}")
if p_len < 0.05:
    print(f"   --> Length differs significantly (potential confound)")
else:
    print(f"   --> Length NOT significantly different")

# Check 2: MIDDLE ending character (phonotactic)
req_endings = Counter(t['middle'][-1] if t['middle'] else '' for t in req_tokens)
forb_endings = Counter(t['middle'][-1] if t['middle'] else '' for t in forb_tokens)

print(f"\n2. MIDDLE ENDING CHARACTER (top 5):")
print(f"   PREFIX-REQUIRED: {req_endings.most_common(5)}")
print(f"   PREFIX-FORBIDDEN: {forb_endings.most_common(5)}")

# Check if endings differ
all_endings = set(req_endings.keys()) | set(forb_endings.keys())
# Chi-square for ending distribution
req_end_counts = [req_endings.get(e, 0) for e in sorted(all_endings)]
forb_end_counts = [forb_endings.get(e, 0) for e in sorted(all_endings)]

# Only use endings with >5 total count for chi-square
valid_endings = [e for e in all_endings if req_endings.get(e, 0) + forb_endings.get(e, 0) > 5]
if len(valid_endings) >= 2:
    req_valid = [req_endings.get(e, 0) for e in valid_endings]
    forb_valid = [forb_endings.get(e, 0) for e in valid_endings]
    chi2, p_end = stats.chisquare(req_valid, f_exp=forb_valid)
    print(f"   Chi-square p-value: {p_end:.4f}")
else:
    print(f"   (Not enough data for chi-square)")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

significant_ol = p_ol < 0.01
significant_ar = p_ar < 0.01

print(f"""
-ol suffix divergence:
  Odds ratio: {odds_ol:.2f} (PREFIX-REQ vs PREFIX-FORB)
  p-value: {p_ol:.4f}
  Significant at p < 0.01: {significant_ol}

-ar suffix divergence:
  Odds ratio: {odds_ar:.2f} (PREFIX-REQ vs PREFIX-FORB)
  p-value: {p_ar:.4f}
  Significant at p < 0.01: {significant_ar}

RECOMMENDATION:
""")

if significant_ol and significant_ar:
    print("  BOTH -ol and -ar divergences are statistically significant.")
    print("  --> Document as C528.a")
elif significant_ol or significant_ar:
    print("  ONE divergence is significant, the other is not.")
    print("  --> Document as C528.a with appropriate caveats")
else:
    print("  NEITHER divergence is statistically significant.")
    print("  --> Do NOT document as constraint (note in INTERPRETATION_SUMMARY as Tier 4)")
