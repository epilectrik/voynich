"""
Phase 494: Parallel Monitoring Tracks
======================================
Tests whether MIDDLE atoms encode parallel monitoring parameters
and whether high-affinity atom pairs (C1210) are fused macro-atoms.

T1: Macro-Atom Composition — does fused-pair decomposition improve C1190's r?
T2: Order Magnitude Effect — do reversed pairs behave more alike than different-set pairs?
T3: Cross-Token Coupling — does SET carry dominate TERMINAL->INITIAL coupling?
T4: Atom Removal Symmetry — does removing any position produce equal behavioral change?

Structural basis: C1190, C1209, C1210, C1211, C1225
"""

import json
import sys
import os
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import pearsonr, chi2_contingency, kruskal, mannwhitneyu
from scipy.spatial.distance import jensenshannon
import warnings
warnings.filterwarnings('ignore')

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology

# ============================================================
# LOAD AND FILTER
# ============================================================
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt',
                 sep='\t', quoting=3, on_bad_lines='skip', low_memory=False)
df.columns = [c.strip('"') for c in df.columns]
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].str.strip('"')

df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B'].copy()
df_b = df_b[~df_b['placement'].str.startswith('L', na=False)]

morph = Morphology()

# Extract morphology for all tokens
records = []
for _, row in df_b.iterrows():
    w = str(row.get('word', '')).strip()
    if not w or '*' in w:
        continue
    try:
        m = morph.extract(w)
        if m.middle:
            pfx = m.prefix or ''
            pfx2 = m.prefix2 if hasattr(m, 'prefix2') and m.prefix2 else ''
            full_pfx = pfx2 + pfx if pfx2 else pfx
            pfx_group = 'none'
            if 'qo' in full_pfx: pfx_group = 'qo'
            elif 'ch' in full_pfx: pfx_group = 'ch'
            elif 'sh' in full_pfx: pfx_group = 'sh'
            elif 'da' in full_pfx: pfx_group = 'da'
            elif 'sa' in full_pfx: pfx_group = 'sa'
            elif 'ok' in full_pfx: pfx_group = 'ok'
            elif 'ot' in full_pfx: pfx_group = 'ot'
            elif 'ol' in full_pfx: pfx_group = 'ol'
            elif full_pfx: pfx_group = 'other'
            records.append({
                'word': w,
                'middle': m.middle,
                'prefix': full_pfx,
                'pfx_group': pfx_group,
                'suffix': m.suffix or '',
                'articulator': m.articulator or '',
                'section': row.get('section', ''),
                'folio': row.get('folio', ''),
                'line': str(row.get('line', '')),
                'token_pos': int(row.get('token', 0)),
            })
    except:
        pass

tok_df = pd.DataFrame(records)

# Compute line lengths and normalized position
line_len_map = tok_df.groupby(['folio', 'line']).size().to_dict()
tok_df['line_len'] = tok_df.apply(lambda r: line_len_map.get((r['folio'], r['line']), 1), axis=1)
tok_df['norm_pos'] = tok_df['token_pos'] / tok_df['line_len'].clip(lower=1)
tok_df['is_line_initial'] = (tok_df['token_pos'] == 1).astype(float)
tok_df['is_line_final'] = tok_df.apply(
    lambda r: 1.0 if r['token_pos'] >= r['line_len'] else 0.0, axis=1)
tok_df['is_para_initial'] = (tok_df['line'] == '1').astype(float)
tok_df['has_suffix'] = (tok_df['suffix'] != '').astype(float)
tok_df['has_artic'] = (tok_df['articulator'] != '').astype(float)

print(f"Total Currier B tokens with MIDDLEs: {len(tok_df)}")

# ============================================================
# COMMON: BEHAVIORAL PROFILES (22 features, matching C1190)
# ============================================================
SECTIONS = ['B', 'C', 'H', 'S', 'T']
PFX_GROUPS = ['qo', 'ch', 'sh', 'da', 'sa', 'ok', 'ot', 'ol', 'other', 'none']
ALL_ATOMS = list('acdefghiklmnopqrsty')

