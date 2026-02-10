"""
04_section_t_anomaly.py

Investigate why Section T shows no FL gradient (rho=0.188, p=0.60).

Q: Why does Section T show no FL gradient?
- Profile Section T: FL tokens per MIDDLE, line lengths, paragraph structure
- Compare T's FL frequency profile to other sections
- Test if T uses a restricted FL subset
- Check if T lines are systematically shorter
- Pass (structural): T anomaly explained by sample size or MIDDLE restriction
- Fail (genuine): T genuinely operates differently
"""
import sys
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import spearmanr, chi2_contingency

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

# Collect all B tokens by section, line
section_line_tokens = defaultdict(lambda: defaultdict(list))
all_line_lengths = defaultdict(list)

for t in tx.currier_b():
    line_key = (t.folio, t.line)
    section_line_tokens[t.section][line_key].append(t)

# Build per-section profiles
section_profiles = {}
for section in sorted(section_line_tokens.keys()):
    lines = section_line_tokens[section]
    line_lengths = [len(tokens) for tokens in lines.values()]

    # FL tokens
    fl_by_middle = defaultdict(list)
    total_tokens = 0
    for line_key, tokens in lines.items():
        n = len(tokens)
        total_tokens += n
        if n <= 1:
            continue
        for idx, t in enumerate(tokens):
            m = morph.extract(t.word)
            if m and m.middle and m.middle in FL_STAGE_MAP:
                fl_by_middle[m.middle].append(idx / (n - 1))

    fl_count = sum(len(v) for v in fl_by_middle.values())
    fl_rate = fl_count / total_tokens if total_tokens > 0 else 0

    # Gradient test within this section
    mid_means = {}
    for mid, positions in fl_by_middle.items():
        if len(positions) >= 3:
            mid_means[mid] = statistics.mean(positions)

    if len(mid_means) >= 5:
        expected = [FL_STAGE_MAP[m][1] for m in mid_means]
        actual = [mid_means[m] for m in mid_means]
        rho, p = spearmanr(expected, actual)
    else:
        rho, p = None, None

    section_profiles[section] = {
        'n_lines': len(lines),
        'n_tokens': total_tokens,
        'mean_line_length': round(statistics.mean(line_lengths), 1) if line_lengths else 0,
        'median_line_length': round(statistics.median(line_lengths), 1) if line_lengths else 0,
        'std_line_length': round(statistics.stdev(line_lengths), 1) if len(line_lengths) > 1 else 0,
        'short_lines_pct': round(sum(1 for l in line_lengths if l < 7) / len(line_lengths) * 100, 1) if line_lengths else 0,
        'fl_count': fl_count,
        'fl_rate': round(fl_rate, 4),
        'fl_middles_present': sorted(fl_by_middle.keys()),
        'fl_n_middles': len(fl_by_middle),
        'fl_per_middle': {mid: len(pos) for mid, pos in sorted(fl_by_middle.items())},
        'gradient_rho': round(rho, 3) if rho is not None else None,
        'gradient_p': round(p, 4) if p is not None else None,
    }

    rho_str = f"{rho:.3f}" if rho is not None else "N/A"
    print(f"Section {section}: {len(lines)} lines, {total_tokens} tokens, "
          f"mean_len={statistics.mean(line_lengths):.1f}, "
          f"FL={fl_count} ({fl_rate:.3f}), {len(fl_by_middle)} MIDDLEs, "
          f"rho={rho_str}")

# ============================================================
# T-specific deep dive
# ============================================================
print(f"\n{'='*60}")
print("SECTION T DEEP DIVE")

