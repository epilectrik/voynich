#!/usr/bin/env python3
"""
STATE-C HANDOFF HYPOTHESIS

Following the finding that 68.8% of STATE-C terminals are followed by
transitional-start folios (vs 38.6% base rate = 1.78x enrichment),
we test whether STATE-C is a HANDOFF/COMMIT POINT in multi-step workflows.

Model:
  PROCEDURE A: → STATE-C [COMMIT POINT]
  PROCEDURE B: transitional → STATE-C [COMMIT POINT]
  PROCEDURE C: transitional → final STATE-C

Tests:
  5b: Quantify enrichment + p-value
  5c: Bidirectional pattern test
  7: Token continuity through STATE-C boundaries
  8: A-section prediction
"""

import os
import json
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
import re

os.chdir('C:/git/voynich')

print("=" * 70)
print("STATE-C HANDOFF HYPOTHESIS TEST")
print("Is STATE-C a commit/handoff point in multi-step workflows?")
print("=" * 70)

# Load control signatures
with open('results/control_signatures.json', 'r') as f:
    signatures = json.load(f)

sigs = signatures.get('signatures', {})

# Load transcription data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        # Filter to H (PRIMARY) transcriber only
        transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
        if transcriber != 'H':
            continue
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Build per-folio token sequences
folio_tokens = defaultdict(list)
for t in all_tokens:
    if t.get('language', '') == 'B':
        folio = t.get('folio', '')
        folio_tokens[folio].append(t.get('word', ''))

# Get ordered list of Currier B folios
def folio_sort_key(f):
    match = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (999, 0, 0)

b_folios = sorted([f for f in sigs.keys()], key=folio_sort_key)

def get_terminal_state(folio):
    return sigs.get(folio, {}).get('terminal_state', 'unknown')

def get_initial_state(folio):
    """Infer initial state from first tokens."""
    tokens = folio_tokens.get(folio, [])
    if not tokens:
        return 'unknown'

    first_5 = tokens[:5]
    link_count = sum(1 for t in first_5 if 'ol' in t)
    kernel_count = sum(1 for t in first_5 if any(k in t for k in ['ok', 'yk', 'ak', 'oh', 'yh', 'ah']))

    if link_count > kernel_count:
        return 'STATE-C'
    elif kernel_count > 0:
        return 'transitional'
    else:
        return 'other'

# Get base rates
terminal_states = [get_terminal_state(f) for f in b_folios]
initial_states = [get_initial_state(f) for f in b_folios]

terminal_dist = Counter(terminal_states)
initial_dist = Counter(initial_states)

print(f"\nBase rates:")
print(f"  Terminal: {dict(terminal_dist)}")
print(f"  Initial: {dict(initial_dist)}")

base_rate_transitional = initial_dist.get('transitional', 0) / len(b_folios)
base_rate_statec_terminal = terminal_dist.get('STATE-C', 0) / len(b_folios)

print(f"\n  P(transitional start): {base_rate_transitional:.3f}")
print(f"  P(STATE-C terminal): {base_rate_statec_terminal:.3f}")

# =========================================================================
# TEST 5b: STATE-C -> Transitional Enrichment (with p-value)
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5b: STATE-C -> TRANSITIONAL ENRICHMENT")
print("Quantify the enrichment with statistical significance")
print("=" * 70)

state_c_terminals = []
for i, f in enumerate(b_folios[:-1]):
    if get_terminal_state(f) == 'STATE-C':
        next_f = b_folios[i + 1]
        state_c_terminals.append({
            'folio': f,
            'next_folio': next_f,
            'next_initial': get_initial_state(next_f)
        })

transitional_following = sum(1 for s in state_c_terminals if s['next_initial'] == 'transitional')
state_c_following = sum(1 for s in state_c_terminals if s['next_initial'] == 'STATE-C')
other_following = sum(1 for s in state_c_terminals if s['next_initial'] == 'other')

total_state_c = len(state_c_terminals)

print(f"\nSTATE-C terminals followed by:")
print(f"  Transitional start: {transitional_following}/{total_state_c} ({transitional_following/total_state_c*100:.1f}%)")
print(f"  STATE-C start: {state_c_following}/{total_state_c} ({state_c_following/total_state_c*100:.1f}%)")
print(f"  Other start: {other_following}/{total_state_c} ({other_following/total_state_c*100:.1f}%)")

observed_rate = transitional_following / total_state_c
expected_rate = base_rate_transitional
enrichment = observed_rate / expected_rate

print(f"\nEnrichment analysis:")
print(f"  Observed rate: {observed_rate:.3f}")
print(f"  Expected rate (base): {expected_rate:.3f}")
print(f"  Enrichment: {enrichment:.2f}x")