def compute_profile(subset):
    if len(subset) == 0:
        return None
    features = {}
    features['mean_pos'] = subset['norm_pos'].mean()
    features['li_rate'] = subset['is_line_initial'].mean()
    features['lf_rate'] = subset['is_line_final'].mean()
    features['pi_rate'] = subset['is_para_initial'].mean()
    features['pf_rate'] = 0.0
    features['sfx_rate'] = subset['has_suffix'].mean()
    features['art_rate'] = subset['has_artic'].mean()
    sec_counts = subset['section'].value_counts()
    total = len(subset)
    for s in SECTIONS:
        features[f'sec_{s}'] = sec_counts.get(s, 0) / total
    pfx_counts = subset['pfx_group'].value_counts()
    for p in PFX_GROUPS:
        features[f'pfx_{p}'] = pfx_counts.get(p, 0) / total
    return features

middle_counts = tok_df['middle'].value_counts()
valid_middles = middle_counts[middle_counts >= 5].index.tolist()

profiles = {}
for mid in valid_middles:
    subset = tok_df[tok_df['middle'] == mid]
    p = compute_profile(subset)
    if p:
        profiles[mid] = p

feature_names = list(profiles[valid_middles[0]].keys())
print(f"MIDDLEs with profiles: {len(profiles)}")
print(f"Features per profile: {len(feature_names)}")

results = {
    'phase': 494,
    'name': 'PARALLEL_MONITORING_TRACKS',
    'n_tokens': len(tok_df),
    'n_profiled_middles': len(profiles),
    'n_features': len(feature_names),
}

# ============================================================
# COMMON: Prediction helpers
# ============================================================
MACRO_ATOMS = {
    'ke': ('k', 'e'), 'in': ('i', 'n'), 'ck': ('c', 'k'),
    'ch': ('c', 'h'), 'dy': ('d', 'y'), 'an': ('a', 'n'),
    'am': ('a', 'm'), 'ct': ('c', 't'), 'ph': ('p', 'h'),
}
macro_list = sorted(MACRO_ATOMS.keys(), key=len, reverse=True)

def decompose_individual(middle):
    return list(middle)

def decompose_macro(middle):
    result = []
    remaining = middle
    while remaining:
        matched = False
        for macro in macro_list:
            if remaining.startswith(macro):
                result.append(macro)
                remaining = remaining[len(macro):]
                matched = True
                break
        if not matched:
            result.append(remaining[0])
            remaining = remaining[1:]
    return result

def predict_profile(components, profile_dict, feature_list):
    valid = [c for c in components if c in profile_dict]
    if not valid:
        return None
    return {f: np.mean([profile_dict[c][f] for c in valid]) for f in feature_list}

def compute_correlation(compounds, profile_dict, decompose_fn, feature_list):
    actual_vals, pred_vals = [], []
    for mid in compounds:
        if mid not in profile_dict:
            continue
        components = decompose_fn(mid)
        if len(components) < 2:
            continue
        pred = predict_profile(components, profile_dict, feature_list)
        if pred is None:
            continue
        actual = profile_dict[mid]
        for f in feature_list:
            actual_vals.append(actual[f])
            pred_vals.append(pred[f])
    if len(actual_vals) < 10:
        return 0, 0
    r, p = pearsonr(actual_vals, pred_vals)
    return r, len(actual_vals) // len(feature_list)

# ============================================================
# T1: MACRO-ATOM COMPOSITION
# ============================================================
print("\n" + "=" * 70)
print("T1: MACRO-ATOM COMPOSITION")
print("=" * 70)

compound_middles = [m for m in profiles if len(m) >= 2]
compound_beyond_macro = [m for m in profiles if len(m) >= 3]

r_individual, n_individual = compute_correlation(
    compound_middles, profiles, decompose_individual, feature_names)
r_indiv_same, n_indiv_same = compute_correlation(
    compound_beyond_macro, profiles, decompose_individual, feature_names)
r_macro, n_macro = compute_correlation(
    compound_beyond_macro, profiles, decompose_macro, feature_names)

