"""
Q8: Line Length by REGIME

Are some REGIMEs more verbose? Does REGIME correlate with program complexity?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

print("=" * 70)
print("Q8: LINE LENGTH BY REGIME")
print("=" * 70)

# Group tokens by line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    lines[(folio, line)].append(word)

# Calculate line lengths by REGIME
regime_lengths = defaultdict(list)
for (folio, line), words in lines.items():
    regime = folio_regime.get(folio)
    if regime:
        regime_lengths[regime].append(len(words))

print("\n" + "-" * 70)
print("1. LINE LENGTH STATISTICS")
print("-" * 70)

print("\n| REGIME | Lines | Mean | Median | Std | Min | Max |")
print("|--------|-------|------|--------|-----|-----|-----|")

all_lengths = []
for regime in sorted(regime_lengths.keys()):
    lengths = regime_lengths[regime]
    all_lengths.extend(lengths)
    print(f"| {regime} | {len(lengths):5d} | {np.mean(lengths):.2f} | {np.median(lengths):.1f}    | {np.std(lengths):.2f} | {min(lengths):3d} | {max(lengths):3d} |")

print(f"| TOTAL    | {len(all_lengths):5d} | {np.mean(all_lengths):.2f} | {np.median(all_lengths):.1f}    | {np.std(all_lengths):.2f} | {min(all_lengths):3d} | {max(all_lengths):3d} |")

# Statistical test: Kruskal-Wallis
print("\n" + "-" * 70)
print("2. STATISTICAL COMPARISON")
print("-" * 70)

regime_arrays = [regime_lengths[r] for r in sorted(regime_lengths.keys())]
stat, p = stats.kruskal(*regime_arrays)
print(f"\nKruskal-Wallis test: H={stat:.2f}, p={p:.6f}")

if p < 0.05:
    print("SIGNIFICANT: REGIMEs have different line lengths")
else:
    print("NOT SIGNIFICANT: REGIMEs have similar line lengths")

# Pairwise comparisons
print("\nPairwise Mann-Whitney U tests (Bonferroni corrected):")
print("| Comparison | U | p-value | Significant |")
print("|------------|---|---------|-------------|")

regimes = sorted(regime_lengths.keys())
n_comparisons = len(regimes) * (len(regimes) - 1) // 2
alpha = 0.05 / n_comparisons

for i, r1 in enumerate(regimes):
    for r2 in regimes[i+1:]:
        stat, p = stats.mannwhitneyu(regime_lengths[r1], regime_lengths[r2], alternative='two-sided')
        sig = "YES" if p < alpha else "no"
        print(f"| {r1} vs {r2} | {stat:.0f} | {p:.6f} | {sig} |")

# Line length distribution by REGIME
print("\n" + "-" * 70)
print("3. LINE LENGTH DISTRIBUTION")
print("-" * 70)

print("\nPercentage of lines by length category:")
print("| REGIME | Short (1-3) | Medium (4-7) | Long (8+) |")
print("|--------|-------------|--------------|-----------|")

for regime in sorted(regime_lengths.keys()):
    lengths = regime_lengths[regime]
    total = len(lengths)
    short = sum(1 for l in lengths if l <= 3) / total * 100
    medium = sum(1 for l in lengths if 4 <= l <= 7) / total * 100
    long = sum(1 for l in lengths if l >= 8) / total * 100
    print(f"| {regime} | {short:10.1f}% | {medium:11.1f}% | {long:8.1f}% |")

# Folio-level analysis
print("\n" + "-" * 70)
print("4. FOLIO-LEVEL AVERAGE LINE LENGTH")
print("-" * 70)

folio_avg_lengths = defaultdict(list)
for (folio, line), words in lines.items():
    folio_avg_lengths[folio].append(len(words))

folio_means = {f: np.mean(lengths) for f, lengths in folio_avg_lengths.items()}

print("\nTop 10 longest average line length folios:")
print("| Folio | REGIME | Avg Length | Lines |")
print("|-------|--------|------------|-------|")
for folio in sorted(folio_means.keys(), key=lambda f: folio_means[f], reverse=True)[:10]:
    regime = folio_regime.get(folio, 'N/A')
    print(f"| {folio:5s} | {regime} | {folio_means[folio]:.2f}      | {len(folio_avg_lengths[folio]):5d} |")

print("\nTop 10 shortest average line length folios:")
print("| Folio | REGIME | Avg Length | Lines |")
print("|-------|--------|------------|-------|")
for folio in sorted(folio_means.keys(), key=lambda f: folio_means[f])[:10]:
    regime = folio_regime.get(folio, 'N/A')
    print(f"| {folio:5s} | {regime} | {folio_means[folio]:.2f}      | {len(folio_avg_lengths[folio]):5d} |")

# Correlation with folio position
print("\n" + "-" * 70)
print("5. LINE LENGTH vs MANUSCRIPT POSITION")
print("-" * 70)

# Sort folios by their numeric value (approximating manuscript order)
folio_order = []
for folio in folio_means.keys():
    # Extract numeric part
    try:
        num = int(''.join(c for c in folio if c.isdigit()))
        folio_order.append((num, folio, folio_means[folio]))
    except:
        pass

folio_order.sort()
positions = list(range(len(folio_order)))
lengths = [f[2] for f in folio_order]

corr, p = stats.spearmanr(positions, lengths)
print(f"\nSpearman correlation (position vs avg line length): rho={corr:.3f}, p={p:.4f}")

if abs(corr) > 0.3:
    direction = "LONGER" if corr > 0 else "SHORTER"
    print(f"Lines get {direction} as manuscript progresses")
else:
    print("No significant trend across manuscript")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

means = {r: np.mean(regime_lengths[r]) for r in regime_lengths}
max_regime = max(means, key=means.get)
min_regime = min(means, key=means.get)

print(f"""
1. REGIME LINE LENGTH:
   - Longest: {max_regime} (mean {means[max_regime]:.2f} words/line)
   - Shortest: {min_regime} (mean {means[min_regime]:.2f} words/line)
   - Ratio: {means[max_regime]/means[min_regime]:.2f}x

2. STATISTICAL SIGNIFICANCE: {'YES' if p < 0.05 else 'NO'}
   - Kruskal-Wallis p={p:.6f}

3. MANUSCRIPT TREND: {'YES' if abs(corr) > 0.3 else 'NO'}
   - Spearman rho={corr:.3f}
""")

# Save results
results = {
    'regime_stats': {
        r: {
            'mean': float(np.mean(regime_lengths[r])),
            'median': float(np.median(regime_lengths[r])),
            'std': float(np.std(regime_lengths[r])),
            'count': len(regime_lengths[r])
        }
        for r in regime_lengths
    },
    'kruskal_wallis': {'stat': float(stat), 'p': float(p)},
    'manuscript_correlation': {'rho': float(corr), 'p': float(p)}
}

with open(RESULTS / 'line_length_by_regime.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'line_length_by_regime.json'}")
