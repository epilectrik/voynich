#!/usr/bin/env python3
"""
Tri-Layer Touchpoint Test: HT x A x AZC

Question: Do HT-heavy programs preferentially interact with A-heavy registries
under certain AZC regimes?

This tests cognitive load stratification: which stewardship modes are most
cognitively demanding (produce more attentional scaffolding).
"""

import os
import json
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

os.chdir('C:/git/voynich')

print("=" * 70)
print("TRI-LAYER TOUCHPOINT TEST: HT x A x AZC")
print("=" * 70)

# =============================================================================
# DATA LOADING
# =============================================================================

def is_clean_token(token):
    """Filter out damaged/artifact tokens."""
    return '*' not in token and token.isalpha() and len(token) >= 2

# Load all tokens
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip() != 'H':
            continue
        if is_clean_token(row.get('word', '')):
            all_tokens.append(row)

# Separate by language
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]

# Build vocabularies
a_vocab = set(t['word'] for t in a_tokens)
b_vocab = set(t['word'] for t in b_tokens)
azc_vocab = set(t['word'] for t in azc_tokens)

print(f"\nData loaded:")
print(f"  A vocab: {len(a_vocab)} types")
print(f"  B vocab: {len(b_vocab)} types")
print(f"  AZC vocab: {len(azc_vocab)} types")

# =============================================================================
# LOAD HT CLASSIFICATION (from HTD phase)
# =============================================================================

# HT tokens = tokens NOT in grammar vocabulary
# Load from HTD results or recompute

HAZARD_TOKENS = {
    'daiin', 'ol', 'chedy', 'shedy', 'qokeedy', 'qokedy', 'chey',
    'qokaiin', 'qokeey', 'okaiin', 'shey', 'qokain', 'otedy',
    'okedy', 'cheedy', 'qokey', 'okeedy'
}

OPERATIONAL_TOKENS = {
    'daiin', 'ol', 'chedy', 'shedy', 'qokeedy', 'qokedy', 'chey',
    'qokaiin', 'qokeey', 'okaiin', 'shey', 'qokain', 'otedy',
    'okedy', 'cheedy', 'qokey', 'okeedy', 'aiin', 'ain', 'ar',
    'or', 'al', 'y', 'dy', 'shy', 'chy', 'cthy', 'dar', 'dal',
    'dol', 'dan', 'dain', 'dainy', 'chain', 'chol', 'chor',
    'shor', 'shol', 'qol', 'qor', 'qokal', 'qokar', 'okal',
    'okar', 'okol', 'okor', 'otal', 'otar', 'otol', 'otor'
}

GRAMMAR_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def is_grammar_token(token):
    """Check if token is part of core grammar."""
    for prefix in GRAMMAR_PREFIXES:
        if token.startswith(prefix):
            return True
    return False

def is_strict_ht(token):
    """Strict human-track classification."""
    t = token.lower().strip()
    if len(t) < 2 or not t.isalpha():
        return False
    if t in HAZARD_TOKENS or t in OPERATIONAL_TOKENS:
        return False
    if is_grammar_token(t):
        return False
    return True

# =============================================================================
# COMPUTE PER-FOLIO METRICS
# =============================================================================

# Group B tokens by folio
b_by_folio = defaultdict(list)
for t in b_tokens:
    folio = t.get('folio', '')
    if folio:
        b_by_folio[folio].append(t['word'])

b_folios = sorted(b_by_folio.keys())
print(f"\nB folios: {len(b_folios)}")

# For each B folio, compute:
# 1. HT density
# 2. A-vocabulary density (what % of folio vocab is in A)
# 3. AZC-vocabulary density (what % of folio vocab is in AZC)

folio_metrics = {}

for folio in b_folios:
    tokens = b_by_folio[folio]
    n_tokens = len(tokens)
    vocab = set(tokens)

    if n_tokens < 10:
        continue

    # HT density
    ht_tokens = [t for t in tokens if is_strict_ht(t)]
    ht_density = len(ht_tokens) / n_tokens

    # A-vocabulary overlap (what % of folio vocab also appears in A)
    a_overlap = vocab & a_vocab
    a_density = len(a_overlap) / len(vocab) if vocab else 0

    # A-token density (what % of tokens are from A-vocab)
    a_token_count = sum(1 for t in tokens if t in a_vocab)
    a_token_density = a_token_count / n_tokens

    # AZC-vocabulary overlap
    azc_overlap = vocab & azc_vocab
    azc_density = len(azc_overlap) / len(vocab) if vocab else 0

    # AZC-token density
    azc_token_count = sum(1 for t in tokens if t in azc_vocab)
    azc_token_density = azc_token_count / n_tokens

    folio_metrics[folio] = {
        'n_tokens': n_tokens,
        'vocab_size': len(vocab),
        'ht_density': ht_density,
        'a_vocab_density': a_density,
        'a_token_density': a_token_density,
        'azc_vocab_density': azc_density,
        'azc_token_density': azc_token_density,
    }