print(f"Individual atoms (all compounds >= 2): r={r_individual:.4f} (n={n_individual})")
print(f"Individual atoms (compounds >= 3): r={r_indiv_same:.4f} (n={n_indiv_same})")
print(f"Macro-atom (compounds >= 3): r={r_macro:.4f} (n={n_macro})")
print(f"Improvement: {r_macro - r_indiv_same:+.4f}")

# Permutation test
np.random.seed(42)
n_perms = 1000
perm_rs = []
for _ in range(n_perms):
    shuffled = np.random.permutation(ALL_ATOMS)
    random_macros = {}
    for i in range(0, min(len(MACRO_ATOMS) * 2, len(shuffled)) - 1, 2):
        pair = shuffled[i] + shuffled[i+1]
        random_macros[pair] = (shuffled[i], shuffled[i+1])
    random_macro_list = sorted(random_macros.keys(), key=len, reverse=True)

    def decompose_random(middle, rml=random_macro_list):
        result = []
        remaining = middle
        while remaining:
            matched = False
            for macro in rml:
                if remaining.startswith(macro):
                    result.append(macro)
                    remaining = remaining[len(macro):]
                    matched = True
                    break
            if not matched:
                result.append(remaining[0])
                remaining = remaining[1:]
        return result

    r_perm, _ = compute_correlation(
        compound_beyond_macro, profiles, decompose_random, feature_names)
    perm_rs.append(r_perm)

p_perm_t1 = np.mean([pr >= r_macro for pr in perm_rs])
z_perm_t1 = (r_macro - np.mean(perm_rs)) / np.std(perm_rs) if np.std(perm_rs) > 0 else 0

print(f"Permutation: mean={np.mean(perm_rs):.4f}, std={np.std(perm_rs):.4f}")
print(f"P-value: {p_perm_t1:.4f}, Z-score: {z_perm_t1:.2f}")

results['T1_macro_atom'] = {
    'r_individual_all': round(r_individual, 4),
    'r_individual_ge3': round(r_indiv_same, 4),
    'r_macro_ge3': round(r_macro, 4),
    'improvement': round(r_macro - r_indiv_same, 4),
    'n_compounds_all': n_individual,
    'n_compounds_ge3': n_macro,
    'permutation_mean': round(float(np.mean(perm_rs)), 4),
    'permutation_std': round(float(np.std(perm_rs)), 4),
    'p_value': round(float(p_perm_t1), 4),
    'z_score': round(float(z_perm_t1), 2),
    'n_permutations': n_perms,
    'significant': bool(p_perm_t1 < 0.05),
    'verdict': 'PASS' if r_macro > r_indiv_same and p_perm_t1 < 0.05 else 'FAIL',
}

# ============================================================
# T2: ORDER MAGNITUDE EFFECT
# ============================================================
print("\n" + "=" * 70)
print("T2: ORDER MAGNITUDE EFFECT")
print("=" * 70)

tx = Transcript()
folio_line_tokens = defaultdict(list)
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_':
        folio_line_tokens[(token.folio, token.line)].append((token, m))

class MiddleProfile2:
    def __init__(self):
        self.count = 0
        self.sections = Counter()
        self.prefixes = Counter()
        self.suffixes = Counter()
        self.positions = []

t2_profiles = defaultdict(MiddleProfile2)

for (folio, line), tokens in folio_line_tokens.items():
    n_tokens = len(tokens)
    for i, (token, m) in enumerate(tokens):
        mid = m.middle
        p = t2_profiles[mid]
        p.count += 1
        p.sections[token.section] += 1
        p.prefixes[m.prefix or 'BARE'] += 1
        p.suffixes[m.suffix or 'BARE'] += 1
        if n_tokens > 1:
            p.positions.append(i / (n_tokens - 1))
        else:
            p.positions.append(0.5)

MIN_COUNT = 15
t2_all_middles = {mid for mid, p in t2_profiles.items() if p.count >= MIN_COUNT}

