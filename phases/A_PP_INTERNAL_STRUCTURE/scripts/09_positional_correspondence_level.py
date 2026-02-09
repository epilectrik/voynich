#!/usr/bin/env python3
"""
Test 9: Positional Correspondence Aggregation Level

Question: Does A-B positional correspondence hold at paragraph level or folio level?

C899 established corpus-wide correspondence (r=0.654).
C885 says folio is the operational unit for vocabulary correspondence.
Does positional correspondence also operate at folio level?
"""

import sys
import io
from pathlib import Path
from collections import defaultdict
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

print("="*70)
print("TEST 9: POSITIONAL CORRESPONDENCE AGGREGATION LEVEL")
print("="*70)

# =========================================================================
# Collect positions by folio
# =========================================================================
print("\nCollecting positions by folio...")

# A positions by folio
a_folio_positions = defaultdict(lambda: defaultdict(list))  # folio -> middle -> [positions]
a_lines = defaultdict(list)

for token in tx.currier_a():
    if '*' not in token.word:
        a_lines[(token.folio, token.line)].append(token.word)

for (folio, line), tokens in a_lines.items():
    if len(tokens) < 2:
        continue
    for i, word in enumerate(tokens):
        try:
            m = morph.extract(word)
            if m.prefix not in RI_PREFIXES and m.middle:
                norm_pos = i / (len(tokens) - 1)
                a_folio_positions[folio][m.middle].append(norm_pos)
        except:
            pass

# B positions by folio
b_folio_positions = defaultdict(lambda: defaultdict(list))
b_lines = defaultdict(list)

for token in tx.currier_b():
    if '*' not in token.word:
        b_lines[(token.folio, token.line)].append(token.word)

for (folio, line), tokens in b_lines.items():
    if len(tokens) < 2:
        continue
    for i, word in enumerate(tokens):
        try:
            m = morph.extract(word)
            if m.middle:
                norm_pos = i / (len(tokens) - 1)
                b_folio_positions[folio][m.middle].append(norm_pos)
        except:
            pass

print(f"  A folios: {len(a_folio_positions)}")
print(f"  B folios: {len(b_folio_positions)}")

# =========================================================================
# Test 1: Within-folio correspondence (for shared folios - should be none)
# =========================================================================
print("\n" + "="*70)
print("TEST 1: SHARED FOLIOS (expecting none per C229)")
print("="*70)

shared_folios = set(a_folio_positions.keys()) & set(b_folio_positions.keys())
print(f"\nShared folios: {len(shared_folios)}")

if shared_folios:
    print("  WARNING: C229 says A and B are folio-disjoint!")
    print(f"  Shared: {list(shared_folios)[:5]}")

# =========================================================================
# Test 2: Cross-folio correspondence at corpus level
# This is what C899 already measured - baseline
# =========================================================================
print("\n" + "="*70)
print("TEST 2: CORPUS-LEVEL CORRESPONDENCE (C899 baseline)")
print("="*70)

# Aggregate all A positions, all B positions
a_all = defaultdict(list)
b_all = defaultdict(list)

for folio, middles in a_folio_positions.items():
    for middle, positions in middles.items():
        a_all[middle].extend(positions)

for folio, middles in b_folio_positions.items():
    for middle, positions in middles.items():
        b_all[middle].extend(positions)

# Find shared MIDDLEs
MIN_COUNT = 20
shared = []
for middle in a_all:
    if middle in b_all:
        if len(a_all[middle]) >= MIN_COUNT and len(b_all[middle]) >= MIN_COUNT:
            shared.append({
                'middle': middle,
                'a_mean': np.mean(a_all[middle]),
                'b_mean': np.mean(b_all[middle]),
            })

a_means = [m['a_mean'] for m in shared]
b_means = [m['b_mean'] for m in shared]
r_corpus, p_corpus = stats.pearsonr(a_means, b_means)

print(f"\nCorpus-level (n={len(shared)} MIDDLEs):")
print(f"  r = {r_corpus:.3f}, p = {p_corpus:.6f}")