# Binomial test
# One-sided test: is observed significantly GREATER than expected?
# Using binomtest (scipy >= 1.7) or manual calculation
try:
    from scipy.stats import binomtest
    result = binomtest(transitional_following, total_state_c, expected_rate, alternative='greater')
    p_value = result.pvalue
except ImportError:
    p_value = 1 - stats.binom.cdf(transitional_following - 1, total_state_c, expected_rate)
print(f"  Binomial p-value (one-sided): {p_value:.6f}")

if p_value < 0.05:
    test5b_verdict = f"SIGNIFICANT (p={p_value:.4f}, {enrichment:.2f}x enrichment)"
else:
    test5b_verdict = f"NOT SIGNIFICANT (p={p_value:.4f})"

print(f"\nTEST 5b VERDICT: {test5b_verdict}")

# =========================================================================
# TEST 5c: Bidirectional Pattern Test
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5c: BIDIRECTIONAL PATTERN TEST")
print("Do transitional-start folios preferentially FOLLOW STATE-C terminals?")
print("=" * 70)

transitional_starters = []
for i, f in enumerate(b_folios[1:], 1):
    if get_initial_state(f) == 'transitional':
        prev_f = b_folios[i - 1]
        transitional_starters.append({
            'folio': f,
            'prev_folio': prev_f,
            'prev_terminal': get_terminal_state(prev_f)
        })

state_c_preceding = sum(1 for s in transitional_starters if s['prev_terminal'] == 'STATE-C')
other_preceding = sum(1 for s in transitional_starters if s['prev_terminal'] == 'other')
initial_preceding = sum(1 for s in transitional_starters if s['prev_terminal'] == 'initial')

total_transitional = len(transitional_starters)

print(f"\nTransitional starters preceded by:")
print(f"  STATE-C terminal: {state_c_preceding}/{total_transitional} ({state_c_preceding/total_transitional*100:.1f}%)")
print(f"  Other terminal: {other_preceding}/{total_transitional} ({other_preceding/total_transitional*100:.1f}%)")
print(f"  Initial terminal: {initial_preceding}/{total_transitional} ({initial_preceding/total_transitional*100:.1f}%)")

observed_rate_reverse = state_c_preceding / total_transitional
expected_rate_reverse = base_rate_statec_terminal
enrichment_reverse = observed_rate_reverse / expected_rate_reverse

print(f"\nEnrichment analysis (reverse direction):")
print(f"  Observed rate: {observed_rate_reverse:.3f}")
print(f"  Expected rate (base): {expected_rate_reverse:.3f}")
print(f"  Enrichment: {enrichment_reverse:.2f}x")

# Binomial test
p_value_reverse = 1 - stats.binom.cdf(state_c_preceding - 1, total_transitional, expected_rate_reverse)
print(f"  Binomial p-value (one-sided): {p_value_reverse:.6f}")

if p_value_reverse < 0.05:
    test5c_verdict = f"SIGNIFICANT (p={p_value_reverse:.4f}, {enrichment_reverse:.2f}x enrichment)"
else:
    test5c_verdict = f"NOT SIGNIFICANT (p={p_value_reverse:.4f})"

print(f"\nTEST 5c VERDICT: {test5c_verdict}")

# =========================================================================
# TEST 7: Token Continuity Through STATE-C Boundaries
# =========================================================================

print("\n" + "=" * 70)
print("TEST 7: TOKEN CONTINUITY THROUGH STATE-C")
print("Do vocabulary patterns persist across STATE-C boundaries?")
print("=" * 70)

def get_vocabulary(folio):
    return set(folio_tokens.get(folio, []))

# STATE-C -> Transitional pairs
state_c_trans_pairs = []
for s in state_c_terminals:
    if s['next_initial'] == 'transitional':
        state_c_trans_pairs.append((s['folio'], s['next_folio']))

# Calculate vocabulary overlap for these pairs
state_c_trans_overlaps = []
for f1, f2 in state_c_trans_pairs:
    v1, v2 = get_vocabulary(f1), get_vocabulary(f2)
    if v1 and v2:
        jaccard = len(v1 & v2) / len(v1 | v2)
        state_c_trans_overlaps.append(jaccard)

# Random pairs baseline
import random
random.seed(42)
random_pairs = []
for _ in range(100):
    f1, f2 = random.sample(b_folios, 2)
    v1, v2 = get_vocabulary(f1), get_vocabulary(f2)
    if v1 and v2:
        jaccard = len(v1 & v2) / len(v1 | v2)
        random_pairs.append(jaccard)