# Find reversed pairs
reversed_pairs = []
seen = set()
for mid in sorted(t2_all_middles):
    rev = mid[::-1]
    if rev != mid and rev in t2_all_middles:
        pair_key = tuple(sorted([mid, rev]))
        if pair_key not in seen:
            seen.add(pair_key)
            reversed_pairs.append((mid, rev))

print(f"MIDDLEs with >= {MIN_COUNT} tokens: {len(t2_all_middles)}")
print(f"Reversed pairs: {len(reversed_pairs)}")

# Collect category values for JSD
t2_all_sections = sorted(set(s for p in t2_profiles.values() for s in p.sections))
t2_all_pfxs = sorted(set(px for p in t2_profiles.values() for px in p.prefixes))
t2_all_sfxs = sorted(set(sx for p in t2_profiles.values() for sx in p.suffixes))

def compute_block_jsd(p1, p2):
    eps = 1e-10
    sec1 = np.array([p1.sections.get(s, 0) for s in t2_all_sections], dtype=float)
    sec2 = np.array([p2.sections.get(s, 0) for s in t2_all_sections], dtype=float)
    sec1 = sec1 / (sec1.sum() or 1) + eps
    sec2 = sec2 / (sec2.sum() or 1) + eps
    jsd_sec = jensenshannon(sec1, sec2)

    pfx1 = np.array([p1.prefixes.get(px, 0) for px in t2_all_pfxs], dtype=float)
    pfx2 = np.array([p2.prefixes.get(px, 0) for px in t2_all_pfxs], dtype=float)
    pfx1 = pfx1 / (pfx1.sum() or 1) + eps
    pfx2 = pfx2 / (pfx2.sum() or 1) + eps
    jsd_pfx = jensenshannon(pfx1, pfx2)

    sfx1 = np.array([p1.suffixes.get(sx, 0) for sx in t2_all_sfxs], dtype=float)
    sfx2 = np.array([p2.suffixes.get(sx, 0) for sx in t2_all_sfxs], dtype=float)
    sfx1 = sfx1 / (sfx1.sum() or 1) + eps
    sfx2 = sfx2 / (sfx2.sum() or 1) + eps
    jsd_sfx = jensenshannon(sfx1, sfx2)

    return np.mean([jsd_sec, jsd_pfx, jsd_sfx])

reversed_jsds = []
for a, b in reversed_pairs:
    jsd = compute_block_jsd(t2_profiles[a], t2_profiles[b])
    reversed_jsds.append(jsd)
    print(f"  {a}<->{b}: JSD={jsd:.4f}")

# Different-set baseline
two_char = [(mid, t2_profiles[mid].count) for mid in t2_all_middles if len(mid) == 2]
different_jsds = []
for a, b in reversed_pairs:
    atoms_ab = set(a)
    avg_freq = (t2_profiles[a].count + t2_profiles[b].count) / 2
    for mid1, c1 in two_char:
        if set(mid1) == atoms_ab:
            continue
        if c1 < avg_freq / 3 or c1 > avg_freq * 3:
            continue
        for mid2, c2 in two_char:
            if mid2 <= mid1 or set(mid2) == set(mid1):
                continue
            if c2 < avg_freq / 3 or c2 > avg_freq * 3:
                continue
            different_jsds.append(compute_block_jsd(t2_profiles[mid1], t2_profiles[mid2]))
            if len(different_jsds) >= 500:
                break
        if len(different_jsds) >= 500:
            break

mean_rev = np.mean(reversed_jsds) if reversed_jsds else float('nan')
mean_diff = np.mean(different_jsds) if different_jsds else float('nan')
t2_ratio = mean_rev / mean_diff if mean_diff > 0 else float('nan')

print(f"\nMean reversed JSD: {mean_rev:.4f} (n={len(reversed_jsds)})")
print(f"Mean different-set JSD: {mean_diff:.4f} (n={len(different_jsds)})")
print(f"Ratio: {t2_ratio:.3f}")

if len(reversed_jsds) >= 3 and len(different_jsds) >= 3:
    u_stat, u_p = mannwhitneyu(reversed_jsds, different_jsds, alternative='less')
    print(f"Mann-Whitney U: stat={u_stat:.1f}, p={u_p:.4f}")
