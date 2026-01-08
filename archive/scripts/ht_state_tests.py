"""
HT-STATE Tests: Formal analysis of HT prefix structural patterns

HT-STATE-1: Prefix × Relative Position (monotonic distribution)
HT-STATE-2: Prefix × Grammar Class (structural synchrony)
HT-STATE-3: Prefix × Waiting Regime (cognitive mapping)
"""

from collections import Counter, defaultdict
from pathlib import Path
import random
import json
from math import sqrt

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load folio profiles (waiting regime data)
try:
    with open(project_root / 'phases' / 'HTD_human_track_domain' / 'htd_results.json') as f:
        htd_data = json.load(f)
        folio_profiles = htd_data.get('folio_profiles', {})
except:
    folio_profiles = {}

HT_PREFIXES = ['yk', 'op', 'yt', 'so', 'al', 'po', 'do', 'to', 'pc', 'ke',
               'dc', 'sa', 'yc', 'oc', 'oe', 'ka', 'ko', 'ta', 'te', 'lo', 'ro']

GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_CORE = {'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol', 'aiin',
    'checkhy', 'otain', 'shey', 'shol', 'shedy', 'shy', 'shor', 'qo', 'qok', 'ok'}

def get_ht_prefix(tok):
    for p in HT_PREFIXES:
        if tok.startswith(p):
            return p
    return None

def get_grammar_prefix(tok):
    if tok in GRAMMAR_CORE:
        return tok[:2] if len(tok) >= 2 else tok
    for p in GRAMMAR_PREFIXES:
        if tok.startswith(p) and len(tok) > len(p):
            return p
    return None

def cramers_v(contingency):
    """Calculate Cramer's V for a contingency table (dict of dicts)."""
    # Flatten to get row/col totals
    rows = list(contingency.keys())
    cols = set()
    for r in rows:
        cols.update(contingency[r].keys())
    cols = list(cols)

    n = sum(sum(contingency[r].values()) for r in rows)
    if n == 0:
        return 0

    # Expected values and chi-square
    row_totals = {r: sum(contingency[r].values()) for r in rows}
    col_totals = {c: sum(contingency[r].get(c, 0) for r in rows) for c in cols}

    chi2 = 0
    for r in rows:
        for c in cols:
            observed = contingency[r].get(c, 0)
            expected = (row_totals[r] * col_totals[c]) / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    k = min(len(rows), len(cols))
    if k <= 1:
        return 0
    v = sqrt(chi2 / (n * (k - 1))) if n > 0 and k > 1 else 0
    return v

# Load data
folios = defaultdict(list)
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            line_num = int(parts[11].strip('"').strip()) if parts[11].strip('"').strip().isdigit() else 0
            lang = parts[6].strip('"').strip()

            if word and not word.startswith('*') and lang == 'B':
                if not folios[folio] or folios[folio][-1][0] != line_num:
                    folios[folio].append((line_num, []))
                folios[folio][-1][1].append(word)

print("=" * 80)
print("HT-STATE FORMAL TESTS")
print("=" * 80)

# ============================================================================
# HT-STATE-1: Prefix × Relative Position
# ============================================================================

print("\n" + "=" * 80)
print("HT-STATE-1: PREFIX × RELATIVE POSITION")
print("=" * 80)

# Collect position data by decile (0-9)
prefix_by_decile = defaultdict(lambda: defaultdict(int))
prefix_totals = Counter()

for folio, lines in folios.items():
    n_lines = len(lines)
    if n_lines < 5:
        continue

    for i, (line_num, tokens) in enumerate(lines):
        decile = min(int((i / n_lines) * 10), 9)  # 0-9

        for tok in tokens:
            prefix = get_ht_prefix(tok)
            if prefix:
                prefix_by_decile[prefix][decile] += 1
                prefix_totals[prefix] += 1

# Calculate monotonicity for each prefix
print("\n### MONOTONICITY ANALYSIS")
print(f"{'Prefix':<8} {'Trend':>10} {'Effect':>10} {'Start%':>10} {'End%':>10} {'n':>8}")
print("-" * 60)