# Compare
mean_state_c_trans = np.mean(state_c_trans_overlaps) if state_c_trans_overlaps else 0
mean_random = np.mean(random_pairs) if random_pairs else 0

print(f"\nVocabulary overlap (Jaccard):")
print(f"  STATE-C -> Transitional pairs: {mean_state_c_trans:.4f} (n={len(state_c_trans_overlaps)})")
print(f"  Random pairs: {mean_random:.4f} (n={len(random_pairs)})")

if state_c_trans_overlaps and random_pairs:
    stat, p_value_vocab = stats.mannwhitneyu(state_c_trans_overlaps, random_pairs, alternative='greater')
    print(f"  Mann-Whitney U p-value: {p_value_vocab:.6f}")

    ratio = mean_state_c_trans / mean_random if mean_random > 0 else 0
    if p_value_vocab < 0.05:
        test7_verdict = f"SIGNIFICANT (p={p_value_vocab:.4f}, {ratio:.2f}x baseline)"
    else:
        test7_verdict = f"NOT SIGNIFICANT (p={p_value_vocab:.4f})"
else:
    test7_verdict = "INSUFFICIENT DATA"

print(f"\nTEST 7 VERDICT: {test7_verdict}")

# =========================================================================
# TEST 8: A-Section Material Prediction
# =========================================================================

print("\n" + "=" * 70)
print("TEST 8: A-SECTION MATERIAL PREDICTION")
print("Do STATE-C -> Transitional pairs share A-section references?")
print("=" * 70)

# Get A vocabulary
a_tokens_set = set()
for t in all_tokens:
    if t.get('language', '') == 'A':
        a_tokens_set.add(t.get('word', ''))

print(f"\nA-section vocabulary: {len(a_tokens_set)} unique tokens")

# For each B folio, find which A-tokens appear
def get_a_references(folio):
    """Get A-section tokens that appear in this B folio."""
    b_vocab = get_vocabulary(folio)
    return b_vocab & a_tokens_set

# Calculate A-reference overlap for STATE-C -> Transitional pairs
a_ref_overlaps_stc_trans = []
for f1, f2 in state_c_trans_pairs:
    a1, a2 = get_a_references(f1), get_a_references(f2)
    if a1 and a2:
        jaccard = len(a1 & a2) / len(a1 | a2)
        a_ref_overlaps_stc_trans.append(jaccard)
    elif a1 or a2:
        a_ref_overlaps_stc_trans.append(0)

# Random pairs baseline
a_ref_random = []
for _ in range(100):
    f1, f2 = random.sample(b_folios, 2)
    a1, a2 = get_a_references(f1), get_a_references(f2)
    if a1 and a2:
        jaccard = len(a1 & a2) / len(a1 | a2)
        a_ref_random.append(jaccard)
    elif a1 or a2:
        a_ref_random.append(0)

mean_a_stc = np.mean(a_ref_overlaps_stc_trans) if a_ref_overlaps_stc_trans else 0
mean_a_random = np.mean(a_ref_random) if a_ref_random else 0

print(f"\nA-section reference overlap:")
print(f"  STATE-C -> Transitional pairs: {mean_a_stc:.4f} (n={len(a_ref_overlaps_stc_trans)})")
print(f"  Random pairs: {mean_a_random:.4f} (n={len(a_ref_random)})")

if a_ref_overlaps_stc_trans and a_ref_random:
    stat, p_value_a = stats.mannwhitneyu(a_ref_overlaps_stc_trans, a_ref_random, alternative='greater')
    print(f"  Mann-Whitney U p-value: {p_value_a:.6f}")

    ratio_a = mean_a_stc / mean_a_random if mean_a_random > 0 else 0
    if p_value_a < 0.05:
        test8_verdict = f"SIGNIFICANT (p={p_value_a:.4f}, {ratio_a:.2f}x baseline)"
    else:
        test8_verdict = f"NOT SIGNIFICANT (p={p_value_a:.4f})"
else:
    test8_verdict = "INSUFFICIENT DATA"

print(f"\nTEST 8 VERDICT: {test8_verdict}")

# =========================================================================
# RESTART FOLIO ANALYSIS
# =========================================================================

print("\n" + "=" * 70)
print("RESTART FOLIO ANALYSIS")
print("Do restart folios (f50v, f57r, f82v) start major operational sequences?")
print("=" * 70)

restart_folios = ['f50v', 'f57r', 'f82v']