t_profile = section_profiles.get('T', {})
if t_profile:
    print(f"  Lines: {t_profile['n_lines']}")
    print(f"  Tokens: {t_profile['n_tokens']}")
    print(f"  Mean line length: {t_profile['mean_line_length']}")
    print(f"  Short lines (<7): {t_profile['short_lines_pct']}%")
    print(f"  FL tokens: {t_profile['fl_count']} (rate={t_profile['fl_rate']})")
    print(f"  FL MIDDLEs present: {t_profile['fl_middles_present']}")
    print(f"  FL per MIDDLE: {t_profile['fl_per_middle']}")
    print(f"  Gradient: rho={t_profile['gradient_rho']}, p={t_profile['gradient_p']}")

    # Compare T's MIDDLE distribution to global
    print("\n  MIDDLE frequency comparison (T vs all-B):")
    # Global FL frequencies
    all_fl = defaultdict(int)
    for s, p in section_profiles.items():
        for mid, count in p.get('fl_per_middle', {}).items():
            all_fl[mid] += count
    global_total = sum(all_fl.values())

    for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
        t_count = t_profile['fl_per_middle'].get(mid, 0)
        g_count = all_fl.get(mid, 0)
        t_pct = t_count / t_profile['fl_count'] * 100 if t_profile['fl_count'] > 0 else 0
        g_pct = g_count / global_total * 100 if global_total > 0 else 0
        delta = t_pct - g_pct
        marker = " **" if abs(delta) > 3 else ""
        print(f"    {mid:>4}: T={t_count:>3} ({t_pct:>5.1f}%)  global={g_count:>4} ({g_pct:>5.1f}%)  "
              f"delta={delta:>+5.1f}pp{marker}")

# ============================================================
# Test: is T's anomaly from sample size?
# ============================================================
print(f"\n{'='*60}")
print("SAMPLE SIZE TEST")

# Bootstrap: draw 188 FL tokens randomly from S (largest section) and test gradient
s_fl_records = []
for line_key, tokens in section_line_tokens.get('S', {}).items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            s_fl_records.append({
                'middle': m.middle,
                'actual_pos': idx / (n - 1),
            })

t_fl_count = t_profile.get('fl_count', 0)
n_bootstrap = 1000
failed_gradients = 0

np.random.seed(42)
for _ in range(n_bootstrap):
    sample = np.random.choice(len(s_fl_records), size=min(t_fl_count, len(s_fl_records)), replace=False)
    sampled = [s_fl_records[i] for i in sample]

    mid_means = defaultdict(list)
    for r in sampled:
        mid_means[r['middle']].append(r['actual_pos'])

    mid_avg = {m: statistics.mean(p) for m, p in mid_means.items() if len(p) >= 3}
    if len(mid_avg) >= 5:
        expected = [FL_STAGE_MAP[m][1] for m in mid_avg]
        actual = [mid_avg[m] for m in mid_avg]
        rho, p = spearmanr(expected, actual)
        if p > 0.05:
            failed_gradients += 1
    else:
        failed_gradients += 1

sample_failure_rate = failed_gradients / n_bootstrap
print(f"  Bootstrap: {failed_gradients}/{n_bootstrap} random samples of n={t_fl_count} "
      f"from Section S fail gradient test ({sample_failure_rate:.1%})")
print(f"  T's gradient failure: rho={t_profile.get('gradient_rho')}, p={t_profile.get('gradient_p')}")

# ============================================================
# Verdict
# ============================================================
t_n_middles = t_profile.get('fl_n_middles', 0)
t_fl_n = t_profile.get('fl_count', 0)

if sample_failure_rate > 0.20:
    verdict = "SAMPLE_SIZE_ARTIFACT"
    explanation = (f"T's gradient failure is explainable by small sample size: "
                   f"{sample_failure_rate:.1%} of random subsamples at n={t_fl_n} also fail")
elif t_n_middles < 10:
    verdict = "RESTRICTED_VOCABULARY"
    explanation = (f"T uses only {t_n_middles}/15 FL MIDDLEs — restricted vocabulary "
                   f"collapses gradient discrimination")
else:
    verdict = "GENUINE_ANOMALY"
    explanation = (f"T has sufficient sample ({t_fl_n} FL tokens, {t_n_middles} MIDDLEs) "
                   f"but gradient fails — genuine section-specific behavior")

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'section_profiles': section_profiles,
    'bootstrap_failure_rate': round(sample_failure_rate, 4),
    'bootstrap_n': n_bootstrap,
    'bootstrap_sample_size': t_fl_count,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "04_section_t_anomaly.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
