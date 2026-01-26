"""
AX_CLASS_BEHAVIOR Script 2: Per-class positional profiles.
Full positional CDFs, KS tests vs population, pairwise KS matrix.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Transcript

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
RESULTS = BASE / 'phases/AX_CLASS_BEHAVIOR/results'

# Load class map
with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load AX census
with open(CENSUS_FILE) as f:
    census = json.load(f)
AX_CLASSES = set(census['definitive_ax_classes'])

# Load transcript and collect positions per class
tx = Transcript()
lines = defaultdict(list)
for token in tx.currier_b():
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append(cls)

# Compute normalized positions for each AX class
class_positions = defaultdict(list)
all_ax_positions = []

for line_key, classes in lines.items():
    n = len(classes)
    if n < 2:
        continue
    for i, cls in enumerate(classes):
        if cls is not None and cls in AX_CLASSES:
            pos = i / (n - 1)
            class_positions[cls].append(pos)
            all_ax_positions.append(pos)

print(f"Total AX tokens with positions: {len(all_ax_positions)}")
print(f"AX classes found: {sorted(class_positions.keys())}")

sorted_classes = sorted(AX_CLASSES)

# ── Compute CDFs in 10 bins ──

def compute_histogram(positions, n_bins=10):
    counts = [0] * n_bins
    for p in positions:
        b = min(int(p * n_bins), n_bins - 1)
        counts[b] += 1
    total = len(positions)
    freqs = [c / total if total > 0 else 0 for c in counts]
    cdf = []
    cumsum = 0
    for f in freqs:
        cumsum += f
        cdf.append(round(cumsum, 4))
    bin_centers = [round((i + 0.5) / n_bins, 2) for i in range(n_bins)]
    return {
        'bin_centers': bin_centers,
        'counts': counts,
        'frequencies': [round(f, 4) for f in freqs],
        'cdf': cdf,
    }

population_cdf = compute_histogram(all_ax_positions)

per_class_cdf = {}
per_class_stats = {}
for cls in sorted_classes:
    positions = class_positions.get(cls, [])
    per_class_cdf[str(cls)] = compute_histogram(positions)
    if positions:
        positions_sorted = sorted(positions)
        n = len(positions)
        mean = sum(positions) / n
        var = sum((p - mean) ** 2 for p in positions) / n
        per_class_stats[str(cls)] = {
            'n': n,
            'mean': round(mean, 4),
            'std': round(math.sqrt(var), 4),
            'median': round(positions_sorted[n // 2], 4),
            'q25': round(positions_sorted[n // 4], 4),
            'q75': round(positions_sorted[3 * n // 4], 4),
            'min': round(positions_sorted[0], 4),
            'max': round(positions_sorted[-1], 4),
        }
    else:
        per_class_stats[str(cls)] = {'n': 0}

# ── KS test implementation ──

def ks_2sample(data1, data2):
    """Two-sample Kolmogorov-Smirnov test. Returns D-statistic and approximate p-value."""
    n1, n2 = len(data1), len(data2)
    if n1 == 0 or n2 == 0:
        return 0, 1.0

    s1 = sorted(data1)
    s2 = sorted(data2)

    # Merge and compute ECDFs
    all_vals = sorted(set(s1 + s2))
    max_d = 0

    idx1, idx2 = 0, 0
    for val in all_vals:
        while idx1 < n1 and s1[idx1] <= val:
            idx1 += 1
        while idx2 < n2 and s2[idx2] <= val:
            idx2 += 1
        d = abs(idx1 / n1 - idx2 / n2)
        if d > max_d:
            max_d = d

    # Approximate p-value (asymptotic)
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * max_d

    # Kolmogorov distribution approximation
    if lam < 0.001:
        p = 1.0
    else:
        # Series approximation
        p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 101))
        p = max(0.0, min(1.0, p))

    return round(max_d, 4), p

# ── Per-class vs population KS tests ──

print(f"\n=== Per-Class vs Population KS Tests ===")
per_class_ks = {}
for cls in sorted_classes:
    positions = class_positions.get(cls, [])
    D, p = ks_2sample(positions, all_ax_positions)
    significant_raw = p < 0.01
    significant_bonferroni = p < (0.01 / 20)
    per_class_ks[str(cls)] = {
        'D': D,
        'p': round(p, 8),
        'significant_raw': significant_raw,
        'significant_bonferroni': significant_bonferroni,
        'n': len(positions),
    }
    sig = "**DISTINCT**" if significant_bonferroni else ("*distinct*" if significant_raw else "similar")
    print(f"  Class {cls:2d} (n={len(positions):4d}): D={D:.4f}, p={p:.2e} {sig}")

# ── Pairwise KS matrix ──

print(f"\n=== Pairwise KS Tests (190 pairs) ===")
pairwise_ks = {}
pairs_raw = 0
pairs_bonferroni = 0
n_pairs = len(sorted_classes) * (len(sorted_classes) - 1) // 2
bonferroni_threshold = 0.01 / n_pairs

for i, cls_a in enumerate(sorted_classes):
    for cls_b in sorted_classes[i + 1:]:
        pos_a = class_positions.get(cls_a, [])
        pos_b = class_positions.get(cls_b, [])
        D, p = ks_2sample(pos_a, pos_b)
        key = f"{cls_a}_{cls_b}"
        pairwise_ks[key] = {
            'D': D,
            'p': round(p, 8),
            'significant_raw': p < 0.01,
            'significant_bonferroni': p < bonferroni_threshold,
        }
        if p < 0.01:
            pairs_raw += 1
        if p < bonferroni_threshold:
            pairs_bonferroni += 1

# Position heatmap (20 x 10)
heatmap = []
heatmap_classes = []
for cls in sorted_classes:
    cdf_data = per_class_cdf[str(cls)]
    heatmap.append(cdf_data['frequencies'])
    heatmap_classes.append(cls)

# ── Find most/least distinguishable pairs ──

sorted_pairs = sorted(pairwise_ks.items(), key=lambda x: x[1]['D'], reverse=True)
most_distinct = sorted_pairs[:5]
least_distinct = sorted_pairs[-5:]

# ── Summary ──

distinct_from_pop_raw = sum(1 for v in per_class_ks.values() if v['significant_raw'])
distinct_from_pop_bonf = sum(1 for v in per_class_ks.values() if v['significant_bonferroni'])

print(f"\nClasses distinct from population (raw p<0.01): {distinct_from_pop_raw}/20")
print(f"Classes distinct from population (Bonferroni p<{0.01/20:.4f}): {distinct_from_pop_bonf}/20")
print(f"Pairs distinct (raw p<0.01): {pairs_raw}/{n_pairs}")
print(f"Pairs distinct (Bonferroni p<{bonferroni_threshold:.2e}): {pairs_bonferroni}/{n_pairs}")

print(f"\nMost distinct pairs:")
for key, val in most_distinct:
    print(f"  {key}: D={val['D']:.4f}, p={val['p']:.2e}")

print(f"\nLeast distinct pairs:")
for key, val in least_distinct:
    print(f"  {key}: D={val['D']:.4f}, p={val['p']:.2e}")

# ── Save results ──

results = {
    'population_cdf': population_cdf,
    'per_class_cdf': per_class_cdf,
    'per_class_stats': per_class_stats,
    'per_class_vs_population_ks': per_class_ks,
    'pairwise_ks': pairwise_ks,
    'summary': {
        'total_ax_tokens': len(all_ax_positions),
        'n_classes': len(sorted_classes),
        'classes_distinct_from_population_raw': distinct_from_pop_raw,
        'classes_distinct_from_population_bonferroni': distinct_from_pop_bonf,
        'pairs_distinct_raw': pairs_raw,
        'pairs_distinct_bonferroni': pairs_bonferroni,
        'total_pairs': n_pairs,
        'bonferroni_threshold': round(bonferroni_threshold, 8),
        'position_heatmap': heatmap,
        'heatmap_classes': heatmap_classes,
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_class_positional_profiles.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_class_positional_profiles.json'}")
