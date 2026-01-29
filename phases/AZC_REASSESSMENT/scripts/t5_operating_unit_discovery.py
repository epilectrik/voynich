"""
T5: Operating Unit Discovery

Objective: Empirically find the granularity at which A->B routing is non-degenerate

Method: Vary unit size (1 line, 2-line window, 5-line window, half-folio, full folio)
        For each, compute:
        - Number of A units that uniquely serve as best-match for some B folio
        - Mean coverage of B vocabulary
        - Discrimination ratio (best-match coverage / second-best coverage)

Success: Find unit size where discrimination ratio > 1.5 AND unique best-matches > 30

This is the key test: if we can't find ANY granularity with non-degenerate routing,
the routing model is falsified.
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=== T5: OPERATING UNIT DISCOVERY ===\n")

# Build A data organized by folio and line
print("Building A data by folio and line...")
a_folio_lines = defaultdict(lambda: defaultdict(list))
a_folio_section = {}

for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    a_folio_lines[t.folio][t.line].append(w)
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

# Collect B folio tokens with morphology
b_folio_tokens = defaultdict(list)
b_folio_section = {}
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    b_folio_tokens[t.folio].append(w)
    if t.folio not in b_folio_section:
        b_folio_section[t.folio] = t.section

b_folios = sorted(b_folio_tokens.keys())

# Pre-compute B morphologies
b_folio_morphs = {}
for b_fol in b_folios:
    b_folio_morphs[b_fol] = [morph.extract(w) for w in b_folio_tokens[b_fol]]

print(f"  {len(a_folio_lines)} A folios, {len(b_folios)} B folios")

# Count total A lines
total_a_lines = sum(len(lines) for lines in a_folio_lines.values())
print(f"  {total_a_lines} total A lines")

def build_unit_pools(unit_size):
    """
    Build A units at specified granularity.

    unit_size:
        1 = single line
        2, 3, 5 = sliding window of N lines
        'half' = half folio
        'full' = full folio
    """
    units = []

    for fol in sorted(a_folio_lines.keys()):
        lines = a_folio_lines[fol]
        sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

        if unit_size == 'full':
            # Full folio
            all_words = []
            for ln in sorted_line_nums:
                all_words.extend(lines[ln])
            if all_words:
                units.append({
                    'id': f"{fol}_full",
                    'folio': fol,
                    'words': all_words,
                })

        elif unit_size == 'half':
            # Half folio
            mid = len(sorted_line_nums) // 2
            first_half = []
            second_half = []
            for i, ln in enumerate(sorted_line_nums):
                if i < mid:
                    first_half.extend(lines[ln])
                else:
                    second_half.extend(lines[ln])
            if first_half:
                units.append({
                    'id': f"{fol}_h1",
                    'folio': fol,
                    'words': first_half,
                })
            if second_half:
                units.append({
                    'id': f"{fol}_h2",
                    'folio': fol,
                    'words': second_half,
                })

        elif isinstance(unit_size, int):
            # Sliding window
            for start_idx in range(0, len(sorted_line_nums), max(1, unit_size // 2)):
                end_idx = min(start_idx + unit_size, len(sorted_line_nums))
                window_words = []
                for i in range(start_idx, end_idx):
                    window_words.extend(lines[sorted_line_nums[i]])
                if window_words:
                    units.append({
                        'id': f"{fol}_L{start_idx}_{end_idx}",
                        'folio': fol,
                        'words': window_words,
                    })

    # Build component pools for each unit
    for unit in units:
        mids, prefs, sufs = set(), set(), set()
        for w in unit['words']:
            m = morph.extract(w)
            if m.middle:
                mids.add(m.middle)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
        unit['pool'] = (mids, prefs, sufs)
        unit['pool_size'] = len(mids)

    return units

def compute_coverage_matrix(units, b_folios, b_folio_tokens, b_folio_morphs):
    """Compute coverage matrix for given A units."""
    coverage = np.zeros((len(units), len(b_folios)))

    for i, unit in enumerate(units):
        a_m, a_p, a_s = unit['pool']
        for j, b_fol in enumerate(b_folios):
            tokens = b_folio_tokens[b_fol]
            morphs = b_folio_morphs[b_fol]
            legal = 0
            for w, mo in zip(tokens, morphs):
                if mo.middle and mo.middle in a_m:
                    if (not mo.prefix or mo.prefix in a_p):
                        if (not mo.suffix or mo.suffix in a_s):
                            legal += 1
            coverage[i, j] = legal / len(tokens) if tokens else 0

    return coverage

def analyze_granularity(units, coverage):
    """Analyze assignment map at this granularity."""
    n_units = len(units)
    n_b = coverage.shape[1]

    # For each B folio, find best-match unit
    best_matches = []
    for j in range(n_b):
        col = coverage[:, j]
        if col.max() == 0:
            best_matches.append(None)
            continue

        ranked = np.argsort(-col)
        best_i = ranked[0]
        second_i = ranked[1] if n_units > 1 else 0

        best_cov = col[best_i]
        second_cov = col[second_i]
        disc_ratio = best_cov / second_cov if second_cov > 0 else float('inf')

        best_matches.append({
            'best_unit': units[best_i]['id'],
            'best_folio': units[best_i]['folio'],
            'best_cov': best_cov,
            'second_cov': second_cov,
            'disc_ratio': disc_ratio,
        })

    # Count unique best-match units
    unique_units = len(set(bm['best_unit'] for bm in best_matches if bm is not None))

    # Mean coverage
    valid_matches = [bm for bm in best_matches if bm is not None]
    mean_cov = np.mean([bm['best_cov'] for bm in valid_matches]) if valid_matches else 0
    mean_disc = np.mean([min(bm['disc_ratio'], 10) for bm in valid_matches]) if valid_matches else 0

    # Count B folios with strong discrimination (ratio > 1.5)
    strong_disc = sum(1 for bm in valid_matches if bm['disc_ratio'] > 1.5)

    return {
        'n_units': n_units,
        'unique_best_matches': unique_units,
        'mean_coverage': mean_cov,
        'mean_discrimination': mean_disc,
        'strong_discrimination_count': strong_disc,
    }

# Test different granularities
granularities = [
    ('1_line', 1),
    ('2_line', 2),
    ('3_line', 3),
    ('5_line', 5),
    ('half_folio', 'half'),
    ('full_folio', 'full'),
]

print("\n=== TESTING GRANULARITIES ===\n")
print(f"{'Granularity':<15s} {'N Units':>10s} {'Unique BM':>12s} {'Mean Cov':>10s} {'Mean Disc':>10s} {'Strong':>8s}")
print("-" * 70)

results_by_gran = {}

for name, unit_size in granularities:
    units = build_unit_pools(unit_size)
    if len(units) == 0:
        print(f"{name:<15s} {'No units':<10s}")
        continue

    coverage = compute_coverage_matrix(units, b_folios, b_folio_tokens, b_folio_morphs)
    analysis = analyze_granularity(units, coverage)

    print(f"{name:<15s} {analysis['n_units']:>10d} {analysis['unique_best_matches']:>12d} "
          f"{analysis['mean_coverage']*100:>9.1f}% {analysis['mean_discrimination']:>10.2f} "
          f"{analysis['strong_discrimination_count']:>8d}")

    results_by_gran[name] = {
        'unit_size': str(unit_size),
        **analysis,
    }

# Find best granularity
print("\n=== ANALYSIS ===\n")

# Success criteria: disc > 1.5 AND unique > 30
best_gran = None
best_score = 0

for name, res in results_by_gran.items():
    # Score = unique_best_matches if mean_discrimination > 1.2
    if res['mean_discrimination'] > 1.2:
        score = res['unique_best_matches']
        if score > best_score:
            best_score = score
            best_gran = name

if best_gran:
    print(f"Best granularity: {best_gran}")
    print(f"  Unique best-matches: {results_by_gran[best_gran]['unique_best_matches']}")
    print(f"  Mean discrimination: {results_by_gran[best_gran]['mean_discrimination']:.2f}")
else:
    print("No granularity achieves both discrimination > 1.2 AND unique > 30")

# Check if ANY granularity achieves the success threshold
threshold_disc = 1.5
threshold_unique = 30

success = False
success_gran = None
for name, res in results_by_gran.items():
    if res['mean_discrimination'] > threshold_disc and res['unique_best_matches'] > threshold_unique:
        success = True
        success_gran = name
        break

if success:
    verdict = "GRANULARITY_FOUND"
    explanation = f"{success_gran} achieves disc > {threshold_disc} AND unique > {threshold_unique}"
else:
    # Check what's closest
    closest_name = None
    closest_gap = float('inf')
    for name, res in results_by_gran.items():
        disc_gap = max(0, threshold_disc - res['mean_discrimination'])
        unique_gap = max(0, threshold_unique - res['unique_best_matches']) / threshold_unique
        total_gap = disc_gap + unique_gap
        if total_gap < closest_gap:
            closest_gap = total_gap
            closest_name = name

    verdict = "NO_GRANULARITY"
    explanation = f"No granularity achieves thresholds. Closest: {closest_name}"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Additional insight: is degeneracy unavoidable?
print("\n=== DEGENERACY ANALYSIS ===\n")

# At each granularity, what fraction of B folios are served by the top N units?
for name, unit_size in granularities:
    units = build_unit_pools(unit_size)
    if len(units) == 0:
        continue

    coverage = compute_coverage_matrix(units, b_folios, b_folio_tokens, b_folio_morphs)

    # Count how many B folios each unit best-serves
    serve_count = Counter()
    for j in range(len(b_folios)):
        col = coverage[:, j]
        if col.max() > 0:
            best_i = np.argmax(col)
            serve_count[units[best_i]['id']] += 1

    # Top 3 units
    top3 = serve_count.most_common(3)
    top3_total = sum(c for _, c in top3)

    print(f"{name}: top 3 units serve {top3_total}/{len(b_folios)} B folios ({top3_total/len(b_folios)*100:.0f}%)")

# Save results
results = {
    'test': 'T5_operating_unit_discovery',
    'b_folios_count': len(b_folios),
    'granularities': results_by_gran,
    'thresholds': {
        'discrimination': threshold_disc,
        'unique_matches': threshold_unique,
    },
    'best_granularity': best_gran,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't5_operating_unit_discovery.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
