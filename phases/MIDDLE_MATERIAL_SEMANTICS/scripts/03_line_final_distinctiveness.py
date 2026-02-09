"""
03_line_final_distinctiveness.py

Test 3: Line-Final Vocabulary Distinctiveness

Question: Are line-final middles systematically rarer and more folio-specific
than line-medial middles?

Method:
1. Load Currier B tokens (H track, no labels, no uncertain, no empty)
2. Extract MIDDLEs via Morphology
3. Pre-compute folio_count for each unique MIDDLE
4. Classify each token as LINE-FINAL or LINE-OTHER based on line position
5. Compare folio_count distributions between the two groups
6. Control for line-length confound by binning lines
7. Statistical tests: Mann-Whitney U, Chi-square, Cohen's d
"""

import json
import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy import stats

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# ============================================================
# Step 1: Collect all Currier B tokens with MIDDLEs
# ============================================================
print("=" * 70)
print("LINE-FINAL VOCABULARY DISTINCTIVENESS")
print("=" * 70)

# Group tokens by folio+line to determine line-final position independently
# (the Token already has line_final, but we also need line grouping for length bins)
line_groups = defaultdict(list)
all_tokens = []

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle is None or m.is_empty_middle:
        continue
    entry = {
        'word': token.word,
        'folio': token.folio,
        'line': token.line,
        'middle': m.middle,
        'line_final': token.line_final,
    }
    all_tokens.append(entry)
    line_groups[(token.folio, token.line)].append(entry)

print(f"Total B tokens with valid MIDDLEs: {len(all_tokens)}")

# ============================================================
# Step 2: Pre-compute folio_count for each MIDDLE
# ============================================================
middle_folios = defaultdict(set)
for entry in all_tokens:
    middle_folios[entry['middle']].add(entry['folio'])

folio_count = {mid: len(folios) for mid, folios in middle_folios.items()}
total_folios = len({entry['folio'] for entry in all_tokens})

print(f"Unique MIDDLEs: {len(folio_count)}")
print(f"Total folios in B: {total_folios}")

# ============================================================
# Step 3: Classify LINE-FINAL vs LINE-OTHER
# ============================================================
final_folio_counts = []
other_folio_counts = []

for entry in all_tokens:
    fc = folio_count[entry['middle']]
    if entry['line_final']:
        final_folio_counts.append(fc)
    else:
        other_folio_counts.append(fc)

n_final = len(final_folio_counts)
n_other = len(other_folio_counts)
print(f"\nLINE-FINAL tokens: {n_final}")
print(f"LINE-OTHER tokens: {n_other}")

# ============================================================
# Step 4: Basic distribution comparison
# ============================================================
final_arr = np.array(final_folio_counts)
other_arr = np.array(other_folio_counts)

mean_final = float(np.mean(final_arr))
mean_other = float(np.mean(other_arr))
median_final = float(np.median(final_arr))
median_other = float(np.median(other_arr))

print(f"\nMean folio_count  - FINAL: {mean_final:.2f}  OTHER: {mean_other:.2f}")
print(f"Median folio_count - FINAL: {median_final:.1f}  OTHER: {median_other:.1f}")

# Rare middles: < 15 folios
RARE_THRESHOLD = 15
rare_final = int(np.sum(final_arr < RARE_THRESHOLD))
rare_other = int(np.sum(other_arr < RARE_THRESHOLD))
pct_rare_final = 100 * rare_final / n_final
pct_rare_other = 100 * rare_other / n_other

print(f"\n% rare MIDDLEs (<{RARE_THRESHOLD} folios):")
print(f"  FINAL: {pct_rare_final:.1f}% ({rare_final}/{n_final})")
print(f"  OTHER: {pct_rare_other:.1f}% ({rare_other}/{n_other})")

# Folio-unique middles: exactly 1 folio
unique_final = int(np.sum(final_arr == 1))
unique_other = int(np.sum(other_arr == 1))
pct_unique_final = 100 * unique_final / n_final
pct_unique_other = 100 * unique_other / n_other

print(f"\n% folio-unique MIDDLEs (1 folio):")
print(f"  FINAL: {pct_unique_final:.1f}% ({unique_final}/{n_final})")
print(f"  OTHER: {pct_unique_other:.1f}% ({unique_other}/{n_other})")

# ============================================================
# Step 5: Statistical tests
# ============================================================
print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

# Mann-Whitney U test (two-sided)
u_stat, p_mw = stats.mannwhitneyu(final_arr, other_arr, alternative='two-sided')
print(f"\nMann-Whitney U: {u_stat:.0f}")
print(f"  p-value: {p_mw:.2e}")

# Cohen's d (effect size)
pooled_std = math.sqrt(
    ((n_final - 1) * float(np.var(final_arr, ddof=1))
     + (n_other - 1) * float(np.var(other_arr, ddof=1)))
    / (n_final + n_other - 2)
)
cohens_d = (mean_final - mean_other) / pooled_std if pooled_std > 0 else 0.0
print(f"  Cohen's d: {cohens_d:.4f}")

# Chi-square for rare-middle enrichment
# Contingency table: [rare_final, not_rare_final], [rare_other, not_rare_other]
not_rare_final = n_final - rare_final
not_rare_other = n_other - rare_other
contingency = np.array([[rare_final, not_rare_final],
                         [rare_other, not_rare_other]])
chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square (rare enrichment): {chi2:.4f}")
print(f"  p-value: {p_chi:.2e}")

