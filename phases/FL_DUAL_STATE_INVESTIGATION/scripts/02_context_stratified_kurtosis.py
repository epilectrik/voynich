"""
02_context_stratified_kurtosis.py

Test whether FL bimodality correlates with specific contexts.

Q: Does bimodality arise from context mixing, or is it intrinsic to FL?
- For each FL MIDDLE, compute kurtosis stratified by:
  preceding token role, following token role, line half
- Compare within-stratum kurtosis to global kurtosis
- Pass (context): Within-stratum kurtosis is unimodal (>0)
- Fail (intrinsic): Within-stratum kurtosis remains negative
"""
import sys
import json
import statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kurtosis

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

tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records with context
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            norm_pos = idx / (n - 1)
            stage, expected = FL_STAGE_MAP[m.middle]

            prev_role = token_to_role.get(tokens[idx - 1].word, 'UNKNOWN') if idx > 0 else 'LINE_START'
            next_role = token_to_role.get(tokens[idx + 1].word, 'UNKNOWN') if idx < n - 1 else 'LINE_END'
            line_half = 'FIRST' if norm_pos < 0.5 else 'SECOND'

            fl_records.append({
                'middle': m.middle,
                'actual_pos': norm_pos,
                'prev_role': prev_role,
                'next_role': next_role,
                'line_half': line_half,
            })

print(f"Total FL records: {len(fl_records)}")

# ============================================================
# Global kurtosis per MIDDLE
# ============================================================
global_kurtosis = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    positions = [r['actual_pos'] for r in fl_records if r['middle'] == mid]
    if len(positions) >= 20:
        global_kurtosis[mid] = round(float(kurtosis(np.array(positions))), 3)

# ============================================================
# Stratified kurtosis
# ============================================================
def compute_stratified_kurtosis(records, strat_key, min_n=15):
    """For each MIDDLE, compute kurtosis within each stratum."""
    results = {}
    for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
        mid_records = [r for r in records if r['middle'] == mid]
        if len(mid_records) < 20:
            continue

        strata = defaultdict(list)
        for r in mid_records:
            strata[r[strat_key]].append(r['actual_pos'])

        strat_results = {}
        for stratum, positions in strata.items():
            if len(positions) >= min_n:
                k = float(kurtosis(np.array(positions)))
                strat_results[stratum] = {
                    'n': len(positions),
                    'kurtosis': round(k, 3),
                    'mean': round(float(np.mean(positions)), 3),
                }

        if strat_results:
            kurtosis_values = [v['kurtosis'] for v in strat_results.values()]
            results[mid] = {
                'strata': strat_results,
                'mean_within_kurtosis': round(statistics.mean(kurtosis_values), 3),
                'global_kurtosis': global_kurtosis.get(mid, None),
                'n_strata': len(strat_results),
            }

    return results

print("\n--- Stratified by PRECEDING ROLE ---")
prev_strat = compute_stratified_kurtosis(fl_records, 'prev_role')
for mid, data in prev_strat.items():
    g = data['global_kurtosis']
    w = data['mean_within_kurtosis']
    shift = w - g if g is not None else None
    print(f"  {mid:>4}: global={g:>7.3f}, within-stratum={w:>7.3f}, "
          f"shift={shift:>+7.3f}, n_strata={data['n_strata']}")

print("\n--- Stratified by FOLLOWING ROLE ---")
next_strat = compute_stratified_kurtosis(fl_records, 'next_role')
for mid, data in next_strat.items():
    g = data['global_kurtosis']
    w = data['mean_within_kurtosis']
    shift = w - g if g is not None else None
    print(f"  {mid:>4}: global={g:>7.3f}, within-stratum={w:>7.3f}, "
          f"shift={shift:>+7.3f}, n_strata={data['n_strata']}")

print("\n--- Stratified by LINE HALF ---")
half_strat = compute_stratified_kurtosis(fl_records, 'line_half')
for mid, data in half_strat.items():
    g = data['global_kurtosis']
    w = data['mean_within_kurtosis']
    shift = w - g if g is not None else None
    print(f"  {mid:>4}: global={g:>7.3f}, within-stratum={w:>7.3f}, "
          f"shift={shift:>+7.3f}, n_strata={data['n_strata']}")

# ============================================================
# Verdict
# ============================================================
# Check if within-stratum kurtosis becomes positive (unimodal)
all_strats = {'prev_role': prev_strat, 'next_role': next_strat, 'line_half': half_strat}

context_explains = 0
intrinsic_count = 0
total_tested = 0

for mid in global_kurtosis:
    if global_kurtosis[mid] >= -0.5:
        continue  # Skip already non-bimodal MIDDLEs
    total_tested += 1

    # Check if ANY stratification resolves bimodality for this MIDDLE
    resolved = False
    for strat_name, strat_data in all_strats.items():
        if mid in strat_data:
            if strat_data[mid]['mean_within_kurtosis'] > -0.3:
                resolved = True
                break

    if resolved:
        context_explains += 1
    else:
        intrinsic_count += 1

if total_tested == 0:
    verdict = "NO_BIMODAL_MIDDLES"
    explanation = "No FL MIDDLEs show bimodal kurtosis"
elif context_explains > intrinsic_count:
    verdict = "CONTEXT_DRIVEN"
    explanation = (f"{context_explains}/{total_tested} bimodal MIDDLEs resolved by context "
                   f"stratification; {intrinsic_count} remain intrinsic")
elif intrinsic_count > context_explains:
    verdict = "INTRINSIC"
    explanation = (f"{intrinsic_count}/{total_tested} bimodal MIDDLEs persist after context "
                   f"stratification; only {context_explains} resolved by context")
else:
    verdict = "MIXED"
    explanation = f"Even split: {context_explains} context-driven, {intrinsic_count} intrinsic"

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_fl_records': len(fl_records),
    'global_kurtosis': global_kurtosis,
    'stratified_by_prev_role': prev_strat,
    'stratified_by_next_role': next_strat,
    'stratified_by_line_half': half_strat,
    'bimodal_middles_tested': total_tested,
    'context_explains_count': context_explains,
    'intrinsic_count': intrinsic_count,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "02_context_stratified_kurtosis.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
