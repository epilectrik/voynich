"""
10_prefix_fl_mode_interaction.py

Test whether PREFIX choice determines which FL mode is active.

Q: Does PREFIX choice determine which FL mode is active?
- For common FL MIDDLEs (n >= 100), stratify by PREFIX
- Test if PREFIX correlates with FL position
- Compute Kruskal-Wallis: position ~ PREFIX for each MIDDLE
- Pass: PREFIX significantly shifts position for >50% of MIDDLEs
- Fail: PREFIX has no effect on FL position
"""
import sys
import json
import statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal

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

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records with PREFIX
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            prefix = m.prefix if m.prefix else 'NONE'
            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': prefix,
                'actual_pos': idx / (n - 1),
            })

print(f"Total FL records: {len(fl_records)}")

# ============================================================
# PREFIX distribution across FL
# ============================================================
prefix_counts = defaultdict(int)
for r in fl_records:
    prefix_counts[r['prefix']] += 1

print(f"\nPREFIX distribution in FL tokens:")
for prefix, count in sorted(prefix_counts.items(), key=lambda x: -x[1]):
    print(f"  {prefix:>6}: {count:>5} ({count/len(fl_records)*100:.1f}%)")

# ============================================================
# Per-MIDDLE: position ~ PREFIX (Kruskal-Wallis)
# ============================================================
MIN_N = 100  # MIDDLEs with >= 100 total tokens
MIN_PREFIX_N = 10  # Each prefix group needs >= 10 tokens

print(f"\n{'='*60}")
print(f"Per-MIDDLE Kruskal-Wallis: position ~ PREFIX")

per_middle_results = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    mid_records = [r for r in fl_records if r['middle'] == mid]
    if len(mid_records) < MIN_N:
        continue

    # Group by PREFIX
    prefix_positions = defaultdict(list)
    for r in mid_records:
        prefix_positions[r['prefix']].append(r['actual_pos'])

    # Filter to prefixes with enough tokens
    valid_prefixes = {p: pos for p, pos in prefix_positions.items() if len(pos) >= MIN_PREFIX_N}

    if len(valid_prefixes) < 2:
        print(f"  {mid:>4}: n={len(mid_records):>4} — only {len(valid_prefixes)} valid prefix groups, SKIP")
        continue

    # Kruskal-Wallis
    groups = list(valid_prefixes.values())
    H, p = kruskal(*groups)

    # Effect size: eta-squared approximation from Kruskal-Wallis
    N = sum(len(g) for g in groups)
    k = len(groups)
    eta_sq = (H - k + 1) / (N - k) if N > k else 0

    # Per-prefix means
    prefix_means = {pfx: round(statistics.mean(pos), 3) for pfx, pos in valid_prefixes.items()}
    spread = max(prefix_means.values()) - min(prefix_means.values())

    sig = p < 0.01
    stage = FL_STAGE_MAP[mid][0]

    per_middle_results[mid] = {
        'n': len(mid_records),
        'stage': stage,
        'n_valid_prefixes': len(valid_prefixes),
        'prefix_means': prefix_means,
        'prefix_ns': {p: len(v) for p, v in valid_prefixes.items()},
        'kruskal_H': round(float(H), 2),
        'kruskal_p': round(float(p), 6),
        'eta_squared': round(float(eta_sq), 4),
        'position_spread': round(spread, 3),
        'significant': bool(sig),
    }

    sig_str = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {mid:>4} ({stage:>10}): n={len(mid_records):>4} "
          f"prefixes={len(valid_prefixes)} H={H:>7.2f} p={p:.4f}{sig_str} "
          f"spread={spread:.3f} means={prefix_means}")

# ============================================================
# Summary
# ============================================================
tested = len(per_middle_results)
sig_count = sum(1 for v in per_middle_results.values() if v['significant'])
large_spread = sum(1 for v in per_middle_results.values() if v['position_spread'] > 0.10)

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  MIDDLEs tested (n >= {MIN_N}): {tested}")
print(f"  Significant PREFIX effect (p < 0.01): {sig_count}/{tested}")
print(f"  Large position spread (>0.10): {large_spread}/{tested}")

# ============================================================
# Verdict
# ============================================================
sig_pct = sig_count / tested if tested > 0 else 0

if sig_pct > 0.50:
    verdict = "PREFIX_SELECTS_MODE"
    explanation = (f"PREFIX significantly shifts FL position for {sig_count}/{tested} "
                   f"({sig_pct:.0%}) of MIDDLEs (p < 0.01). PREFIX selects FL mode.")
elif sig_pct > 0.25:
    verdict = "PARTIAL_PREFIX_EFFECT"
    explanation = (f"PREFIX effect significant for {sig_count}/{tested} ({sig_pct:.0%}). "
                   f"Some MIDDLEs are PREFIX-modulated, others not.")
else:
    verdict = "NO_PREFIX_EFFECT"
    explanation = (f"PREFIX has no significant effect: only {sig_count}/{tested} ({sig_pct:.0%}) "
                   f"show p < 0.01. Mode selection is independent of PREFIX.")

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_fl_records': len(fl_records),
    'prefix_distribution': dict(prefix_counts),
    'min_n': MIN_N,
    'min_prefix_n': MIN_PREFIX_N,
    'middles_tested': tested,
    'significant_count': sig_count,
    'significant_pct': round(sig_pct, 3),
    'per_middle': per_middle_results,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "10_prefix_fl_mode_interaction.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