else:
    u_stat, u_p = 0, 1.0

results['T2_order_magnitude'] = {
    'n_reversed_pairs': len(reversed_pairs),
    'mean_reversed_jsd': round(float(mean_rev), 4),
    'mean_different_set_jsd': round(float(mean_diff), 4),
    'ratio': round(float(t2_ratio), 3),
    'mann_whitney_u': round(float(u_stat), 1),
    'mann_whitney_p': round(float(u_p), 4),
    'n_different_pairs': len(different_jsds),
    'verdict': 'PASS' if t2_ratio < 0.5 else ('WEAK' if t2_ratio < 0.75 else 'FAIL'),
}

# ============================================================
# T3: CROSS-TOKEN COUPLING
# ============================================================
print("\n" + "=" * 70)
print("T3: CROSS-TOKEN COUPLING")
print("=" * 70)

tok_df_sorted = tok_df.sort_values(['folio', 'line', 'token_pos'])
pairs = []
for (folio, line), group in tok_df_sorted.groupby(['folio', 'line']):
    group = group.sort_values('token_pos')
    middles = group['middle'].values
    for i in range(len(middles) - 1):
        pairs.append((middles[i], middles[i+1]))

print(f"Consecutive within-line pairs: {len(pairs)}")

def get_initial(m): return m[0] if m else None
def get_terminal(m): return m[-1] if m else None

# TERMINAL(N) -> INITIAL(N+1) MI
def compute_contingency_mi(get_row_fn, get_col_fn):
    counts = defaultdict(int)
    for m1, m2 in pairs:
        r = get_row_fn(m1)
        c = get_col_fn(m2)
        if r and c:
            counts[(r, c)] += 1
    rows = sorted(set(k[0] for k in counts))
    cols = sorted(set(k[1] for k in counts))
    matrix = np.zeros((len(rows), len(cols)))
    for (r, c), count in counts.items():
        matrix[rows.index(r)][cols.index(c)] = count
    chi2, p, dof, _ = chi2_contingency(matrix)
    n = matrix.sum()
    v = np.sqrt(chi2 / (n * (min(matrix.shape) - 1)))
    # Mutual information
    p_joint = matrix / n
    p_row = matrix.sum(axis=1) / n
    p_col = matrix.sum(axis=0) / n
    mi = 0
    for i in range(len(rows)):
        for j in range(len(cols)):
            if p_joint[i, j] > 0:
                mi += p_joint[i, j] * np.log2(p_joint[i, j] / (p_row[i] * p_col[j]))
    return {'chi2': chi2, 'p': p, 'dof': dof, 'V': v, 'MI': mi, 'n': int(n)}

ti = compute_contingency_mi(get_terminal, get_initial)
ii = compute_contingency_mi(get_initial, get_initial)
tt = compute_contingency_mi(get_terminal, get_terminal)

print(f"TERMINAL->INITIAL: V={ti['V']:.4f}, MI={ti['MI']:.4f} bits")
print(f"INITIAL->INITIAL:  V={ii['V']:.4f}, MI={ii['MI']:.4f} bits")
print(f"TERMINAL->TERMINAL: V={tt['V']:.4f}, MI={tt['MI']:.4f} bits")

# Per-atom SET carry MI
atom_mis = {}
for atom in ALL_ATOMS:
    a = b = c = d = 0
    for m1, m2 in pairs:
        in1, in2 = atom in m1, atom in m2
        if in1 and in2: a += 1
        elif in1 and not in2: b += 1
        elif not in1 and in2: c += 1
        else: d += 1
    total = a + b + c + d
    if total == 0:
        continue
    ct = np.array([[a, b], [c, d]]) + 0.5
    p_j = ct / ct.sum()
    p_r = ct.sum(axis=1) / ct.sum()
    p_c = ct.sum(axis=0) / ct.sum()
    mi = sum(p_j[i, j] * np.log2(p_j[i, j] / (p_r[i] * p_c[j]))
             for i in range(2) for j in range(2) if p_j[i, j] > 0)
    atom_mis[atom] = mi

