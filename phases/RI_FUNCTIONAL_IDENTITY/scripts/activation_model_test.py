"""
RI_FUNCTIONAL_IDENTITY - Activation Model Test

Tests the hypothesis: B folio activation requires all PP-pure lines
(shared toolbox) + a single RI-bearing line (entry-specific PP).

Computes B class survival under three conditions:
  (A) PP-pure lines only (shared toolbox alone)
  (B) PP-pure lines + each individual RI-bearing line
  (C) Full folio (all lines) -- baseline from C705

If the user's model is correct:
  - Condition A should give substantial but incomplete coverage
  - Condition B should approach Condition C
  - The RI-bearing line's specialized PP should close the gap
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("RI_FUNCTIONAL_IDENTITY - Activation Model Test")
print("=" * 70)

# -- Load data --
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()
print(f"A folios: {len(folios)}")

# -- Pre-compute all records --
folio_records = {}
for fol in folios:
    folio_records[fol] = analyzer.analyze_folio(fol)

# -- Build B token inventory (O(n) once) --
class_token_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_token_map_path, 'r') as f:
    class_token_map = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_token_map['token_to_class'].items()}

b_tokens = {}       # token_str -> (prefix, middle, suffix)
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set()
b_prefixes_set = set()
b_suffixes_set = set()
for tok, (pref, mid, suf) in b_tokens.items():
    b_middles_set.add(mid)
    if pref:
        b_prefixes_set.add(pref)
    if suf:
        b_suffixes_set.add(suf)

b_token_class = {tok: token_to_class[tok] for tok in b_tokens if tok in token_to_class}

print(f"B token types: {len(b_tokens)}")
print(f"B classified tokens: {len(b_token_class)}")
print()

# -- Filtering function: PP vocabulary -> legal B tokens -> legal B classes --
def filter_b(pp_middles, pp_prefixes, pp_suffixes):
    """C502.a filtering: returns (legal_tokens, legal_classes)."""
    shared_mids = pp_middles & b_middles_set
    shared_prefs = pp_prefixes & b_prefixes_set
    shared_sufs = pp_suffixes & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            pref_ok = (pref is None or pref in shared_prefs)
            suf_ok = (suf is None or suf in shared_sufs)
            if pref_ok and suf_ok:
                legal.add(tok)
    classes = frozenset(b_token_class[t] for t in legal if t in b_token_class)
    return legal, classes

# -- Extract PP vocabulary from a set of records (O(records * tokens)) --
def extract_pp_vocab(records):
    """Returns (pp_middles, pp_prefixes, pp_suffixes) from a list of records."""
    mids = set()
    prefs = set()
    sufs = set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                if t.prefix:
                    prefs.add(t.prefix)
                if t.suffix:
                    sufs.add(t.suffix)
    return mids, prefs, sufs

# ============================================================
# Compute three conditions per folio
# ============================================================
print("-" * 60)
print("Computing B class survival under three conditions per folio")
print("-" * 60)

folio_results = {}

# Pre-classify lines per folio (O(1) per folio after this)
folio_pp_pure = {}    # folio -> list of PP-pure records
folio_ri_bearing = {} # folio -> list of RI-bearing records

for fol in folios:
    pure = []
    ri = []
    for rec in folio_records[fol]:
        if rec.ri_count > 0:
            ri.append(rec)
        else:
            pure.append(rec)
    folio_pp_pure[fol] = pure
    folio_ri_bearing[fol] = ri

# Condition A: PP-pure only
# Condition B: PP-pure + each RI-bearing line (one at a time)
# Condition C: Full folio

condition_a_classes = []
condition_b_classes = []  # best single RI addition per folio
condition_b_mean_classes = []  # mean across all RI additions
condition_b_all = []  # every individual RI addition
condition_c_classes = []

condition_a_middles = []
condition_b_middles_gain = []

for fol in folios:
    pure_recs = folio_pp_pure[fol]
    ri_recs = folio_ri_bearing[fol]
    all_recs = folio_records[fol]

    # Condition C: full folio
    c_mids, c_prefs, c_sufs = extract_pp_vocab(all_recs)
    _, c_classes = filter_b(c_mids, c_prefs, c_sufs)
    n_c = len(c_classes)
    condition_c_classes.append(n_c)

    # Condition A: PP-pure only
    a_mids, a_prefs, a_sufs = extract_pp_vocab(pure_recs)
    _, a_classes = filter_b(a_mids, a_prefs, a_sufs)
    n_a = len(a_classes)
    condition_a_classes.append(n_a)
    condition_a_middles.append(len(a_mids))

    # Condition B: PP-pure + each RI-bearing line
    if ri_recs:
        b_class_counts = []
        b_middle_gains = []
        for ri_rec in ri_recs:
            # Combine PP-pure vocab with this RI line's PP vocab
            ri_mids, ri_prefs, ri_sufs = extract_pp_vocab([ri_rec])
            combined_mids = a_mids | ri_mids
            combined_prefs = a_prefs | ri_prefs
            combined_sufs = a_sufs | ri_sufs
            _, b_classes = filter_b(combined_mids, combined_prefs, combined_sufs)
            n_b = len(b_classes)
            b_class_counts.append(n_b)
            b_middle_gains.append(len(combined_mids) - len(a_mids))
            condition_b_all.append(n_b)

        condition_b_classes.append(max(b_class_counts))
        condition_b_mean_classes.append(float(np.mean(b_class_counts)))
        condition_b_middles_gain.append(float(np.mean(b_middle_gains)))
    else:
        # No RI lines in this folio
        condition_b_classes.append(n_a)
        condition_b_mean_classes.append(float(n_a))
        condition_b_middles_gain.append(0.0)

condition_a_classes = np.array(condition_a_classes)
condition_b_classes = np.array(condition_b_classes)
condition_b_mean_classes = np.array(condition_b_mean_classes)
condition_c_classes = np.array(condition_c_classes)

print(f"\nCondition A (PP-pure only):")
print(f"  Mean classes: {np.mean(condition_a_classes):.1f}/49")
print(f"  Mean PP MIDDLEs: {np.mean(condition_a_middles):.1f}")

print(f"\nCondition B (PP-pure + best single RI line):")
print(f"  Mean classes: {np.mean(condition_b_classes):.1f}/49")
print(f"  Mean PP MIDDLE gain from 1 RI line: {np.mean(condition_b_middles_gain):.1f}")

print(f"\nCondition B-mean (PP-pure + average RI line):")
print(f"  Mean classes: {np.mean(condition_b_mean_classes):.1f}/49")

print(f"\nCondition C (full folio, all lines):")
print(f"  Mean classes: {np.mean(condition_c_classes):.1f}/49")

# Gap analysis
gap_a_to_c = condition_c_classes - condition_a_classes
gap_b_to_c = condition_c_classes - condition_b_classes
gap_bmean_to_c = condition_c_classes - condition_b_mean_classes

a_recovery = condition_a_classes / np.where(condition_c_classes > 0, condition_c_classes, 1)
b_recovery = condition_b_classes / np.where(condition_c_classes > 0, condition_c_classes, 1)
bmean_recovery = condition_b_mean_classes / np.where(condition_c_classes > 0, condition_c_classes, 1)

print(f"\nGap Analysis:")
print(f"  A -> C gap: mean {np.mean(gap_a_to_c):.1f} classes")
print(f"  B(best) -> C gap: mean {np.mean(gap_b_to_c):.1f} classes")
print(f"  B(mean) -> C gap: mean {np.mean(gap_bmean_to_c):.1f} classes")
print(f"\n  A recovers {np.mean(a_recovery)*100:.1f}% of full folio")
print(f"  B(best) recovers {np.mean(b_recovery)*100:.1f}% of full folio")
print(f"  B(mean) recovers {np.mean(bmean_recovery)*100:.1f}% of full folio")

# ============================================================
# How many RI lines needed to close the gap?
# ============================================================
print()
print("-" * 60)
print("Incremental RI Line Addition (cumulative)")
print("-" * 60)

# For each folio: add RI lines one at a time (best-first by class gain)
# Track how many RI lines needed to reach 95% and 100% of full folio
max_ri_lines = max(len(folio_ri_bearing[fol]) for fol in folios)

# Per folio: greedy addition of RI lines
recovery_at_k = defaultdict(list)  # k -> list of recovery fractions

for fol in folios:
    pure_recs = folio_pp_pure[fol]
    ri_recs = folio_ri_bearing[fol]
    all_recs = folio_records[fol]

    c_mids, c_prefs, c_sufs = extract_pp_vocab(all_recs)
    _, c_classes = filter_b(c_mids, c_prefs, c_sufs)
    n_c = len(c_classes)
    if n_c == 0:
        continue

    # Start with PP-pure vocab
    cum_mids, cum_prefs, cum_sufs = extract_pp_vocab(pure_recs)

    # k=0: PP-pure only
    _, cur_classes = filter_b(cum_mids, cum_prefs, cum_sufs)
    recovery_at_k[0].append(len(cur_classes) / n_c)

    if not ri_recs:
        continue

    # Pre-compute each RI line's PP vocab
    ri_vocabs = []
    for ri_rec in ri_recs:
        ri_m, ri_p, ri_s = extract_pp_vocab([ri_rec])
        ri_vocabs.append((ri_m, ri_p, ri_s))

    # Greedy: at each step, pick the RI line that adds most classes
    remaining = list(range(len(ri_recs)))

    for k in range(1, len(ri_recs) + 1):
        best_idx = None
        best_n = -1
        best_mids = None
        best_prefs = None
        best_sufs = None

        for idx in remaining:
            test_mids = cum_mids | ri_vocabs[idx][0]
            test_prefs = cum_prefs | ri_vocabs[idx][1]
            test_sufs = cum_sufs | ri_vocabs[idx][2]
            _, test_classes = filter_b(test_mids, test_prefs, test_sufs)
            if len(test_classes) > best_n:
                best_n = len(test_classes)
                best_idx = idx
                best_mids = test_mids
                best_prefs = test_prefs
                best_sufs = test_sufs

        remaining.remove(best_idx)
        cum_mids = best_mids
        cum_prefs = best_prefs
        cum_sufs = best_sufs
        recovery_at_k[k].append(best_n / n_c)

# Print recovery curve
print(f"\n  {'k RI lines':>12}  {'Mean Recovery':>14}  {'Median':>8}  {'Min':>8}  {'N folios':>10}")
for k in sorted(recovery_at_k.keys()):
    vals = np.array(recovery_at_k[k])
    if len(vals) > 0:
        print(f"  {k:>12}  {np.mean(vals)*100:>13.1f}%  {np.median(vals)*100:>7.1f}%  {np.min(vals)*100:>7.1f}%  {len(vals):>10}")
    if k > 15:
        print(f"  ... (truncated at k=15)")
        break

# ============================================================
# What does the single-RI-line PP bring?
# ============================================================
print()
print("-" * 60)
print("What PP vocabulary does each RI line contribute?")
print("-" * 60)

# For each RI-bearing line: how many of its PP MIDDLEs are NOT on PP-pure lines?
ri_exclusive_counts = []
ri_shared_counts = []
ri_pp_total = []

for fol in folios:
    pure_mids, _, _ = extract_pp_vocab(folio_pp_pure[fol])
    for ri_rec in folio_ri_bearing[fol]:
        ri_pp_mids = set(t.middle for t in ri_rec.tokens if t.is_pp and t.middle)
        exclusive = ri_pp_mids - pure_mids
        shared = ri_pp_mids & pure_mids
        ri_exclusive_counts.append(len(exclusive))
        ri_shared_counts.append(len(shared))
        ri_pp_total.append(len(ri_pp_mids))

ri_exclusive_counts = np.array(ri_exclusive_counts)
ri_shared_counts = np.array(ri_shared_counts)
ri_pp_total = np.array(ri_pp_total)

print(f"  Per RI-bearing line:")
print(f"    Total PP MIDDLEs:     mean={np.mean(ri_pp_total):.2f}")
print(f"    Shared with PP-pure:  mean={np.mean(ri_shared_counts):.2f}")
print(f"    Exclusive (new):      mean={np.mean(ri_exclusive_counts):.2f}")
print(f"    Exclusive fraction:   {np.mean(ri_exclusive_counts)/np.mean(ri_pp_total)*100:.1f}%")
print()
print(f"  Distribution of exclusive PP MIDDLEs per RI line:")
for n in range(6):
    count = int(np.sum(ri_exclusive_counts == n))
    print(f"    {n} exclusive: {count} lines ({100*count/len(ri_exclusive_counts):.1f}%)")
count_6plus = int(np.sum(ri_exclusive_counts >= 6))
print(f"    6+  exclusive: {count_6plus} lines ({100*count_6plus/len(ri_exclusive_counts):.1f}%)")

# ============================================================
# Does single-record class survival depend on RI presence?
# ============================================================
print()
print("-" * 60)
print("Single-Record B Class Survival: PP-pure vs RI-bearing")
print("-" * 60)

# For each individual line, compute its B class survival
single_pure_classes = []
single_ri_classes = []

for fol in folios:
    for rec in folio_pp_pure[fol]:
        mids, prefs, sufs = extract_pp_vocab([rec])
        _, classes = filter_b(mids, prefs, sufs)
        single_pure_classes.append(len(classes))
    for rec in folio_ri_bearing[fol]:
        mids, prefs, sufs = extract_pp_vocab([rec])
        _, classes = filter_b(mids, prefs, sufs)
        single_ri_classes.append(len(classes))

single_pure_classes = np.array(single_pure_classes)
single_ri_classes = np.array(single_ri_classes)

from scipy import stats as scipy_stats
u_sr, p_sr = scipy_stats.mannwhitneyu(single_pure_classes, single_ri_classes, alternative='two-sided')

print(f"  PP-pure single-record:    mean={np.mean(single_pure_classes):.2f}/49, median={np.median(single_pure_classes):.0f}")
print(f"  RI-bearing single-record: mean={np.mean(single_ri_classes):.2f}/49, median={np.median(single_ri_classes):.0f}")
print(f"  Mann-Whitney U p={p_sr:.4e}")

# ============================================================
# Summary
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
  Model: B activation = PP-pure toolbox + single RI entry

  Condition A (PP-pure only):     {np.mean(condition_a_classes):.1f}/49 classes ({np.mean(a_recovery)*100:.1f}% of full folio)
  Condition B (+ best RI line):   {np.mean(condition_b_classes):.1f}/49 classes ({np.mean(b_recovery)*100:.1f}% of full folio)
  Condition B (+ average RI):     {np.mean(condition_b_mean_classes):.1f}/49 classes ({np.mean(bmean_recovery)*100:.1f}% of full folio)
  Condition C (full folio):       {np.mean(condition_c_classes):.1f}/49 classes (100%)

  Per RI line: {np.mean(ri_exclusive_counts):.2f} exclusive PP MIDDLEs (not on PP-pure lines)
  Single-record survival: PP-pure {np.mean(single_pure_classes):.1f}/49 vs RI-bearing {np.mean(single_ri_classes):.1f}/49
""")