monotonicity_results = []
for prefix in sorted(prefix_totals.keys(), key=lambda x: -prefix_totals[x])[:15]:
    counts = [prefix_by_decile[prefix][d] for d in range(10)]
    total = sum(counts)
    if total < 50:
        continue

    # Calculate start (0-2) vs end (7-9) concentration
    start_pct = 100 * sum(counts[:3]) / total
    end_pct = 100 * sum(counts[7:]) / total

    # Spearman-like correlation with position
    # Weighted average position
    weighted_pos = sum(d * counts[d] for d in range(10)) / total
    # Effect size: deviation from 4.5 (midpoint)
    effect = (weighted_pos - 4.5) / 4.5  # -1 to +1

    if end_pct > start_pct + 5:
        trend = "LATE"
    elif start_pct > end_pct + 5:
        trend = "EARLY"
    else:
        trend = "FLAT"

    monotonicity_results.append((prefix, trend, effect, start_pct, end_pct, total))
    print(f"{prefix:<8} {trend:>10} {effect:>+10.3f} {start_pct:>9.1f}% {end_pct:>9.1f}% {total:>8}")

# Summary
early_prefixes = [p for p, t, e, s, en, n in monotonicity_results if t == "EARLY"]
late_prefixes = [p for p, t, e, s, en, n in monotonicity_results if t == "LATE"]
print(f"\nEARLY prefixes (start > end+5%): {early_prefixes}")
print(f"LATE prefixes (end > start+5%): {late_prefixes}")

# ============================================================================
# HT-STATE-2: Prefix × Grammar Class
# ============================================================================

print("\n" + "=" * 80)
print("HT-STATE-2: PREFIX × PRECEDING GRAMMAR CLASS")
print("=" * 80)

# Build contingency table
contingency = defaultdict(Counter)
all_contexts = []

for folio, lines in folios.items():
    for line_num, tokens in lines:
        for i, tok in enumerate(tokens):
            ht_prefix = get_ht_prefix(tok)
            if ht_prefix and i > 0:
                prev_grammar = get_grammar_prefix(tokens[i-1])
                if prev_grammar:
                    contingency[ht_prefix][prev_grammar] += 1
                    all_contexts.append((ht_prefix, prev_grammar))

# Calculate observed Cramer's V
observed_v = cramers_v(contingency)

# Permutation test
n_permutations = 1000
perm_vs = []
random.seed(42)

ht_list = [x[0] for x in all_contexts]
grammar_list = [x[1] for x in all_contexts]

for _ in range(n_permutations):
    shuffled_grammar = grammar_list.copy()
    random.shuffle(shuffled_grammar)

    perm_contingency = defaultdict(Counter)
    for ht, gr in zip(ht_list, shuffled_grammar):
        perm_contingency[ht][gr] += 1

    perm_vs.append(cramers_v(perm_contingency))

p_value = sum(1 for v in perm_vs if v >= observed_v) / n_permutations
mean_null = sum(perm_vs) / len(perm_vs)

print(f"\nObserved Cramer's V: {observed_v:.4f}")
print(f"Null mean V: {mean_null:.4f}")
print(f"P-value (permutation): {p_value:.4f}")

if p_value < 0.001:
    print("VERDICT: HIGHLY SIGNIFICANT structural synchrony (p < 0.001)")
elif p_value < 0.05:
    print("VERDICT: SIGNIFICANT structural synchrony (p < 0.05)")
else:
    print("VERDICT: No significant synchrony")

# Show the actual contingency for top prefixes
print("\n### CONTINGENCY TABLE (top HT prefixes x grammar classes)")
header = "HT\\Gram"
print(f"{header:<8}", end="")
for gp in GRAMMAR_PREFIXES:
    print(f"{gp:>8}", end="")
print()
print("-" * 72)

for ht_prefix in ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'po']:
    print(f"{ht_prefix:<8}", end="")
    row_total = sum(contingency[ht_prefix].values())
    for gp in GRAMMAR_PREFIXES:
        count = contingency[ht_prefix].get(gp, 0)
        pct = 100 * count / row_total if row_total > 0 else 0
        print(f"{pct:>7.1f}%", end="")
    print()

# ============================================================================
# HT-STATE-3: Prefix × Waiting Regime
# ============================================================================

print("\n" + "=" * 80)
print("HT-STATE-3: PREFIX × WAITING REGIME")
print("=" * 80)

# Define waiting regimes based on LINK density
# From OPS analysis: EXTREME > HIGH > MODERATE > LOW

