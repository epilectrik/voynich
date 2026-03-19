"""
Phase 608: SUBROUTINE_REPERTOIRE_CHARACTERIZATION

Tests whether folio-level paragraph zone co-occurrence structure is:
- A genuine combinatorial constraint (hard exclusions)
- Independently informative beyond PREFIX + section + paragraph_count
- Structured but PREFIX-mediated
- Weak / not surviving section controls

5 tests:
  T1: Pairwise zone co-occurrence (global + section-stratified nulls)
  T2: Repertoire typology (binary signatures, entropy)
  T3: Nested model comparison (feature ~ prefix+section+parcount vs +repertoire)
  T4: Section x repertoire (descriptive)
  T5: Mono-type characterization
"""

import json
import os
import hashlib
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
from scipy import stats
from pathlib import Path

# ---------- paths ----------
BASE = Path(__file__).resolve().parents[3]
RESULTS_DIR = BASE / 'phases' / 'SUBROUTINE_REPERTOIRE_CHARACTERIZATION' / 'results'
PRED_PATH = BASE / 'phases' / 'SUBROUTINE_REPERTOIRE_CHARACTERIZATION' / 'PREDICTIONS.md'

ZONE_NAMES = {
    0: "THERMAL-QO",
    1: "CONTAINMENT-Sealing",
    2: "OPERATION-Iteration",
    3: "MONITORING-Phase"
}
ZONE_SHORT = {0: "TQ", 1: "CS", 2: "OI", 3: "MP"}
N_ZONES = 4
N_PERM_COOCCUR = 10000
N_PERM_T3 = 1000

rng = np.random.default_rng(608)


def convert_numpy(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_numpy(v) for v in obj]
    return obj


# ==================== DATA LOADING ====================

print("=== Phase 608: SUBROUTINE_REPERTOIRE_CHARACTERIZATION ===\n")

# Verify predictions hash
pred_hash = hashlib.sha256(PRED_PATH.read_bytes()).hexdigest()
print(f"PREDICTIONS.md SHA-256: {pred_hash}")