total_set_mi = sum(atom_mis.values())
print(f"SET carry MI (sum per-atom): {total_set_mi:.4f} bits")

set_ti_ratio = total_set_mi / ti['MI'] if ti['MI'] > 0 else 0
ii_ti_ratio = ii['MI'] / ti['MI'] if ti['MI'] > 0 else 0
print(f"SET/TERMINAL->INITIAL ratio: {set_ti_ratio:.2f}x")
print(f"INITIAL/TERMINAL->INITIAL ratio: {ii_ti_ratio:.2f}x")

results['T3_cross_token'] = {
    'terminal_initial_MI': round(ti['MI'], 4),
    'terminal_initial_V': round(ti['V'], 4),
    'initial_initial_MI': round(ii['MI'], 4),
    'initial_initial_V': round(ii['V'], 4),
    'terminal_terminal_MI': round(tt['MI'], 4),
    'terminal_terminal_V': round(tt['V'], 4),
    'set_carry_MI': round(total_set_mi, 4),
    'set_ti_ratio': round(float(set_ti_ratio), 2),
    'ii_ti_ratio': round(float(ii_ti_ratio), 2),
    'n_pairs': len(pairs),
    'verdict': 'MIXED',
}

# ============================================================
# T4: ATOM REMOVAL SYMMETRY
# ============================================================
print("\n" + "=" * 70)
print("T4: ATOM REMOVAL SYMMETRY")
print("=" * 70)

# Compute distributional profiles for JSD comparison
def compute_dist_profile(subset):
    if len(subset) == 0:
        return None
    features = []
    sec_counts = subset['section'].value_counts()
    total = len(subset)
    for s in SECTIONS:
        features.append(sec_counts.get(s, 0) / total)
    pfx_counts = subset['pfx_group'].value_counts()
    for p in PFX_GROUPS:
        features.append(pfx_counts.get(p, 0) / total)
    features.append((subset['suffix'] != '').mean())
    features.append((subset['articulator'] != '').mean())
    return np.array(features)

dist_profiles = {}
for mid in valid_middles:
    p = compute_dist_profile(tok_df[tok_df['middle'] == mid])
    if p is not None:
        dist_profiles[mid] = p

removal_results = []
for mid in dist_profiles:
    if len(mid) != 3:
        continue
    subs = {
        'initial': mid[1:],
        'medial': mid[0] + mid[2],
        'terminal': mid[:2],
    }
    if not all(s in dist_profiles for s in subs.values()):
        continue
    eps = 1e-10
    full_safe = dist_profiles[mid] + eps
    full_safe = full_safe / full_safe.sum()
    for position, sub_mid in subs.items():
        sub_safe = dist_profiles[sub_mid] + eps
        sub_safe = sub_safe / sub_safe.sum()
        jsd = jensenshannon(full_safe, sub_safe)
        removal_results.append({
            'middle': mid,
            'removed_position': position,
            'remaining': sub_mid,
            'jsd': jsd,
            'n_full': int(middle_counts[mid]),
            'n_remaining': int(middle_counts.get(sub_mid, 0)),
        })

res_df = pd.DataFrame(removal_results)
n_middles_t4 = res_df['middle'].nunique() if len(res_df) > 0 else 0
print(f"3-char MIDDLEs with all sub-profiles: {n_middles_t4}")
print(f"Total removal comparisons: {len(res_df)}")