# =========================================================================
# Test 3: Folio-level correspondence
# For each A folio, compute mean positions, correlate with corpus B means
# =========================================================================
print("\n" + "="*70)
print("TEST 3: FOLIO-LEVEL CORRESPONDENCE")
print("="*70)

# For each A folio, how well do its PP positions predict corpus-level B positions?
folio_correlations = []

for a_folio, middles in a_folio_positions.items():
    # Get folio's mean positions for shared MIDDLEs
    folio_a = []
    corpus_b = []

    for middle, positions in middles.items():
        if middle in b_all and len(b_all[middle]) >= MIN_COUNT and len(positions) >= 3:
            folio_a.append(np.mean(positions))
            corpus_b.append(np.mean(b_all[middle]))

    if len(folio_a) >= 5:
        r, p = stats.pearsonr(folio_a, corpus_b)
        folio_correlations.append({
            'folio': a_folio,
            'n_middles': len(folio_a),
            'r': r,
            'p': p,
        })

print(f"\nA folios with sufficient shared MIDDLEs: {len(folio_correlations)}")

if folio_correlations:
    rs = [f['r'] for f in folio_correlations]
    print(f"\nFolio-level correlations (A folio positions vs corpus B positions):")
    print(f"  Mean r: {np.mean(rs):.3f}")
    print(f"  Median r: {np.median(rs):.3f}")
    print(f"  Std r: {np.std(rs):.3f}")
    print(f"  Range: {min(rs):.3f} to {max(rs):.3f}")

    # How many folios show significant positive correlation?
    sig_positive = sum(1 for f in folio_correlations if f['r'] > 0 and f['p'] < 0.05)
    sig_negative = sum(1 for f in folio_correlations if f['r'] < 0 and f['p'] < 0.05)
    not_sig = len(folio_correlations) - sig_positive - sig_negative

    print(f"\n  Significant positive: {sig_positive}/{len(folio_correlations)} ({100*sig_positive/len(folio_correlations):.1f}%)")
    print(f"  Significant negative: {sig_negative}/{len(folio_correlations)}")
    print(f"  Not significant: {not_sig}/{len(folio_correlations)}")

    # Top and bottom folios
    sorted_folios = sorted(folio_correlations, key=lambda x: x['r'], reverse=True)

    print("\nTop 5 folios (strongest A-B positional correspondence):")
    for f in sorted_folios[:5]:
        print(f"  {f['folio']}: r={f['r']:.3f} (n={f['n_middles']}, p={f['p']:.4f})")

    print("\nBottom 5 folios (weakest correspondence):")
    for f in sorted_folios[-5:]:
        print(f"  {f['folio']}: r={f['r']:.3f} (n={f['n_middles']}, p={f['p']:.4f})")

# =========================================================================
# Test 4: Is folio-level r different from corpus-level r?
# =========================================================================
print("\n" + "="*70)
print("TEST 4: FOLIO vs CORPUS COMPARISON")
print("="*70)

if folio_correlations:
    mean_folio_r = np.mean(rs)

    print(f"\nCorpus-level r: {r_corpus:.3f}")
    print(f"Mean folio-level r: {mean_folio_r:.3f}")
    print(f"Difference: {r_corpus - mean_folio_r:.3f}")

    # One-sample t-test: is mean folio r different from corpus r?
    t_stat, t_p = stats.ttest_1samp(rs, r_corpus)
    print(f"\nT-test (folio mean vs corpus): t={t_stat:.2f}, p={t_p:.4f}")

    if t_p < 0.05:
        if mean_folio_r < r_corpus:
            print("** Folio-level r is LOWER than corpus r **")
            print("   Interpretation: Correspondence is stronger at corpus level")
        else:
            print("** Folio-level r is HIGHER than corpus r **")
            print("   Interpretation: Correspondence is even stronger within folios")
    else:
        print("No significant difference between folio and corpus level")

# =========================================================================
# Test 5: Variance in folio positions
# Does each folio have its own positional profile, or do they share one?
# =========================================================================
print("\n" + "="*70)
print("TEST 5: FOLIO POSITIONAL VARIANCE")
print("="*70)