# 1. Paragraph zone assignments (C1398)
with open(BASE / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json') as f:
    p510 = json.load(f)
labels = p510['paragraph_labels']  # 264 entries
print(f"Loaded {len(labels)} paragraph labels")

# Build per-folio data
folio_zones = defaultdict(list)  # folio -> [cluster_ids]
folio_section = {}
for entry in labels:
    folio_zones[entry['folio']].append(entry['cluster'])
    folio_section[entry['folio']] = entry['section']

# 2. Folio operational profiles
with open(BASE / 'results' / 'folio_operational_profiles.json') as f:
    op_raw = json.load(f)
op_profiles = {p['folio']: p for p in op_raw['profiles']}

# 3. T0 covariates (strong_close_fraction)
with open(BASE / 'phases' / 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES' / 'results' / 't0_opportunity_normalization.json') as f:
    t0_data = json.load(f)
t0_cov = t0_data['covariates']

# 4. Scaffold features
with open(BASE / 'results' / 'b_macro_scaffold_audit.json') as f:
    scaffold = json.load(f)
scaf_feat = scaffold['features']

# 5. Compute PREFIX fractions per folio from transcript
print("Computing PREFIX fractions from transcript...")
import sys
sys.path.insert(0, str(BASE))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

folio_prefix_data = defaultdict(lambda: {'total': 0, 'qo': 0, 'chsh': 0, 'bare': 0})
for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    if token.placement.startswith('L'):
        continue
    m = morph.extract(token.word)
    fpd = folio_prefix_data[token.folio]
    fpd['total'] += 1
    pfx = m.prefix
    if pfx is None:
        fpd['bare'] += 1
    elif pfx in ('qo', 'o'):
        fpd['qo'] += 1
    elif pfx in ('ch', 'sh', 'cth', 'ckh', 'cfh', 'cph'):
        fpd['chsh'] += 1
    # other prefixes not counted toward these 3 channels

folio_prefix_fracs = {}
for folio, pd in folio_prefix_data.items():
    t = pd['total']
    if t > 0:
        folio_prefix_fracs[folio] = {
            'qo_frac': pd['qo'] / t,
            'chsh_frac': pd['chsh'] / t,
            'bare_frac': pd['bare'] / t,
        }

print(f"PREFIX fractions computed for {len(folio_prefix_fracs)} folios")


# ==================== BUILD FOLIO OBJECTS ====================

# Binary zone signatures and zone count vectors
folio_data = {}
for folio, zones in folio_zones.items():
    zone_set = set(zones)
    zone_counts = Counter(zones)
    sig = ''.join('1' if i in zone_set else '0' for i in range(N_ZONES))
    breadth = len(zone_set)
    n_par = len(zones)
    dominant = max(zone_counts, key=zone_counts.get)

    folio_data[folio] = {
        'zones': zones,
        'zone_set': zone_set,
        'zone_counts': dict(zone_counts),
        'signature': sig,
        'breadth': breadth,
        'n_paragraphs': n_par,
        'dominant_zone': dominant,
        'section': folio_section.get(folio, '?'),
    }

all_folios = sorted(folio_data.keys())
multi_folios = [f for f in all_folios if folio_data[f]['n_paragraphs'] >= 2]
print(f"\nTotal folios: {len(all_folios)}, multi-paragraph: {len(multi_folios)}")


# ==================== T1: PAIRWISE CO-OCCURRENCE ====================

print("\n--- T1: Pairwise Zone Co-Occurrence ---")

zone_pairs = list(combinations(range(N_ZONES), 2))
pair_names = [f"{ZONE_SHORT[a]}-{ZONE_SHORT[b]}" for a, b in zone_pairs]


def compute_cooccurrence(folio_list):
    """Compute observed co-occurrence counts for 6 zone pairs."""
    counts = {}
    for a, b in zone_pairs:
        n = sum(1 for f in folio_list
                if a in folio_data[f]['zone_set'] and b in folio_data[f]['zone_set'])
        counts[(a, b)] = n
    return counts


def permutation_null_cooccurrence(folio_list, all_labels, section_stratified=False, n_perm=N_PERM_COOCCUR):
    """Run permutation null for co-occurrence.

    If section_stratified: shuffle zone labels within section.
    Always preserves per-folio paragraph count.
    """
    # Build paragraph list with folio and section assignments
    par_list = []  # (folio_index_in_folio_list, zone_label, section)
    folio_to_idx = {f: i for i, f in enumerate(folio_list)}

    # We need all paragraphs for folios in folio_list
    relevant = set(folio_list)
    par_entries = [(e['folio'], e['cluster'], folio_section.get(e['folio'], '?'))
                   for e in all_labels if e['folio'] in relevant]

    if section_stratified:
        # Group paragraphs by section
        sec_groups = defaultdict(list)
        for folio, cluster, sec in par_entries:
            sec_groups[sec].append((folio, cluster))

        null_counts = {pair: [] for pair in zone_pairs}
        for _ in range(n_perm):
            # Shuffle within each section
            shuffled = {}
            for sec, entries in sec_groups.items():
                clusters = [c for _, c in entries]
                rng.shuffle(clusters)
                for i, (folio, _) in enumerate(entries):
                    shuffled.setdefault(folio, []).append(clusters[i])

            # Compute co-occurrence
            for a, b in zone_pairs:
                n = sum(1 for f in folio_list
                        if a in set(shuffled.get(f, [])) and b in set(shuffled.get(f, [])))
                null_counts[(a, b)].append(n)
    else:
        # Global shuffle
        clusters_all = [c for _, c, _ in par_entries]
        folio_parcounts = [(f, len(folio_data[f]['zones'])) for f in folio_list]

        null_counts = {pair: [] for pair in zone_pairs}
        for _ in range(n_perm):
            rng.shuffle(clusters_all)
            # Reassign to folios preserving paragraph counts
            shuffled = {}
            idx = 0
            for f, n in folio_parcounts:
                shuffled[f] = list(clusters_all[idx:idx + n])
                idx += n

            for a, b in zone_pairs:
                n = sum(1 for f in folio_list
                        if a in set(shuffled.get(f, [])) and b in set(shuffled.get(f, [])))
                null_counts[(a, b)].append(n)

    return null_counts


def run_t1(folio_list, label, all_labels):
    """Run T1 for a given folio list."""
    obs = compute_cooccurrence(folio_list)
    results = {}

    for null_type in ['global', 'section_stratified']:
        null_counts = permutation_null_cooccurrence(
            folio_list, all_labels,
            section_stratified=(null_type == 'section_stratified'))

        pair_results = {}
        for pair in zone_pairs:
            name = f"{ZONE_SHORT[pair[0]]}-{ZONE_SHORT[pair[1]]}"
            o = obs[pair]
            null_arr = np.array(null_counts[pair])
            e = null_arr.mean()
            oe = o / e if e > 0 else float('inf')
            # Two-sided p-value
            p_depl = np.mean(null_arr <= o)  # depletion
            p_enr = np.mean(null_arr >= o)   # enrichment
            p_val = min(p_depl, p_enr) * 2   # two-sided
            p_val = min(p_val, 1.0)

            direction = 'depleted' if o < e else 'enriched' if o > e else 'neutral'
            significant = p_val < 0.0083  # Bonferroni

            pair_results[name] = {
                'observed': o,
                'expected': round(e, 2),
                'O_E': round(oe, 3),
                'p_value': round(p_val, 4),
                'direction': direction,
                'significant': significant,
            }

            print(f"  {label} {null_type} {name}: O={o}, E={e:.1f}, O/E={oe:.3f}, "
                  f"p={p_val:.4f} {'*' if significant else ''} [{direction}]")

        results[null_type] = pair_results

    return results


t1_results = {}
print("\nMulti-paragraph folios (n=57):")
t1_results['multi_paragraph'] = run_t1(multi_folios, 'multi', labels)
print("\nAll folios (n=80):")
t1_results['all_folios'] = run_t1(all_folios, 'all', labels)

# Count significant pairs under section-stratified null (multi-paragraph)
t1_sig_section = sum(1 for v in t1_results['multi_paragraph']['section_stratified'].values()
                     if v['significant'])
t1_hard_exclusion = any(v['observed'] == 0 and v['p_value'] < 0.001
                        for v in t1_results['multi_paragraph']['section_stratified'].values())
print(f"\nT1 significant pairs (section-stratified, multi): {t1_sig_section}")
print(f"T1 hard exclusion found: {t1_hard_exclusion}")


# ==================== T2: REPERTOIRE TYPOLOGY ====================

print("\n--- T2: Repertoire Typology ---")

sig_counts = Counter(folio_data[f]['signature'] for f in all_folios)
sig_counts_multi = Counter(folio_data[f]['signature'] for f in multi_folios)

print(f"\nAll folios - observed signatures:")
for sig in sorted(sig_counts.keys(), key=lambda s: -sig_counts[s]):
    zone_names = [ZONE_SHORT[i] for i in range(N_ZONES) if sig[i] == '1']
    print(f"  {sig} ({'+'.join(zone_names)}): n={sig_counts[sig]}")

# Shannon entropy
def shannon_entropy(counts_dict):
    total = sum(counts_dict.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts_dict.values() if c > 0]
    return -sum(p * np.log2(p) for p in probs)

obs_entropy = shannon_entropy(sig_counts)
max_entropy = np.log2(15)  # 15 possible non-empty 4-bit signatures
entropy_ratio = obs_entropy / max_entropy

print(f"\nObserved entropy: {obs_entropy:.3f} bits")
print(f"Max entropy: {max_entropy:.3f} bits")
print(f"Entropy ratio: {entropy_ratio:.3f}")

n_sigs_ge3 = sum(1 for c in sig_counts.values() if c >= 3)
print(f"Signatures with n >= 3: {n_sigs_ge3}")

# Compare to null entropy (section-stratified)
null_entropies_global = []
null_entropies_section = []

# Build paragraph assignment structure
par_by_section = defaultdict(list)
for entry in labels:
    par_by_section[entry['section']].append((entry['folio'], entry['cluster']))

folio_parcounts = {f: len(folio_data[f]['zones']) for f in all_folios}

for _ in range(N_PERM_COOCCUR):
    # Global shuffle
    all_clusters = [e['cluster'] for e in labels]
    rng.shuffle(all_clusters)
    shuffled_global = {}
    idx = 0
    for f in all_folios:
        n = folio_parcounts[f]
        shuffled_global[f] = all_clusters[idx:idx + n]
        idx += n

    null_sigs_g = Counter()
    for f in all_folios:
        zs = set(shuffled_global[f])
        sig = ''.join('1' if i in zs else '0' for i in range(N_ZONES))
        null_sigs_g[sig] += 1
    null_entropies_global.append(shannon_entropy(null_sigs_g))

    # Section-stratified shuffle
    shuffled_sec = defaultdict(list)
    for sec, entries in par_by_section.items():
        clusters = [c for _, c in entries]
        rng.shuffle(clusters)
        for i, (folio, _) in enumerate(entries):
            shuffled_sec[folio].append(clusters[i])

    null_sigs_s = Counter()
    for f in all_folios:
        zs = set(shuffled_sec[f])
        sig = ''.join('1' if i in zs else '0' for i in range(N_ZONES))
        null_sigs_s[sig] += 1
    null_entropies_section.append(shannon_entropy(null_sigs_s))

null_ent_g = np.array(null_entropies_global)
null_ent_s = np.array(null_entropies_section)

ent_p_global = np.mean(null_ent_g <= obs_entropy)
ent_p_section = np.mean(null_ent_s <= obs_entropy)
print(f"\nNull entropy (global): {null_ent_g.mean():.3f} +/- {null_ent_g.std():.3f}")
print(f"Obs < null (global): p={ent_p_global:.4f}")
print(f"Null entropy (section-stratified): {null_ent_s.mean():.3f} +/- {null_ent_s.std():.3f}")
print(f"Obs < null (section-stratified): p={ent_p_section:.4f}")

# Descriptive: zone count vectors
zone_count_summary = defaultdict(list)
for f in all_folios:
    fd = folio_data[f]
    zone_count_summary[fd['signature']].append({
        'folio': f,
        'zone_counts': fd['zone_counts'],
        'dominant_zone': ZONE_SHORT[fd['dominant_zone']],
        'n_paragraphs': fd['n_paragraphs'],
    })

t2_results = {
    'signature_counts': dict(sig_counts),
    'signature_counts_multi': dict(sig_counts_multi),
    'observed_entropy': round(obs_entropy, 4),
    'max_entropy': round(max_entropy, 4),
    'entropy_ratio': round(entropy_ratio, 4),
    'n_signatures_ge3': n_sigs_ge3,
    'null_entropy_global_mean': round(float(null_ent_g.mean()), 4),
    'null_entropy_global_std': round(float(null_ent_g.std()), 4),
    'entropy_p_global': round(float(ent_p_global), 4),
    'null_entropy_section_mean': round(float(null_ent_s.mean()), 4),
    'null_entropy_section_std': round(float(null_ent_s.std()), 4),
    'entropy_p_section': round(float(ent_p_section), 4),
    'below_section_null': bool(obs_entropy < null_ent_s.mean()),
}


# ==================== T3: NESTED MODEL COMPARISON ====================

print("\n--- T3: Nested Model Comparison ---")

# Assemble feature matrix for folios that have zone data + all features
target_features = ['thermo_ke', 'h_ratio', 'strong_close_fraction', 'cei_total', 'link_density']
feature_sources = {
    'thermo_ke': ('op_profiles', 'thermo_ke'),
    'h_ratio': ('op_profiles', 'h_ratio'),
    'strong_close_fraction': ('t0_cov', 'strong_close_fraction'),
    'cei_total': ('scaf_feat', 'cei_total'),
    'link_density': ('scaf_feat', 'link_density'),
}


def get_feature(folio, feat_name):
    source, key = feature_sources[feat_name]
    if source == 'op_profiles':
        return op_profiles.get(folio, {}).get(key)
    elif source == 't0_cov':
        return t0_cov.get(folio, {}).get(key)
    elif source == 'scaf_feat':
        return scaf_feat.get(folio, {}).get(key)
    return None


# Build complete feature table
complete_folios = []
for f in all_folios:
    vals = {feat: get_feature(f, feat) for feat in target_features}
    pfx = folio_prefix_fracs.get(f)
    if all(v is not None for v in vals.values()) and pfx is not None:
        complete_folios.append(f)

print(f"Folios with complete data: {len(complete_folios)}")

# Merge rare repertoire types
sig_counts_complete = Counter(folio_data[f]['signature'] for f in complete_folios)
rare_sigs = {s for s, c in sig_counts_complete.items() if c < 5}
print(f"Repertoire types: {len(sig_counts_complete)}, rare (n<5, merged): {len(rare_sigs)}")


def get_rep_type(folio):
    sig = folio_data[folio]['signature']
    return 'RARE' if sig in rare_sigs else sig


# Encode section as numeric
section_map = {s: i for i, s in enumerate(sorted(set(folio_data[f]['section'] for f in complete_folios)))}

# Paragraph count bins for permutation stratification
def parcount_bin(f):
    n = folio_data[f]['n_paragraphs']
    if n == 1:
        return 0
    elif n <= 3:
        return 1
    else:
        return 2


# Build design matrices
from numpy.linalg import lstsq

def build_baseline_X(folio_list):
    """Model A: prefix fracs + section dummies + paragraph_count."""
    sections = sorted(set(folio_data[f]['section'] for f in folio_list))
    sec_to_idx = {s: i for i, s in enumerate(sections[1:])}  # drop first for dummy coding
    n = len(folio_list)
    # columns: intercept, qo_frac, chsh_frac, bare_frac, paragraph_count, section dummies
    n_sec_dummies = len(sections) - 1
    X = np.zeros((n, 5 + n_sec_dummies))
    for i, f in enumerate(folio_list):
        pfx = folio_prefix_fracs[f]
        X[i, 0] = 1  # intercept
        X[i, 1] = pfx['qo_frac']
        X[i, 2] = pfx['chsh_frac']
        X[i, 3] = pfx['bare_frac']
        X[i, 4] = folio_data[f]['n_paragraphs']
        sec = folio_data[f]['section']
        if sec in sec_to_idx:
            X[i, 5 + sec_to_idx[sec]] = 1
    return X


def build_full_X(folio_list, rep_types):
    """Model B: baseline + repertoire type dummies."""
    X_base = build_baseline_X(folio_list)
    unique_reps = sorted(set(rep_types))
    rep_to_idx = {r: i for i, r in enumerate(unique_reps[1:])}  # drop first
    n_rep_dummies = len(unique_reps) - 1
    X_full = np.zeros((len(folio_list), X_base.shape[1] + n_rep_dummies))
    X_full[:, :X_base.shape[1]] = X_base
    for i, rt in enumerate(rep_types):
        if rt in rep_to_idx:
            X_full[i, X_base.shape[1] + rep_to_idx[rt]] = 1
    return X_full, X_base.shape[1], n_rep_dummies


def ols_r2(X, y):
    """Compute R-squared from OLS."""
    coef, _, _, _ = lstsq(X, y, rcond=None)
    y_pred = X @ coef
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot


def f_test_nested(r2_full, r2_base, n, p_full, p_base):
    """F-test for nested model comparison."""
    df1 = p_full - p_base  # extra parameters
    df2 = n - p_full        # residual df
    if df1 <= 0 or df2 <= 0 or r2_full <= r2_base:
        return 0.0, 1.0
    f_stat = ((r2_full - r2_base) / df1) / ((1 - r2_full) / df2)
    p_val = 1 - stats.f.cdf(f_stat, df1, df2)
    return f_stat, p_val


# Actual repertoire types
rep_types_actual = [get_rep_type(f) for f in complete_folios]

t3_results = {}
for feat in target_features:
    y_raw = np.array([get_feature(f, feat) for f in complete_folios])
    # Rank transform
    y = stats.rankdata(y_raw)

    X_full, n_base_cols, n_rep_dummies = build_full_X(complete_folios, rep_types_actual)
    X_base = X_full[:, :n_base_cols]

    n = len(complete_folios)
    p_base = n_base_cols
    p_full = n_base_cols + n_rep_dummies

    r2_base = ols_r2(X_base, y)
    r2_full = ols_r2(X_full, y)
    delta_r2 = r2_full - r2_base

    f_stat, f_p = f_test_nested(r2_full, r2_base, n, p_full, p_base)

    # Raw KW (no controls)
    groups = defaultdict(list)
    for i, f in enumerate(complete_folios):
        groups[get_rep_type(f)].append(y_raw[i])
    group_vals = [v for v in groups.values() if len(v) >= 2]
    if len(group_vals) >= 2:
        kw_stat, kw_p = stats.kruskal(*group_vals)
    else:
        kw_stat, kw_p = 0.0, 1.0

    # Permutation test: shuffle repertoire labels within section x parcount-bin
    strata = defaultdict(list)
    for i, f in enumerate(complete_folios):
        key = (folio_data[f]['section'], parcount_bin(f))
        strata[key].append(i)

    null_delta_r2s = []
    for _ in range(N_PERM_T3):
        perm_rep = list(rep_types_actual)
        for indices in strata.values():
            if len(indices) > 1:
                vals = [perm_rep[i] for i in indices]
                rng.shuffle(vals)
                for j, idx in enumerate(indices):
                    perm_rep[idx] = vals[j]

        X_full_perm, _, _ = build_full_X(complete_folios, perm_rep)
        r2_full_perm = ols_r2(X_full_perm, y)
        null_delta_r2s.append(r2_full_perm - r2_base)

    perm_p = np.mean(np.array(null_delta_r2s) >= delta_r2)

    t3_results[feat] = {
        'r2_baseline': round(r2_base, 4),
        'r2_full': round(r2_full, 4),
        'delta_r2': round(delta_r2, 4),
        'f_stat': round(f_stat, 3),
        'f_p': round(f_p, 4),
        'perm_p': round(float(perm_p), 4),
        'kw_stat': round(kw_stat, 3),
        'kw_p': round(kw_p, 4),
        'significant': bool(f_p < 0.05 and perm_p < 0.05),
    }

    print(f"  {feat}: dR2={delta_r2:.4f}, F={f_stat:.3f}, F_p={f_p:.4f}, "
          f"perm_p={perm_p:.4f}, KW_p={kw_p:.4f} {'*' if t3_results[feat]['significant'] else ''}")

t3_n_significant = sum(1 for v in t3_results.values() if v['significant'])
print(f"\nT3 features significant (F + perm): {t3_n_significant}/5")


# ==================== T4: SECTION X REPERTOIRE (DESCRIPTIVE) ====================

print("\n--- T4: Section x Repertoire (Descriptive) ---")

# Contingency table
sections_use = sorted(set(folio_data[f]['section'] for f in all_folios))
rep_types_all = sorted(set(folio_data[f]['signature'] for f in all_folios))

contingency = np.zeros((len(sections_use), len(rep_types_all)), dtype=int)
sec_idx = {s: i for i, s in enumerate(sections_use)}
rep_idx = {r: i for i, r in enumerate(rep_types_all)}

for f in all_folios:
    contingency[sec_idx[folio_data[f]['section']], rep_idx[folio_data[f]['signature']]] += 1

# Remove columns with all zeros
nonzero_cols = contingency.sum(axis=0) > 0
contingency_clean = contingency[:, nonzero_cols]

if contingency_clean.shape[0] >= 2 and contingency_clean.shape[1] >= 2:
    # Chi-squared (Fisher not available in scipy for >2x2 easily, use chi2)
    chi2, chi2_p, chi2_dof, _ = stats.chi2_contingency(contingency_clean)
    n_total = contingency_clean.sum()
    k = min(contingency_clean.shape)
    cramers_v = np.sqrt(chi2 / (n_total * (k - 1))) if n_total * (k - 1) > 0 else 0
else:
    chi2, chi2_p, cramers_v = 0, 1, 0

# Per-section entropy
sec_entropies = {}
for sec in sections_use:
    sec_folios = [f for f in all_folios if folio_data[f]['section'] == sec]
    if len(sec_folios) < 3:
        continue
    sec_sig_counts = Counter(folio_data[f]['signature'] for f in sec_folios)
    sec_entropies[sec] = round(shannon_entropy(sec_sig_counts), 4)

print(f"Chi2={chi2:.2f}, p={chi2_p:.4f}, Cramer's V={cramers_v:.3f}")
print(f"Per-section entropy: {sec_entropies}")

t4_results = {
    'chi2': round(chi2, 3),
    'chi2_p': round(chi2_p, 4),
    'cramers_v': round(cramers_v, 4),
    'section_entropies': sec_entropies,
    'sections': sections_use,
    'contingency_shape': list(contingency_clean.shape),
}


# ==================== T5: MONO-TYPE CHARACTERIZATION ====================

print("\n--- T5: Mono-Type Characterization ---")

mono_folios = [f for f in all_folios if folio_data[f]['breadth'] == 1]
multi_type_folios = [f for f in all_folios if folio_data[f]['breadth'] > 1]
mono_genuine = [f for f in mono_folios if folio_data[f]['n_paragraphs'] >= 2]
mono_forced = [f for f in mono_folios if folio_data[f]['n_paragraphs'] == 1]

print(f"Mono-type: {len(mono_folios)} total ({len(mono_forced)} forced, {len(mono_genuine)} genuine)")
print(f"Multi-type: {len(multi_type_folios)}")

# Zone distribution of mono-types
mono_zone_all = Counter(folio_data[f]['dominant_zone'] for f in mono_folios)
mono_zone_genuine = Counter(folio_data[f]['dominant_zone'] for f in mono_genuine)

print("\nMono-type zone distribution (all):")
for z in range(N_ZONES):
    print(f"  {ZONE_NAMES[z]}: {mono_zone_all.get(z, 0)}")

print("\nMono-type zone distribution (genuine, 2+ paragraphs):")
for z in range(N_ZONES):
    print(f"  {ZONE_NAMES[z]}: {mono_zone_genuine.get(z, 0)}")

# Mann-Whitney: mono vs multi on features
t5_mw_results = {}
for feat in target_features:
    mono_vals = [get_feature(f, feat) for f in mono_folios if get_feature(f, feat) is not None]
    multi_vals = [get_feature(f, feat) for f in multi_type_folios if get_feature(f, feat) is not None]
    if len(mono_vals) >= 3 and len(multi_vals) >= 3:
        u_stat, mw_p = stats.mannwhitneyu(mono_vals, multi_vals, alternative='two-sided')
        mono_med = np.median(mono_vals)
        multi_med = np.median(multi_vals)
        t5_mw_results[feat] = {
            'mono_median': round(mono_med, 4),
            'multi_median': round(multi_med, 4),
            'U': round(u_stat, 1),
            'p': round(mw_p, 4),
            'significant': bool(mw_p < 0.05),
            'n_mono': len(mono_vals),
            'n_multi': len(multi_vals),
        }
        print(f"  {feat}: mono={mono_med:.4f}, multi={multi_med:.4f}, p={mw_p:.4f} "
              f"{'*' if mw_p < 0.05 else ''}")

t5_n_significant = sum(1 for v in t5_mw_results.values() if v['significant'])

# P5 check: most common genuine mono-type
if mono_zone_genuine:
    most_common_mono = max(mono_zone_genuine, key=mono_zone_genuine.get)
    p5_pass = (most_common_mono == 0)  # THERMAL-QO
    print(f"\nP5: Most common genuine mono-type = {ZONE_NAMES[most_common_mono]} "
          f"({'PASS' if p5_pass else 'FAIL'})")
else:
    p5_pass = False

# Within mono-type KW across zone identities
t5_within_mono = {}
for feat in target_features:
    groups = defaultdict(list)
    for f in mono_folios:
        val = get_feature(f, feat)
        if val is not None:
            groups[folio_data[f]['dominant_zone']].append(val)
    group_vals = [v for v in groups.values() if len(v) >= 2]
    if len(group_vals) >= 2:
        kw_stat, kw_p = stats.kruskal(*group_vals)
        t5_within_mono[feat] = {'kw_stat': round(kw_stat, 3), 'kw_p': round(kw_p, 4)}
        print(f"  Within-mono KW {feat}: H={kw_stat:.3f}, p={kw_p:.4f}")

t5_results = {
    'n_mono_total': len(mono_folios),
    'n_mono_forced': len(mono_forced),
    'n_mono_genuine': len(mono_genuine),
    'n_multi_type': len(multi_type_folios),
    'mono_zone_all': {ZONE_NAMES[k]: v for k, v in mono_zone_all.items()},
    'mono_zone_genuine': {ZONE_NAMES[k]: v for k, v in mono_zone_genuine.items()},
    'mw_results': t5_mw_results,
    'n_mw_significant': t5_n_significant,
    'p5_most_common_genuine': ZONE_NAMES.get(most_common_mono, 'N/A') if mono_zone_genuine else 'N/A',
    'p5_pass': p5_pass,
    'within_mono_kw': t5_within_mono,
}


# ==================== VERDICT ====================

print("\n=== VERDICT DETERMINATION ===\n")

# Check predictions
p1_pass = False
tq_mp_key = 'TQ-MP'
sec_strat_multi = t1_results.get('multi_paragraph', {}).get('section_stratified', {})
if tq_mp_key in sec_strat_multi:
    tq_mp = sec_strat_multi[tq_mp_key]
    p1_pass = tq_mp['direction'] == 'depleted' and tq_mp['significant']
    print(f"P1 (TQ-MP depleted, section-strat): O/E={tq_mp['O_E']}, p={tq_mp['p_value']} "
          f"-> {'PASS' if p1_pass else 'FAIL'}")

p2_below_null = t2_results['below_section_null']
p2_few_sigs = t2_results['n_signatures_ge3'] < 8
p2_pass = p2_below_null and p2_few_sigs
print(f"P2 (entropy < section null & <8 sigs): below_null={p2_below_null}, "
      f"n_sigs_ge3={t2_results['n_signatures_ge3']} -> {'PASS' if p2_pass else 'FAIL'}")

p3_pass = t3_n_significant == 0  # null prediction: repertoire adds nothing
print(f"P3 (repertoire null after controls): {t3_n_significant}/5 significant "
      f"-> {'PASS' if p3_pass else 'FAIL (surprise!)'}")

p4_assoc = chi2_p < 0.01 and cramers_v > 0.25
max_ent_sec = max(sec_entropies.values()) if sec_entropies else None
p4_herbal_max = max_ent_sec is not None and sec_entropies.get('H') == max_ent_sec
p4_pass = p4_assoc and p4_herbal_max
print(f"P4 (section assoc + Herbal max entropy): assoc={p4_assoc}, herbal_max={p4_herbal_max} "
      f"-> {'PASS' if p4_pass else 'FAIL'}")

print(f"P5 (THERMAL-QO most common genuine mono): {'PASS' if p5_pass else 'FAIL'}")

p6_pass = t5_n_significant >= 2
print(f"P6 (mono vs multi >=2 features): {t5_n_significant}/5 "
      f"-> {'PASS' if p6_pass else 'FAIL'}")

# Verdict
if t1_hard_exclusion:
    verdict = "REPERTOIRE_CONSTRAINT_DISCOVERED"
elif t3_n_significant >= 2:
    verdict = "REPERTOIRE_INDEPENDENTLY_INFORMATIVE"
elif t1_sig_section >= 2:
    verdict = "REPERTOIRE_STRUCTURED_PREFIX_MEDIATED"
else:
    verdict = "REPERTOIRE_WEAK"

print(f"\n*** VERDICT: {verdict} ***")

# ==================== WRITE RESULTS ====================

results = {
    'phase': 608,
    'name': 'SUBROUTINE_REPERTOIRE_CHARACTERIZATION',
    'predictions_sha256': pred_hash,
    'verdict': verdict,
    'summary': {
        'n_folios_total': len(all_folios),
        'n_folios_multi_paragraph': len(multi_folios),
        'n_folios_complete_data': len(complete_folios),
        't1_sig_pairs_section_stratified': t1_sig_section,
        't1_hard_exclusion': t1_hard_exclusion,
        't2_entropy_ratio': t2_results['entropy_ratio'],
        't2_below_section_null': t2_results['below_section_null'],
        't3_n_significant': t3_n_significant,
        't5_n_mono': len(mono_folios),
        't5_n_mono_genuine': len(mono_genuine),
    },
    'predictions': {
        'P1': {'pass': p1_pass, 'description': 'TQ-MP depleted under section-stratified null'},
        'P2': {'pass': p2_pass, 'description': 'Entropy below section null, <8 sigs with n>=3'},
        'P3': {'pass': p3_pass, 'description': 'Repertoire null after PREFIX+section+parcount control'},
        'P4': {'pass': p4_pass, 'description': 'Section association + Herbal max entropy'},
        'P5': {'pass': p5_pass, 'description': 'THERMAL-QO most common genuine mono-type'},
        'P6': {'pass': p6_pass, 'description': 'Mono vs multi differ on >=2 features'},
    },
    't1_cooccurrence': t1_results,
    't2_typology': t2_results,
    't3_nested_model': t3_results,
    't4_section_repertoire': t4_results,
    't5_monotype': t5_results,
}

os.makedirs(RESULTS_DIR, exist_ok=True)
out_path = RESULTS_DIR / 'subroutine_repertoire_results.json'
with open(out_path, 'w') as f:
    json.dump(convert_numpy(results), f, indent=2)

print(f"\nResults written to {out_path}")
