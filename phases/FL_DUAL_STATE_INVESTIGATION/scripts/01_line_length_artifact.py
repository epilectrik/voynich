"""
01_line_length_artifact.py

Test whether FL bimodal distributions are an artifact of line length.
Short lines compress positions, potentially creating artificial spread.

Q: Is the bimodal spread an artifact of line length?
- Bin lines by length (short <7, medium 7-12, long >12 tokens)
- Compute per-MIDDLE kurtosis within each length bin
- Compute concordance rate per length bin
- Pass (artifact): Kurtosis unimodal in long lines AND concordance > 65%
- Fail (real): Bimodality persists across all line-length bins
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

LENGTH_BINS = {
    'short': (0, 7),    # <7 tokens
    'medium': (7, 13),  # 7-12 tokens
    'long': (13, 999),  # >12 tokens
}

tx = Transcript()
morph = Morphology()

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL token records with line-length info
fl_tokens = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            stage, expected = FL_STAGE_MAP[m.middle]
            fl_tokens.append({
                'middle': m.middle,
                'stage': stage,
                'expected_pos': expected,
                'actual_pos': idx / (n - 1),
                'line_len': n,
                'line_key': line_key,
                'idx': idx,
            })

print(f"Total FL tokens: {len(fl_tokens)}")

# ============================================================
# Per-bin kurtosis analysis
# ============================================================
bin_kurtosis = {}
for bin_name, (lo, hi) in LENGTH_BINS.items():
    bin_fl = [ft for ft in fl_tokens if lo <= ft['line_len'] < hi]
    print(f"\n--- {bin_name} lines (len {lo}-{hi-1}): {len(bin_fl)} FL tokens ---")

    mid_results = {}
    for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
        positions = [ft['actual_pos'] for ft in bin_fl if ft['middle'] == mid]
        if len(positions) < 10:
            continue
        arr = np.array(positions)
        k = float(kurtosis(arr))
        mid_results[mid] = {
            'n': len(positions),
            'mean': round(float(np.mean(arr)), 3),
            'std': round(float(np.std(arr)), 3),
            'kurtosis': round(k, 3),
        }
        label = "BIMODAL" if k < -0.5 else "FLAT" if k < 0 else "PEAKED"
        print(f"  {mid:>4} n={len(positions):>4} mean={np.mean(arr):.3f} "
              f"std={np.std(arr):.3f} kurt={k:>7.3f} [{label}]")

    bin_kurtosis[bin_name] = mid_results

# ============================================================
# Per-bin concordance analysis
# ============================================================
bin_concordance = {}
for bin_name, (lo, hi) in LENGTH_BINS.items():
    bin_fl = [ft for ft in fl_tokens if lo <= ft['line_len'] < hi]

    # Group by line
    fl_by_line = defaultdict(list)
    for ft in bin_fl:
        fl_by_line[ft['line_key']].append(ft)

    concordant = 0
    discordant = 0
    tied = 0
    for line_key, fts in fl_by_line.items():
        if len(fts) < 2:
            continue
        fts_sorted = sorted(fts, key=lambda x: x['idx'])
        for i in range(len(fts_sorted)):
            for j in range(i + 1, len(fts_sorted)):
                ei = fts_sorted[i]['expected_pos']
                ej = fts_sorted[j]['expected_pos']
                if ei < ej:
                    concordant += 1
                elif ei > ej:
                    discordant += 1
                else:
                    tied += 1

    total = concordant + discordant
    rate = concordant / total if total > 0 else 0
    multi_lines = sum(1 for v in fl_by_line.values() if len(v) >= 2)

    bin_concordance[bin_name] = {
        'multi_fl_lines': multi_lines,
        'concordant': concordant,
        'discordant': discordant,
        'tied': tied,
        'concordance_rate': round(rate, 4),
    }
    print(f"\n{bin_name} concordance: {concordant}/{total} = {rate:.3f} "
          f"(from {multi_lines} multi-FL lines)")

# ============================================================
# Verdict
# ============================================================

# Check if long lines show unimodal kurtosis
long_results = bin_kurtosis.get('long', {})
long_bimodal_count = sum(1 for v in long_results.values() if v['kurtosis'] < -0.5)
long_total = len(long_results)

# Check if long-line concordance exceeds threshold
long_concordance = bin_concordance.get('long', {}).get('concordance_rate', 0)

artifact = (long_bimodal_count == 0 and long_concordance > 0.65) if long_total > 0 else False

# Check persistence across bins
all_bins_bimodal = all(
    sum(1 for v in bin_kurtosis.get(b, {}).values() if v['kurtosis'] < -0.5) > 0
    for b in LENGTH_BINS
)

if artifact:
    verdict = "ARTIFACT"
    explanation = (f"Long lines show unimodal kurtosis ({long_bimodal_count}/{long_total} bimodal) "
                   f"and concordance {long_concordance:.3f} > 0.65")
elif all_bins_bimodal:
    verdict = "REAL"
    explanation = (f"Bimodality persists in all bins including long lines "
                   f"({long_bimodal_count}/{long_total} bimodal, "
                   f"concordance {long_concordance:.3f})")
else:
    verdict = "PARTIAL"
    explanation = "Mixed: some bins show bimodality, others don't"

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_fl_tokens': len(fl_tokens),
    'length_bin_kurtosis': bin_kurtosis,
    'length_bin_concordance': bin_concordance,
    'long_line_bimodal_count': long_bimodal_count,
    'long_line_total_middles': long_total,
    'long_line_concordance': long_concordance,
    'all_bins_bimodal': all_bins_bimodal,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "01_line_length_artifact.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
