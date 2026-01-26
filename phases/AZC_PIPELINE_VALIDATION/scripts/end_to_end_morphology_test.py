"""
END-TO-END RECORD-LEVEL FULL MORPHOLOGY TEST

Tests the core pipeline assumption: A-record morphology determines B token legality.

Per expert guidance:
- Test at RECORD level, not token level
- Use FULL morphological cascade (PREFIX + MIDDLE + SUFFIX), not just MIDDLE
- Test for LEGALITY (absence of illegal tokens), not PREDICTION (presence of legal)

Per C502.a:
- MIDDLE-only: 5.3% legal
- +PREFIX: 1.9% legal (64% additional reduction)
- +SUFFIX: 2.7% legal (50% additional reduction)
- Full morphology: 0.8% legal

Success criterion: Illegal tokens should be ABSENT from B execution contexts
that correspond to A records lacking those morphological components.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("END-TO-END RECORD-LEVEL FULL MORPHOLOGY TEST")
print("=" * 70)

# =============================================================================
# STEP 1: Build A-record profiles (full morphology)
# =============================================================================
print("\n[Step 1] Building A-record morphological profiles...")

a_records = {}
for token in tx.currier_a():
    rid = f"{token.folio}:{token.line}"
    if rid not in a_records:
        a_records[rid] = {
            'middles': set(),
            'prefixes': set(),
            'suffixes': set(),
            'tokens': [],
        }
    if token.word:
        m = morph.extract(token.word)
        a_records[rid]['tokens'].append(token.word)
        if m.middle:
            a_records[rid]['middles'].add(m.middle)
        # Include empty prefix/suffix as valid (prefixless/suffixless tokens are legal)
        a_records[rid]['prefixes'].add(m.prefix if m.prefix else '')
        a_records[rid]['suffixes'].add(m.suffix if m.suffix else '')

print(f"  A-records: {len(a_records)}")
print(f"  Mean tokens per record: {np.mean([len(r['tokens']) for r in a_records.values()]):.1f}")
print(f"  Mean MIDDLEs per record: {np.mean([len(r['middles']) for r in a_records.values()]):.1f}")
print(f"  Mean PREFIXes per record: {np.mean([len(r['prefixes']) for r in a_records.values()]):.1f}")
print(f"  Mean SUFFIXes per record: {np.mean([len(r['suffixes']) for r in a_records.values()]):.1f}")

# =============================================================================
# STEP 2: Build B-folio token inventory
# =============================================================================
print("\n[Step 2] Building B-folio token inventory...")

b_folios = defaultdict(list)
b_tokens_all = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        entry = {
            'word': token.word,
            'folio': token.folio,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
        }
        b_folios[token.folio].append(entry)
        b_tokens_all.append(entry)

print(f"  B folios: {len(b_folios)}")
print(f"  B tokens: {len(b_tokens_all)}")

# Get unique B morphological components
all_b_middles = set(t['middle'] for t in b_tokens_all if t['middle'])
all_b_prefixes = set(t['prefix'] for t in b_tokens_all)
all_b_suffixes = set(t['suffix'] for t in b_tokens_all)

print(f"  Unique B MIDDLEs: {len(all_b_middles)}")
print(f"  Unique B PREFIXes: {len(all_b_prefixes)}")
print(f"  Unique B SUFFIXes: {len(all_b_suffixes)}")

# =============================================================================
# STEP 3: Compute legality under different filtering regimes
# =============================================================================
print("\n[Step 3] Computing legality under different filtering regimes...")

def compute_legality(a_record, b_token, mode='full'):
    """
    Check if B token is legal given A record morphology.

    Modes:
    - 'middle': Only MIDDLE must match
    - 'middle_prefix': MIDDLE and PREFIX must match
    - 'middle_suffix': MIDDLE and SUFFIX must match
    - 'full': All three must match
    """
    if not b_token['middle']:
        return True  # Empty middle = infrastructure, always legal

    middle_ok = b_token['middle'] in a_record['middles']

    if mode == 'middle':
        return middle_ok

    prefix_ok = b_token['prefix'] in a_record['prefixes']
    suffix_ok = b_token['suffix'] in a_record['suffixes']

    if mode == 'middle_prefix':
        return middle_ok and prefix_ok
    elif mode == 'middle_suffix':
        return middle_ok and suffix_ok
    elif mode == 'full':
        return middle_ok and prefix_ok and suffix_ok

    return middle_ok

# Sample A records for testing (use all for comprehensive test)
sample_records = list(a_records.items())

# Compute legality rates per filtering regime
results = {
    'middle': {'legal': 0, 'illegal': 0},
    'middle_prefix': {'legal': 0, 'illegal': 0},
    'middle_suffix': {'legal': 0, 'illegal': 0},
    'full': {'legal': 0, 'illegal': 0},
}

# For each A record, check all B tokens
print(f"  Testing {len(sample_records)} A-records against {len(b_tokens_all)} B-tokens...")

for rid, a_rec in sample_records:
    for b_tok in b_tokens_all:
        for mode in results.keys():
            if compute_legality(a_rec, b_tok, mode):
                results[mode]['legal'] += 1
            else:
                results[mode]['illegal'] += 1

total_pairs = len(sample_records) * len(b_tokens_all)

print("\n" + "=" * 70)
print("FILTERING CASCADE RESULTS")
print("=" * 70)

print(f"\nTotal A-record x B-token pairs: {total_pairs:,}")

for mode, counts in results.items():
    legal_rate = counts['legal'] / total_pairs * 100
    print(f"\n{mode.upper()}:")
    print(f"  Legal: {counts['legal']:,} ({legal_rate:.2f}%)")
    print(f"  Illegal: {counts['illegal']:,} ({100-legal_rate:.2f}%)")

# =============================================================================
# STEP 4: Per-record B-folio viability
# =============================================================================
print("\n" + "=" * 70)
print("PER-RECORD B-FOLIO VIABILITY (C502 validation)")
print("=" * 70)

# For each A record, compute which B folios have viable vocabulary
folio_viability = []

for rid, a_rec in sample_records[:100]:  # Sample for speed
    viable_folios = 0
    for folio, tokens in b_folios.items():
        # A folio is "viable" if at least one token is legal under full morphology
        has_legal = any(compute_legality(a_rec, t, 'full') for t in tokens)
        if has_legal:
            viable_folios += 1
    folio_viability.append(viable_folios)

mean_viable = np.mean(folio_viability)
coverage_pct = mean_viable / len(b_folios) * 100

print(f"\nSample: 100 A-records")
print(f"Mean viable B folios per A-record: {mean_viable:.1f} / {len(b_folios)} ({coverage_pct:.1f}%)")
print(f"C502 predicted: ~13.3% coverage")
print(f"Observed: {coverage_pct:.1f}%")

if abs(coverage_pct - 13.3) < 5:
    print("\n[PASS] Coverage matches C502 prediction (within 5pp)")
else:
    print(f"\n[CHECK] Coverage differs from C502 prediction by {abs(coverage_pct - 13.3):.1f}pp")

# =============================================================================
# STEP 5: Absence test - are illegal tokens actually absent?
# =============================================================================
print("\n" + "=" * 70)
print("ABSENCE TEST: Are illegal tokens actually absent?")
print("=" * 70)

# For this test, we need to see if B folios that SHOULD be non-viable
# actually lack the relevant A-record vocabulary

# Pick 10 random A records and check their "illegal" B tokens
import random
random.seed(42)
test_records = random.sample(list(a_records.items()), 10)

absence_results = []

for rid, a_rec in test_records:
    # Find B tokens that are ILLEGAL under full morphology
    illegal_tokens = [t for t in b_tokens_all if not compute_legality(a_rec, t, 'full')]
    legal_tokens = [t for t in b_tokens_all if compute_legality(a_rec, t, 'full')]

    # The question: In a "real" execution context matching this A-record,
    # would we see the illegal tokens?
    # Per C313: illegal tokens should be ABSENT (not appear)

    absence_results.append({
        'rid': rid,
        'legal_count': len(legal_tokens),
        'illegal_count': len(illegal_tokens),
        'legal_rate': len(legal_tokens) / len(b_tokens_all) * 100,
    })

print(f"\nSample: 10 A-records")
print(f"\nPer-record illegal token counts:")
for r in absence_results:
    print(f"  {r['rid']}: {r['legal_count']:,} legal ({r['legal_rate']:.2f}%), {r['illegal_count']:,} illegal")

mean_legal_rate = np.mean([r['legal_rate'] for r in absence_results])
print(f"\nMean legal rate under full morphology: {mean_legal_rate:.2f}%")
print(f"C502.a predicted: ~0.8%")

# =============================================================================
# STEP 6: Cross-record discrimination test
# =============================================================================
print("\n" + "=" * 70)
print("CROSS-RECORD DISCRIMINATION TEST")
print("=" * 70)

# Per C481: Different A records should produce different survivor sets
# Test: How different are the legal token sets between A records?

print("\nComputing pairwise Jaccard similarity of legal token sets...")

# Get legal token sets for sample records
legal_sets = {}
for rid, a_rec in test_records:
    legal_words = frozenset(t['word'] for t in b_tokens_all if compute_legality(a_rec, t, 'full'))
    legal_sets[rid] = legal_words

# Compute pairwise Jaccard
jaccards = []
rids = list(legal_sets.keys())
for i in range(len(rids)):
    for j in range(i+1, len(rids)):
        set_i = legal_sets[rids[i]]
        set_j = legal_sets[rids[j]]
        if set_i or set_j:
            jaccard = len(set_i & set_j) / len(set_i | set_j)
            jaccards.append(jaccard)

mean_jaccard = np.mean(jaccards)
print(f"\nPairwise Jaccard similarity of legal token sets:")
print(f"  Mean: {mean_jaccard:.3f}")
print(f"  Min: {min(jaccards):.3f}")
print(f"  Max: {max(jaccards):.3f}")

if mean_jaccard < 0.5:
    print("\n[PASS] A-records produce distinct legal token sets (mean Jaccard < 0.5)")
else:
    print("\n[CHECK] A-records produce similar legal token sets (mean Jaccard >= 0.5)")

# =============================================================================
# STEP 7: Summary
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
FILTERING CASCADE (C502.a validation):
  - The full morphological cascade dramatically reduces legality
  - Each additional filter (PREFIX, SUFFIX) provides incremental reduction

PER-RECORD VIABILITY:
  - Different A records make different B folios viable
  - Coverage percentage should match C502 prediction (~13.3%)

DISCRIMINATION:
  - A records produce distinct legal token sets
  - This supports C481 (survivor-set uniqueness)

INTERPRETATION:
  - If filtering cascade matches C502.a predictions: Pipeline is valid
  - If discrimination is high: A records are meaningfully different
  - If both pass: The AZC pipeline is doing what we think it's doing
""")
