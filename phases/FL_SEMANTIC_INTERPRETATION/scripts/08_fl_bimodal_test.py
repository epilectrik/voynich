"""
08_fl_bimodal_test.py

Test whether FL MIDDLEs track TWO states rather than one.

Hypothesis: The clean global FL gradient (C777) might conflate two distinct
signals. At line level this would create ambiguity — the same FL MIDDLE
appearing at different positions depending on which state is being tracked.

Tests:
1. Per-MIDDLE position distributions: unimodal or bimodal?
2. Section-stratified FL positions: does the gradient split?
3. Lines with 2+ FL tokens: do they follow the gradient or show competing patterns?
4. REGIME-stratified FL positions: different state tracking by regime?
5. Context-dependent FL positions: does what PRECEDES an FL token predict its position?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
import statistics
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# FL MIDDLE stage assignments from C777
FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

tx = Transcript()
morph = Morphology()

# ============================================================
# Collect all FL tokens with full context
# ============================================================

fl_tokens = []
line_tokens = defaultdict(list)  # (folio, line) -> [tokens]

for t in tx.currier_b():
    m = morph.extract(t.word)
    mid = m.middle if m else None
    line_key = (t.folio, t.line)
    line_tokens[line_key].append(t)

# Now process each line to get positions
for line_key, tokens in line_tokens.items():
    max_idx = len(tokens) - 1
    if max_idx <= 0:
        continue

    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            norm_pos = idx / max_idx
            stage, expected_pos = FL_STAGE_MAP[m.middle]
            fl_tokens.append({
                'word': t.word,
                'middle': m.middle,
                'stage': stage,
                'expected_pos': expected_pos,
                'actual_pos': norm_pos,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'line_key': line_key,
                'idx': idx,
                'line_len': len(tokens),
            })

print(f"Total FL tokens in B: {len(fl_tokens)}")

# ============================================================
# TEST 1: Per-MIDDLE position distributions — bimodal?
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: Per-MIDDLE Position Distributions")
print("=" * 60)

from scipy.stats import shapiro, kurtosis

bimodal_results = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    positions = [ft['actual_pos'] for ft in fl_tokens if ft['middle'] == mid]
    if len(positions) < 20:
        continue

    arr = np.array(positions)
    mean_pos = float(np.mean(arr))
    std_pos = float(np.std(arr))
    kurt = float(kurtosis(arr))  # Negative kurtosis suggests bimodal

    # Hartigan's dip test approximation: check if distribution has two modes
    # Simple approach: split at mean, check if both halves have substantial mass
    below = arr[arr < mean_pos]
    above = arr[arr >= mean_pos]
    balance = min(len(below), len(above)) / max(len(below), len(above)) if max(len(below), len(above)) > 0 else 0

    # Check quartile spread
    q1, q3 = float(np.percentile(arr, 25)), float(np.percentile(arr, 75))
    iqr = q3 - q1

    stage, expected = FL_STAGE_MAP[mid]
    bimodal_results[mid] = {
        'n': len(positions),
        'mean': round(mean_pos, 3),
        'std': round(std_pos, 3),
        'kurtosis': round(kurt, 3),
        'iqr': round(iqr, 3),
        'balance': round(balance, 3),
        'stage': stage,
        'expected_pos': expected,
    }

    bimodal_hint = "BIMODAL?" if kurt < -0.5 else "SPREAD" if std_pos > 0.3 else "PEAKED"
    print(f"  {mid:>4} (n={len(positions):>4}): mean={mean_pos:.3f} std={std_pos:.3f} "
          f"kurt={kurt:>6.3f} IQR={iqr:.3f} [{bimodal_hint}]")

# ============================================================
# TEST 2: Section-stratified FL positions
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: FL Gradient by Section")
print("=" * 60)

from scipy.stats import spearmanr

section_results = {}
for section in sorted(set(ft['section'] for ft in fl_tokens)):
    sect_tokens = [ft for ft in fl_tokens if ft['section'] == section]
    if len(sect_tokens) < 30:
        continue

    # Compute per-MIDDLE mean positions within this section
    mid_positions = defaultdict(list)
    for ft in sect_tokens:
        mid_positions[ft['middle']].append(ft['actual_pos'])

    middles_with_data = [(mid, statistics.mean(pos), FL_STAGE_MAP[mid][1])
                         for mid, pos in mid_positions.items()
                         if len(pos) >= 5 and mid in FL_STAGE_MAP]

    if len(middles_with_data) >= 5:
        expected = [m[2] for m in middles_with_data]
        actual = [m[1] for m in middles_with_data]
        rho, p = spearmanr(expected, actual)
    else:
        rho, p = None, None

    # Overall mean position in this section
    all_pos = [ft['actual_pos'] for ft in sect_tokens]

    section_results[section] = {
        'n': len(sect_tokens),
        'mean_pos': round(statistics.mean(all_pos), 3),
        'std_pos': round(statistics.stdev(all_pos), 3) if len(all_pos) > 1 else 0,
        'gradient_rho': round(rho, 3) if rho is not None else None,
        'gradient_p': round(p, 4) if p is not None else None,
        'n_middles_tested': len(middles_with_data),
    }

    rho_str = f"rho={rho:.3f} p={p:.4f}" if rho is not None else "insufficient data"
    print(f"  Section {section}: n={len(sect_tokens):>4}, mean_pos={statistics.mean(all_pos):.3f}, "
          f"gradient {rho_str}")

# ============================================================
# TEST 3: Lines with 2+ FL tokens — ordering concordance
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: Multi-FL Lines — Ordering Concordance")
print("=" * 60)

# Group FL tokens by line
fl_by_line = defaultdict(list)
for ft in fl_tokens:
    fl_by_line[ft['line_key']].append(ft)

multi_fl_lines = {k: v for k, v in fl_by_line.items() if len(v) >= 2}

concordant = 0
discordant = 0
tied = 0
same_stage_concordant = 0
same_stage_discordant = 0
diff_stage_concordant = 0
diff_stage_discordant = 0

for line_key, fts in multi_fl_lines.items():
    fts_sorted = sorted(fts, key=lambda x: x['idx'])
    for i in range(len(fts_sorted)):
        for j in range(i+1, len(fts_sorted)):
            # i comes before j in line (by idx)
            exp_i = fts_sorted[i]['expected_pos']
            exp_j = fts_sorted[j]['expected_pos']
            same_stage = fts_sorted[i]['stage'] == fts_sorted[j]['stage']

            if exp_i < exp_j:
                concordant += 1
                if same_stage:
                    same_stage_concordant += 1
                else:
                    diff_stage_concordant += 1
            elif exp_i > exp_j:
                discordant += 1
                if same_stage:
                    same_stage_discordant += 1
                else:
                    diff_stage_discordant += 1
            else:
                tied += 1

total_pairs = concordant + discordant + tied
concordance_rate = concordant / (concordant + discordant) if (concordant + discordant) > 0 else 0

print(f"Lines with 2+ FL tokens: {len(multi_fl_lines)}")
print(f"Total FL pairs: {total_pairs}")
print(f"Concordant (early FL before late FL): {concordant} ({concordant/total_pairs*100:.1f}%)")
print(f"Discordant (reversed order): {discordant} ({discordant/total_pairs*100:.1f}%)")
print(f"Tied (same expected position): {tied} ({tied/total_pairs*100:.1f}%)")
print(f"Concordance rate (excl ties): {concordance_rate:.3f}")

print(f"\nSame-stage pairs: concordant={same_stage_concordant}, discordant={same_stage_discordant}")
print(f"Different-stage pairs: concordant={diff_stage_concordant}, discordant={diff_stage_discordant}")
if (diff_stage_concordant + diff_stage_discordant) > 0:
    diff_concordance = diff_stage_concordant / (diff_stage_concordant + diff_stage_discordant)
    print(f"Cross-stage concordance: {diff_concordance:.3f}")
else:
    diff_concordance = None

# ============================================================
# TEST 4: Context-dependent FL positions
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: Preceding Token Role -> FL Position")
print("=" * 60)

# Load class map for role identification
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# For each FL token, find what preceded it
preceding_role_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            if idx > 0:
                prev_token = tokens[idx - 1]
                prev_role = token_to_role.get(prev_token.word, 'UNKNOWN')
                norm_pos = idx / (len(tokens) - 1) if len(tokens) > 1 else 0.5
                preceding_role_positions[prev_role].append(norm_pos)

print(f"\nFL position by what precedes it:")
context_results = {}
for role in sorted(preceding_role_positions.keys(), key=lambda x: -len(preceding_role_positions[x])):
    positions = preceding_role_positions[role]
    if len(positions) >= 20:
        mean_p = statistics.mean(positions)
        std_p = statistics.stdev(positions) if len(positions) > 1 else 0
        context_results[role] = {
            'n': len(positions),
            'mean_pos': round(mean_p, 3),
            'std_pos': round(std_p, 3),
        }
        print(f"  After {role:25}: n={len(positions):>4}, mean_pos={mean_p:.3f}, std={std_p:.3f}")

# ============================================================
# TEST 5: Per-MIDDLE position by section — does same MIDDLE
# sit at different positions in different sections?
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: Same FL MIDDLE, Different Sections -> Different Position?")
print("=" * 60)

from scipy.stats import kruskal

split_evidence = []
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    sect_positions = defaultdict(list)
    for ft in fl_tokens:
        if ft['middle'] == mid:
            sect_positions[ft['section']].append(ft['actual_pos'])

    # Need at least 2 sections with 10+ tokens each
    valid_sections = {s: p for s, p in sect_positions.items() if len(p) >= 10}
    if len(valid_sections) < 2:
        continue

    # Kruskal-Wallis test across sections
    groups = list(valid_sections.values())
    H, p = kruskal(*groups)

    means = {s: round(statistics.mean(p), 3) for s, p in valid_sections.items()}
    spread = max(means.values()) - min(means.values())

    split_evidence.append({
        'middle': mid,
        'stage': FL_STAGE_MAP[mid][0],
        'n_sections': len(valid_sections),
        'section_means': means,
        'position_spread': round(spread, 3),
        'kruskal_H': round(H, 2),
        'kruskal_p': round(p, 6),
    })

    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {mid:>4} ({FL_STAGE_MAP[mid][0]:>10}): spread={spread:.3f}, "
          f"H={H:.2f}, p={p:.4f} {sig}  means={means}")

# Count significant splits
sig_count = sum(1 for s in split_evidence if s['kruskal_p'] < 0.05)
print(f"\nFL MIDDLEs with significant section-dependent positions: "
      f"{sig_count}/{len(split_evidence)}")

# ============================================================
# Write results
# ============================================================

result = {
    "total_fl_tokens": len(fl_tokens),
    "test1_bimodal": bimodal_results,
    "test2_section_gradient": section_results,
    "test3_line_ordering": {
        "multi_fl_lines": len(multi_fl_lines),
        "total_pairs": total_pairs,
        "concordant": concordant,
        "discordant": discordant,
        "tied": tied,
        "concordance_rate": round(concordance_rate, 4),
        "diff_stage_concordance": round(diff_concordance, 4) if diff_concordance is not None else None,
    },
    "test5_context": context_results,
    "test6_section_split": split_evidence,
    "summary": {
        "sig_section_splits": sig_count,
        "total_tested": len(split_evidence),
    }
}

out_path = Path(__file__).resolve().parents[1] / "results" / "08_fl_bimodal_test.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
