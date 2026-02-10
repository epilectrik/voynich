"""
Test 03: Line Length Determinants
=================================
Phase: LINE_CONTROL_BLOCK_GRAMMAR
Purpose: Determine what predicts line length (token count) in Currier B.
         If opener instruction class adds significant partial R-squared
         beyond folio and regime, line length is partly grammar-driven.
Method:
  - For each line, record: length, opener_class, opener_role, folio,
    section, regime, par_position, line_position_in_folio
  - Compute R-squared for each predictor alone (group-mean R2 for categorical,
    OLS for continuous)
  - Hierarchical R-squared: folio -> regime -> opener_class -> opener_token -> par_position
  - Shuffle test (1000x): shuffle line lengths within each folio, recompute
    opener_class R-squared to get null distribution
Verdict:
  PASS   = opener adds >=3% partial R-squared beyond folio+regime
  WEAK   = opener adds 1-2% partial R-squared
  FAIL   = opener adds <1%
"""
import sys
import json
import random
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology
PROJECT_ROOT = Path("C:/git/voynich").resolve()
# ---------------------------------------------------------------------------
# Load external maps
# ---------------------------------------------------------------------------
with open(PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json",
          "r", encoding="utf-8") as f:
    class_map = json.load(f)
token_to_class = class_map["token_to_class"]
token_to_role = class_map["token_to_role"]
class_to_role = class_map["class_to_role"]
with open(PROJECT_ROOT / "phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json",
          "r", encoding="utf-8") as f:
    regime_map_raw = json.load(f)
# Invert: regime -> [folios] => folio -> regime
folio_to_regime = {}
for regime_name, folio_list in regime_map_raw.items():
    for fol in folio_list:
        folio_to_regime[fol] = regime_name
# ---------------------------------------------------------------------------
# Build per-line data
# ---------------------------------------------------------------------------
tx = Transcript()
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(t)
# Count lines per folio for normalized position
folio_line_keys = defaultdict(list)
for (fol, ln) in sorted(lines.keys()):
    folio_line_keys[fol].append(ln)
# Build feature table: one row per line
records = []
for (fol, ln), tokens in sorted(lines.items()):
    length = len(tokens)
    first_tok = tokens[0]
    opener_word = first_tok.word.replace("*", "").strip()
    opener_class = str(token_to_class.get(opener_word, "UNKNOWN"))
    opener_role = token_to_role.get(opener_word, "UNKNOWN")
    section = first_tok.section
    regime = folio_to_regime.get(fol, "UNKNOWN")
    par_pos = 1 if first_tok.par_initial else 0
    # Normalized line position in folio (0 = first, 1 = last)
    folio_lines = folio_line_keys[fol]
    if len(folio_lines) > 1:
        idx = folio_lines.index(ln)
        line_pos_norm = idx / (len(folio_lines) - 1)
    else:
        line_pos_norm = 0.0
    records.append({
        "folio": fol,
        "line": ln,
        "length": length,
        "opener_word": opener_word,
        "opener_class": opener_class,
        "opener_role": opener_role,
        "section": section,
        "regime": regime,
        "par_position": par_pos,
        "line_position_in_folio": line_pos_norm,
    })
n_lines = len(records)
lengths = [r["length"] for r in records]
mean_length = sum(lengths) / n_lines
ss_total = sum((l - mean_length) ** 2 for l in lengths)
std_length = (ss_total / n_lines) ** 0.5
print("Lines: {}".format(n_lines))
print("Mean line length: {:.2f} +/- {:.2f}".format(mean_length, std_length))
print("SS_total: {:.1f}".format(ss_total))
print()# ---------------------------------------------------------------------------
# R-squared helpers
# ---------------------------------------------------------------------------
def group_mean_r2(records, group_key, length_key="length"):
    """R2 = 1 - SS_within / SS_total for a categorical grouping."""
    groups = defaultdict(list)
    for r in records:
        groups[r[group_key]].append(r[length_key])
    overall_mean = sum(r[length_key] for r in records) / len(records)
    ss_tot = sum((r[length_key] - overall_mean) ** 2 for r in records)
    if ss_tot == 0:
        return 0.0
    ss_within = 0.0
    for grp, vals in groups.items():
        grp_mean = sum(vals) / len(vals)
        ss_within += sum((v - grp_mean) ** 2 for v in vals)
    return 1.0 - ss_within / ss_tot