print(f"Folios with metrics: {len(folio_metrics)}")

# =============================================================================
# LOAD WAITING PROFILE (from OPS-1)
# =============================================================================

try:
    with open('phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json', 'r') as f:
        ops1_data = json.load(f)

    # Data is nested under 'signatures'
    signatures = ops1_data.get('signatures', ops1_data)

    for folio in folio_metrics:
        if folio in signatures:
            classifications = signatures[folio].get('classifications', {})
            folio_metrics[folio]['waiting_profile'] = classifications.get('waiting_profile', 'UNKNOWN')
        else:
            folio_metrics[folio]['waiting_profile'] = 'UNKNOWN'

    # Count profiles
    profile_counts = defaultdict(int)
    for f in folio_metrics:
        profile_counts[folio_metrics[f]['waiting_profile']] += 1
    print(f"Waiting profiles loaded: {dict(profile_counts)}")
except Exception as e:
    print(f"Warning: Could not load OPS-1 data: {e}")
    for folio in folio_metrics:
        folio_metrics[folio]['waiting_profile'] = 'UNKNOWN'

# =============================================================================
# TEST 1: HT x A-VOCAB CORRELATION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 1: HT x A-VOCAB CORRELATION")
print("Do HT-heavy programs use more A-vocabulary?")
print("=" * 70)

ht_densities = [folio_metrics[f]['ht_density'] for f in folio_metrics]
a_densities = [folio_metrics[f]['a_token_density'] for f in folio_metrics]

r_ht_a, p_ht_a = stats.pearsonr(ht_densities, a_densities)
rho_ht_a, p_rho_ht_a = stats.spearmanr(ht_densities, a_densities)

print(f"\nHT density vs A-token density:")
print(f"  Pearson r = {r_ht_a:.3f}, p = {p_ht_a:.4f}")
print(f"  Spearman rho = {rho_ht_a:.3f}, p = {p_rho_ht_a:.4f}")

if p_rho_ht_a < 0.05:
    direction = "POSITIVE" if rho_ht_a > 0 else "NEGATIVE"
    print(f"  SIGNIFICANT {direction} correlation")
else:
    print(f"  NOT significant")

# =============================================================================
# TEST 2: HT x AZC-VOCAB CORRELATION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 2: HT x AZC-VOCAB CORRELATION")
print("Do HT-heavy programs share more vocabulary with AZC?")
print("=" * 70)

azc_densities = [folio_metrics[f]['azc_token_density'] for f in folio_metrics]

r_ht_azc, p_ht_azc = stats.pearsonr(ht_densities, azc_densities)
rho_ht_azc, p_rho_ht_azc = stats.spearmanr(ht_densities, azc_densities)

print(f"\nHT density vs AZC-token density:")
print(f"  Pearson r = {r_ht_azc:.3f}, p = {p_ht_azc:.4f}")
print(f"  Spearman rho = {rho_ht_azc:.3f}, p = {p_rho_ht_azc:.4f}")

if p_rho_ht_azc < 0.05:
    direction = "POSITIVE" if rho_ht_azc > 0 else "NEGATIVE"
    print(f"  SIGNIFICANT {direction} correlation")
else:
    print(f"  NOT significant")

# =============================================================================
# TEST 3: A x AZC CORRELATION (within B folios)
# =============================================================================

print("\n" + "=" * 70)
print("TEST 3: A x AZC CORRELATION (within B folios)")
print("Do A-heavy B programs also reference AZC vocabulary?")
print("=" * 70)

r_a_azc, p_a_azc = stats.pearsonr(a_densities, azc_densities)
rho_a_azc, p_rho_a_azc = stats.spearmanr(a_densities, azc_densities)

print(f"\nA-token density vs AZC-token density:")
print(f"  Pearson r = {r_a_azc:.3f}, p = {p_a_azc:.4f}")
print(f"  Spearman rho = {rho_a_azc:.3f}, p = {p_rho_a_azc:.4f}")

