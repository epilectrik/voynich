"""
09_hazard_safe_bimodality.py

Test whether FL bimodality is simply the hazard/safe split (C773).

Q: Is the bimodality the hazard/safe split manifesting at per-MIDDLE level?
- For each FL MIDDLE, separate tokens by hazard class vs safe class vs other
- Compare per-class position distributions
- If hazard and safe populations exist for same MIDDLE, test position separation
- Pass (C773 explains): Bimodality disappears when hazard/safe controlled
- Fail (independent): Bimodality persists within hazard-only and/or safe-only subsets
"""
import sys
import json
import statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kurtosis, mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

HAZARD_CLASSES = {7, 30}
SAFE_CLASSES = {38, 40}

tx = Transcript()
morph = Morphology()

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records with hazard classification
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            cls = token_to_class.get(t.word, -1)
            if cls in HAZARD_CLASSES:
                haz = 'HAZARD'
            elif cls in SAFE_CLASSES:
                haz = 'SAFE'
            else:
                haz = 'OTHER'

            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'actual_pos': idx / (n - 1),
                'hazard_class': haz,
                'token_class': cls,
            })

print(f"Total FL records: {len(fl_records)}")
for hc in ['HAZARD', 'SAFE', 'OTHER']:
    n = sum(1 for r in fl_records if r['hazard_class'] == hc)
    print(f"  {hc}: {n} ({n/len(fl_records)*100:.1f}%)")

# ============================================================
# Per-MIDDLE analysis: split by hazard class
# ============================================================
print(f"\n{'='*60}")
print("Per-MIDDLE hazard/safe position analysis")

per_middle_results = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    mid_records = [r for r in fl_records if r['middle'] == mid]
    if len(mid_records) < 20:
        continue

    # Split by hazard class
    class_positions = defaultdict(list)
    for r in mid_records:
        class_positions[r['hazard_class']].append(r['actual_pos'])

    # Global kurtosis
    all_pos = np.array([r['actual_pos'] for r in mid_records])
    global_kurt = float(kurtosis(all_pos))

    # Per-class kurtosis
    class_analysis = {}
    for hc in ['HAZARD', 'SAFE', 'OTHER']:
        positions = class_positions.get(hc, [])
        if len(positions) >= 10:
            arr = np.array(positions)
            class_analysis[hc] = {
                'n': len(positions),
                'mean': round(float(np.mean(arr)), 3),
                'std': round(float(np.std(arr)), 3),
                'kurtosis': round(float(kurtosis(arr)), 3),
            }

    # Mann-Whitney between hazard and safe if both present with sufficient n
    mw_result = None
    if 'HAZARD' in class_analysis and 'SAFE' in class_analysis:
        h_pos = np.array(class_positions['HAZARD'])
        s_pos = np.array(class_positions['SAFE'])
        if len(h_pos) >= 10 and len(s_pos) >= 10:
            stat, p = mannwhitneyu(h_pos, s_pos, alternative='two-sided')
            mw_result = {
                'U': round(float(stat), 1),
                'p': round(float(p), 6),
                'hazard_mean': round(float(np.mean(h_pos)), 3),
                'safe_mean': round(float(np.mean(s_pos)), 3),
                'separation': round(abs(float(np.mean(s_pos)) - float(np.mean(h_pos))), 3),
            }

    # Check if within-class kurtosis is still bimodal
    within_bimodal = any(
        v['kurtosis'] < -0.5 for v in class_analysis.values()
        if v['n'] >= 20
    )

    per_middle_results[mid] = {
        'n': len(mid_records),
        'global_kurtosis': round(global_kurt, 3),
        'class_analysis': class_analysis,
        'mann_whitney': mw_result,
        'within_class_bimodal': within_bimodal,
    }

    stage = FL_STAGE_MAP[mid][0]
    class_str = " | ".join(
        f"{hc}:n={v['n']},k={v['kurtosis']:.2f}"
        for hc, v in class_analysis.items()
    )
    mw_str = f" MW_p={mw_result['p']:.4f} sep={mw_result['separation']:.3f}" if mw_result else ""
    bimodal_str = " WITHIN-BIMODAL" if within_bimodal else ""
    print(f"  {mid:>4} ({stage:>10}): global_k={global_kurt:>7.3f} | {class_str}{mw_str}{bimodal_str}")

# ============================================================
# Summary statistics
# ============================================================
globally_bimodal = [mid for mid, v in per_middle_results.items()
                    if v['global_kurtosis'] < -0.5]
resolved_by_class = [mid for mid in globally_bimodal
                     if not per_middle_results[mid]['within_class_bimodal']]
persists_within = [mid for mid in globally_bimodal
                   if per_middle_results[mid]['within_class_bimodal']]

# MIDDLEs where hazard vs safe position significantly differs
sig_separation = [
    mid for mid, v in per_middle_results.items()
    if v['mann_whitney'] and v['mann_whitney']['p'] < 0.05 and v['mann_whitney']['separation'] > 0.10
]

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Globally bimodal (kurt < -0.5): {len(globally_bimodal)}")
print(f"  Resolved by hazard/safe control: {len(resolved_by_class)} — {resolved_by_class}")
print(f"  Persists within class: {len(persists_within)} — {persists_within}")
print(f"  Significant hazard/safe separation: {len(sig_separation)} — {sig_separation}")

# ============================================================
# Verdict
# ============================================================
if len(globally_bimodal) == 0:
    verdict = "NO_BIMODALITY"
    explanation = "No FL MIDDLEs show bimodal kurtosis"
elif len(resolved_by_class) > len(persists_within):
    verdict = "C773_EXPLAINS"
    explanation = (f"Hazard/safe split explains bimodality: {len(resolved_by_class)}/{len(globally_bimodal)} "
                   f"bimodal MIDDLEs resolved. {len(sig_separation)} show significant position separation.")
elif len(persists_within) > len(resolved_by_class):
    verdict = "INDEPENDENT"
    explanation = (f"Bimodality persists within hazard/safe classes: "
                   f"{len(persists_within)}/{len(globally_bimodal)} remain bimodal. "
                   f"Dual-state is independent of C773.")
else:
    verdict = "PARTIAL_EXPLANATION"
    explanation = (f"C773 partially explains: {len(resolved_by_class)} resolved, "
                   f"{len(persists_within)} persist")

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_fl_records': len(fl_records),
    'per_middle': per_middle_results,
    'globally_bimodal': globally_bimodal,
    'resolved_by_hazard_safe': resolved_by_class,
    'persists_within_class': persists_within,
    'significant_separation': sig_separation,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "09_hazard_safe_bimodality.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