def ols_r2(records, cont_key, length_key="length"):
    """Simple OLS R2 for a single continuous predictor."""
    n = len(records)
    xs = [r[cont_key] for r in records]
    ys = [r[length_key] for r in records]
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    return (sxy ** 2) / (sxx * syy)
def composite_group_key(records, keys):
    """Add a composite key to records (tuple of values)."""
    for r in records:
        r["_composite"] = tuple(r[k] for k in keys)
# ---------------------------------------------------------------------------
# Individual R-squared for each predictor
# ---------------------------------------------------------------------------
categorical_preds = ["opener_class", "opener_role", "folio", "section", "regime", "par_position"]
continuous_preds = ["line_position_in_folio"]
print("=" * 60)
print("INDIVIDUAL R-SQUARED (each predictor alone)")
print("=" * 60)
individual_r2 = {}
for pred in categorical_preds:
    r2 = group_mean_r2(records, pred)
    individual_r2[pred] = r2
    n_groups = len(set(r[pred] for r in records))
    print("  {:30s}  R2 = {:.4f}  (groups={})".format(pred, r2, n_groups))
for pred in continuous_preds:
    r2 = ols_r2(records, pred)
    individual_r2[pred] = r2
    print("  {:30s}  R2 = {:.4f}  (continuous)".format(pred, r2))
print()
# ---------------------------------------------------------------------------
# Hierarchical / partial R-squared
# ---------------------------------------------------------------------------
print("=" * 60)
print("HIERARCHICAL R-SQUARED (cumulative, incremental)")
print("=" * 60)
hierarchy = ["folio", "regime", "opener_class", "opener_word", "par_position"]
cumulative_keys = []
prev_r2 = 0.0
hierarchical_results = []
for pred in hierarchy:
    cumulative_keys.append(pred)
    composite_group_key(records, cumulative_keys)
    cum_r2 = group_mean_r2(records, "_composite")
    incr_r2 = cum_r2 - prev_r2
    hierarchical_results.append({
        "step": pred,
        "cumulative_r2": round(cum_r2, 6),
        "incremental_r2": round(incr_r2, 6),
    })
    print("  +{:20s}  cumulative R2 = {:.4f}  incremental = {:.4f}".format(pred, cum_r2, incr_r2))
    prev_r2 = cum_r2
# The critical number: opener_class partial R2 beyond folio+regime
opener_partial_r2 = hierarchical_results[2]["incremental_r2"]
print()
print("  ** Opener class partial R2 (beyond folio+regime): {:.4f} **".format(opener_partial_r2))
print()# ---------------------------------------------------------------------------
# Shuffle test: null distribution for opener_class R2
# ---------------------------------------------------------------------------
print("=" * 60)
print("SHUFFLE TEST (1000 permutations, within-folio)")
print("=" * 60)
folio_groups = defaultdict(list)
for i, r in enumerate(records):
    folio_groups[r["folio"]].append(i)
observed_opener_r2 = individual_r2["opener_class"]
rng = random.Random(42)
n_shuffles = 1000
shuffle_r2s = []
for s in range(n_shuffles):
    shuffled_lengths = [0] * n_lines
    for fol, indices in folio_groups.items():
        fol_lengths = [records[i]["length"] for i in indices]
        rng.shuffle(fol_lengths)
        for idx, length_val in zip(indices, fol_lengths):
            shuffled_lengths[idx] = length_val
    groups = defaultdict(list)
    for i, r in enumerate(records):
        groups[r["opener_class"]].append(shuffled_lengths[i])
    overall_mean_s = sum(shuffled_lengths) / n_lines
    ss_tot_s = sum((l - overall_mean_s) ** 2 for l in shuffled_lengths)
    if ss_tot_s == 0:
        shuffle_r2s.append(0.0)
        continue
    ss_within_s = 0.0
    for grp, vals in groups.items():
        gm = sum(vals) / len(vals)
        ss_within_s += sum((v - gm) ** 2 for v in vals)
    shuffle_r2s.append(1.0 - ss_within_s / ss_tot_s)