# Odds ratio for rare middles
if not_rare_final > 0 and rare_other > 0 and not_rare_other > 0:
    odds_ratio = (rare_final / not_rare_final) / (rare_other / not_rare_other)
else:
    odds_ratio = float('inf')
print(f"  Odds ratio: {odds_ratio:.4f}")

# ============================================================
# Step 6: Line-length controlled analysis
# ============================================================
print("\n" + "=" * 70)
print("LINE-LENGTH CONTROLLED ANALYSIS")
print("=" * 70)

# Compute line lengths and bin
line_lengths = {key: len(tokens) for key, tokens in line_groups.items()}

# Bins: short (2-5), medium (6-9), long (10+)
bins = {
    'short': (2, 5),
    'medium': (6, 9),
    'long': (10, 999),
}

line_length_controlled = {}

for bin_name, (lo, hi) in bins.items():
    # Identify lines in this bin
    qualifying_lines = {key for key, length in line_lengths.items() if lo <= length <= hi}

    bin_final = []
    bin_other = []

    for entry in all_tokens:
        key = (entry['folio'], entry['line'])
        if key not in qualifying_lines:
            continue
        fc = folio_count[entry['middle']]
        if entry['line_final']:
            bin_final.append(fc)
        else:
            bin_other.append(fc)

    n_bf = len(bin_final)
    n_bo = len(bin_other)

    if n_bf >= 5 and n_bo >= 5:
        mean_bf = float(np.mean(bin_final))
        mean_bo = float(np.mean(bin_other))
        _, p_bin = stats.mannwhitneyu(bin_final, bin_other, alternative='two-sided')
        print(f"\n{bin_name} lines ({lo}-{hi} tokens): n_final={n_bf}, n_other={n_bo}")
        print(f"  Final mean: {mean_bf:.2f}, Other mean: {mean_bo:.2f}, p={p_bin:.2e}")
    else:
        mean_bf = float(np.mean(bin_final)) if n_bf > 0 else None
        mean_bo = float(np.mean(bin_other)) if n_bo > 0 else None
        p_bin = None
        print(f"\n{bin_name} lines ({lo}-{hi} tokens): n_final={n_bf}, n_other={n_bo} (too few)")

    line_length_controlled[bin_name] = {
        'n_final': n_bf,
        'n_other': n_bo,
        'final_mean': round(mean_bf, 4) if mean_bf is not None else None,
        'other_mean': round(mean_bo, 4) if mean_bo is not None else None,
        'p': float(f"{p_bin:.6e}") if (p_bin is not None and p_bin < 1e-6) else (round(p_bin, 6) if p_bin is not None else None),
    }

# ============================================================
# Step 7: Verdict
# ============================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

# SUPPORTED if:
# 1. Line-final mean folio_count is lower than line-other (rarer)
# 2. Mann-Whitney p < 0.05
# 3. Effect holds in at least 2 of 3 line-length bins
rarer = mean_final < mean_other
significant = p_mw < 0.05
bins_supporting = sum(
    1 for v in line_length_controlled.values()
    if v['final_mean'] is not None and v['other_mean'] is not None
    and v['final_mean'] < v['other_mean']
    and v['p'] is not None and v['p'] < 0.05
)

verdict = "SUPPORTED" if (rarer and significant and bins_supporting >= 2) else "NOT_SUPPORTED"

notes_parts = []
if rarer:
    notes_parts.append(f"Line-final MIDDLEs are rarer (mean {mean_final:.2f} vs {mean_other:.2f} folios)")
else:
    notes_parts.append(f"Line-final MIDDLEs are NOT rarer (mean {mean_final:.2f} vs {mean_other:.2f} folios)")
notes_parts.append(f"Mann-Whitney p={p_mw:.2e}, d={cohens_d:.4f}")
notes_parts.append(f"Rare enrichment OR={odds_ratio:.3f}, chi2 p={p_chi:.2e}")
notes_parts.append(f"Line-length bins supporting: {bins_supporting}/3")
notes = "; ".join(notes_parts)

print(f"\nVerdict: {verdict}")
print(f"Notes: {notes}")

# ============================================================
# Step 8: Save results
# ============================================================
results = {
    "test": "Line-Final Vocabulary Distinctiveness",
    "n_line_final": n_final,
    "n_line_other": n_other,
    "mean_folio_count_final": round(mean_final, 4),
    "mean_folio_count_other": round(mean_other, 4),
    "median_folio_count_final": round(median_final, 4),
    "median_folio_count_other": round(median_other, 4),
    "pct_rare_final": round(pct_rare_final, 4),
    "pct_rare_other": round(pct_rare_other, 4),
    "pct_unique_final": round(pct_unique_final, 4),
    "pct_unique_other": round(pct_unique_other, 4),
    "mann_whitney_u": round(float(u_stat), 4),
    "p_value": float(f"{float(p_mw):.6e}") if p_mw < 1e-6 else round(float(p_mw), 8),
    "effect_size_d": round(cohens_d, 4),
    "chi_square_rare": round(float(chi2), 4),
    "chi_square_p": float(f"{float(p_chi):.6e}") if p_chi < 1e-6 else round(float(p_chi), 8),
    "odds_ratio_rare": round(odds_ratio, 4),
    "line_length_controlled": line_length_controlled,
    "verdict": verdict,
    "notes": notes,
}

output_path = results_dir / "line_final_distinctiveness.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved to {output_path}")