# For each shared MIDDLE, compute variance of mean positions across A folios
middle_folio_variance = []

for middle in a_all:
    if middle in b_all and len(a_all[middle]) >= MIN_COUNT:
        # Get mean position in each A folio
        folio_means = []
        for folio, middles in a_folio_positions.items():
            if middle in middles and len(middles[middle]) >= 3:
                folio_means.append(np.mean(middles[middle]))

        if len(folio_means) >= 5:
            middle_folio_variance.append({
                'middle': middle,
                'n_folios': len(folio_means),
                'variance': np.var(folio_means),
                'std': np.std(folio_means),
                'corpus_mean': np.mean(a_all[middle]),
            })

if middle_folio_variance:
    vars = [m['variance'] for m in middle_folio_variance]
    stds = [m['std'] for m in middle_folio_variance]

    print(f"\nMIDDLEs with position data in 5+ folios: {len(middle_folio_variance)}")
    print(f"\nVariance of mean positions across folios:")
    print(f"  Mean variance: {np.mean(vars):.4f}")
    print(f"  Mean std: {np.mean(stds):.3f}")

    # Low variance = positions are consistent across folios
    # High variance = each folio has its own positional profile

    print("\nMIDDLEs with LOWEST cross-folio variance (most stable positions):")
    sorted_var = sorted(middle_folio_variance, key=lambda x: x['variance'])
    for m in sorted_var[:5]:
        print(f"  {m['middle']:<12} var={m['variance']:.4f}, std={m['std']:.3f}, mean={m['corpus_mean']:.3f}")

    print("\nMIDDLEs with HIGHEST cross-folio variance (folio-specific positions):")
    for m in sorted_var[-5:]:
        print(f"  {m['middle']:<12} var={m['variance']:.4f}, std={m['std']:.3f}, mean={m['corpus_mean']:.3f}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

findings = []

if folio_correlations:
    if mean_folio_r > 0.3:
        findings.append(f"FOLIO-LEVEL CORRESPONDENCE EXISTS: mean r={mean_folio_r:.2f}")

    if t_p >= 0.05:
        findings.append("FOLIO and CORPUS levels show SIMILAR correspondence strength")
    elif mean_folio_r < r_corpus:
        findings.append("CORPUS level shows STRONGER correspondence than individual folios")
    else:
        findings.append("FOLIO level shows STRONGER correspondence than corpus aggregate")

    pct_sig = 100 * sig_positive / len(folio_correlations)
    if pct_sig > 50:
        findings.append(f"MAJORITY ({pct_sig:.0f}%) of folios show significant positive correspondence")

if middle_folio_variance:
    mean_std = np.mean(stds)
    if mean_std < 0.1:
        findings.append(f"STABLE positions across folios (mean std={mean_std:.3f})")
    elif mean_std > 0.15:
        findings.append(f"VARIABLE positions across folios (mean std={mean_std:.3f})")

print("\nKey findings:")
for i, f in enumerate(findings, 1):
    print(f"  {i}. {f}")

# Determine verdict
if folio_correlations and mean_folio_r > 0.3 and sig_positive > len(folio_correlations) / 2:
    verdict = "FOLIO-LEVEL"
    explanation = "Correspondence operates at folio level - individual A folios predict B positions"
elif folio_correlations and mean_folio_r > 0 and r_corpus > mean_folio_r + 0.1:
    verdict = "CORPUS-LEVEL"
    explanation = "Correspondence is emergent - stronger when aggregated across folios"
else:
    verdict = "INCONCLUSIVE"
    explanation = "Cannot determine primary aggregation level"

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'corpus_r': float(r_corpus),
    'n_folios_tested': len(folio_correlations) if folio_correlations else 0,
    'mean_folio_r': float(mean_folio_r) if folio_correlations else None,
    'pct_significant_positive': float(100 * sig_positive / len(folio_correlations)) if folio_correlations else None,
    'mean_cross_folio_std': float(np.mean(stds)) if middle_folio_variance else None,
    'findings': findings,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'positional_correspondence_level.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to {output_path}")
