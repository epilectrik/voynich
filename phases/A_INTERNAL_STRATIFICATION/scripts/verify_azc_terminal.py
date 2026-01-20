#!/usr/bin/env python3
"""
Verification checks for AZC-terminal MIDDLEs.

Pre-registered checks before any constraint promotion:
1. C304 overlap - are the 31 a strict subset of AZC-unique vocabulary?
2. C300 cross-check - consistently "NA" across transcribers?
3. Placement legality audit - X/Y truly disconnected from C/P/R/S legality?
4. Transcriber robustness - not H-only artifacts?
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
RESULTS_PATH = Path(__file__).parent.parent / 'results'

# Load the middle classes data
with open(RESULTS_PATH / 'middle_classes.json') as f:
    data = json.load(f)

AZC_TERMINAL = set(data['a_exclusive_in_azc'])  # 31 MIDDLEs
A_SHARED = set(data['a_shared_middles'])

# AZC folios
AZC_FOLIOS = ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73', 'f57']

# Standard morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]


def extract_middle(token):
    """Extract (prefix, middle, suffix) from token."""
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None, None, None
    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix


print("=" * 70)
print("VERIFICATION CHECKS FOR AZC-TERMINAL MIDDLEs")
print("=" * 70)
print(f"\nAZC-terminal MIDDLEs to verify: {len(AZC_TERMINAL)}")
print(f"MIDDLEs: {sorted(AZC_TERMINAL)[:10]}... (showing first 10)")
print()

# ============================================================================
# CHECK 1: C304 Overlap
# Are the 31 a strict subset of AZC-unique vocabulary?
# C304 says 27.4% (903 types) are AZC-unique
# ============================================================================
print("=" * 70)
print("CHECK 1: C304 OVERLAP - AZC-Unique Vocabulary Subset")
print("=" * 70)

# Collect vocabulary by system (using ALL transcribers for this check)
a_vocab = set()  # Vocabulary in Currier A (non-AZC)
b_vocab = set()  # Vocabulary in Currier B
azc_vocab = set()  # Vocabulary in AZC folios

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        lang = row.get('language', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)

        if is_azc:
            azc_vocab.add(word)
        elif lang == 'A':
            a_vocab.add(word)
        elif lang == 'B':
            b_vocab.add(word)

# AZC-unique = in AZC but not in A or B
azc_unique = azc_vocab - (a_vocab | b_vocab)
print(f"\nAZC vocabulary: {len(azc_vocab)} types")
print(f"A vocabulary (non-AZC): {len(a_vocab)} types")
print(f"B vocabulary: {len(b_vocab)} types")
print(f"AZC-unique (not in A or B): {len(azc_unique)} types ({100*len(azc_unique)/len(azc_vocab):.1f}%)")

# Now check if AZC-terminal MIDDLEs appear in AZC-unique TOKENS
# We need to find tokens in AZC that have these MIDDLEs
azc_terminal_tokens_in_azc = set()
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if not is_azc:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle in AZC_TERMINAL:
            azc_terminal_tokens_in_azc.add(word)

# How many of these tokens are AZC-unique?
terminal_in_unique = azc_terminal_tokens_in_azc & azc_unique
terminal_not_unique = azc_terminal_tokens_in_azc - azc_unique

print(f"\nAZC-terminal tokens appearing in AZC: {len(azc_terminal_tokens_in_azc)}")
print(f"  - In AZC-unique vocabulary: {len(terminal_in_unique)} ({100*len(terminal_in_unique)/len(azc_terminal_tokens_in_azc):.1f}%)")
print(f"  - NOT in AZC-unique (also in A or B): {len(terminal_not_unique)} ({100*len(terminal_not_unique)/len(azc_terminal_tokens_in_azc):.1f}%)")

if terminal_not_unique:
    print(f"\n  Tokens NOT unique to AZC:")
    for t in sorted(terminal_not_unique)[:10]:
        in_a = t in a_vocab
        in_b = t in b_vocab
        print(f"    {t:20} | in A: {in_a} | in B: {in_b}")

check1_pass = len(terminal_in_unique) / len(azc_terminal_tokens_in_azc) > 0.9 if azc_terminal_tokens_in_azc else False
print(f"\n>>> CHECK 1 RESULT: {'PASS' if check1_pass else 'FAIL'} ({100*len(terminal_in_unique)/len(azc_terminal_tokens_in_azc):.1f}% in AZC-unique)")


# ============================================================================
# CHECK 2: C300 Cross-Check
# Are these consistently "NA" across transcribers?
# ============================================================================
print()
print("=" * 70)
print("CHECK 2: C300 CROSS-CHECK - Consistent NA Classification")
print("=" * 70)

# Collect language classifications for AZC-terminal tokens across ALL transcribers
terminal_lang_by_transcriber = defaultdict(lambda: defaultdict(int))

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        lang = row.get('language', '')
        transcriber = row.get('transcriber', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if not is_azc:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle in AZC_TERMINAL:
            terminal_lang_by_transcriber[transcriber][lang] += 1

print("\nLanguage classification by transcriber for AZC-terminal tokens:")
all_na = True
for transcriber in sorted(terminal_lang_by_transcriber.keys()):
    langs = terminal_lang_by_transcriber[transcriber]
    total = sum(langs.values())
    na_count = langs.get('NA', 0) + langs.get('', 0)  # NA or empty
    na_pct = 100 * na_count / total if total > 0 else 0
    print(f"  {transcriber:3}: {dict(langs)} (NA/empty: {na_pct:.1f}%)")
    if na_pct < 90:
        all_na = False

# Also check if shared MIDDLEs have different classification pattern
shared_lang_by_transcriber = defaultdict(lambda: defaultdict(int))
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        lang = row.get('language', '')
        transcriber = row.get('transcriber', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if not is_azc:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle in A_SHARED:
            shared_lang_by_transcriber[transcriber][lang] += 1

print("\nComparison - A/B-shared MIDDLEs in AZC:")
for transcriber in sorted(shared_lang_by_transcriber.keys())[:3]:  # Just show first 3
    langs = shared_lang_by_transcriber[transcriber]
    total = sum(langs.values())
    na_count = langs.get('NA', 0) + langs.get('', 0)
    na_pct = 100 * na_count / total if total > 0 else 0
    print(f"  {transcriber:3}: NA/empty: {na_pct:.1f}% (vs A: {100*langs.get('A',0)/total:.1f}%, B: {100*langs.get('B',0)/total:.1f}%)")

check2_pass = all_na
print(f"\n>>> CHECK 2 RESULT: {'PASS' if check2_pass else 'FAIL'} (consistent NA across transcribers: {all_na})")


# ============================================================================
# CHECK 3: Placement Legality Audit
# X/Y truly disconnected from C/P/R/S legality zones?
# ============================================================================
print()
print("=" * 70)
print("CHECK 3: PLACEMENT LEGALITY AUDIT")
print("=" * 70)

# Collect placement codes for AZC-terminal vs shared
terminal_placements = Counter()
shared_placements = Counter()

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') != 'H':
            continue

        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        placement = row.get('placement', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if not is_azc:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle in AZC_TERMINAL:
            terminal_placements[placement] += 1
        elif middle in A_SHARED:
            shared_placements[placement] += 1

# Define legality zones vs peripheral positions
LEGALITY_ZONES = {'C', 'C1', 'C2', 'P', 'R', 'R1', 'R2', 'R3', 'R4', 'S', 'S0', 'S1', 'S2', 'S3'}
PERIPHERAL_ZONES = {'X', 'Y', 'Z', 'L', 'I', 'O', 'B', 'W', 'U', 'F', 'T'}

terminal_total = sum(terminal_placements.values())
shared_total = sum(shared_placements.values())

terminal_in_legality = sum(terminal_placements[p] for p in LEGALITY_ZONES)
terminal_in_peripheral = sum(terminal_placements[p] for p in PERIPHERAL_ZONES)
shared_in_legality = sum(shared_placements[p] for p in LEGALITY_ZONES)
shared_in_peripheral = sum(shared_placements[p] for p in PERIPHERAL_ZONES)

print("\nPlacement zone distribution:")
print(f"\n  AZC-terminal MIDDLEs (n={terminal_total}):")
print(f"    Legality zones (C/P/R/S): {terminal_in_legality} ({100*terminal_in_legality/terminal_total:.1f}%)")
print(f"    Peripheral zones (X/Y/Z/L/etc): {terminal_in_peripheral} ({100*terminal_in_peripheral/terminal_total:.1f}%)")

print(f"\n  A/B-shared MIDDLEs (n={shared_total}):")
print(f"    Legality zones (C/P/R/S): {shared_in_legality} ({100*shared_in_legality/shared_total:.1f}%)")
print(f"    Peripheral zones (X/Y/Z/L/etc): {shared_in_peripheral} ({100*shared_in_peripheral/shared_total:.1f}%)")

# Calculate enrichment ratio for peripheral zones
terminal_peripheral_rate = terminal_in_peripheral / terminal_total if terminal_total > 0 else 0
shared_peripheral_rate = shared_in_peripheral / shared_total if shared_total > 0 else 0
enrichment = terminal_peripheral_rate / shared_peripheral_rate if shared_peripheral_rate > 0 else float('inf')

print(f"\n  Peripheral enrichment ratio: {enrichment:.2f}x")

# Key question: are AZC-terminal tokens PREDOMINANTLY in peripheral zones?
predominantly_peripheral = terminal_in_peripheral > terminal_in_legality

print(f"\n  Are AZC-terminal predominantly peripheral? {predominantly_peripheral}")
print(f"    ({terminal_in_peripheral} peripheral vs {terminal_in_legality} legality)")

# Actually, the key check is whether X/Y positions bypass legality grammar
# Per the architecture, X/Y are "miscellaneous" - but we need to verify they're
# truly disconnected. The fact that terminal tokens ALSO appear in C/R positions
# means they're not purely peripheral.

check3_pass = enrichment > 2.0  # At least 2x enriched in peripheral
print(f"\n>>> CHECK 3 RESULT: {'PASS' if check3_pass else 'INCONCLUSIVE'}")
print(f"    AZC-terminal shows {enrichment:.1f}x peripheral enrichment")
print(f"    BUT {100*terminal_in_legality/terminal_total:.1f}% still appear in legality zones")


# ============================================================================
# CHECK 4: Transcriber Robustness
# Not H-only artifacts?
# ============================================================================
print()
print("=" * 70)
print("CHECK 4: TRANSCRIBER ROBUSTNESS")
print("=" * 70)

# Check if AZC-terminal tokens appear across multiple transcribers
terminal_by_transcriber = defaultdict(set)  # transcriber -> set of tokens

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        transcriber = row.get('transcriber', '')

        if not word or '*' in word:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if not is_azc:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle in AZC_TERMINAL:
            terminal_by_transcriber[transcriber].add(word)

print("\nAZC-terminal tokens by transcriber:")
for t in sorted(terminal_by_transcriber.keys()):
    tokens = terminal_by_transcriber[t]
    print(f"  {t:3}: {len(tokens)} unique tokens")

# Check token overlap across transcribers
h_tokens = terminal_by_transcriber.get('H', set())
all_other_tokens = set()
for t, tokens in terminal_by_transcriber.items():
    if t != 'H':
        all_other_tokens.update(tokens)

h_only = h_tokens - all_other_tokens
h_confirmed = h_tokens & all_other_tokens

print(f"\nH-transcriber analysis:")
print(f"  H-only tokens (not in other transcribers): {len(h_only)}")
print(f"  H tokens confirmed by others: {len(h_confirmed)}")

if h_only:
    print(f"\n  H-only tokens (potential artifacts):")
    for t in sorted(h_only)[:10]:
        print(f"    {t}")

# Also check if these tokens have uncertain readings (contain special chars)
uncertain_count = 0
for t in h_tokens:
    if any(c in t for c in ['?', '[', ']', '!', '.']):
        uncertain_count += 1

print(f"\n  Tokens with uncertain markers: {uncertain_count}/{len(h_tokens)}")

check4_pass = len(h_confirmed) / len(h_tokens) > 0.5 if h_tokens else False
print(f"\n>>> CHECK 4 RESULT: {'PASS' if check4_pass else 'FAIL'}")
print(f"    {100*len(h_confirmed)/len(h_tokens):.1f}% of H tokens confirmed by other transcribers")


# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

results = {
    'check1_c304_overlap': {
        'pass': check1_pass,
        'azc_unique_pct': 100*len(terminal_in_unique)/len(azc_terminal_tokens_in_azc) if azc_terminal_tokens_in_azc else 0,
        'tokens_in_unique': len(terminal_in_unique),
        'tokens_not_unique': len(terminal_not_unique),
    },
    'check2_c300_na_classification': {
        'pass': check2_pass,
        'consistent_na': all_na,
    },
    'check3_placement_legality': {
        'pass': check3_pass,
        'peripheral_enrichment': enrichment,
        'terminal_in_legality_pct': 100*terminal_in_legality/terminal_total if terminal_total else 0,
        'terminal_in_peripheral_pct': 100*terminal_in_peripheral/terminal_total if terminal_total else 0,
    },
    'check4_transcriber_robustness': {
        'pass': check4_pass,
        'h_confirmed_pct': 100*len(h_confirmed)/len(h_tokens) if h_tokens else 0,
        'h_only_count': len(h_only),
        'h_confirmed_count': len(h_confirmed),
    },
}

print(f"\n  CHECK 1 (C304 overlap):        {'✓ PASS' if check1_pass else '✗ FAIL'}")
print(f"  CHECK 2 (C300 NA consistent):  {'✓ PASS' if check2_pass else '✗ FAIL'}")
print(f"  CHECK 3 (Placement legality):  {'✓ PASS' if check3_pass else '? INCONCLUSIVE'}")
print(f"  CHECK 4 (Transcriber robust):  {'✓ PASS' if check4_pass else '✗ FAIL'}")

all_pass = check1_pass and check2_pass and check3_pass and check4_pass
print(f"\n  OVERALL: {'ALL CHECKS PASS' if all_pass else 'SOME CHECKS FAILED'}")

if not all_pass:
    print("\n  RECOMMENDATION: Do NOT promote to Tier 2 constraint.")
    print("  Add Tier 3 clarification note only.")

# Save results
with open(RESULTS_PATH / 'azc_terminal_verification.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved to {RESULTS_PATH / 'azc_terminal_verification.json'}")
