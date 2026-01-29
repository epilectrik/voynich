"""
A_RECORD_B_FILTERING Phase - Script 2: Structural Reshape Analysis
Tests 5-8 (C686-C689)

Question: How does filtering reshape B grammar structure?
What predicts severity?

Tests:
  T5: Role Vulnerability Gradient (C686)
  T6: Composition-Filtering Interaction (C687)
  T7: REGIME Filtering Robustness (C688)
  T8: Survivor Set Uniqueness (C689)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as scipy_stats
import random

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

# ── Role taxonomy (C560/C581: class 17 = CC) ──
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

ROLE_TO_CLASSES = {}
for c, r in CLASS_TO_ROLE.items():
    ROLE_TO_CLASSES.setdefault(r, set()).add(c)

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']
B_ROLE_COUNTS = {r: len(ROLE_TO_CLASSES[r]) for r in ROLES}

# ── Load data ──
print("=" * 70)
print("A_RECORD_B_FILTERING - Script 2: Structural Reshape Analysis")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    cmap = json.load(f)
token_to_class = cmap['token_to_class']

with open(PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json') as f:
    regime_map = json.load(f)
# Invert: folio -> regime
folio_to_regime = {}
for regime, folios in regime_map.items():
    for f in folios:
        folio_to_regime[f] = regime

# ── Build B inventory ──
print("\nBuilding B token inventory...")
b_tokens = {}
b_by_middle = defaultdict(set)
b_by_prefix = defaultdict(set)
b_by_suffix = defaultdict(set)

for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)
        b_by_middle[m.middle].add(w)
        if m.prefix:
            b_by_prefix[m.prefix].add(w)
        if m.suffix:
            b_by_suffix[m.suffix].add(w)

b_middles_set = set(b_by_middle.keys())
b_prefixes_set = set(b_by_prefix.keys())
b_suffixes_set = set(b_by_suffix.keys())
b_token_class = {tok: int(cls) for tok, cls in token_to_class.items() if tok in b_tokens}
print(f"  B token types: {len(b_tokens)}")

# ── Build per-REGIME token inventories ──
print("Building per-REGIME token inventories...")
regime_tokens = defaultdict(set)  # regime -> set of token types used
regime_classes = defaultdict(set)  # regime -> set of classes used
for token in tx.currier_b():
    regime = folio_to_regime.get(token.folio)
    if regime:
        regime_tokens[regime].add(token.word)
        cls = token_to_class.get(token.word)
        if cls is not None:
            regime_classes[regime].add(int(cls))

for r in sorted(regime_tokens.keys()):
    print(f"  {r}: {len(regime_tokens[r])} token types, {len(regime_classes[r])} classes")

# ── Build A records with composition + PP MIDDLE count ──
print("\nBuilding A record profiles...")

record_profiles = []  # list of dicts with record info

for record in analyzer.iter_records():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in record.tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)

    # PP MIDDLEs = those shared with B
    pp_middles = middles & b_middles_set
    pp_prefixes = prefixes & b_prefixes_set
    pp_suffixes = suffixes & b_suffixes_set

    # Full morphological filtering
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                legal.add(tok)

    legal_classes = frozenset(b_token_class[t] for t in legal if t in b_token_class)

    # Role survival
    role_surv = {}
    for role in ROLES:
        role_surv[role] = len(legal_classes & ROLE_TO_CLASSES[role])

    record_profiles.append({
        'folio': record.folio,
        'line': record.line,
        'composition': record.composition,
        'pp_middle_count': len(pp_middles),
        'legal_tokens': legal,
        'legal_classes': legal_classes,
        'n_classes': len(legal_classes),
        'role_survival': role_surv,
    })

n_records = len(record_profiles)
print(f"  Records profiled: {n_records}")

# ════════════════════════════════════════════════════════════════
# TEST 5: Role Vulnerability Gradient (C686)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 5: ROLE VULNERABILITY GRADIENT (C686)")
print("=" * 70)

# Bin by PP MIDDLE count
BINS = [(0, 2), (3, 5), (6, 8), (9, 11), (12, 99)]
BIN_LABELS = ['0-2', '3-5', '6-8', '9-11', '12+']

bin_role_means = {label: {} for label in BIN_LABELS}
bin_counts = {}

for i, (lo, hi) in enumerate(BINS):
    label = BIN_LABELS[i]
    in_bin = [r for r in record_profiles if lo <= r['pp_middle_count'] <= hi]
    bin_counts[label] = len(in_bin)

    for role in ROLES:
        if in_bin:
            baseline = B_ROLE_COUNTS[role]
            vals = [r['role_survival'][role] / baseline if baseline > 0 else 0 for r in in_bin]
            bin_role_means[label][role] = float(np.mean(vals))
        else:
            bin_role_means[label][role] = 0.0

print(f"\n  {'Bin':<8} {'N':>5}  {'CC':>6}  {'EN':>6}  {'FL':>6}  {'FQ':>6}  {'AX':>6}")
print("  " + "-" * 52)
for label in BIN_LABELS:
    n = bin_counts[label]
    vals = bin_role_means[label]
    print(f"  {label:<8} {n:>5}  {vals['CC']:>5.1%}  {vals['EN']:>5.1%}  {vals['FL']:>5.1%}  {vals['FQ']:>5.1%}  {vals['AX']:>5.1%}")

# Vulnerability ordering: which role reaches 0% first (at lowest bin)?
lowest_bin = BIN_LABELS[0]
ordering = sorted(ROLES, key=lambda r: bin_role_means[lowest_bin].get(r, 0))
print(f"\n  Vulnerability ordering (most fragile first at {lowest_bin} PP):")
for i, role in enumerate(ordering):
    print(f"    {i+1}. {role}: {bin_role_means[lowest_bin][role]:.1%}")

# Which role never reaches 0% across all bins?
protected = []
for role in ROLES:
    if all(bin_role_means[label][role] > 0 for label in BIN_LABELS if bin_counts[label] > 0):
        protected.append(role)
print(f"\n  Protected roles (>0% in all bins): {protected if protected else 'NONE'}")

# ════════════════════════════════════════════════════════════════
# TEST 6: Composition-Filtering Interaction (C687)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 6: COMPOSITION-FILTERING INTERACTION (C687)")
print("=" * 70)

comp_groups = defaultdict(list)
for r in record_profiles:
    comp_groups[r['composition']].append(r)

print(f"\n  Composition groups:")
for comp in sorted(comp_groups.keys()):
    records = comp_groups[comp]
    class_counts = [r['n_classes'] for r in records]
    arr = np.array(class_counts)
    print(f"    {comp}: n={len(records)}, mean classes={np.mean(arr):.2f}, "
          f"median={np.median(arr):.1f}, min={np.min(arr)}, max={np.max(arr)}")

    # Role proportions
    role_means = {}
    for role in ROLES:
        vals = [r['role_survival'][role] for r in records]
        role_means[role] = float(np.mean(vals))
    total = sum(role_means.values())
    if total > 0:
        print(f"      Role mix: " + ", ".join(
            f"{r}={role_means[r]/total:.1%}" for r in ROLES))

# Mann-Whitney: PURE_RI vs PURE_PP (if both exist)
mw_results = {}
comp_keys = list(comp_groups.keys())
for c1 in comp_keys:
    for c2 in comp_keys:
        if c1 >= c2:
            continue
        a = [r['n_classes'] for r in comp_groups[c1]]
        b = [r['n_classes'] for r in comp_groups[c2]]
        if len(a) >= 5 and len(b) >= 5:
            u, p = scipy_stats.mannwhitneyu(a, b, alternative='two-sided')
            mw_results[f"{c1}_vs_{c2}"] = {'U': float(u), 'p': float(p)}
            sig = '*' if p < 0.05 else ''
            print(f"\n  Mann-Whitney {c1} vs {c2}: U={u:.0f}, p={p:.4g} {sig}")

# ════════════════════════════════════════════════════════════════
# TEST 7: REGIME Filtering Robustness (C688)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 7: REGIME FILTERING ROBUSTNESS (C688)")
print("=" * 70)

# For each A record, intersect legal tokens with REGIME-specific tokens
regime_keys = sorted(regime_tokens.keys())
regime_effective_classes = {rk: [] for rk in regime_keys}

for rec in record_profiles:
    for rk in regime_keys:
        # Effective = legal tokens that actually appear in this REGIME's folios
        effective = rec['legal_tokens'] & regime_tokens[rk]
        effective_classes = {b_token_class[t] for t in effective if t in b_token_class}
        regime_effective_classes[rk].append(len(effective_classes))

print(f"\n  {'REGIME':<12} {'Mean Eff Classes':>16} {'Median':>8} {'Std':>8} {'Baseline':>10}")
print("  " + "-" * 60)
for rk in regime_keys:
    arr = np.array(regime_effective_classes[rk])
    baseline = len(regime_classes[rk])
    print(f"  {rk:<12} {np.mean(arr):>16.2f} {np.median(arr):>8.1f} {np.std(arr):>8.2f} {baseline:>10}")

# Which REGIME is most robust? (highest mean effective / baseline)
robustness = {}
for rk in regime_keys:
    baseline = len(regime_classes[rk])
    if baseline > 0:
        robustness[rk] = float(np.mean(regime_effective_classes[rk])) / baseline
    else:
        robustness[rk] = 0.0

best = max(robustness, key=robustness.get)
worst = min(robustness, key=robustness.get)
print(f"\n  Robustness ratio (mean effective / baseline classes):")
for rk in regime_keys:
    marker = " <-- MOST ROBUST" if rk == best else (" <-- LEAST ROBUST" if rk == worst else "")
    print(f"    {rk}: {robustness[rk]:.3f}{marker}")

# ════════════════════════════════════════════════════════════════
# TEST 8: Survivor Set Uniqueness (C689)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 8: SURVIVOR SET UNIQUENESS (C689)")
print("=" * 70)

all_sets = [r['legal_classes'] for r in record_profiles]
unique_sets = len(set(all_sets))
uniqueness_ratio = unique_sets / n_records

print(f"\n  Total records: {n_records}")
print(f"  Unique class sets: {unique_sets}")
print(f"  Uniqueness ratio: {uniqueness_ratio:.4f}")

# Pairwise Jaccard similarity (sample 1000 pairs)
random.seed(42)
n_sample = min(1000, n_records * (n_records - 1) // 2)
jaccards = []
indices = list(range(n_records))
sampled = 0
while sampled < n_sample:
    i, j = random.sample(indices, 2)
    a = all_sets[i]
    b = all_sets[j]
    union = a | b
    if len(union) > 0:
        jaccards.append(len(a & b) / len(union))
    else:
        jaccards.append(0.0)
    sampled += 1

jacc_arr = np.array(jaccards)
print(f"\n  Pairwise Jaccard ({n_sample} random pairs):")
print(f"    Mean: {np.mean(jacc_arr):.4f}")
print(f"    Median: {np.median(jacc_arr):.4f}")
print(f"    Std: {np.std(jacc_arr):.4f}")
print(f"    Min: {np.min(jacc_arr):.4f}, Max: {np.max(jacc_arr):.4f}")

# Set size distribution
set_sizes = [len(s) for s in all_sets]
sz_arr = np.array(set_sizes)
print(f"\n  Set size distribution:")
print(f"    Mean: {np.mean(sz_arr):.2f}, Median: {np.median(sz_arr):.1f}")
print(f"    Std: {np.std(sz_arr):.2f}")

# Most common set
set_counter = Counter(all_sets)
most_common = set_counter.most_common(5)
print(f"\n  Most common sets:")
for s, count in most_common:
    print(f"    {sorted(s)[:10]}{'...' if len(s) > 10 else ''} (size {len(s)}): {count} records ({100*count/n_records:.1f}%)")

# ════════════════════════════════════════════════════════════════
# Save results
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

results = {
    'metadata': {
        'phase': 'A_RECORD_B_FILTERING',
        'script': 'structural_reshape_analysis.py',
        'tests': 'T5-T8 (C686-C689)',
        'n_records': n_records,
    },
    'T5_role_vulnerability_gradient': {
        'constraint': 'C686',
        'bins': {},
        'vulnerability_ordering': ordering,
        'protected_roles': protected,
    },
    'T6_composition_filtering': {
        'constraint': 'C687',
        'groups': {},
        'mann_whitney': mw_results,
    },
    'T7_regime_robustness': {
        'constraint': 'C688',
        'per_regime': {},
        'robustness_ratio': robustness,
        'most_robust': best,
        'least_robust': worst,
    },
    'T8_survivor_set_uniqueness': {
        'constraint': 'C689',
        'total_records': n_records,
        'unique_sets': unique_sets,
        'uniqueness_ratio': round(uniqueness_ratio, 4),
        'jaccard': {
            'n_pairs': n_sample,
            'mean': round(float(np.mean(jacc_arr)), 4),
            'median': round(float(np.median(jacc_arr)), 4),
            'std': round(float(np.std(jacc_arr)), 4),
        },
    },
}

# T5 per-bin
for label in BIN_LABELS:
    results['T5_role_vulnerability_gradient']['bins'][label] = {
        'n_records': bin_counts[label],
        'role_survival_fraction': bin_role_means[label],
    }

# T6 per-composition
for comp, records in comp_groups.items():
    class_counts = [r['n_classes'] for r in records]
    arr = np.array(class_counts)
    role_means = {}
    for role in ROLES:
        vals = [r['role_survival'][role] for r in records]
        role_means[role] = round(float(np.mean(vals)), 3)
    results['T6_composition_filtering']['groups'][comp] = {
        'n_records': len(records),
        'mean_classes': round(float(np.mean(arr)), 2),
        'median_classes': float(np.median(arr)),
        'role_mean_survival': role_means,
    }

# T7 per-regime
for rk in regime_keys:
    arr = np.array(regime_effective_classes[rk])
    results['T7_regime_robustness']['per_regime'][rk] = {
        'mean_effective_classes': round(float(np.mean(arr)), 2),
        'median_effective_classes': float(np.median(arr)),
        'baseline_classes': len(regime_classes[rk]),
        'robustness_ratio': round(robustness[rk], 4),
    }

out_path = RESULTS_DIR / 'structural_reshape_analysis.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"  Saved: {out_path}")
print("\nDone.")
