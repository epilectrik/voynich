"""
T6: AZC-B Vocabulary Compatibility

Question: Which AZC folios most constrain (or enable) B vocabulary?

Method:
1. Build AZC folio x B folio vocabulary overlap matrix
2. Identify which AZC folios have highest/lowest B vocabulary coverage
3. Test: do certain AZC folios serve as "hubs" for B vocabulary?
4. Compare Zodiac vs A/C family B coverage
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ZODIAC_FOLIOS = {
    'f72v3', 'f72v2', 'f72v1', 'f72r3', 'f72r2', 'f72r1',
    'f71v', 'f71r', 'f70v2', 'f70v1', 'f73v', 'f73r', 'f57v'
}

# Collect AZC vocabulary by folio (diagram text only)
print("Collecting AZC vocabulary...")
azc_folio_middles = defaultdict(set)

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    placement = getattr(token, 'placement', '')
    if placement.startswith('P'):
        continue

    m = morph.extract(w)
    if m.middle:
        azc_folio_middles[token.folio].add(m.middle)

# Collect B vocabulary by folio
print("Collecting B vocabulary...")
b_folio_middles = defaultdict(set)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if m.middle:
        b_folio_middles[token.folio].add(m.middle)

azc_folios = sorted(azc_folio_middles.keys())
b_folios = sorted(b_folio_middles.keys())

print(f"AZC folios: {len(azc_folios)}")
print(f"B folios: {len(b_folios)}")

# Build overlap matrix
print(f"\nBuilding {len(azc_folios)} x {len(b_folios)} overlap matrix...")

overlap_matrix = np.zeros((len(azc_folios), len(b_folios)))
jaccard_matrix = np.zeros((len(azc_folios), len(b_folios)))

for i, azc_f in enumerate(azc_folios):
    azc_vocab = azc_folio_middles[azc_f]
    for j, b_f in enumerate(b_folios):
        b_vocab = b_folio_middles[b_f]

        intersection = len(azc_vocab & b_vocab)
        union = len(azc_vocab | b_vocab)

        overlap_matrix[i, j] = intersection
        jaccard_matrix[i, j] = intersection / union if union > 0 else 0

# AZC folio coverage metrics
print("\n" + "="*60)
print("AZC FOLIO B-COVERAGE ANALYSIS")
print("="*60)

results = {
    'azc_stats': {},
    'summary': {},
}

azc_coverage = []
for i, azc_f in enumerate(azc_folios):
    vocab_size = len(azc_folio_middles[azc_f])
    mean_jaccard = np.mean(jaccard_matrix[i, :])
    max_jaccard = np.max(jaccard_matrix[i, :])
    b_covered = np.sum(jaccard_matrix[i, :] > 0)  # B folios with any overlap

    family = 'Zodiac' if azc_f in ZODIAC_FOLIOS else 'A/C'

    results['azc_stats'][azc_f] = {
        'family': family,
        'vocab_size': vocab_size,
        'mean_jaccard': float(mean_jaccard),
        'max_jaccard': float(max_jaccard),
        'b_folios_covered': int(b_covered),
    }

    azc_coverage.append((azc_f, family, vocab_size, mean_jaccard, b_covered))

# Sort by mean Jaccard
azc_coverage.sort(key=lambda x: x[3], reverse=True)

print(f"\nTop 10 AZC folios by B-coverage (mean Jaccard):")
for azc_f, family, vocab, mean_j, b_cov in azc_coverage[:10]:
    print(f"  {azc_f:8} ({family:6}): vocab={vocab:3}, mean_J={mean_j:.3f}, B_covered={b_cov}")

print(f"\nBottom 5 AZC folios by B-coverage:")
for azc_f, family, vocab, mean_j, b_cov in azc_coverage[-5:]:
    print(f"  {azc_f:8} ({family:6}): vocab={vocab:3}, mean_J={mean_j:.3f}, B_covered={b_cov}")

# Family comparison
print("\n" + "="*60)
print("ZODIAC vs A/C FAMILY B-COVERAGE")
print("="*60)

zodiac_jaccards = []
ac_jaccards = []

for i, azc_f in enumerate(azc_folios):
    mean_j = np.mean(jaccard_matrix[i, :])
    if azc_f in ZODIAC_FOLIOS:
        zodiac_jaccards.append(mean_j)
    else:
        ac_jaccards.append(mean_j)

print(f"Zodiac family ({len(zodiac_jaccards)} folios):")
print(f"  Mean B-coverage: {np.mean(zodiac_jaccards):.4f} (std={np.std(zodiac_jaccards):.4f})")

print(f"\nA/C family ({len(ac_jaccards)} folios):")
print(f"  Mean B-coverage: {np.mean(ac_jaccards):.4f} (std={np.std(ac_jaccards):.4f})")

# t-test
t_stat, t_p = stats.ttest_ind(zodiac_jaccards, ac_jaccards)
print(f"\nt-test: t={t_stat:.3f}, p={t_p:.4f}")

# Hub analysis: do a few AZC folios dominate B coverage?
print("\n" + "="*60)
print("AZC HUB ANALYSIS")
print("="*60)

# Sort AZC folios by total B coverage contribution
azc_by_coverage = sorted(
    [(azc_f, np.sum(jaccard_matrix[i, :])) for i, azc_f in enumerate(azc_folios)],
    key=lambda x: x[1], reverse=True
)

total_jaccard = np.sum(jaccard_matrix)

print(f"\nCumulative B coverage by top AZC folios:")
cumulative = 0
for i, (azc_f, contrib) in enumerate(azc_by_coverage[:15]):
    cumulative += contrib
    pct = 100.0 * cumulative / total_jaccard
    family = 'Z' if azc_f in ZODIAC_FOLIOS else 'AC'
    if i < 10 or i == len(azc_by_coverage) - 1:
        print(f"  +{azc_f:8} ({family:2}): cumulative {pct:.1f}%")

# Concentration metric
top5_contrib = sum(x[1] for x in azc_by_coverage[:5])
top10_contrib = sum(x[1] for x in azc_by_coverage[:10])

print(f"\nTop 5 AZC folios provide: {100*top5_contrib/total_jaccard:.1f}% of B coverage")
print(f"Top 10 AZC folios provide: {100*top10_contrib/total_jaccard:.1f}% of B coverage")

# B folio perspective: how many AZC folios does each B folio overlap with?
print("\n" + "="*60)
print("B FOLIO PERSPECTIVE")
print("="*60)

b_azc_overlap_counts = []
for j, b_f in enumerate(b_folios):
    azc_count = np.sum(jaccard_matrix[:, j] > 0)
    b_azc_overlap_counts.append(azc_count)

print(f"Mean AZC folios overlapping per B folio: {np.mean(b_azc_overlap_counts):.1f}")
print(f"Median: {np.median(b_azc_overlap_counts):.0f}")
print(f"Range: {min(b_azc_overlap_counts)} - {max(b_azc_overlap_counts)}")

# Save results
results['summary'] = {
    'azc_folio_count': len(azc_folios),
    'b_folio_count': len(b_folios),
    'zodiac_mean_coverage': float(np.mean(zodiac_jaccards)),
    'ac_mean_coverage': float(np.mean(ac_jaccards)),
    'family_ttest_p': float(t_p),
    'top5_coverage_pct': 100 * top5_contrib / total_jaccard,
    'top10_coverage_pct': 100 * top10_contrib / total_jaccard,
    'b_azc_overlap_mean': float(np.mean(b_azc_overlap_counts)),
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if t_p < 0.01:
    verdict = "FAMILY_B_DIFFERENTIATED"
    print(f"Zodiac and A/C families have DIFFERENT B-coverage profiles (p={t_p:.4f})")
elif top5_contrib / total_jaccard > 0.5:
    verdict = "HUB_DOMINATED"
    print(f"Top 5 AZC folios provide {100*top5_contrib/total_jaccard:.1f}% of B coverage - HUB structure")
else:
    verdict = "DISTRIBUTED_COVERAGE"
    print("B coverage is distributed across AZC folios")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't6_azc_b_compatibility.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")