if p_rho_a_azc < 0.05:
    direction = "POSITIVE" if rho_a_azc > 0 else "NEGATIVE"
    print(f"  SIGNIFICANT {direction} correlation")
else:
    print(f"  NOT significant")

# =============================================================================
# TEST 4: THREE-WAY INTERACTION BY WAITING PROFILE
# =============================================================================

print("\n" + "=" * 70)
print("TEST 4: THREE-WAY STRATIFICATION BY WAITING PROFILE")
print("Does HT x A x AZC pattern differ across waiting profiles?")
print("=" * 70)

# Group folios by waiting profile
by_profile = defaultdict(list)
for folio, metrics in folio_metrics.items():
    profile = metrics.get('waiting_profile', 'UNKNOWN')
    if profile != 'UNKNOWN':
        by_profile[profile].append(metrics)

print(f"\nFolios per profile:")
for profile in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']:
    if profile in by_profile:
        folios = by_profile[profile]
        mean_ht = np.mean([f['ht_density'] for f in folios])
        mean_a = np.mean([f['a_token_density'] for f in folios])
        mean_azc = np.mean([f['azc_token_density'] for f in folios])
        print(f"  {profile}: n={len(folios)}, HT={mean_ht:.3f}, A={mean_a:.3f}, AZC={mean_azc:.3f}")

# Compute HT-A correlation WITHIN each profile
print(f"\nHT-A correlation by profile:")
profile_correlations = {}
for profile in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']:
    if profile in by_profile and len(by_profile[profile]) >= 5:
        folios = by_profile[profile]
        ht = [f['ht_density'] for f in folios]
        a = [f['a_token_density'] for f in folios]
        if len(set(ht)) > 1 and len(set(a)) > 1:
            rho, p = stats.spearmanr(ht, a)
            profile_correlations[profile] = {'rho': rho, 'p': p, 'n': len(folios)}
            sig = "*" if p < 0.05 else ""
            print(f"  {profile}: rho={rho:.3f}, p={p:.3f}, n={len(folios)} {sig}")

# =============================================================================
# TEST 5: COGNITIVE LOAD PROXY
# =============================================================================

print("\n" + "=" * 70)
print("TEST 5: COGNITIVE LOAD PROXY")
print("Combined HT + A + AZC density as cognitive complexity measure")
print("=" * 70)

# Create composite score: HT * A * AZC (interaction term)
# Or additive: HT + A + AZC

for folio in folio_metrics:
    m = folio_metrics[folio]
    # Multiplicative interaction (captures co-occurrence)
    m['complexity_mult'] = m['ht_density'] * m['a_token_density'] * m['azc_token_density']
    # Additive (captures total cognitive load)
    m['complexity_add'] = m['ht_density'] + m['a_token_density'] + m['azc_token_density']

# Distribution by waiting profile
print(f"\nComplexity scores by waiting profile:")
print(f"{'Profile':<12} {'HT':<8} {'A':<8} {'AZC':<8} {'Add':<8} {'Mult':<10}")
print("-" * 60)

profile_complexity = {}
for profile in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']:
    if profile in by_profile:
        folios = by_profile[profile]
        mean_ht = np.mean([f['ht_density'] for f in folios])
        mean_a = np.mean([f['a_token_density'] for f in folios])
        mean_azc = np.mean([f['azc_token_density'] for f in folios])
        mean_add = np.mean([f['complexity_add'] for f in folios])
        mean_mult = np.mean([f['complexity_mult'] for f in folios])

        profile_complexity[profile] = {
            'ht': mean_ht, 'a': mean_a, 'azc': mean_azc,
            'add': mean_add, 'mult': mean_mult, 'n': len(folios)
        }
        print(f"{profile:<12} {mean_ht:<8.3f} {mean_a:<8.3f} {mean_azc:<8.3f} {mean_add:<8.3f} {mean_mult:<10.5f}")

# Test: Does complexity differ by profile?
if len(profile_complexity) >= 3:
    groups = []
    for profile in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']:
        if profile in by_profile:
            groups.append([f['complexity_add'] for f in by_profile[profile]])

    if len(groups) >= 3:
        h_stat, p_kw = stats.kruskal(*groups)
        print(f"\nKruskal-Wallis (complexity_add by profile): H={h_stat:.2f}, p={p_kw:.4f}")

        if p_kw < 0.05:
            print("  SIGNIFICANT: Cognitive complexity varies by waiting profile")
        else:
            print("  NOT significant")