# Verdict
a_pct = np.mean(a_recovery) * 100
b_pct = np.mean(b_recovery) * 100
if a_pct > 90:
    verdict = "PP-pure lines ALONE nearly sufficient. RI adds minimal filtering value."
elif b_pct > 90:
    verdict = "PP-pure + 1 RI line approaches full folio. USER MODEL SUPPORTED."
elif b_pct > 75:
    verdict = "PP-pure + 1 RI line is substantial but not sufficient. Partial support."
else:
    verdict = "Single RI line insufficient. Multiple RI lines needed."

print(f"  VERDICT: {verdict}")

results = {
    'metadata': {
        'phase': 'RI_FUNCTIONAL_IDENTITY',
        'script': 'activation_model_test.py',
        'hypothesis': 'B activation = PP-pure toolbox + single RI entry',
        'n_folios': len(folios),
    },
    'condition_a_pp_pure_only': {
        'mean_classes': round(float(np.mean(condition_a_classes)), 1),
        'mean_recovery_pct': round(float(np.mean(a_recovery)) * 100, 1),
        'mean_pp_middles': round(float(np.mean(condition_a_middles)), 1),
    },
    'condition_b_best_ri': {
        'mean_classes': round(float(np.mean(condition_b_classes)), 1),
        'mean_recovery_pct': round(float(np.mean(b_recovery)) * 100, 1),
    },
    'condition_b_mean_ri': {
        'mean_classes': round(float(np.mean(condition_b_mean_classes)), 1),
        'mean_recovery_pct': round(float(np.mean(bmean_recovery)) * 100, 1),
    },
    'condition_c_full_folio': {
        'mean_classes': round(float(np.mean(condition_c_classes)), 1),
    },
    'ri_line_pp_contribution': {
        'mean_total_pp_middles': round(float(np.mean(ri_pp_total)), 2),
        'mean_shared': round(float(np.mean(ri_shared_counts)), 2),
        'mean_exclusive': round(float(np.mean(ri_exclusive_counts)), 2),
        'exclusive_fraction': round(float(np.mean(ri_exclusive_counts)) / float(np.mean(ri_pp_total)) * 100, 1),
    },
    'single_record_survival': {
        'pp_pure_mean': round(float(np.mean(single_pure_classes)), 2),
        'ri_bearing_mean': round(float(np.mean(single_ri_classes)), 2),
        'mann_whitney_p': float(p_sr),
    },
    'recovery_curve': {
        k: round(float(np.mean(recovery_at_k[k])) * 100, 1)
        for k in sorted(recovery_at_k.keys()) if k <= 15
    },
    'verdict': verdict,
}

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
output_path = RESULTS_DIR / 'activation_model_test.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {output_path}")