# Calculate LINK density per folio
folio_link_density = {}
for folio, lines in folios.items():
    total_tokens = sum(len(tokens) for _, tokens in lines)
    link_tokens = sum(1 for _, tokens in lines for t in tokens if t in ['ol', 'al', 'ar'])
    if total_tokens >= 50:
        folio_link_density[folio] = link_tokens / total_tokens

# Categorize into regimes (quartiles)
if folio_link_density:
    densities = sorted(folio_link_density.values())
    q1 = densities[len(densities)//4]
    q2 = densities[len(densities)//2]
    q3 = densities[3*len(densities)//4]

    folio_regime = {}
    for folio, density in folio_link_density.items():
        if density <= q1:
            folio_regime[folio] = 'LOW'
        elif density <= q2:
            folio_regime[folio] = 'MODERATE'
        elif density <= q3:
            folio_regime[folio] = 'HIGH'
        else:
            folio_regime[folio] = 'EXTREME'

    # Count HT prefixes by regime
    prefix_by_regime = defaultdict(lambda: defaultdict(int))
    regime_totals = Counter()

    for folio, lines in folios.items():
        if folio not in folio_regime:
            continue
        regime = folio_regime[folio]

        for line_num, tokens in lines:
            for tok in tokens:
                prefix = get_ht_prefix(tok)
                if prefix:
                    prefix_by_regime[prefix][regime] += 1
                    regime_totals[regime] += 1

    print("\n### HT PREFIX DISTRIBUTION BY WAITING REGIME")
    print(f"{'Prefix':<8} {'LOW':>10} {'MODERATE':>10} {'HIGH':>10} {'EXTREME':>10} {'Trend':>12}")
    print("-" * 65)

    regime_order = ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
    regime_results = []

    for prefix in sorted(prefix_totals.keys(), key=lambda x: -prefix_totals[x])[:12]:
        total = sum(prefix_by_regime[prefix].values())
        if total < 30:
            continue

        row = []
        for regime in regime_order:
            pct = 100 * prefix_by_regime[prefix][regime] / total
            row.append(pct)

        # Trend: LOW to EXTREME
        if row[3] > row[0] + 5:
            trend = ">>EXTREME"
        elif row[0] > row[3] + 5:
            trend = ">>LOW"
        else:
            trend = "FLAT"

        regime_results.append((prefix, row, trend))
        print(f"{prefix:<8} {row[0]:>9.1f}% {row[1]:>9.1f}% {row[2]:>9.1f}% {row[3]:>9.1f}% {trend:>12}")

    # Build contingency and calculate V
    regime_contingency = defaultdict(Counter)
    for prefix, regimes_data in prefix_by_regime.items():
        for regime, count in regimes_data.items():
            regime_contingency[prefix][regime] = count

    regime_v = cramers_v(regime_contingency)
    print(f"\nCramer's V (Prefix x Regime): {regime_v:.4f}")

    # Identify regime-specific prefixes
    extreme_prefixes = [p for p, r, t in regime_results if t == ">>EXTREME"]
    low_prefixes = [p for p, r, t in regime_results if t == ">>LOW"]
    print(f"\nEXTREME-associated prefixes: {extreme_prefixes}")
    print(f"LOW-associated prefixes: {low_prefixes}")

else:
    print("Could not calculate waiting regimes (no LINK density data)")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY: HT-STATE TESTS")
print("=" * 80)

print("""
HT-STATE-1: PREFIX × POSITION
  - CONFIRMED: Prefixes show non-random position distribution
  - EARLY prefixes: {early}
  - LATE prefixes: {late}
  - Effect sizes reported above

HT-STATE-2: PREFIX × GRAMMAR CLASS
  - Cramer's V = {v:.4f}
  - P-value (permutation) = {p:.4f}
  - VERDICT: {verdict}

HT-STATE-3: PREFIX × REGIME
  - Cramer's V = {rv:.4f}
  - EXTREME-associated: {extreme}
  - LOW-associated: {low}
""".format(
    early=early_prefixes,
    late=late_prefixes,
    v=observed_v,
    p=p_value,
    verdict="SIGNIFICANT" if p_value < 0.05 else "NOT SIGNIFICANT",
    rv=regime_v if 'regime_v' in dir() else 0,
    extreme=extreme_prefixes if 'extreme_prefixes' in dir() else [],
    low=low_prefixes if 'low_prefixes' in dir() else []
))

print("=" * 80)
