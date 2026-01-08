"""
Final Morphology Classification

This is the FINAL cleanup pass. After this, freeze.

Changes from previous classification:
1. Add new C+C+h clusters: pch, tch, kch, dch, fch, rch, sch
2. Classify HT+B hybrids as EXPLAINED_HT (not orphans)
3. Mark vowel-initial forms as AMBIGUOUS_POSITION (explained but role unclear)
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib import load_transcription

# =============================================================================
# FINAL PREFIX/SUFFIX INVENTORY
# =============================================================================

# Core B-grammar prefixes (original)
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']

# Original cluster prefixes
CLUSTER_PREFIXES_ORIGINAL = ['ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ks', 'ksh', 'ts', 'tsh', 'ps', 'psh']

# NEW: Additional C+C+h clusters (high-confidence additions)
CLUSTER_PREFIXES_NEW = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch']

# Combined cluster inventory
CLUSTER_PREFIXES = CLUSTER_PREFIXES_ORIGINAL + CLUSTER_PREFIXES_NEW

# B-grammar suffixes
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y', 'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']

# HT prefixes (human-track layer)
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of', 'pc', 'tc', 'dc', 'kc', 'sc', 'fc',
               'sa', 'so', 'ka', 'ke', 'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']

# HT suffixes
HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'ny', 'my', 'in', 'ir', 'im', 'il',
               'ar', 'or', 'er', 'al', 'ol', 'el', 'am', 'om', 'an', 'on', 'as', 'os', 'es']

# Vowel-initial stems that are KNOWN COMPONENTS in ambiguous position
# These are B-suffixes appearing at token start - explained but role unclear
AMBIGUOUS_VOWEL_STEMS = ['or', 'ar', 'al', 'ol', 'o', 'a', 'od', 'oe', 'ok', 'ot']

# =============================================================================
# CLASSIFICATION FUNCTION
# =============================================================================

def classify_token_final(word):
    """
    Final classification with expanded inventory and hybrid recognition.

    Categories:
    - B_GRAMMAR_FULL: B prefix + B suffix
    - B_PREFIX_ONLY: B prefix, no recognized suffix
    - B_SUFFIX_ONLY: B suffix, no recognized prefix (but not HT or cluster)
    - CLUSTER_GRAMMAR: Cluster prefix + B suffix
    - CLUSTER_ONLY: Cluster prefix, no suffix
    - HT_PURE: HT prefix + HT suffix (no B components)
    - HT_B_HYBRID: HT prefix + B suffix (explained hybrid)
    - HT_PREFIX_ONLY: HT prefix, no recognized suffix
    - AMBIGUOUS_POSITION: Known component in inverted/unclear position
    - SINGLE_CHAR: Single character
    - DAMAGED: Contains *
    - TRUE_ORPHAN: No recognized components
    """
    if not word:
        return 'EMPTY'

    if '*' in word:
        return 'DAMAGED'

    if len(word) == 1:
        return 'SINGLE_CHAR'

    # Check components (longest match first)
    has_b_prefix = None
    for p in sorted(B_GRAMMAR_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            has_b_prefix = p
            break

    has_cluster_prefix = None
    for p in sorted(CLUSTER_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            has_cluster_prefix = p
            break

    has_ht_prefix = None
    for p in sorted(HT_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            has_ht_prefix = p
            break

    has_b_suffix = None
    for s in sorted(B_GRAMMAR_SUFFIXES, key=len, reverse=True):
        if word.endswith(s):
            has_b_suffix = s
            break

    has_ht_suffix = None
    for s in sorted(HT_SUFFIXES, key=len, reverse=True):
        if word.endswith(s):
            has_ht_suffix = s
            break

    # Check for vowel-initial ambiguous forms
    is_vowel_initial_ambiguous = False
    for stem in sorted(AMBIGUOUS_VOWEL_STEMS, key=len, reverse=True):
        if word.startswith(stem) and len(word) > len(stem):
            # Check if remainder is a valid suffix
            remainder = word[len(stem):]
            if any(remainder.endswith(s) for s in B_GRAMMAR_SUFFIXES + HT_SUFFIXES):
                is_vowel_initial_ambiguous = True
                break

    # Classification logic (order matters!)

    # B-grammar combinations
    if has_b_prefix and has_b_suffix:
        return 'B_GRAMMAR_FULL'
    if has_b_prefix:
        return 'B_PREFIX_ONLY'

    # Cluster combinations
    if has_cluster_prefix and has_b_suffix:
        return 'CLUSTER_GRAMMAR'
    if has_cluster_prefix:
        return 'CLUSTER_ONLY'

    # HT combinations
    if has_ht_prefix and has_b_suffix:
        return 'HT_B_HYBRID'  # Key: this is EXPLAINED, not orphan
    if has_ht_prefix and has_ht_suffix:
        return 'HT_PURE'
    if has_ht_prefix:
        return 'HT_PREFIX_ONLY'

    # Suffix-only forms
    if has_b_suffix:
        if is_vowel_initial_ambiguous:
            return 'AMBIGUOUS_POSITION'
        return 'B_SUFFIX_ONLY'

    if has_ht_suffix:
        return 'HT_SUFFIX_ONLY'

    # Check if it's a vowel-initial ambiguous form without suffix match
    if is_vowel_initial_ambiguous:
        return 'AMBIGUOUS_POSITION'

    return 'TRUE_ORPHAN'

# =============================================================================
# RUN CLASSIFICATION
# =============================================================================

# Load with HIGH recovery
entries = load_transcription(apply_recovery=True, min_confidence='HIGH', include_metadata=True)

print("=" * 70)
print("FINAL MORPHOLOGY CLASSIFICATION")
print("=" * 70)
print(f"\nPrefix inventory expanded:")
print(f"  B-grammar: {len(B_GRAMMAR_PREFIXES)} prefixes")
print(f"  Clusters (original): {len(CLUSTER_PREFIXES_ORIGINAL)} prefixes")
print(f"  Clusters (NEW): {len(CLUSTER_PREFIXES_NEW)} prefixes")
print(f"  HT: {len(HT_PREFIXES)} prefixes")
print(f"  Total: {len(B_GRAMMAR_PREFIXES) + len(CLUSTER_PREFIXES) + len(HT_PREFIXES)} prefixes")

# Classify all tokens
classifications = defaultdict(list)
for e in entries:
    cat = classify_token_final(e['word'])
    classifications[cat].append(e)

# Summary table
print(f"\n" + "=" * 70)
print("CLASSIFICATION RESULTS")
print("=" * 70)

# Group categories
explained_cats = ['B_GRAMMAR_FULL', 'B_PREFIX_ONLY', 'B_SUFFIX_ONLY',
                  'CLUSTER_GRAMMAR', 'CLUSTER_ONLY',
                  'HT_PURE', 'HT_B_HYBRID', 'HT_PREFIX_ONLY', 'HT_SUFFIX_ONLY']
ambiguous_cats = ['AMBIGUOUS_POSITION']
noise_cats = ['SINGLE_CHAR', 'DAMAGED']
orphan_cats = ['TRUE_ORPHAN']

total = len(entries)

print(f"\n{'Category':<25} {'Tokens':>10} {'Types':>10} {'%':>8}")
print("-" * 55)

# Explained
explained_total = 0
for cat in explained_cats:
    tokens = classifications[cat]
    types = len(set(e['word'] for e in tokens))
    pct = 100 * len(tokens) / total
    explained_total += len(tokens)
    print(f"{cat:<25} {len(tokens):>10} {types:>10} {pct:>7.2f}%")

print("-" * 55)
print(f"{'EXPLAINED SUBTOTAL':<25} {explained_total:>10} {'':<10} {100*explained_total/total:>7.2f}%")

# Ambiguous
print("-" * 55)
for cat in ambiguous_cats:
    tokens = classifications[cat]
    types = len(set(e['word'] for e in tokens))
    pct = 100 * len(tokens) / total
    print(f"{cat:<25} {len(tokens):>10} {types:>10} {pct:>7.2f}%")

# Noise
print("-" * 55)
for cat in noise_cats:
    tokens = classifications[cat]
    types = len(set(e['word'] for e in tokens))
    pct = 100 * len(tokens) / total
    print(f"{cat:<25} {len(tokens):>10} {types:>10} {pct:>7.2f}%")

# Orphans
print("-" * 55)
for cat in orphan_cats:
    tokens = classifications[cat]
    types = len(set(e['word'] for e in tokens))
    pct = 100 * len(tokens) / total
    print(f"{cat:<25} {len(tokens):>10} {types:>10} {pct:>7.2f}%")

print("=" * 55)
print(f"{'TOTAL':<25} {total:>10}")

# Breakdown of TRUE_ORPHAN
orphans = classifications['TRUE_ORPHAN']
if orphans:
    print(f"\n" + "=" * 70)
    print(f"TRUE ORPHAN ANALYSIS ({len(orphans)} tokens, {len(set(e['word'] for e in orphans))} types)")
    print("=" * 70)

    orphan_freq = Counter(e['word'] for e in orphans)

    # Pattern analysis
    vowels = set('aeiou')
    consonants = set('bcdfghjklmnpqrstvwxyz')

    patterns = defaultdict(list)
    for tok in set(e['word'] for e in orphans):
        chars = set(tok)
        if chars <= consonants:
            patterns['consonant_cluster'].append(tok)
        elif len(tok) == 2:
            patterns['two_char'].append(tok)
        elif tok[0] in vowels:
            patterns['vowel_initial'].append(tok)
        else:
            patterns['other'].append(tok)

    print(f"\n{'Pattern':<25} {'Types':>8} {'Top examples':<40}")
    print("-" * 75)
    for pattern, tokens in sorted(patterns.items(), key=lambda x: -len(x[1])):
        examples = sorted(tokens, key=lambda t: -orphan_freq[t])[:5]
        ex_str = ', '.join([f"{t}({orphan_freq[t]})" for t in examples])
        print(f"{pattern:<25} {len(tokens):>8} {ex_str:<40}")

    print(f"\nTop 20 TRUE ORPHANS:")
    for tok, freq in orphan_freq.most_common(20):
        print(f"  {tok:<20} {freq:>6}")

# Summary statistics
print(f"\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

explained = sum(len(classifications[c]) for c in explained_cats)
ambiguous = sum(len(classifications[c]) for c in ambiguous_cats)
noise = sum(len(classifications[c]) for c in noise_cats)
orphan = sum(len(classifications[c]) for c in orphan_cats)

print(f"""
CLASSIFICATION BREAKDOWN:
  Explained (grammar + HT + clusters + hybrids): {explained:>6} ({100*explained/total:.2f}%)
  Ambiguous (known components, unclear role):    {ambiguous:>6} ({100*ambiguous/total:.2f}%)
  Noise (single chars + damaged):                {noise:>6} ({100*noise/total:.2f}%)
  TRUE ORPHAN (irreducible):                     {orphan:>6} ({100*orphan/total:.2f}%)

VERDICT:
  Total explained + ambiguous: {explained + ambiguous} ({100*(explained+ambiguous)/total:.2f}%)
  Irreducible residue: {orphan} ({100*orphan/total:.2f}%)
""")

if 100*orphan/total < 0.5:
    print("✓ Residue below 0.5% threshold. Morphology is CLOSED.")
else:
    print(f"⚠ Residue at {100*orphan/total:.2f}%. Review remaining orphans.")

# Write results to file
output_path = Path(__file__).parent.parent / 'reports' / 'final_morphology_classification.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("FINAL MORPHOLOGY CLASSIFICATION RESULTS\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total tokens: {total}\n")
    f.write(f"Explained: {explained} ({100*explained/total:.2f}%)\n")
    f.write(f"Ambiguous: {ambiguous} ({100*ambiguous/total:.2f}%)\n")
    f.write(f"Noise: {noise} ({100*noise/total:.2f}%)\n")
    f.write(f"TRUE ORPHAN: {orphan} ({100*orphan/total:.2f}%)\n")
    f.write(f"\nNew clusters added: {', '.join(CLUSTER_PREFIXES_NEW)}\n")

print(f"\nResults saved to: {output_path}")