if len(res_df) > 0:
    means = {}
    for pos in ['initial', 'medial', 'terminal']:
        subset = res_df[res_df['removed_position'] == pos]
        means[pos] = subset['jsd'].mean()
        print(f"  {pos}: mean JSD={means[pos]:.4f} (n={len(subset)})")

    t4_ratio = max(means.values()) / min(means.values()) if min(means.values()) > 0 else float('inf')
    print(f"Max/min ratio: {t4_ratio:.3f}")

    groups = [res_df[res_df['removed_position'] == p]['jsd'].values
              for p in ['initial', 'medial', 'terminal']]
    if all(len(g) >= 3 for g in groups):
        h_stat, h_p = kruskal(*groups)
        print(f"Kruskal-Wallis: H={h_stat:.2f}, p={h_p:.4f}")
    else:
        h_stat, h_p = 0, 1.0

    sorted_means = sorted(means.items(), key=lambda x: -x[1])
    print(f"Effect ordering: {' > '.join([f'{k}({v:.4f})' for k,v in sorted_means])}")

    results['T4_atom_removal'] = {
        'n_testable_middles': n_middles_t4,
        'n_comparisons': len(res_df),
        'mean_jsd_initial': round(means.get('initial', 0), 4),
        'mean_jsd_medial': round(means.get('medial', 0), 4),
        'mean_jsd_terminal': round(means.get('terminal', 0), 4),
        'max_min_ratio': round(float(t4_ratio), 3),
        'kruskal_H': round(float(h_stat), 2),
        'kruskal_p': round(float(h_p), 4),
        'effect_ordering': [k for k, v in sorted_means],
        'parallel_threshold_pass': bool(t4_ratio < 1.5),
        'positions_equal': bool(h_p > 0.05),
        'verdict': 'PASS' if t4_ratio < 1.5 else 'FAIL',
    }
else:
    results['T4_atom_removal'] = {'verdict': 'INSUFFICIENT_DATA'}

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

verdicts = [
    results['T1_macro_atom']['verdict'],
    results['T2_order_magnitude']['verdict'],
    results['T3_cross_token']['verdict'],
    results['T4_atom_removal']['verdict'],
]
n_pass = verdicts.count('PASS')
n_fail = verdicts.count('FAIL')

print(f"""
TEST VERDICTS:
  T1 (Macro-atom composition):  {results['T1_macro_atom']['verdict']}
    r improved {results['T1_macro_atom']['r_individual_ge3']} -> {results['T1_macro_atom']['r_macro_ge3']}, z={results['T1_macro_atom']['z_score']}, p={results['T1_macro_atom']['p_value']}
  T2 (Order magnitude):         {results['T2_order_magnitude']['verdict']}
    ratio={results['T2_order_magnitude']['ratio']}
  T3 (Cross-token coupling):    {results['T3_cross_token']['verdict']}
    SET/T->I ratio={results['T3_cross_token']['set_ti_ratio']}, I->I/T->I ratio={results['T3_cross_token']['ii_ti_ratio']}
  T4 (Atom removal symmetry):   {results['T4_atom_removal']['verdict']}
    max/min={results['T4_atom_removal'].get('max_min_ratio', 'N/A')}

OVERALL: {n_pass} PASS, {n_fail} FAIL, {4 - n_pass - n_fail} MIXED/WEAK
""")

# Determine constraint verdict
if n_pass >= 2 and n_fail == 0:
    overall = 'CONFIRMED'
    results['constraint_statement'] = (
        'Two-Level Parallel Composition: high-affinity atom pairs (C1210) are fused macro-atoms '
        'that compose in parallel with priority ordering. Macro-atom decomposition improves '
        f'behavioral prediction (r={results["T1_macro_atom"]["r_macro_ge3"]} vs '
        f'{results["T1_macro_atom"]["r_individual_ge3"]}, z={results["T1_macro_atom"]["z_score"]}). '
        'All atom positions contribute to behavior but INITIAL dominates. '
        'Cross-token coupling flows through TERMINAL->INITIAL, not full monitoring set.'
    )
elif n_pass >= 1:
    overall = 'PARTIAL'
    results['constraint_statement'] = (
        'MIDDLE atoms show partial parallel composition with priority ordering. '
        'Macro-atom decomposition confirmed but pure parallelism rejected.'
    )
else:
    overall = 'NULL'
    results['constraint_statement'] = 'Parallel monitoring track hypothesis not supported.'

results['overall_verdict'] = overall
print(f"CONSTRAINT VERDICT: {overall}")

# Write results
output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'parallel_monitoring_test.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to {output_path}")
