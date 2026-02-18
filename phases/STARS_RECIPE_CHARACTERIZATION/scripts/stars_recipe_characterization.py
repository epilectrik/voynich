#!/usr/bin/env python3
"""
Phase 392: Stars/Recipe Section Characterization -- 10-test battery

Tests whether the Stars/Recipe section (section S, ~23 folios) encodes a
structurally distinct application domain AND probes the Stars Paradox:
Stars has the most REGIME diversity but the LOWEST AXM variance.

Tests S1-S4: Mirror battery (Phase 385 structure) -- Stars distinctiveness
Tests S5-S6: Extended profiling -- LINK density, vocabulary specialization
Tests S7-S10: Clamping mechanism -- why Stars has low variance

Core hypothesis: Stars programs converge to similar dynamics despite
different REGIMEs because low bridge density restricts the behavioral
option space and e-stability vocabulary concentration clamps outcomes.

Grounding constraints:
  C109 (5 hazard classes), C494 (k/h/e REGIME dimensions),
  C552 (section role profiles), C930 (lk Stars concentration),
  C1048 (Stars LOO R²=-0.319), C1084 (section AXM ordering),
  C1099 (bridge density gradient), C1104 (bridge enables freedom)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats
from itertools import combinations

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, BFolioDecoder,
                              BTokenAnalysis)

RESULTS = ROOT / "phases" / "STARS_RECIPE_CHARACTERIZATION" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

ALPHA_BONFERRONI = 0.005  # 10 tests, family-wise 0.05

# C109: 17 forbidden transitions (Tier 0, FROZEN)
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

HAZARD_CLASSES = {
    ('shey', 'aiin'): 'PHASE_ORDERING',
    ('shey', 'al'): 'PHASE_ORDERING',
    ('shey', 'c'): 'PHASE_ORDERING',
    ('chol', 'r'): 'PHASE_ORDERING',
    ('dy', 'chey'): 'PHASE_ORDERING',
    ('chey', 'chedy'): 'PHASE_ORDERING',
    ('chey', 'shedy'): 'PHASE_ORDERING',
    ('chedy', 'ee'): 'COMPOSITION_JUMP',
    ('dy', 'aiin'): 'COMPOSITION_JUMP',
    ('c', 'ee'): 'COMPOSITION_JUMP',
    ('shedy', 'aiin'): 'COMPOSITION_JUMP',
    ('l', 'chol'): 'CONTAINMENT_TIMING',
    ('ar', 'dal'): 'CONTAINMENT_TIMING',
    ('he', 't'): 'CONTAINMENT_TIMING',
    ('shedy', 'o'): 'CONTAINMENT_TIMING',
    ('or', 'dal'): 'RATE_MISMATCH',
    ('he', 'or'): 'ENERGY_OVERSHOOT',
}

HAZARD_SOURCES = set(a for a, b in FORBIDDEN_TRANSITIONS)

CC_TRIGGERS = {
    'daiin': 'CHSH_PRECISION',
    'dain': 'CHSH_PRECISION',
    'aiin': 'FQ_FREQUENT',
    'ain': 'FQ_FREQUENT',
    'ol': 'QO_ENERGY',
    'or': 'CLOSE_FLOW',
    'al': 'CLOSE_FLOW',
    'ar': 'CLOSE_FLOW',
}


def round_floats(obj, decimals=4):
    """Recursively round floats for JSON serialization."""
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


# ===================================================================
# Initialize
# ===================================================================
print("=" * 70)
print("PHASE 392: STARS/RECIPE SECTION CHARACTERIZATION")
print("=" * 70)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load regime assignments
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Load AXM decomposition data
axm_path = ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
with open(axm_path, 'r', encoding='utf-8') as f:
    axm_data = json.load(f)
axm_folio_data = axm_data['folio_data']

# Load bridge density from Phase 391
bridge_path = ROOT / 'phases' / 'SECTION_BRIDGE_DYNAMICS' / 'results' / 'section_bridge_dynamics.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_folio_data = bridge_data['folio_data']

# Build token lists per folio
folio_tokens = defaultdict(list)
folio_section = {}

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens[tok.folio].append(tok)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

# Partition: Stars vs non-Stars (B+H only, exclude T and C)
stars_folios = set(f for f, s in folio_section.items() if s == 'S')
non_stars_folios = set(f for f, s in folio_section.items() if s in ('B', 'H'))

stars_token_count = sum(len(folio_tokens[f]) for f in stars_folios)
non_stars_token_count = sum(len(folio_tokens[f]) for f in non_stars_folios)

print(f"Stars folios: {len(stars_folios)} ({stars_token_count} tokens)")
print(f"Non-Stars folios (B+H): {len(non_stars_folios)} ({non_stars_token_count} tokens)")
print(f"Stars sections: {Counter(folio_section[f] for f in stars_folios)}")
print(f"Non-Stars sections: {Counter(folio_section[f] for f in non_stars_folios)}")
print()

# REGIME distribution
stars_regimes = Counter(folio_regime.get(f, 'X') for f in stars_folios)
non_stars_regimes = Counter(folio_regime.get(f, 'X') for f in non_stars_folios)
print(f"Stars REGIME distribution: {dict(stars_regimes)}")
print(f"Non-Stars REGIME distribution: {dict(non_stars_regimes)}")
print()

# REGIME-matched subsets
stars_r1 = set(f for f in stars_folios if folio_regime.get(f) == 'REGIME_1')
non_stars_r1 = set(f for f in non_stars_folios if folio_regime.get(f) == 'REGIME_1')
stars_r3 = set(f for f in stars_folios if folio_regime.get(f) == 'REGIME_3')
non_stars_r3 = set(f for f in non_stars_folios if folio_regime.get(f) == 'REGIME_3')

print(f"REGIME_1: Stars={len(stars_r1)}, Non-Stars={len(non_stars_r1)}")
print(f"REGIME_3: Stars={len(stars_r3)}, Non-Stars={len(non_stars_r3)}")
print()


# ===================================================================
# Helper functions (adapted from Phase 385)
# ===================================================================

def count_kernels(folio_set):
    """Count kernel characters across all tokens in folio set."""
    counts = Counter()
    total_tokens = 0
    for folio in folio_set:
        for tok in folio_tokens[folio]:
            m = morph.extract(tok.word)
            if m.middle:
                total_tokens += 1
                for c in m.middle:
                    if c in ('k', 'h', 'e'):
                        counts[c] += 1
    return counts, total_tokens


def count_hazard_proximity(folio_set):
    """Count hazard source events by class."""
    class_counts = Counter()
    total_transitions = 0
    for folio in folio_set:
        words = [t.word for t in folio_tokens[folio]]
        for i, w in enumerate(words):
            if w in HAZARD_SOURCES:
                for (a, b), hclass in HAZARD_CLASSES.items():
                    if a == w:
                        class_counts[hclass] += 1
                        total_transitions += 1
    return class_counts, total_transitions


def count_cc_triggers(folio_set):
    """Count CC trigger tokens by type."""
    counts = Counter()
    total = 0
    for folio in folio_set:
        for tok in folio_tokens[folio]:
            if tok.word in CC_TRIGGERS:
                counts[CC_TRIGGERS[tok.word]] += 1
                total += 1
    return counts, total


def compute_folio_profile(folio):
    """Compute operational profile for a single folio."""
    tokens = folio_tokens[folio]
    words = [t.word for t in tokens]
    n = len(words)
    if n == 0:
        return None

    # Kernel counts (character-level)
    k_chars = Counter()
    for w in words:
        m = morph.extract(w)
        if m.middle:
            for c in m.middle:
                if c in ('k', 'h', 'e'):
                    k_chars[c] += 1
    k_total = sum(k_chars.values())

    # Lane distribution
    lanes = Counter()
    for w in words:
        m = morph.extract(w)
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            lanes[lane] += 1

    # Hazard source density
    haz_sources = sum(1 for w in words if w in HAZARD_SOURCES)

    # AXM self-transition
    states = []
    for w in words:
        tc = decoder._token_to_class.get(w)
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc))
            if ms:
                states.append(ms)
    axm_trans = sum(1 for i in range(len(states) - 1) if states[i] == 'AXM')
    axm_self = sum(1 for i in range(len(states) - 1)
                   if states[i] == 'AXM' and states[i + 1] == 'AXM')
    axm_rate = axm_self / axm_trans if axm_trans > 5 else None

    # Vocabulary metrics
    middles = set()
    e_middle_count = 0
    total_middle_count = 0
    for w in words:
        m = morph.extract(w)
        if m.middle:
            middles.add(m.middle)
            total_middle_count += 1
            # e-kernel fraction: count MIDDLEs containing 'e'
            if 'e' in m.middle:
                e_middle_count += 1

    ttr = len(middles) / n if n > 0 else 0
    e_kernel_frac = e_middle_count / total_middle_count if total_middle_count > 0 else 0

    return {
        'k_pct': k_chars['k'] / k_total if k_total > 0 else 0,
        'h_pct': k_chars['h'] / k_total if k_total > 0 else 0,
        'e_pct': k_chars['e'] / k_total if k_total > 0 else 0,
        'qo_pct': lanes.get('QO', 0) / n,
        'chsh_pct': lanes.get('CHSH', 0) / n,
        'link_pct': lanes.get('LINK', 0) / n,
        'haz_density': haz_sources / n,
        'axm_self': axm_rate,
        'n_tokens': n,
        'ttr': ttr,
        'e_kernel_fraction': e_kernel_frac,
        'n_unique_middles': len(middles),
    }


def get_folio_middle_set(folio):
    """Get set of unique MIDDLEs for a folio."""
    middles = set()
    for tok in folio_tokens[folio]:
        m = morph.extract(tok.word)
        if m.middle:
            middles.add(m.middle)
    return middles


def jaccard(s1, s2):
    """Jaccard similarity between two sets."""
    if not s1 and not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


# Pre-compute all folio profiles
all_profiles = {}
for f in stars_folios | non_stars_folios:
    p = compute_folio_profile(f)
    if p:
        all_profiles[f] = p

# Pre-compute MIDDLE sets
folio_middle_sets = {}
for f in stars_folios | non_stars_folios:
    folio_middle_sets[f] = get_folio_middle_set(f)


# ===================================================================
# S1: KERNEL BALANCE PARTITION
# ===================================================================
print("-" * 70)
print("S1: Kernel Balance Partition (Stars vs Non-Stars)")
print("-" * 70)
print()

stars_kernels, stars_tok_n = count_kernels(stars_folios)
non_stars_kernels, non_stars_tok_n = count_kernels(non_stars_folios)

stars_total_k = sum(stars_kernels.values())
non_stars_total_k = sum(non_stars_kernels.values())

s1_data = {}
print(f"  {'Kernel':<8} {'Stars':>10} {'Stars%':>8} {'Non-Stars':>10} {'NS%':>8} {'Ratio':>8}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*8} {'-'*8}")

for k in ['k', 'h', 'e']:
    sp = 100 * stars_kernels[k] / stars_total_k if stars_total_k > 0 else 0
    nsp = 100 * non_stars_kernels[k] / non_stars_total_k if non_stars_total_k > 0 else 0
    ratio = sp / nsp if nsp > 0 else 0
    print(f"  {k:<8} {stars_kernels[k]:>10} {sp:>7.1f}% {non_stars_kernels[k]:>10} {nsp:>7.1f}% {ratio:>7.2f}x")
    s1_data[k] = {'stars': int(stars_kernels[k]), 'non_stars': int(non_stars_kernels[k]),
                   'stars_pct': sp, 'non_stars_pct': nsp, 'ratio': ratio}

ct_s1 = np.array([
    [stars_kernels['k'], stars_kernels['h'], stars_kernels['e']],
    [non_stars_kernels['k'], non_stars_kernels['h'], non_stars_kernels['e']]
])
chi2_s1, p_s1, dof_s1, _ = sp_stats.chi2_contingency(ct_s1)
v_s1 = np.sqrt(chi2_s1 / (ct_s1.sum() * (min(ct_s1.shape) - 1)))
print(f"\n  Chi-square: chi2={chi2_s1:.1f}, dof={dof_s1}, p={p_s1:.2e}, Cramer's V={v_s1:.4f}")

k_ratio = s1_data['k']['ratio']
h_ratio = s1_data['h']['ratio']
e_ratio = s1_data['e']['ratio']

if p_s1 < 0.05:
    if e_ratio > 1.05:
        s1_direction = "E_STABILITY"
    elif k_ratio > 1.1 and h_ratio < 0.95:
        s1_direction = "K_ENRICHED"
    elif h_ratio > 1.1:
        s1_direction = "H_MONITORING"
    else:
        s1_direction = "MIXED"
else:
    s1_direction = "NULL"

if p_s1 < ALPHA_BONFERRONI:
    s1_verdict = f"PASS_{s1_direction}"
elif p_s1 < 0.05:
    s1_verdict = f"MARGINAL_{s1_direction}"
else:
    s1_verdict = "FAIL_NULL"

# REGIME-controlled
print(f"\n  REGIME_1 controlled:")
if stars_r1 and non_stars_r1:
    stars_r1_k, _ = count_kernels(stars_r1)
    non_stars_r1_k, _ = count_kernels(non_stars_r1)
    sr1_tot = sum(stars_r1_k.values())
    nsr1_tot = sum(non_stars_r1_k.values())
    s1_regime_ctrl = {}
    for k in ['k', 'h', 'e']:
        sp = 100 * stars_r1_k[k] / sr1_tot if sr1_tot > 0 else 0
        nsp = 100 * non_stars_r1_k[k] / nsr1_tot if nsr1_tot > 0 else 0
        print(f"    {k}: Stars_R1={sp:.1f}% Non-Stars_R1={nsp:.1f}%")
        s1_regime_ctrl[k] = {'stars_r1_pct': sp, 'non_stars_r1_pct': nsp}
    ct_r1 = np.array([
        [stars_r1_k['k'], stars_r1_k['h'], stars_r1_k['e']],
        [non_stars_r1_k['k'], non_stars_r1_k['h'], non_stars_r1_k['e']]
    ])
    chi2_r1, p_r1, _, _ = sp_stats.chi2_contingency(ct_r1)
    print(f"    Chi-square (R1 only): chi2={chi2_r1:.1f}, p={p_r1:.2e}")
    s1_regime_ctrl['chi2'] = chi2_r1
    s1_regime_ctrl['p'] = p_r1
else:
    s1_regime_ctrl = {'note': 'insufficient data'}

s1_data['chi2'] = chi2_s1
s1_data['p'] = p_s1
s1_data['cramers_v'] = v_s1
s1_data['direction'] = s1_direction
s1_data['regime_controlled'] = s1_regime_ctrl

print(f"\nS1 VERDICT: {s1_verdict}")
print()


# ===================================================================
# S2: HAZARD PROFILE PARTITION
# ===================================================================
print("-" * 70)
print("S2: Hazard Profile Partition (Stars vs Non-Stars)")
print("-" * 70)
print()

stars_hazards, stars_haz_n = count_hazard_proximity(stars_folios)
non_stars_hazards, non_stars_haz_n = count_hazard_proximity(non_stars_folios)

print(f"  Hazard source events: Stars={stars_haz_n}, Non-Stars={non_stars_haz_n}")
print()

classes_ordered = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
                   'RATE_MISMATCH', 'ENERGY_OVERSHOOT']

s2_data = {}
print(f"  {'Class':<22} {'Stars':>6} {'S%':>7} {'Non-Stars':>9} {'NS%':>7}")
print(f"  {'-'*22} {'-'*6} {'-'*7} {'-'*9} {'-'*7}")

for hc in classes_ordered:
    sc = stars_hazards.get(hc, 0)
    nsc = non_stars_hazards.get(hc, 0)
    sp = 100 * sc / stars_haz_n if stars_haz_n > 0 else 0
    nsp = 100 * nsc / non_stars_haz_n if non_stars_haz_n > 0 else 0
    print(f"  {hc:<22} {sc:>6} {sp:>6.1f}% {nsc:>9} {nsp:>6.1f}%")
    s2_data[hc] = {'stars': int(sc), 'non_stars': int(nsc), 'stars_pct': sp, 'non_stars_pct': nsp}

# Chi-square on full distribution
s_vec = [stars_hazards.get(c, 0) for c in classes_ordered]
ns_vec = [non_stars_hazards.get(c, 0) for c in classes_ordered]
ct_s2 = np.array([s_vec, ns_vec])
col_mask = ct_s2.sum(axis=0) > 0
ct_s2_valid = ct_s2[:, col_mask]

s2_chi2, s2_p, s2_dof = 0, 1.0, 0
if ct_s2_valid.shape[1] >= 2:
    s2_chi2, s2_p, s2_dof, _ = sp_stats.chi2_contingency(ct_s2_valid)
    print(f"\n  Chi-square (hazard classes): chi2={s2_chi2:.1f}, dof={s2_dof}, p={s2_p:.4f}")

# Apparatus-specific test (Fisher exact)
stars_apparatus = stars_hazards.get('CONTAINMENT_TIMING', 0) + stars_hazards.get('RATE_MISMATCH', 0)
stars_other = stars_haz_n - stars_apparatus
ns_apparatus = non_stars_hazards.get('CONTAINMENT_TIMING', 0) + non_stars_hazards.get('RATE_MISMATCH', 0)
ns_other = non_stars_haz_n - ns_apparatus

s2_fisher_p = 1.0
s2_fisher_or = 1.0
if stars_haz_n > 0 and non_stars_haz_n > 0:
    s_app_pct = 100 * stars_apparatus / stars_haz_n
    ns_app_pct = 100 * ns_apparatus / non_stars_haz_n
    print(f"\n  Apparatus-specific hazards (CONTAINMENT + RATE):")
    print(f"    Stars: {stars_apparatus}/{stars_haz_n} ({s_app_pct:.1f}%)")
    print(f"    Non-Stars: {ns_apparatus}/{non_stars_haz_n} ({ns_app_pct:.1f}%)")

    ct_app = np.array([[stars_apparatus, stars_other], [ns_apparatus, ns_other]])
    if min(ct_app.sum(axis=0)) > 0 and min(ct_app.sum(axis=1)) > 0:
        s2_fisher_or, s2_fisher_p = sp_stats.fisher_exact(ct_app)
        print(f"    Fisher exact: OR={s2_fisher_or:.3f}, p={s2_fisher_p:.4f}")

if s2_fisher_p < ALPHA_BONFERRONI:
    s2_verdict = "PASS_DISTINCT_HAZARD"
elif s2_fisher_p < 0.05:
    s2_verdict = "MARGINAL_HAZARD"
else:
    s2_verdict = "FAIL_SAME"

s2_data['chi2'] = s2_chi2
s2_data['chi2_p'] = s2_p
s2_data['apparatus_fisher_or'] = s2_fisher_or
s2_data['apparatus_fisher_p'] = s2_fisher_p

print(f"\nS2 VERDICT: {s2_verdict}")
print()


# ===================================================================
# S3: REGIME_1 OPERATIONAL HOMOGENEITY
# ===================================================================
print("-" * 70)
print("S3: REGIME_1 Homogeneity (Stars-R1 vs Non-Stars-R1)")
print("-" * 70)
print()

stars_r1_profiles = {f: all_profiles[f] for f in stars_r1 if f in all_profiles}
non_stars_r1_profiles = {f: all_profiles[f] for f in non_stars_r1 if f in all_profiles}

print(f"  Stars REGIME_1 folios: {len(stars_r1_profiles)}")
print(f"  Non-Stars REGIME_1 folios: {len(non_stars_r1_profiles)}")
print()

dimensions = ['k_pct', 'h_pct', 'e_pct', 'qo_pct', 'chsh_pct',
              'link_pct', 'haz_density', 'axm_self']
dim_labels = ['k kernel%', 'h kernel%', 'e kernel%', 'QO lane%', 'CHSH lane%',
              'LINK lane%', 'Hazard density', 'AXM self-rate']

s3_results = {}
s3_sig_count = 0

print(f"  {'Dimension':<16} {'Stars-R1':>10} {'NS-R1':>10} {'U-stat':>8} {'p-value':>10} {'Sig':>5}")
print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*5}")

for dim, label in zip(dimensions, dim_labels):
    s_vals = [p[dim] for p in stars_r1_profiles.values() if p[dim] is not None]
    ns_vals = [p[dim] for p in non_stars_r1_profiles.values() if p[dim] is not None]

    if len(s_vals) >= 3 and len(ns_vals) >= 3:
        u_stat, p_mw = sp_stats.mannwhitneyu(s_vals, ns_vals, alternative='two-sided')
        sig = "*" if p_mw < 0.05 else ""
        if p_mw < 0.05:
            s3_sig_count += 1
        s_mean = np.mean(s_vals)
        ns_mean = np.mean(ns_vals)
        # Rank-biserial effect size
        n1, n2 = len(s_vals), len(ns_vals)
        rb = 1 - (2 * u_stat) / (n1 * n2)
        print(f"  {label:<16} {s_mean:>10.4f} {ns_mean:>10.4f} {u_stat:>8.0f} {p_mw:>10.4f} {sig:>5}")
        s3_results[dim] = {'stars_r1_mean': float(s_mean), 'ns_r1_mean': float(ns_mean),
                           'u_stat': float(u_stat), 'p': float(p_mw), 'rank_biserial': float(rb)}
    else:
        print(f"  {label:<16} {'(insufficient data)'}")

print(f"\n  Significant dimensions: {s3_sig_count}/{len(dimensions)}")

if s3_sig_count >= 3:
    s3_verdict = "PASS_DIVERGENT"
elif s3_sig_count >= 1:
    s3_verdict = "PARTIAL_DIVERGENCE"
else:
    s3_verdict = "FAIL_IDENTICAL"

s3_data = {'dimensions': s3_results, 'sig_count': s3_sig_count,
           'n_stars_r1': len(stars_r1_profiles), 'n_non_stars_r1': len(non_stars_r1_profiles)}

print(f"\nS3 VERDICT: {s3_verdict}")
print()


# ===================================================================
# S4: CC TRIGGER DECOMPOSITION
# ===================================================================
print("-" * 70)
print("S4: CC Trigger Decomposition (Stars vs Non-Stars)")
print("-" * 70)
print()

stars_cc, stars_cc_n = count_cc_triggers(stars_folios)
non_stars_cc, non_stars_cc_n = count_cc_triggers(non_stars_folios)

print(f"  CC trigger events: Stars={stars_cc_n}, Non-Stars={non_stars_cc_n}")
print()

cc_types = sorted(set(list(stars_cc.keys()) + list(non_stars_cc.keys())))

print(f"  {'Trigger Type':<20} {'Stars':>6} {'S%':>7} {'Non-Stars':>9} {'NS%':>7}")
print(f"  {'-'*20} {'-'*6} {'-'*7} {'-'*9} {'-'*7}")

s4_trigger_data = {}
for ct in cc_types:
    sc = stars_cc.get(ct, 0)
    nsc = non_stars_cc.get(ct, 0)
    sp = 100 * sc / stars_cc_n if stars_cc_n > 0 else 0
    nsp = 100 * nsc / non_stars_cc_n if non_stars_cc_n > 0 else 0
    print(f"  {ct:<20} {sc:>6} {sp:>6.1f}% {nsc:>9} {nsp:>6.1f}%")
    s4_trigger_data[ct] = {'stars': int(sc), 'non_stars': int(nsc), 'stars_pct': sp, 'non_stars_pct': nsp}

s_vec4 = [stars_cc.get(ct, 0) for ct in cc_types]
ns_vec4 = [non_stars_cc.get(ct, 0) for ct in cc_types]
ct_s4 = np.array([s_vec4, ns_vec4])
col_mask4 = ct_s4.sum(axis=0) > 0
ct_s4_valid = ct_s4[:, col_mask4]

s4_chi2, s4_p = 0, 1.0
if ct_s4_valid.shape[1] >= 2:
    s4_chi2, s4_p, s4_dof, _ = sp_stats.chi2_contingency(ct_s4_valid)
    s4_v = np.sqrt(s4_chi2 / (ct_s4_valid.sum() * (min(ct_s4_valid.shape) - 1)))
    print(f"\n  Chi-square: chi2={s4_chi2:.1f}, dof={s4_dof}, p={s4_p:.2e}, Cramer's V={s4_v:.4f}")

if s4_p < ALPHA_BONFERRONI:
    s4_verdict = "PASS_DIFFERENT_TRIGGERS"
elif s4_p < 0.05:
    s4_verdict = "MARGINAL_DIFFERENT"
else:
    s4_verdict = "FAIL_SAME_TRIGGERS"

s4_data = {'chi2': s4_chi2, 'p': s4_p, 'trigger_distribution': s4_trigger_data}

print(f"\nS4 VERDICT: {s4_verdict}")
print()


# ===================================================================
# S5: LINK DENSITY DIFFERENTIATION
# ===================================================================
print("-" * 70)
print("S5: LINK Density Differentiation (Stars vs Non-Stars)")
print("-" * 70)
print()

stars_link_vals = [all_profiles[f]['link_pct'] for f in stars_folios if f in all_profiles]
non_stars_link_vals = [all_profiles[f]['link_pct'] for f in non_stars_folios if f in all_profiles]

s_link_mean = np.mean(stars_link_vals)
ns_link_mean = np.mean(non_stars_link_vals)
print(f"  Stars LINK density: {s_link_mean:.4f} (n={len(stars_link_vals)})")
print(f"  Non-Stars LINK density: {ns_link_mean:.4f} (n={len(non_stars_link_vals)})")

u_s5, p_s5 = sp_stats.mannwhitneyu(stars_link_vals, non_stars_link_vals, alternative='two-sided')
n1, n2 = len(stars_link_vals), len(non_stars_link_vals)
rb_s5 = 1 - (2 * u_s5) / (n1 * n2)
print(f"  Mann-Whitney U={u_s5:.0f}, p={p_s5:.4f}, rank-biserial r={rb_s5:.3f}")

# REGIME_1 controlled
if stars_r1 and non_stars_r1:
    s_r1_link = [all_profiles[f]['link_pct'] for f in stars_r1 if f in all_profiles]
    ns_r1_link = [all_profiles[f]['link_pct'] for f in non_stars_r1 if f in all_profiles]
    if len(s_r1_link) >= 3 and len(ns_r1_link) >= 3:
        u_r1, p_r1_link = sp_stats.mannwhitneyu(s_r1_link, ns_r1_link, alternative='two-sided')
        print(f"  REGIME_1 controlled: Stars_R1={np.mean(s_r1_link):.4f}, NS_R1={np.mean(ns_r1_link):.4f}, p={p_r1_link:.4f}")

if p_s5 < ALPHA_BONFERRONI:
    s5_verdict = "PASS_DISTINCT_LINK"
elif p_s5 < 0.05:
    s5_verdict = "MARGINAL_LINK"
else:
    s5_verdict = "FAIL_SAME"

s5_data = {'stars_mean': s_link_mean, 'non_stars_mean': ns_link_mean,
           'u_stat': float(u_s5), 'p': float(p_s5), 'rank_biserial': float(rb_s5)}

print(f"\nS5 VERDICT: {s5_verdict}")
print()


# ===================================================================
# S6: VOCABULARY SPECIALIZATION
# ===================================================================
print("-" * 70)
print("S6: Vocabulary Specialization (Stars-R1 vs Non-Stars-R1)")
print("-" * 70)
print()

# Type-token ratio
s_ttr = [all_profiles[f]['ttr'] for f in stars_r1 if f in all_profiles]
ns_ttr = [all_profiles[f]['ttr'] for f in non_stars_r1 if f in all_profiles]

s_ttr_mean = np.mean(s_ttr) if s_ttr else 0
ns_ttr_mean = np.mean(ns_ttr) if ns_ttr else 0
print(f"  Type-Token Ratio (REGIME_1):")
print(f"    Stars_R1: {s_ttr_mean:.4f} (n={len(s_ttr)})")
print(f"    Non-Stars_R1: {ns_ttr_mean:.4f} (n={len(ns_ttr)})")

ttr_p = 1.0
if len(s_ttr) >= 3 and len(ns_ttr) >= 3:
    u_ttr, ttr_p = sp_stats.mannwhitneyu(s_ttr, ns_ttr, alternative='two-sided')
    print(f"    Mann-Whitney p={ttr_p:.4f}")

# e-kernel fraction
s_efrac = [all_profiles[f]['e_kernel_fraction'] for f in stars_r1 if f in all_profiles]
ns_efrac = [all_profiles[f]['e_kernel_fraction'] for f in non_stars_r1 if f in all_profiles]

s_efrac_mean = np.mean(s_efrac) if s_efrac else 0
ns_efrac_mean = np.mean(ns_efrac) if ns_efrac else 0
print(f"\n  e-Kernel Fraction (REGIME_1):")
print(f"    Stars_R1: {s_efrac_mean:.4f} (n={len(s_efrac)})")
print(f"    Non-Stars_R1: {ns_efrac_mean:.4f} (n={len(ns_efrac)})")

efrac_p = 1.0
if len(s_efrac) >= 3 and len(ns_efrac) >= 3:
    u_efrac, efrac_p = sp_stats.mannwhitneyu(s_efrac, ns_efrac, alternative='two-sided')
    print(f"    Mann-Whitney p={efrac_p:.4f}")

ttr_sig = ttr_p < 0.05
efrac_sig = efrac_p < 0.05

if ttr_sig and efrac_sig:
    s6_verdict = "PASS_SPECIALIZED"
elif ttr_sig or efrac_sig:
    s6_verdict = "PARTIAL_SPECIALIZED"
else:
    s6_verdict = "FAIL_SAME"

s6_data = {
    'ttr_test': {'stars_r1_mean': s_ttr_mean, 'ns_r1_mean': ns_ttr_mean, 'p': ttr_p},
    'e_fraction_test': {'stars_r1_mean': s_efrac_mean, 'ns_r1_mean': ns_efrac_mean, 'p': efrac_p},
}

print(f"\nS6 VERDICT: {s6_verdict}")
print()


# ===================================================================
# S7: INTRA-REGIME AXM CONVERGENCE (KEY TEST)
# ===================================================================
print("-" * 70)
print("S7: Intra-REGIME AXM Convergence (KEY TEST)")
print("-" * 70)
print()

s7_regime_results = {}

for regime_name, s_set, ns_set in [('REGIME_1', stars_r1, non_stars_r1),
                                     ('REGIME_3', stars_r3, non_stars_r3)]:
    s_axm = [all_profiles[f]['axm_self'] for f in s_set
             if f in all_profiles and all_profiles[f]['axm_self'] is not None]
    ns_axm = [all_profiles[f]['axm_self'] for f in ns_set
              if f in all_profiles and all_profiles[f]['axm_self'] is not None]

    if len(s_axm) >= 3 and len(ns_axm) >= 3:
        s_var = np.var(s_axm, ddof=1)
        ns_var = np.var(ns_axm, ddof=1)
        ratio = s_var / ns_var if ns_var > 0 else float('inf')

        # Levene's test (Brown-Forsythe: median-based)
        lev_stat, lev_p = sp_stats.levene(s_axm, ns_axm, center='median')

        print(f"  {regime_name}:")
        print(f"    Stars: n={len(s_axm)}, mean={np.mean(s_axm):.4f}, var={s_var:.6f}")
        print(f"    Non-Stars: n={len(ns_axm)}, mean={np.mean(ns_axm):.4f}, var={ns_var:.6f}")
        print(f"    Variance ratio (Stars/NS): {ratio:.3f}")
        print(f"    Levene's test: W={lev_stat:.3f}, p={lev_p:.4f}")
        print()

        s7_regime_results[regime_name] = {
            'stars_n': len(s_axm), 'non_stars_n': len(ns_axm),
            'stars_mean': float(np.mean(s_axm)), 'non_stars_mean': float(np.mean(ns_axm)),
            'stars_var': float(s_var), 'non_stars_var': float(ns_var),
            'variance_ratio': float(ratio),
            'levene_stat': float(lev_stat), 'levene_p': float(lev_p),
        }
    else:
        print(f"  {regime_name}: insufficient data (Stars n={len(s_axm)}, NS n={len(ns_axm)})")
        s7_regime_results[regime_name] = {'note': 'insufficient data'}

# Verdict: check R1 and R3 ratios
r1_result = s7_regime_results.get('REGIME_1', {})
r3_result = s7_regime_results.get('REGIME_3', {})

r1_ratio = r1_result.get('variance_ratio', 999)
r3_ratio = r3_result.get('variance_ratio', 999)

if r1_ratio < 0.5 and r3_ratio < 1.0:
    s7_verdict = "PASS_CLAMPED"
elif r1_ratio < 1.0 and r3_ratio < 1.0:
    s7_verdict = "PARTIAL_CLAMPED"
else:
    s7_verdict = "FAIL_NOT_CLAMPED"

# Bayes Factor approximation (using variance ratio as effect)
# BF01 via Bayesian interpretation of F-test
if 'stars_var' in r1_result and 'non_stars_var' in r1_result:
    # Simplified: use p-value calibration (Sellke et al. 2001)
    # BF01 ≈ -1/(e * p * ln(p)) for p < 1/e
    r1_p = r1_result.get('levene_p', 1.0)
    if r1_p > 0 and r1_p < 1.0 / np.e:
        bf01 = -1.0 / (np.e * r1_p * np.log(r1_p))
    else:
        bf01 = 1.0  # No evidence either way
    s7_regime_results['bf01_r1'] = float(bf01)
    print(f"  Bayes Factor (BF01, R1): {bf01:.2f}")

s7_data = {'regime_results': s7_regime_results}

print(f"\nS7 VERDICT: {s7_verdict}")
print()


# ===================================================================
# S8: e-STABILITY CLAMPING MEDIATION
# ===================================================================
print("-" * 70)
print("S8: e-Stability Clamping Mediation")
print("-" * 70)
print()

# Within Stars: e-kernel fraction vs |AXM deviation from Stars mean|
stars_axm_vals = [all_profiles[f]['axm_self'] for f in stars_folios
                  if f in all_profiles and all_profiles[f]['axm_self'] is not None]
stars_mean_axm = np.mean(stars_axm_vals) if stars_axm_vals else 0

stars_efrac_vals = []
stars_axm_dev_vals = []
for f in stars_folios:
    if f in all_profiles and all_profiles[f]['axm_self'] is not None:
        stars_efrac_vals.append(all_profiles[f]['e_kernel_fraction'])
        stars_axm_dev_vals.append(abs(all_profiles[f]['axm_self'] - stars_mean_axm))

s8_rho, s8_p = 0, 1.0
if len(stars_efrac_vals) >= 5:
    s8_rho, s8_p = sp_stats.spearmanr(stars_efrac_vals, stars_axm_dev_vals)
    print(f"  Within Stars: Spearman rho(e_frac, |AXM_dev|) = {s8_rho:.3f}, p={s8_p:.4f}")
    print(f"  Prediction: rho < -0.20 (higher e -> less AXM deviation)")

# Mediation test: section → AXM variance, controlled by e-fraction
# Use all B/H/S folios
all_folios_bhs = list(stars_folios | non_stars_folios)
section_indicator = []
e_fracs = []
axm_vars = []  # Use |deviation from section mean| as proxy for per-folio variance contribution

# Compute section means
section_axm_means = {}
for s in ['S', 'B', 'H']:
    s_folios_here = [f for f in all_folios_bhs if folio_section.get(f) == s]
    s_axm_here = [all_profiles[f]['axm_self'] for f in s_folios_here
                  if f in all_profiles and all_profiles[f]['axm_self'] is not None]
    if s_axm_here:
        section_axm_means[s] = np.mean(s_axm_here)

for f in all_folios_bhs:
    if f in all_profiles and all_profiles[f]['axm_self'] is not None:
        s = folio_section.get(f)
        if s in section_axm_means:
            section_indicator.append(1 if s == 'S' else 0)
            e_fracs.append(all_profiles[f]['e_kernel_fraction'])
            axm_vars.append(abs(all_profiles[f]['axm_self'] - section_axm_means[s]))

s8_mediation_pct = 0
if len(section_indicator) >= 10:
    section_indicator = np.array(section_indicator)
    e_fracs = np.array(e_fracs)
    axm_vars = np.array(axm_vars)

    # Step 1: AXM_dev ~ section (Stars indicator)
    from numpy.linalg import lstsq
    X1 = np.column_stack([np.ones(len(section_indicator)), section_indicator])
    beta1, _, _, _ = lstsq(X1, axm_vars, rcond=None)
    stars_coeff_1 = beta1[1]

    # Step 2: AXM_dev ~ section + e_frac
    X2 = np.column_stack([np.ones(len(section_indicator)), section_indicator, e_fracs])
    beta2, _, _, _ = lstsq(X2, axm_vars, rcond=None)
    stars_coeff_2 = beta2[1]

    if abs(stars_coeff_1) > 0.0001:
        s8_mediation_pct = 100 * (1 - abs(stars_coeff_2) / abs(stars_coeff_1))
    else:
        s8_mediation_pct = 0

    print(f"\n  Mediation analysis (all B/H/S folios):")
    print(f"    Step 1: Stars coeff = {stars_coeff_1:.4f}")
    print(f"    Step 2: Stars coeff (controlling e-frac) = {stars_coeff_2:.4f}")
    print(f"    Coefficient reduction: {s8_mediation_pct:.1f}%")

if s8_rho < -0.20 and s8_mediation_pct > 50:
    s8_verdict = "PASS_MEDIATED"
elif s8_rho < -0.20 or s8_mediation_pct > 50:
    s8_verdict = "PARTIAL_MEDIATION"
else:
    s8_verdict = "FAIL_NO_MEDIATION"

s8_data = {'rho': float(s8_rho), 'p': float(s8_p),
           'mediation_coefficient_reduction': float(s8_mediation_pct),
           'stars_mean_axm': float(stars_mean_axm)}

print(f"\nS8 VERDICT: {s8_verdict}")
print()


# ===================================================================
# S9: BRIDGE BOTTLENECK CLAMPING
# ===================================================================
print("-" * 70)
print("S9: Bridge Bottleneck Clamping")
print("-" * 70)
print()

# Within Stars: bridge density vs |c1017_residual|
stars_bridge = []
stars_resid = []
for f in stars_folios:
    if f in bridge_folio_data and f in axm_folio_data:
        bd = bridge_folio_data[f].get('bridge_density')
        resid = axm_folio_data[f].get('c1017_residual')
        if bd is not None and resid is not None:
            stars_bridge.append(bd)
            stars_resid.append(abs(resid))

s9_rho, s9_p = 0, 1.0
if len(stars_bridge) >= 5:
    s9_rho, s9_p = sp_stats.spearmanr(stars_bridge, stars_resid)
    print(f"  Within Stars: Spearman rho(bridge_density, |c1017_resid|) = {s9_rho:.3f}, p={s9_p:.4f}")
    print(f"  C1104 overall rho = +0.277 (reference)")

# Bridge mediation: does bridge density explain Stars vs non-Stars variance gap?
all_bridge = []
all_resid = []
all_is_stars = []
for f in stars_folios | non_stars_folios:
    if f in bridge_folio_data and f in axm_folio_data:
        bd = bridge_folio_data[f].get('bridge_density')
        resid = axm_folio_data[f].get('c1017_residual')
        if bd is not None and resid is not None:
            all_bridge.append(bd)
            all_resid.append(abs(resid))
            all_is_stars.append(1 if f in stars_folios else 0)

s9_mediation_pct = 0
if len(all_bridge) >= 10:
    all_bridge = np.array(all_bridge)
    all_resid = np.array(all_resid)
    all_is_stars = np.array(all_is_stars)

    # Step 1: |resid| ~ is_stars
    X1 = np.column_stack([np.ones(len(all_is_stars)), all_is_stars])
    beta1, _, _, _ = lstsq(X1, all_resid, rcond=None)
    stars_coeff_1 = beta1[1]

    # Step 2: |resid| ~ is_stars + bridge_density
    X2 = np.column_stack([np.ones(len(all_is_stars)), all_is_stars, all_bridge])
    beta2, _, _, _ = lstsq(X2, all_resid, rcond=None)
    stars_coeff_2 = beta2[1]

    if abs(stars_coeff_1) > 0.0001:
        s9_mediation_pct = 100 * (1 - abs(stars_coeff_2) / abs(stars_coeff_1))
    else:
        s9_mediation_pct = 0

    print(f"\n  Bridge mediation (Stars vs non-Stars |residual|):")
    print(f"    Step 1: Stars coeff = {stars_coeff_1:.4f}")
    print(f"    Step 2: Stars coeff (controlling bridge) = {stars_coeff_2:.4f}")
    print(f"    Coefficient reduction: {s9_mediation_pct:.1f}%")

if s9_rho > 0 and s9_mediation_pct > 30:
    s9_verdict = "PASS_BOTTLENECK"
elif s9_rho > 0:
    s9_verdict = "PARTIAL_BOTTLENECK"
else:
    s9_verdict = "FAIL_NO_BOTTLENECK"

s9_data = {'stars_rho': float(s9_rho), 'stars_p': float(s9_p),
           'bridge_mediation_pct': float(s9_mediation_pct)}

print(f"\nS9 VERDICT: {s9_verdict}")
print()


# ===================================================================
# S10: CROSS-REGIME VOCABULARY HOMOGENEITY
# ===================================================================
print("-" * 70)
print("S10: Cross-REGIME Vocabulary Homogeneity")
print("-" * 70)
print()

# Cross-REGIME Jaccard: Stars R1<->R3 vs non-Stars R1<->R3
def mean_cross_jaccard(set_a_folios, set_b_folios):
    """Mean Jaccard similarity between all pairs from two folio sets."""
    jaccards = []
    for fa in set_a_folios:
        for fb in set_b_folios:
            if fa in folio_middle_sets and fb in folio_middle_sets:
                j = jaccard(folio_middle_sets[fa], folio_middle_sets[fb])
                jaccards.append(j)
    return np.mean(jaccards) if jaccards else 0.0, jaccards

stars_cross_j, stars_cross_jvals = mean_cross_jaccard(stars_r1, stars_r3)
ns_cross_j, ns_cross_jvals = mean_cross_jaccard(non_stars_r1, non_stars_r3)

print(f"  Stars R1<->R3 cross-REGIME Jaccard: {stars_cross_j:.4f} (n_pairs={len(stars_cross_jvals)})")
print(f"  Non-Stars R1<->R3 cross-REGIME Jaccard: {ns_cross_j:.4f} (n_pairs={len(ns_cross_jvals)})")

# Within-REGIME Jaccard for reference
stars_within_r1_j, _ = mean_cross_jaccard(list(stars_r1)[:len(stars_r1)//2],
                                           list(stars_r1)[len(stars_r1)//2:])
ns_within_r1_j, _ = mean_cross_jaccard(list(non_stars_r1)[:len(non_stars_r1)//2],
                                         list(non_stars_r1)[len(non_stars_r1)//2:])

# Permutation test: is Stars cross-REGIME Jaccard > non-Stars?
observed_diff = stars_cross_j - ns_cross_j
print(f"\n  Observed difference: {observed_diff:.4f}")

# Pool all cross-REGIME Jaccard values and permute
all_cross_jvals = stars_cross_jvals + ns_cross_jvals
n_stars_j = len(stars_cross_jvals)
n_total_j = len(all_cross_jvals)

n_perms = 1000
perm_count = 0
rng = np.random.RandomState(42)

if n_total_j > 0:
    all_j_arr = np.array(all_cross_jvals)
    for _ in range(n_perms):
        perm_idx = rng.permutation(n_total_j)
        perm_stars = np.mean(all_j_arr[perm_idx[:n_stars_j]])
        perm_ns = np.mean(all_j_arr[perm_idx[n_stars_j:]])
        if perm_stars - perm_ns >= observed_diff:
            perm_count += 1

    perm_p = (perm_count + 1) / (n_perms + 1)
    print(f"  Permutation test (1000 iters): p={perm_p:.4f}")
else:
    perm_p = 1.0

if perm_p < ALPHA_BONFERRONI and observed_diff > 0:
    s10_verdict = "PASS_HOMOGENEOUS"
elif perm_p < 0.05 and observed_diff > 0:
    s10_verdict = "MARGINAL_HOMOGENEOUS"
else:
    s10_verdict = "FAIL_HETEROGENEOUS"

s10_data = {
    'stars_cross_regime_jaccard': float(stars_cross_j),
    'non_stars_cross_regime_jaccard': float(ns_cross_j),
    'observed_diff': float(observed_diff),
    'permutation_p': float(perm_p),
    'n_stars_pairs': len(stars_cross_jvals),
    'n_non_stars_pairs': len(ns_cross_jvals),
}

print(f"\nS10 VERDICT: {s10_verdict}")
print()


# ===================================================================
# SYNTHESIS
# ===================================================================
print("=" * 70)
print("PHASE 392 SYNTHESIS")
print("=" * 70)
print()

verdicts = {
    'S1': s1_verdict, 'S2': s2_verdict, 'S3': s3_verdict, 'S4': s4_verdict,
    'S5': s5_verdict, 'S6': s6_verdict,
    'S7': s7_verdict, 'S8': s8_verdict, 'S9': s9_verdict, 'S10': s10_verdict,
}

for k, v in verdicts.items():
    print(f"  {k}: {v}")
print()

# Mirror battery (S1-S4): count PASS
mirror_pass = sum(1 for k in ['S1', 'S2', 'S3', 'S4'] if 'PASS' in verdicts[k])
mirror_marginal = sum(1 for k in ['S1', 'S2', 'S3', 'S4'] if 'MARGINAL' in verdicts[k])
mirror_fail = sum(1 for k in ['S1', 'S2', 'S3', 'S4'] if 'FAIL' in verdicts[k])

# Clamping tests (S7-S10): count PASS
clamping_pass = sum(1 for k in ['S7', 'S8', 'S9', 'S10'] if 'PASS' in verdicts[k])
clamping_partial = sum(1 for k in ['S7', 'S8', 'S9', 'S10'] if 'PARTIAL' in verdicts[k])
clamping_fail = sum(1 for k in ['S7', 'S8', 'S9', 'S10'] if 'FAIL' in verdicts[k])

print(f"Mirror battery (S1-S4): {mirror_pass} PASS, {mirror_marginal} MARGINAL, {mirror_fail} FAIL")
print(f"Clamping tests (S7-S10): {clamping_pass} PASS, {clamping_partial} PARTIAL, {clamping_fail} FAIL")
print()

if mirror_pass + mirror_marginal >= 2 and clamping_pass + clamping_partial >= 3:
    overall = "CONVERGENT_CLAMPING"
    summary = ("Stars is structurally distinct AND dynamically clamped by vocabulary composition. "
               "The Stars Paradox (most REGIME diversity, lowest AXM variance) is explained by "
               "low bridge density restricting the behavioral option space.")
elif mirror_pass + mirror_marginal >= 3 and clamping_pass + clamping_partial <= 1:
    overall = "STARS_DISTINCT_UNCLAMPED"
    summary = ("Stars is structurally distinct but no vocabulary clamping mechanism found. "
               "The Stars Paradox remains unexplained.")
elif mirror_pass + mirror_marginal <= 1:
    overall = "REGIME_SUFFICIENT"
    summary = ("Stars distinctiveness is entirely explained by REGIME composition. "
               "Not a real section effect.")
else:
    overall = "INCONCLUSIVE"
    summary = "Mixed results. Stars shows some distinctiveness but clamping evidence is partial."

print(f"OVERALL VERDICT: {overall}")
print(f"  {summary}")
print()

# Build folio-level data
folio_output = {}
for f in sorted(stars_folios | non_stars_folios):
    entry = {
        'section': folio_section.get(f, '?'),
        'regime': folio_regime.get(f, '?'),
    }
    if f in all_profiles:
        for k, v in all_profiles[f].items():
            entry[k] = v
    if f in bridge_folio_data:
        entry['bridge_density'] = bridge_folio_data[f].get('bridge_density')
    if f in axm_folio_data:
        entry['c1017_residual'] = axm_folio_data[f].get('c1017_residual')
    folio_output[f] = entry

# Assemble results
results = round_floats({
    'phase': 392,
    'name': 'STARS_RECIPE_CHARACTERIZATION',
    'test_count': 10,
    'n_stars': len(stars_folios),
    'n_non_stars': len(non_stars_folios),
    'alpha_bonferroni': ALPHA_BONFERRONI,
    'stars_token_count': stars_token_count,
    'non_stars_token_count': non_stars_token_count,
    'stars_regime_distribution': dict(stars_regimes),
    'non_stars_regime_distribution': dict(non_stars_regimes),
    'regime_matched_n': {
        'REGIME_1': {'stars': len(stars_r1), 'non_stars': len(non_stars_r1)},
        'REGIME_3': {'stars': len(stars_r3), 'non_stars': len(non_stars_r3)},
    },
    'verdicts': verdicts,
    'S1_data': s1_data,
    'S2_data': s2_data,
    'S3_data': s3_data,
    'S4_data': s4_data,
    'S5_data': s5_data,
    'S6_data': s6_data,
    'S7_data': s7_data,
    'S8_data': s8_data,
    'S9_data': s9_data,
    'S10_data': s10_data,
    'folio_data': folio_output,
    'synthesis': {
        'mirror_pass': mirror_pass,
        'mirror_marginal': mirror_marginal,
        'mirror_fail': mirror_fail,
        'clamping_pass': clamping_pass,
        'clamping_partial': clamping_partial,
        'clamping_fail': clamping_fail,
        'overall': overall,
        'summary': summary,
    },
})

output_path = RESULTS / 'stars_recipe_characterization.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {output_path}")
