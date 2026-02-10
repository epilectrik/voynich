"""
49_kernel_contact_by_axis.py

Test whether the two FL grid axes (LOW and HIGH) interface with different
kernel operators: k (ENERGY_MODULATOR), h (PHASE_MANAGER), e (STABILITY_ANCHOR).

If the axes are functionally distinct, lines dominated by one axis should
show different kernel contact profiles from lines dominated by the other.

Method:
  1. Build FL grid coordinates (same pipeline as scripts 42-45)
  2. Extract CENTER tokens (non-FL tokens) per line
  3. Classify center tokens for kernel character content in their MIDDLEs
  4. Group lines by axis dominance (LOW_DOMINANT, HIGH_DOMINANT, BALANCED)
  5. Compare kernel profiles across groups
  6. Test kernel-axis correlations along each axis independently
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, kruskal, mannwhitneyu

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
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build data (identical pipeline to scripts 42-45)
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio}

# Fit GMMs
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# Assign coordinates and extract center token kernel profiles per line
line_coords = {}
line_kernel_data = {}  # per-line kernel bearing counts

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    center_count = 0
    k_count = 0
    h_count = 0
    e_count = 0

    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_info.append({'mode': mode, 'stage': stage})
        elif not is_fl and m and m.middle:
            # Center token with a parseable middle -- check for kernel chars
            center_count += 1
            if 'k' in m.middle:
                k_count += 1
            if 'h' in m.middle:
                h_count += 1
            if 'e' in m.middle:
                e_count += 1

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]

    line_coords[line_key] = {'lo': lo, 'ho': ho}

    if center_count >= 2:
        line_kernel_data[line_key] = {
            'center_count': center_count,
            'k_count': k_count,
            'h_count': h_count,
            'e_count': e_count,
            'k_rate': k_count / center_count,
            'h_rate': h_count / center_count,
            'e_rate': e_count / center_count,
        }

print(f"Lines with coordinates: {len(line_coords)}")
print(f"Lines with kernel data (2+ center tokens): {len(line_kernel_data)}")

# ============================================================
# Group lines by axis dominance
# ============================================================
print(f"\n{'='*70}")
print("GROUPING LINES BY AXIS DOMINANCE")
print("=" * 70)

groups = {
    'LOW_DOMINANT': [],    # lo > ho + 1
    'HIGH_DOMINANT': [],   # ho > lo + 1
    'BALANCED': [],        # |lo - ho| <= 1
    'HIGH_LO': [],         # lo >= 4
    'LOW_LO': [],          # lo <= 1
    'HIGH_HO': [],         # ho >= 4
    'LOW_HO': [],          # ho <= 1
}

for line_key in line_kernel_data:
    c = line_coords[line_key]
    lo, ho = c['lo'], c['ho']

    if lo > ho + 1:
        groups['LOW_DOMINANT'].append(line_key)
    elif ho > lo + 1:
        groups['HIGH_DOMINANT'].append(line_key)
    else:
        groups['BALANCED'].append(line_key)

    if lo >= 4:
        groups['HIGH_LO'].append(line_key)
    if lo <= 1:
        groups['LOW_LO'].append(line_key)
    if ho >= 4:
        groups['HIGH_HO'].append(line_key)
    if ho <= 1:
        groups['LOW_HO'].append(line_key)

for g_name, g_keys in groups.items():
    print(f"  {g_name:<16}: {len(g_keys):>4} lines")

# ============================================================
# 1. Kernel profile per group
# ============================================================
print(f"\n{'='*70}")
print("1. KERNEL CONTACT PROFILES BY AXIS DOMINANCE")
print("=" * 70)

group_profiles = {}
for g_name, g_keys in groups.items():
    if len(g_keys) < 5:
        continue
    k_rates = [line_kernel_data[k]['k_rate'] for k in g_keys]
    h_rates = [line_kernel_data[k]['h_rate'] for k in g_keys]
    e_rates = [line_kernel_data[k]['e_rate'] for k in g_keys]
    group_profiles[g_name] = {
        'n': len(g_keys),
        'k_mean': np.mean(k_rates),
        'h_mean': np.mean(h_rates),
        'e_mean': np.mean(e_rates),
        'k_rates': k_rates,
        'h_rates': h_rates,
        'e_rates': e_rates,
    }

print(f"\n  {'Group':<16} {'N':>5}   {'k_rate':>8} {'h_rate':>8} {'e_rate':>8}")
print(f"  {'-'*16} {'-'*5}   {'-'*8} {'-'*8} {'-'*8}")
for g_name in ['LOW_DOMINANT', 'HIGH_DOMINANT', 'BALANCED', 'HIGH_LO', 'LOW_LO', 'HIGH_HO', 'LOW_HO']:
    if g_name in group_profiles:
        gp = group_profiles[g_name]
        print(f"  {g_name:<16} {gp['n']:>5}   {gp['k_mean']*100:>7.1f}% {gp['h_mean']*100:>7.1f}% {gp['e_mean']*100:>7.1f}%")

# ============================================================
# 2. Mann-Whitney comparisons: LOW_DOMINANT vs HIGH_DOMINANT
# ============================================================
print(f"\n{'='*70}")
print("2. MANN-WHITNEY: LOW_DOMINANT vs HIGH_DOMINANT")
print("=" * 70)

mw_results = {}
if 'LOW_DOMINANT' in group_profiles and 'HIGH_DOMINANT' in group_profiles:
    lo_dom = group_profiles['LOW_DOMINANT']
    hi_dom = group_profiles['HIGH_DOMINANT']

    for kernel_char in ['k', 'h', 'e']:
        lo_vals = lo_dom[f'{kernel_char}_rates']
        hi_vals = hi_dom[f'{kernel_char}_rates']
        if len(lo_vals) >= 5 and len(hi_vals) >= 5:
            stat, p = mannwhitneyu(lo_vals, hi_vals, alternative='two-sided')
            mw_results[kernel_char] = {
                'lo_dom_mean': np.mean(lo_vals),
                'hi_dom_mean': np.mean(hi_vals),
                'U': float(stat),
                'p': float(p),
                'significant': bool(p < 0.05),
            }
            diff = np.mean(lo_vals) - np.mean(hi_vals)
            print(f"\n  {kernel_char}: LOW_DOM={np.mean(lo_vals)*100:.1f}%, "
                  f"HIGH_DOM={np.mean(hi_vals)*100:.1f}%, "
                  f"diff={diff*100:+.1f}pp, U={stat:.0f}, p={p:.4f} "
                  f"{'*' if p < 0.05 else ''}")
        else:
            mw_results[kernel_char] = {'p': 1.0, 'significant': False}
            print(f"\n  {kernel_char}: Insufficient data")
else:
    for kernel_char in ['k', 'h', 'e']:
        mw_results[kernel_char] = {'p': 1.0, 'significant': False}
    print("\n  Insufficient data for LOW_DOMINANT vs HIGH_DOMINANT comparison")

# ============================================================
# 3. Axis-specific kernel gradient
# ============================================================
print(f"\n{'='*70}")
print("3. AXIS-SPECIFIC KERNEL GRADIENTS")
print("=" * 70)

# For each value of lo (0-5), compute k_rate, h_rate, e_rate
print("\n  Kernel rates by LOW axis value:")
print(f"  {'lo':>4}  {'N':>5}  {'k_rate':>8}  {'h_rate':>8}  {'e_rate':>8}")

lo_values = defaultdict(lambda: {'k': [], 'h': [], 'e': []})
ho_values = defaultdict(lambda: {'k': [], 'h': [], 'e': []})

for line_key, kd in line_kernel_data.items():
    c = line_coords[line_key]
    lo_values[c['lo']]['k'].append(kd['k_rate'])
    lo_values[c['lo']]['h'].append(kd['h_rate'])
    lo_values[c['lo']]['e'].append(kd['e_rate'])
    ho_values[c['ho']]['k'].append(kd['k_rate'])
    ho_values[c['ho']]['h'].append(kd['h_rate'])
    ho_values[c['ho']]['e'].append(kd['e_rate'])

for lo in range(6):
    if lo in lo_values and lo_values[lo]['k']:
        n = len(lo_values[lo]['k'])
        k_m = np.mean(lo_values[lo]['k']) * 100
        h_m = np.mean(lo_values[lo]['h']) * 100
        e_m = np.mean(lo_values[lo]['e']) * 100
        print(f"  {lo:>4}  {n:>5}  {k_m:>7.1f}%  {h_m:>7.1f}%  {e_m:>7.1f}%")

print("\n  Kernel rates by HIGH axis value:")
print(f"  {'ho':>4}  {'N':>5}  {'k_rate':>8}  {'h_rate':>8}  {'e_rate':>8}")
for ho in range(6):
    if ho in ho_values and ho_values[ho]['k']:
        n = len(ho_values[ho]['k'])
        k_m = np.mean(ho_values[ho]['k']) * 100
        h_m = np.mean(ho_values[ho]['h']) * 100
        e_m = np.mean(ho_values[ho]['e']) * 100
        print(f"  {ho:>4}  {n:>5}  {k_m:>7.1f}%  {h_m:>7.1f}%  {e_m:>7.1f}%")

# Spearman correlations: kernel rate vs axis level
print(f"\n  Spearman correlations (kernel rate vs axis value, per line):")
print(f"  {'Kernel':>8}  {'rho_lo':>8}  {'p_lo':>8}  {'rho_ho':>8}  {'p_ho':>8}  {'|diff|':>8}")

all_lo_arr = np.array([line_coords[k]['lo'] for k in line_kernel_data])
all_ho_arr = np.array([line_coords[k]['ho'] for k in line_kernel_data])

spearman_results = {}
for kernel_char in ['k', 'h', 'e']:
    rates = np.array([line_kernel_data[k][f'{kernel_char}_rate'] for k in line_kernel_data])

    rho_lo, p_lo = spearmanr(all_lo_arr, rates)
    rho_ho, p_ho = spearmanr(all_ho_arr, rates)
    diff = abs(rho_lo - rho_ho)

    spearman_results[kernel_char] = {
        'rho_lo': float(rho_lo), 'p_lo': float(p_lo),
        'rho_ho': float(rho_ho), 'p_ho': float(p_ho),
        'rho_diff': float(diff),
    }

    print(f"  {kernel_char:>8}  {rho_lo:>+7.3f}  {p_lo:>8.4f}  {rho_ho:>+7.3f}  {p_ho:>8.4f}  {diff:>7.3f}")

# ============================================================
# 4. Kruskal-Wallis across axis values
# ============================================================
print(f"\n{'='*70}")
print("4. KRUSKAL-WALLIS: DO KERNEL PROFILES VARY ACROSS AXIS VALUES?")
print("=" * 70)

kw_results = {}
for kernel_char in ['k', 'h', 'e']:
    # Across lo values
    lo_groups = []
    lo_labels = []
    for lo in range(6):
        if lo in lo_values and len(lo_values[lo][kernel_char]) >= 5:
            lo_groups.append(np.array(lo_values[lo][kernel_char]))
            lo_labels.append(lo)
    if len(lo_groups) >= 2:
        kw_lo_stat, kw_lo_p = kruskal(*lo_groups)
    else:
        kw_lo_stat, kw_lo_p = 0.0, 1.0

    # Across ho values
    ho_groups = []
    ho_labels = []
    for ho in range(6):
        if ho in ho_values and len(ho_values[ho][kernel_char]) >= 5:
            ho_groups.append(np.array(ho_values[ho][kernel_char]))
            ho_labels.append(ho)
    if len(ho_groups) >= 2:
        kw_ho_stat, kw_ho_p = kruskal(*ho_groups)
    else:
        kw_ho_stat, kw_ho_p = 0.0, 1.0

    kw_results[kernel_char] = {
        'lo_H': float(kw_lo_stat), 'lo_p': float(kw_lo_p),
        'lo_n_groups': len(lo_groups),
        'ho_H': float(kw_ho_stat), 'ho_p': float(kw_ho_p),
        'ho_n_groups': len(ho_groups),
    }

    print(f"\n  {kernel_char}:")
    print(f"    Across LOW values:  H={kw_lo_stat:.2f}, p={kw_lo_p:.6f} ({len(lo_groups)} groups)")
    print(f"    Across HIGH values: H={kw_ho_stat:.2f}, p={kw_ho_p:.6f} ({len(ho_groups)} groups)")

# ============================================================
# 5. CHECKS AND VERDICT
# ============================================================
print(f"\n{'='*70}")
print("5. CHECKS AND VERDICT")
print("=" * 70)

# check_1: At least one kernel char has significantly different rates
#          between LOW_DOMINANT and HIGH_DOMINANT (Mann-Whitney p < 0.05)
check_1 = bool(any(mw_results[kc]['significant'] for kc in ['k', 'h', 'e']))

# check_2: At least one kernel char has stronger correlation with one axis
#          than the other (|rho_lo - rho_ho| > 0.15)
check_2 = bool(any(spearman_results[kc]['rho_diff'] > 0.15 for kc in ['k', 'h', 'e']))

# check_3: Kernel profiles are not identical across axis values
#          (Kruskal-Wallis p < 0.05 for at least one kernel char across lo
#          values AND across ho values)
kw_lo_any_sig = any(kw_results[kc]['lo_p'] < 0.05 for kc in ['k', 'h', 'e'])
kw_ho_any_sig = any(kw_results[kc]['ho_p'] < 0.05 for kc in ['k', 'h', 'e'])
check_3 = bool(kw_lo_any_sig and kw_ho_any_sig)

n_pass = sum([check_1, check_2, check_3])

print(f"\n  check_1 (MW: LOW_DOM vs HIGH_DOM, p<0.05):   {'PASS' if check_1 else 'FAIL'}")
for kc in ['k', 'h', 'e']:
    if mw_results[kc].get('lo_dom_mean') is not None:
        print(f"    {kc}: p={mw_results[kc]['p']:.4f} {'*' if mw_results[kc]['significant'] else ''}")

print(f"\n  check_2 (Spearman |rho_lo - rho_ho| > 0.15): {'PASS' if check_2 else 'FAIL'}")
for kc in ['k', 'h', 'e']:
    print(f"    {kc}: |diff| = {spearman_results[kc]['rho_diff']:.3f} "
          f"{'*' if spearman_results[kc]['rho_diff'] > 0.15 else ''}")

print(f"\n  check_3 (KW p<0.05 along BOTH axes):         {'PASS' if check_3 else 'FAIL'}")
print(f"    Along LOW:  {kw_lo_any_sig}")
print(f"    Along HIGH: {kw_ho_any_sig}")
for kc in ['k', 'h', 'e']:
    print(f"    {kc}: lo_p={kw_results[kc]['lo_p']:.4f}, ho_p={kw_results[kc]['ho_p']:.4f}")

print(f"\n  Checks passed: {n_pass}/3")

if n_pass >= 2:
    verdict = "AXES_DISTINCT"
    expl = ("The two FL grid axes interface with different kernel operator "
            "profiles. This supports functional distinction of the LOW and "
            "HIGH axes.")
elif n_pass == 1:
    verdict = "WEAK_DISTINCTION"
    expl = ("Some evidence for axis-specific kernel contact, but not enough "
            "for confident distinction. One check passed out of three.")
else:
    verdict = "AXES_IDENTICAL"
    expl = ("No evidence that the two FL grid axes have different kernel "
            "contact profiles. The axes appear functionally equivalent "
            "with respect to kernel operators.")

print(f"\n  VERDICT: {verdict}")
print(f"  {expl}")

# ============================================================
# Write results
# ============================================================
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

results = {
    'n_lines_coordinated': len(line_coords),
    'n_lines_with_kernel_data': len(line_kernel_data),
    'group_sizes': {g: len(keys) for g, keys in groups.items()},
    'group_profiles': {
        g: {
            'n': gp['n'],
            'k_mean': round(gp['k_mean'], 4),
            'h_mean': round(gp['h_mean'], 4),
            'e_mean': round(gp['e_mean'], 4),
        }
        for g, gp in group_profiles.items()
    },
    'mann_whitney_lo_vs_hi_dominant': {
        kc: {
            'lo_dom_mean': round(mw_results[kc].get('lo_dom_mean', 0), 4),
            'hi_dom_mean': round(mw_results[kc].get('hi_dom_mean', 0), 4),
            'U': round(mw_results[kc].get('U', 0), 1),
            'p': round(mw_results[kc]['p'], 6),
            'significant': mw_results[kc]['significant'],
        }
        for kc in ['k', 'h', 'e']
    },
    'spearman_correlations': {
        kc: {
            'rho_lo': round(spearman_results[kc]['rho_lo'], 4),
            'p_lo': round(spearman_results[kc]['p_lo'], 6),
            'rho_ho': round(spearman_results[kc]['rho_ho'], 4),
            'p_ho': round(spearman_results[kc]['p_ho'], 6),
            'rho_diff': round(spearman_results[kc]['rho_diff'], 4),
        }
        for kc in ['k', 'h', 'e']
    },
    'kruskal_wallis': {
        kc: {
            'lo_H': round(kw_results[kc]['lo_H'], 2),
            'lo_p': round(kw_results[kc]['lo_p'], 6),
            'lo_n_groups': kw_results[kc]['lo_n_groups'],
            'ho_H': round(kw_results[kc]['ho_H'], 2),
            'ho_p': round(kw_results[kc]['ho_p'], 6),
            'ho_n_groups': kw_results[kc]['ho_n_groups'],
        }
        for kc in ['k', 'h', 'e']
    },
    'checks': {
        'check_1_mw_significant': bool(check_1),
        'check_2_rho_diff_gt_015': bool(check_2),
        'check_3_kw_both_axes': bool(check_3),
    },
    'n_checks_passed': n_pass,
    'verdict': verdict,
    'explanation': expl,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '49_kernel_contact_by_axis.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
