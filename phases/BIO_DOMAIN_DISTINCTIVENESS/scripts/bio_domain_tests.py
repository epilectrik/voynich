#!/usr/bin/env python3
"""
Phase 385: Bio Section Operational Distinctiveness -- 4-test battery

Tests whether the Bio section (f74-f84) encodes a structurally distinct
application domain from the rest of the manuscript, or whether its
unique coherence (C1048: LOO R2=0.754) reflects a specific stage
(balneum mariae) within a single distillation domain.

Tests:
  T1: Kernel Balance Partition (Bio vs non-Bio k/h/e ratios)
  T2: Hazard Profile Partition (hazard class distribution by section)
  T3: REGIME_1 Homogeneity (Bio REGIME_1 vs non-Bio REGIME_1)
  T4: CC Trigger Decomposition (control-loop entry patterns by section)

Pre-registered alternative: If Bio's kernel, hazard, and REGIME_1
profiles match non-Bio REGIME_1 folios, Bio = balneum mariae stage.
If they diverge on 2+/3 core tests, Bio may encode a distinct domain.

Grounding constraints:
  C103-C105 (kernel operators), C109 (5 hazard classes),
  C552/C553 (section role profiles), C600 (CC triggers),
  C1048 (Bio LOO R2=0.754), C1084 (section AXM ordering)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, BFolioDecoder,
                              BTokenAnalysis)

RESULTS = ROOT / "phases" / "BIO_DOMAIN_DISTINCTIVENESS" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

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
HAZARD_TARGETS = set(b for a, b in FORBIDDEN_TRANSITIONS)
HAZARD_WORDS = HAZARD_SOURCES | HAZARD_TARGETS

# ===================================================================
# Initialize
# ===================================================================
print("=" * 70)
print("PHASE 385: BIO SECTION OPERATIONAL DISTINCTIVENESS")
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

# Build token lists per folio
folio_tokens = defaultdict(list)
folio_section = {}
all_b_tokens = []

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens[tok.folio].append(tok)
    all_b_tokens.append(tok)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

# Partition: Bio vs non-Bio
bio_folios = set(f for f, s in folio_section.items() if s == 'B')
non_bio_folios = set(f for f, s in folio_section.items() if s != 'B')

bio_token_count = sum(len(folio_tokens[f]) for f in bio_folios)
non_bio_token_count = sum(len(folio_tokens[f]) for f in non_bio_folios)

print(f"Bio folios: {len(bio_folios)} ({bio_token_count} tokens)")
print(f"Non-Bio folios: {len(non_bio_folios)} ({non_bio_token_count} tokens)")
print(f"Bio sections: {Counter(folio_section[f] for f in bio_folios)}")
print(f"Non-Bio sections: {Counter(folio_section[f] for f in non_bio_folios)}")
print()

# REGIME distribution
bio_regimes = Counter(folio_regime.get(f, 'X') for f in bio_folios)
non_bio_regimes = Counter(folio_regime.get(f, 'X') for f in non_bio_folios)
print(f"Bio REGIME distribution: {dict(bio_regimes)}")
print(f"Non-Bio REGIME distribution: {dict(non_bio_regimes)}")
print()


# ===================================================================
# TEST 1: KERNEL BALANCE PARTITION
# ===================================================================
# If Bio encodes a different domain (medical treatment), kernel ratios
# should differ: elevated h (patient monitoring), elevated e (stability),
# reduced k (less direct heating).
# If Bio = balneum mariae: k should be ELEVATED (sustained heating).
# ===================================================================
print("-" * 70)
print("TEST 1: Kernel Balance Partition (Bio vs Non-Bio)")
print("  Multi-domain prediction: Bio has elevated h+e, reduced k")
print("  Balneum mariae prediction: Bio has elevated k (sustained heating)")
print("-" * 70)
print()

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

bio_kernels, bio_tok_n = count_kernels(bio_folios)
non_bio_kernels, non_bio_tok_n = count_kernels(non_bio_folios)

# Per-token rates
bio_total_k = sum(bio_kernels.values())
non_bio_total_k = sum(non_bio_kernels.values())

print(f"  {'Kernel':<8} {'Bio':>10} {'Bio%':>8} {'Non-Bio':>10} {'Non-Bio%':>8} {'Ratio':>8}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*8} {'-'*8}")

t1_data = {}
for k in ['k', 'h', 'e']:
    bio_pct = 100 * bio_kernels[k] / bio_total_k if bio_total_k > 0 else 0
    non_bio_pct = 100 * non_bio_kernels[k] / non_bio_total_k if non_bio_total_k > 0 else 0
    ratio = bio_pct / non_bio_pct if non_bio_pct > 0 else 0
    print(f"  {k:<8} {bio_kernels[k]:>10} {bio_pct:>7.1f}% {non_bio_kernels[k]:>10} {non_bio_pct:>7.1f}% {ratio:>7.2f}x")
    t1_data[k] = {'bio': bio_kernels[k], 'non_bio': non_bio_kernels[k],
                   'bio_pct': bio_pct, 'non_bio_pct': non_bio_pct, 'ratio': ratio}

# Chi-square: do Bio and non-Bio have different kernel distributions?
contingency = np.array([
    [bio_kernels['k'], bio_kernels['h'], bio_kernels['e']],
    [non_bio_kernels['k'], non_bio_kernels['h'], non_bio_kernels['e']]
])
chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
print(f"\n  Chi-square (kernel distribution): chi2={chi2:.1f}, dof={dof}, p={p_val:.2e}")

# Effect size: Cramer's V
n_total = contingency.sum()
v = np.sqrt(chi2 / (n_total * (min(contingency.shape) - 1)))
print(f"  Cramer's V = {v:.4f}")

# Interpret direction
k_ratio = t1_data['k']['ratio']
h_ratio = t1_data['h']['ratio']
e_ratio = t1_data['e']['ratio']

if p_val < 0.05:
    if k_ratio > 1.1 and h_ratio < 0.95:
        t1_direction = "BALNEUM_MARIAE"
        print(f"  -> Bio is k-enriched: consistent with SUSTAINED HEATING (balneum mariae)")
    elif h_ratio > 1.1 and k_ratio < 0.95:
        t1_direction = "MULTI_DOMAIN"
        print(f"  -> Bio is h-enriched: consistent with PATIENT MONITORING (multi-domain)")
    elif e_ratio > 1.1:
        t1_direction = "STABILITY_FOCUSED"
        print(f"  -> Bio is e-enriched: consistent with MAINTENANCE/STABILITY focus")
    else:
        t1_direction = "MIXED"
        print(f"  -> Mixed kernel shift: no clear domain signature")
    t1_verdict = f"SIGNIFICANT_{t1_direction}"
else:
    t1_direction = "NULL"
    t1_verdict = "FAIL_NULL"
    print(f"  -> NOT SIGNIFICANT: Bio kernel ratios match non-Bio")

# REGIME-controlled: compare Bio REGIME_1 vs non-Bio REGIME_1
print(f"\n  REGIME-controlled (REGIME_1 only):")
bio_r1 = set(f for f in bio_folios if folio_regime.get(f) == 'REGIME_1')
non_bio_r1 = set(f for f in non_bio_folios if folio_regime.get(f) == 'REGIME_1')
print(f"  Bio REGIME_1: {len(bio_r1)} folios, Non-Bio REGIME_1: {len(non_bio_r1)} folios")

if bio_r1 and non_bio_r1:
    bio_r1_k, _ = count_kernels(bio_r1)
    non_bio_r1_k, _ = count_kernels(non_bio_r1)
    bio_r1_tot = sum(bio_r1_k.values())
    nb_r1_tot = sum(non_bio_r1_k.values())

    for k in ['k', 'h', 'e']:
        bp = 100 * bio_r1_k[k] / bio_r1_tot if bio_r1_tot > 0 else 0
        nbp = 100 * non_bio_r1_k[k] / nb_r1_tot if nb_r1_tot > 0 else 0
        print(f"    {k}: Bio_R1={bp:.1f}% Non-Bio_R1={nbp:.1f}%")

    ct_r1 = np.array([
        [bio_r1_k['k'], bio_r1_k['h'], bio_r1_k['e']],
        [non_bio_r1_k['k'], non_bio_r1_k['h'], non_bio_r1_k['e']]
    ])
    chi2_r1, p_r1, _, _ = sp_stats.chi2_contingency(ct_r1)
    print(f"    Chi-square (REGIME_1 only): chi2={chi2_r1:.1f}, p={p_r1:.2e}")

print(f"\nT1 VERDICT: {t1_verdict}")
print()


# ===================================================================
# TEST 2: HAZARD PROFILE PARTITION
# ===================================================================
# Compare distribution of 5 hazard classes in Bio vs non-Bio.
# Multi-domain: Bio has fewer CONTAINMENT_TIMING, RATE_MISMATCH
# (apparatus-specific). Balneum mariae: similar distribution.
# ===================================================================
print("-" * 70)
print("TEST 2: Hazard Profile Partition (Bio vs Non-Bio)")
print("  Multi-domain: Bio has fewer apparatus-specific hazards")
print("  Null: same hazard class distribution everywhere")
print("-" * 70)
print()

# Count hazard-adjacent tokens by class and section
def count_hazard_proximity(folio_set):
    """Count tokens within 2 positions of each hazard source, by class."""
    class_counts = Counter()
    total_transitions = 0
    for folio in folio_set:
        words = [t.word for t in folio_tokens[folio]]
        for i, w in enumerate(words):
            if w in HAZARD_SOURCES:
                # Find which hazard classes this source participates in
                for (a, b), hclass in HAZARD_CLASSES.items():
                    if a == w:
                        class_counts[hclass] += 1
                        total_transitions += 1
    return class_counts, total_transitions

bio_hazards, bio_haz_n = count_hazard_proximity(bio_folios)
non_bio_hazards, non_bio_haz_n = count_hazard_proximity(non_bio_folios)

print(f"  Hazard source events: Bio={bio_haz_n}, Non-Bio={non_bio_haz_n}")
print()

classes_ordered = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
                   'RATE_MISMATCH', 'ENERGY_OVERSHOOT']

print(f"  {'Class':<22} {'Bio':>6} {'Bio%':>7} {'Non-Bio':>8} {'NB%':>7}")
print(f"  {'-'*22} {'-'*6} {'-'*7} {'-'*8} {'-'*7}")

t2_data = {}
for hc in classes_ordered:
    bc = bio_hazards.get(hc, 0)
    nbc = non_bio_hazards.get(hc, 0)
    bp = 100 * bc / bio_haz_n if bio_haz_n > 0 else 0
    nbp = 100 * nbc / non_bio_haz_n if non_bio_haz_n > 0 else 0
    print(f"  {hc:<22} {bc:>6} {bp:>6.1f}% {nbc:>8} {nbp:>6.1f}%")
    t2_data[hc] = {'bio': bc, 'non_bio': nbc, 'bio_pct': bp, 'non_bio_pct': nbp}

# Chi-square on hazard class distribution
bio_vec = [bio_hazards.get(c, 0) for c in classes_ordered]
non_bio_vec = [non_bio_hazards.get(c, 0) for c in classes_ordered]

# Remove zero-sum columns
ct2 = np.array([bio_vec, non_bio_vec])
col_mask = ct2.sum(axis=0) > 0
ct2_valid = ct2[:, col_mask]

if ct2_valid.shape[1] >= 2:
    chi2_h, p_h, dof_h, _ = sp_stats.chi2_contingency(ct2_valid)
    print(f"\n  Chi-square (hazard class distribution): chi2={chi2_h:.1f}, dof={dof_h}, p={p_h:.4f}")

    # Apparatus-specific test: CONTAINMENT + RATE vs others
    bio_apparatus = bio_hazards.get('CONTAINMENT_TIMING', 0) + bio_hazards.get('RATE_MISMATCH', 0)
    bio_other = bio_haz_n - bio_apparatus
    nb_apparatus = non_bio_hazards.get('CONTAINMENT_TIMING', 0) + non_bio_hazards.get('RATE_MISMATCH', 0)
    nb_other = non_bio_haz_n - nb_apparatus

    if bio_haz_n > 0 and non_bio_haz_n > 0:
        bio_app_pct = 100 * bio_apparatus / bio_haz_n
        nb_app_pct = 100 * nb_apparatus / non_bio_haz_n
        print(f"\n  Apparatus-specific hazards (CONTAINMENT + RATE):")
        print(f"    Bio: {bio_apparatus}/{bio_haz_n} ({bio_app_pct:.1f}%)")
        print(f"    Non-Bio: {nb_apparatus}/{non_bio_haz_n} ({nb_app_pct:.1f}%)")

        ct_app = np.array([[bio_apparatus, bio_other], [nb_apparatus, nb_other]])
        if min(ct_app.sum(axis=0)) > 0 and min(ct_app.sum(axis=1)) > 0:
            odds, p_app = sp_stats.fisher_exact(ct_app)
            print(f"    Fisher exact: OR={odds:.3f}, p={p_app:.4f}")

            if p_app < 0.05 and bio_app_pct < nb_app_pct:
                t2_verdict = "PASS_REDUCED_APPARATUS"
                print(f"    -> Bio has FEWER apparatus hazards (multi-domain supported)")
            elif p_app < 0.05 and bio_app_pct > nb_app_pct:
                t2_verdict = "FAIL_ELEVATED_APPARATUS"
                print(f"    -> Bio has MORE apparatus hazards (opposite of prediction)")
            else:
                t2_verdict = "FAIL_SAME"
                print(f"    -> No significant difference in apparatus hazards")
        else:
            t2_verdict = "UNDERPOWERED"
    else:
        t2_verdict = "UNDERPOWERED"
else:
    t2_verdict = "UNDERPOWERED"
    print("  Insufficient hazard data for comparison")

print(f"\nT2 VERDICT: {t2_verdict}")
print()


# ===================================================================
# TEST 3: REGIME_1 HOMOGENEITY
# ===================================================================
# If Bio's distinctiveness is fully explained by REGIME_1 membership,
# then Bio REGIME_1 and non-Bio REGIME_1 should have identical profiles.
# If Bio has something BEYOND REGIME_1, they should diverge.
# ===================================================================
print("-" * 70)
print("TEST 3: REGIME_1 Homogeneity (Bio-R1 vs Non-Bio-R1)")
print("  Null: Bio = just another REGIME_1 section")
print("  Alternative: Bio diverges from non-Bio REGIME_1")
print("-" * 70)
print()

# Compare multiple profile dimensions between Bio-R1 and non-Bio-R1
def compute_folio_profile(folio):
    """Compute operational profile for a single folio."""
    tokens = folio_tokens[folio]
    words = [t.word for t in tokens]
    n = len(words)
    if n == 0:
        return None

    # Kernel counts
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
    axm_trans = sum(1 for i in range(len(states)-1) if states[i] == 'AXM')
    axm_self = sum(1 for i in range(len(states)-1) if states[i] == 'AXM' and states[i+1] == 'AXM')
    axm_rate = axm_self / axm_trans if axm_trans > 5 else None

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
    }

bio_r1_profiles = {}
non_bio_r1_profiles = {}

for f in bio_r1:
    p = compute_folio_profile(f)
    if p:
        bio_r1_profiles[f] = p

for f in non_bio_r1:
    p = compute_folio_profile(f)
    if p:
        non_bio_r1_profiles[f] = p

print(f"  Bio REGIME_1 folios: {len(bio_r1_profiles)}")
print(f"  Non-Bio REGIME_1 folios: {len(non_bio_r1_profiles)}")
print()

# Compare each profile dimension
dimensions = ['k_pct', 'h_pct', 'e_pct', 'qo_pct', 'chsh_pct',
              'link_pct', 'haz_density', 'axm_self']
dim_labels = ['k kernel%', 'h kernel%', 'e kernel%', 'QO lane%', 'CHSH lane%',
              'LINK lane%', 'Hazard density', 'AXM self-rate']

t3_results = {}
sig_count = 0

print(f"  {'Dimension':<16} {'Bio-R1':>10} {'NB-R1':>10} {'U-stat':>8} {'p-value':>10} {'Sig':>5}")
print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*5}")

for dim, label in zip(dimensions, dim_labels):
    bio_vals = [p[dim] for p in bio_r1_profiles.values() if p[dim] is not None]
    nb_vals = [p[dim] for p in non_bio_r1_profiles.values() if p[dim] is not None]

    if len(bio_vals) >= 3 and len(nb_vals) >= 3:
        u_stat, p_mw = sp_stats.mannwhitneyu(bio_vals, nb_vals, alternative='two-sided')
        sig = "*" if p_mw < 0.05 else ""
        if p_mw < 0.05:
            sig_count += 1
        bio_mean = np.mean(bio_vals)
        nb_mean = np.mean(nb_vals)
        print(f"  {label:<16} {bio_mean:>10.4f} {nb_mean:>10.4f} {u_stat:>8.0f} {p_mw:>10.4f} {sig:>5}")
        t3_results[dim] = {'bio_r1_mean': float(bio_mean), 'nb_r1_mean': float(nb_mean),
                           'u_stat': float(u_stat), 'p': float(p_mw)}
    else:
        print(f"  {label:<16} {'(insufficient data)'}")

print(f"\n  Significant dimensions: {sig_count}/{len(dimensions)}")

if sig_count == 0:
    t3_verdict = "FAIL_IDENTICAL"
    print(f"  -> Bio REGIME_1 = Non-Bio REGIME_1 (Bio distinctiveness = REGIME only)")
elif sig_count <= 2:
    t3_verdict = "PARTIAL_DIVERGENCE"
    print(f"  -> Some divergence: Bio has properties beyond REGIME_1 membership")
else:
    t3_verdict = "PASS_DIVERGENT"
    print(f"  -> Strong divergence: Bio is NOT just another REGIME_1 section")

print(f"\nT3 VERDICT: {t3_verdict}")
print()


# ===================================================================
# TEST 4: CC TRIGGER DECOMPOSITION
# ===================================================================
# C600: CC triggers differentiated. daiin opens CHSH (precision),
# ol-derived opens QO (energy). If Bio uses different CC trigger
# patterns, its control loop differs from distillation.
# ===================================================================
print("-" * 70)
print("TEST 4: CC Trigger Decomposition (Bio vs Non-Bio)")
print("  Test: do Bio and non-Bio use different CC trigger patterns?")
print("-" * 70)
print()

# CC triggers: daiin (and variants), ol, aiin
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

bio_cc, bio_cc_n = count_cc_triggers(bio_folios)
non_bio_cc, non_bio_cc_n = count_cc_triggers(non_bio_folios)

print(f"  CC trigger events: Bio={bio_cc_n}, Non-Bio={non_bio_cc_n}")
print()

cc_types = sorted(set(list(bio_cc.keys()) + list(non_bio_cc.keys())))

print(f"  {'Trigger Type':<20} {'Bio':>6} {'Bio%':>7} {'Non-Bio':>8} {'NB%':>7}")
print(f"  {'-'*20} {'-'*6} {'-'*7} {'-'*8} {'-'*7}")

for ct in cc_types:
    bc = bio_cc.get(ct, 0)
    nbc = non_bio_cc.get(ct, 0)
    bp = 100 * bc / bio_cc_n if bio_cc_n > 0 else 0
    nbp = 100 * nbc / non_bio_cc_n if non_bio_cc_n > 0 else 0
    print(f"  {ct:<20} {bc:>6} {bp:>6.1f}% {nbc:>8} {nbp:>6.1f}%")

# Chi-square on CC trigger distribution
bio_vec4 = [bio_cc.get(ct, 0) for ct in cc_types]
nb_vec4 = [non_bio_cc.get(ct, 0) for ct in cc_types]
ct4 = np.array([bio_vec4, nb_vec4])
col_mask4 = ct4.sum(axis=0) > 0
ct4_valid = ct4[:, col_mask4]

if ct4_valid.shape[1] >= 2:
    chi2_cc, p_cc, dof_cc, _ = sp_stats.chi2_contingency(ct4_valid)
    v_cc = np.sqrt(chi2_cc / (ct4_valid.sum() * (min(ct4_valid.shape) - 1)))
    print(f"\n  Chi-square (CC trigger distribution): chi2={chi2_cc:.1f}, dof={dof_cc}, p={p_cc:.2e}")
    print(f"  Cramer's V = {v_cc:.4f}")

    if p_cc < 0.05:
        t4_verdict = "PASS_DIFFERENT_TRIGGERS"
        print(f"  -> Bio uses DIFFERENT CC trigger patterns")
    else:
        t4_verdict = "FAIL_SAME_TRIGGERS"
        print(f"  -> Bio uses the SAME CC trigger patterns as non-Bio")
else:
    t4_verdict = "UNDERPOWERED"

print(f"\nT4 VERDICT: {t4_verdict}")
print()


# ===================================================================
# SUMMARY
# ===================================================================
print("=" * 70)
print("PHASE 385 SUMMARY: BIO SECTION OPERATIONAL DISTINCTIVENESS")
print("=" * 70)
print()
print(f"  T1 Kernel Balance:     {t1_verdict}")
print(f"  T2 Hazard Profile:     {t2_verdict}")
print(f"  T3 REGIME_1 Homog.:    {t3_verdict}")
print(f"  T4 CC Triggers:        {t4_verdict}")
print()

# Pre-registered decision rule
verdicts = [t1_verdict, t2_verdict, t3_verdict, t4_verdict]
core_tests = [t1_verdict, t2_verdict, t3_verdict]  # T1-T3 are core

core_pass = sum(1 for v in core_tests if 'PASS' in v or 'MULTI_DOMAIN' in v)
core_fail = sum(1 for v in core_tests if 'FAIL' in v or 'NULL' in v or 'SAME' in v or 'IDENTICAL' in v)
core_partial = sum(1 for v in core_tests if 'PARTIAL' in v)

print("Pre-registered decision rule (core tests T1-T3):")
print(f"  PASS (divergent): {core_pass}  PARTIAL: {core_partial}  FAIL (same): {core_fail}")
print()

if core_pass >= 2:
    overall = "BIO_DISTINCT_DOMAIN"
    print("CONCLUSION: Bio section encodes a structurally distinct application domain.")
    print("Multi-domain interpretation SUPPORTED at Tier 3.")
elif core_pass + core_partial >= 2:
    overall = "BIO_PARTIAL_DISTINCTION"
    print("CONCLUSION: Bio shows partial distinctiveness beyond REGIME membership.")
    print("Cannot distinguish multi-domain from specialized stage.")
elif core_fail >= 2:
    # Check if direction is balneum mariae
    if 'BALNEUM_MARIAE' in t1_verdict:
        overall = "BIO_BALNEUM_MARIAE"
        print("CONCLUSION: Bio profiles match SUSTAINED HEATING (balneum mariae).")
        print("Single-domain interpretation (distillation stage) SUPPORTED.")
    else:
        overall = "BIO_REGIME_ONLY"
        print("CONCLUSION: Bio distinctiveness fully explained by REGIME_1 membership.")
        print("No evidence for multi-domain manuscript.")
else:
    overall = "INCONCLUSIVE"
    print("CONCLUSION: Inconclusive. Mixed evidence.")

print()

# Save results
results = {
    'phase': 385,
    'name': 'BIO_DOMAIN_DISTINCTIVENESS',
    'test_count': 4,
    'verdicts': {
        'T1_kernel_balance': t1_verdict,
        'T2_hazard_profile': t2_verdict,
        'T3_regime1_homogeneity': t3_verdict,
        'T4_cc_triggers': t4_verdict,
    },
    'overall': overall,
    'bio_folios': sorted(bio_folios),
    'bio_token_count': bio_token_count,
    'non_bio_token_count': non_bio_token_count,
    'T1_data': t1_data,
    'T2_data': {k: v for k, v in t2_data.items()},
    'T3_data': t3_results,
}

output_path = RESULTS / 'bio_domain_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {output_path}")