# =============================================================================
# TEST 6: HIGH-COMPLEXITY FOLIOS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 6: HIGH-COMPLEXITY FOLIOS")
print("Which folios show the strongest tri-layer interaction?")
print("=" * 70)

# Rank by multiplicative complexity (true interaction)
ranked = sorted(folio_metrics.items(), key=lambda x: x[1]['complexity_mult'], reverse=True)

print(f"\nTop 10 folios by tri-layer complexity (HT * A * AZC):")
print(f"{'Folio':<10} {'HT':<8} {'A':<8} {'AZC':<8} {'Mult':<10} {'Profile':<12}")
print("-" * 60)

for folio, m in ranked[:10]:
    print(f"{folio:<10} {m['ht_density']:<8.3f} {m['a_token_density']:<8.3f} "
          f"{m['azc_token_density']:<8.3f} {m['complexity_mult']:<10.5f} {m.get('waiting_profile', 'UNK'):<12}")

# Bottom 10
print(f"\nBottom 10 folios (lowest tri-layer complexity):")
for folio, m in ranked[-10:]:
    print(f"{folio:<10} {m['ht_density']:<8.3f} {m['a_token_density']:<8.3f} "
          f"{m['azc_token_density']:<8.3f} {m['complexity_mult']:<10.5f} {m.get('waiting_profile', 'UNK'):<12}")

# =============================================================================
# SYNTHESIS
# =============================================================================

print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

results = {
    'test1_ht_a': {
        'rho': float(rho_ht_a),
        'p': float(p_rho_ht_a),
        'significant': p_rho_ht_a < 0.05
    },
    'test2_ht_azc': {
        'rho': float(rho_ht_azc),
        'p': float(p_rho_ht_azc),
        'significant': p_rho_ht_azc < 0.05
    },
    'test3_a_azc': {
        'rho': float(rho_a_azc),
        'p': float(p_rho_a_azc),
        'significant': p_rho_a_azc < 0.05
    },
    'profile_complexity': profile_complexity,
    'top_folios': [(f, m['complexity_mult']) for f, m in ranked[:5]],
}

# Interpretation
print("\nPairwise correlations:")
print(f"  HT x A:   rho={rho_ht_a:.3f} {'(SIG)' if p_rho_ht_a < 0.05 else '(ns)'}")
print(f"  HT x AZC: rho={rho_ht_azc:.3f} {'(SIG)' if p_rho_ht_azc < 0.05 else '(ns)'}")
print(f"  A x AZC:  rho={rho_a_azc:.3f} {'(SIG)' if p_rho_a_azc < 0.05 else '(ns)'}")

sig_count = sum([p_rho_ht_a < 0.05, p_rho_ht_azc < 0.05, p_rho_a_azc < 0.05])

if sig_count >= 2:
    print("\n  FINDING: Multiple significant pairwise correlations")
    print("  -> Tri-layer interaction EXISTS")
    verdict = "INTERACTION_DETECTED"
elif sig_count == 1:
    print("\n  FINDING: Single significant correlation")
    print("  -> Partial coupling, not full tri-layer")
    verdict = "PARTIAL_COUPLING"
else:
    print("\n  FINDING: No significant pairwise correlations")
    print("  -> Layers operate INDEPENDENTLY")
    verdict = "INDEPENDENT_LAYERS"

results['verdict'] = verdict

# Save results
with open('phases/AAZ_a_azc_coordination/trilayer_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to phases/AAZ_a_azc_coordination/trilayer_results.json")

# =============================================================================
# CONSTRAINT EVALUATION
# =============================================================================

print("\n" + "=" * 70)
print("CONSTRAINT EVALUATION")
print("=" * 70)

if verdict == "INTERACTION_DETECTED":
    print("\nPotential constraint:")
    print("  Tri-layer cognitive stratification: HT, A-reference, and AZC-vocabulary")
    print("  densities are mutually correlated within B programs; cognitive load")
    print("  (attentional scaffolding) increases with asset/regime complexity.")
    print("\n  Recommendation: ADD Tier 2 constraint")
elif verdict == "PARTIAL_COUPLING":
    print("\nPartial finding - evaluate case-by-case")
else:
    print("\nNo constraint warranted - layers are independent")