shuffle_mean = sum(shuffle_r2s) / len(shuffle_r2s)
shuffle_std = (sum((x - shuffle_mean) ** 2 for x in shuffle_r2s) / len(shuffle_r2s)) ** 0.5
n_exceed = sum(1 for x in shuffle_r2s if x >= observed_opener_r2)
p_value = n_exceed / n_shuffles
print("  Observed opener_class R2:   {:.4f}".format(observed_opener_r2))
print("  Shuffle mean R2:            {:.4f} +/- {:.4f}".format(shuffle_mean, shuffle_std))
print("  Shuffle max R2:             {:.4f}".format(max(shuffle_r2s)))
print("  p-value (n_exceed/1000):    {:.4f}  ({}/{})".format(p_value, n_exceed, n_shuffles))
print()# ---------------------------------------------------------------------------
# Mean line length per opener class (top 10 most common)
# ---------------------------------------------------------------------------
print("=" * 60)
print("MEAN LINE LENGTH BY OPENER CLASS (top 10 by frequency)")
print("=" * 60)
opener_class_data = defaultdict(list)
for r in records:
    opener_class_data[r["opener_class"]].append(r["length"])
sorted_classes = sorted(opener_class_data.items(), key=lambda x: -len(x[1]))
top10 = sorted_classes[:10]
opener_class_table = []
for cls, lens in top10:
    m = sum(lens) / len(lens)
    sd = (sum((l - m) ** 2 for l in lens) / len(lens)) ** 0.5
    role = class_to_role.get(str(cls), "UNKNOWN")
    opener_class_table.append({
        "class": cls,
        "role": role,
        "count": len(lens),
        "mean_length": round(m, 2),
        "std_length": round(sd, 2),
    })
    print("  Class {:>8s} ({:>20s})  n={:>4d}  mean={:.2f} +/- {:.2f}".format(
        cls, role, len(lens), m, sd))
print()
# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
if opener_partial_r2 >= 0.03:
    verdict = "PASS"
    reason = "Opener class adds {:.4f} partial R2 (>=3%) beyond folio+regime".format(opener_partial_r2)
elif opener_partial_r2 >= 0.01:
    verdict = "WEAK"
    reason = "Opener class adds {:.4f} partial R2 (1-2%) beyond folio+regime".format(opener_partial_r2)
else:
    verdict = "FAIL"
    reason = "Opener class adds {:.4f} partial R2 (<1%) beyond folio+regime".format(opener_partial_r2)
print("=" * 60)
print("VERDICT: {}".format(verdict))
print("  {}".format(reason))
print("  Shuffle p-value: {:.4f}".format(p_value))
print("=" * 60)
# ---------------------------------------------------------------------------
# Save JSON
# ---------------------------------------------------------------------------
output = {
    "test": "Line Length Determinants",
    "test_id": "03_line_length_determinants",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": "Determine what predicts line length in Currier B; test if opener instruction class adds explanatory power beyond folio and regime",
    "method": "Group-mean R2 for categorical predictors, OLS R2 for continuous; hierarchical decomposition; within-folio shuffle null",
    "n_lines": n_lines,
    "mean_line_length": round(mean_length, 4),
    "std_line_length": round(std_length, 4),
    "ss_total": round(ss_total, 2),
    "individual_r2": {k: round(v, 6) for k, v in individual_r2.items()},
    "hierarchical_r2": hierarchical_results,
    "opener_partial_r2_beyond_folio_regime": round(opener_partial_r2, 6),
    "shuffle_test": {
        "n_shuffles": n_shuffles,
        "seed": 42,
        "method": "shuffle line lengths within each folio, recompute opener_class R2",
        "observed_opener_class_r2": round(observed_opener_r2, 6),
        "shuffle_mean_r2": round(shuffle_mean, 6),
        "shuffle_std_r2": round(shuffle_std, 6),
        "shuffle_max_r2": round(max(shuffle_r2s), 6),
        "p_value": round(p_value, 4),
        "n_exceed": n_exceed,
    },
    "opener_class_mean_lengths": opener_class_table,
    "verdict": verdict,
    "verdict_reason": reason,
    "thresholds": {
        "pass": ">=3% partial R2 beyond folio+regime",
        "weak": "1-2% partial R2",
        "fail": "<1% partial R2",
    },
}
out_path = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/03_line_length_determinants.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=True)
print()
print("Results saved to: {}".format(out_path))