for rf in restart_folios:
    idx = b_folios.index(rf) if rf in b_folios else -1
    if idx < 0:
        continue

    print(f"\n{rf} (terminal_state=initial, reset_present=True):")

    # Look at sequence following this restart folio
    sequence = []
    for i in range(idx + 1, min(idx + 6, len(b_folios))):
        f = b_folios[i]
        term = get_terminal_state(f)
        sequence.append(f"{f}({term[:3]})")

    print(f"  Following sequence: {' -> '.join(sequence)}")

    # Count STATE-C checkpoints in following sequence
    checkpoints = 0
    for i in range(idx + 1, min(idx + 10, len(b_folios))):
        if get_terminal_state(b_folios[i]) == 'STATE-C':
            checkpoints += 1

    print(f"  STATE-C checkpoints in next 10 folios: {checkpoints}")

    # Check A-section references
    a_refs = get_a_references(rf)
    print(f"  A-section references: {len(a_refs)} tokens")

# =========================================================================
# OVERALL VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("STATE-C HANDOFF HYPOTHESIS - OVERALL VERDICT")
print("=" * 70)

print(f"\nTest Results:")
print(f"  TEST 5b (Forward enrichment): {test5b_verdict}")
print(f"  TEST 5c (Reverse enrichment): {test5c_verdict}")
print(f"  TEST 7 (Vocabulary continuity): {test7_verdict}")
print(f"  TEST 8 (A-section prediction): {test8_verdict}")

# Count significant tests
significant_count = 0
if "SIGNIFICANT" in test5b_verdict:
    significant_count += 1
if "SIGNIFICANT" in test5c_verdict:
    significant_count += 1
if "SIGNIFICANT" in test7_verdict:
    significant_count += 1
if "SIGNIFICANT" in test8_verdict:
    significant_count += 1

print(f"\nSignificant tests: {significant_count}/4")

if significant_count >= 3:
    overall = "STRONG SUPPORT for STATE-C handoff model"
elif significant_count >= 2:
    overall = "MODERATE SUPPORT for STATE-C handoff model"
elif significant_count == 1:
    overall = "WEAK SUPPORT for STATE-C handoff model"
else:
    overall = "NO SUPPORT for STATE-C handoff model"

print(f"\nOVERALL: {overall}")

if significant_count >= 2:
    print(f"""
INTERPRETATION:

STATE-C appears to function as a COMMIT/HANDOFF POINT:
- Procedures reach STATE-C as a stable checkpoint
- Following procedures start from transitional state
- This creates a STAGED PIPELINE architecture

Model:
  [Procedure A] -> STATE-C -> [Procedure B] -> STATE-C -> [Procedure C] -> ...

Each STATE-C is a "save point" where:
- Current operation is committed/stable
- Next operation can begin safely
- Workflow can be paused if needed

This is MORE SOPHISTICATED than simple chaining - it's
CHECKPOINT-MEDIATED workflow with validation points.
""")

# =========================================================================
# CHAIN RECONSTRUCTION (If supported)
# =========================================================================

if significant_count >= 2:
    print("\n" + "=" * 70)
    print("WORKFLOW CHAIN RECONSTRUCTION")
    print("=" * 70)

    # Identify chains: sequences of STATE-C -> Transitional -> ... -> STATE-C
    chains = []
    current_chain = []
    chain_start = None

    for i, f in enumerate(b_folios):
        term = get_terminal_state(f)
        init = get_initial_state(f)

        if not current_chain:
            # Look for chain start
            current_chain.append(f)
            chain_start = f
        else:
            current_chain.append(f)

        if term == 'STATE-C':
            # Check if this is a handoff or endpoint
            if i < len(b_folios) - 1:
                next_init = get_initial_state(b_folios[i + 1])
                if next_init == 'transitional':
                    # This is a handoff, chain continues
                    pass
                else:
                    # This is an endpoint
                    if len(current_chain) >= 2:
                        chains.append(current_chain.copy())
                    current_chain = []
            else:
                # Last folio
                if len(current_chain) >= 2:
                    chains.append(current_chain.copy())
                current_chain = []

    print(f"\nIdentified {len(chains)} potential workflow chains:")

    for i, chain in enumerate(chains[:10]):
        if len(chain) >= 2:
            terminals = [f"{f}({get_terminal_state(f)[:3]})" for f in chain]
            print(f"\n  Chain {i+1} ({len(chain)} folios):")
            print(f"    {' -> '.join(terminals)}")

            # Count STATE-C checkpoints
            checkpoints = sum(1 for f in chain if get_terminal_state(f) == 'STATE-C')
            print(f"    STATE-C checkpoints: {checkpoints}")

print("\n" + "=" * 70)
print("STATE-C HANDOFF HYPOTHESIS TEST COMPLETE")
print("=" * 70)
