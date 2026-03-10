"""
T5: Integration + Synthesis Report
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

Loads all T0-T4 outputs, determines verdicts, registers constraints
C1639-C1642, and generates REPORT_573.md.

Mechanism verdicts:
  A2_MECHANISM_IDENTIFIED_STRONG    : single ablation >50% of A2 excess CCS1
  A2_MECHANISM_IDENTIFIED_COMPOSITE : top 2 jointly >70%, theoretically coherent
  A2_MECHANISM_PARTIAL              : reproducible but diffuse
  A2_MECHANISM_UNRESOLVED           : no stable decomposition

Family verdicts:
  FAMILY_PARTITION_CONFIRMED        : ARI > 0.5 or cleaner novel partition
  FAMILY_PARTITION_GRADIENT          : real structure, gradient-like (sil 0.15-0.30)
  FAMILY_PARTITION_INCONCLUSIVE      : no stable cluster structure
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PHASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

ABLATION_NAMES = [
    'NO_CROSS_COUPLING',
    'NO_CLOSE_RECOVERY',
    'NO_CONTAINMENT',
    'NO_TR_TO_Y',
    'NO_Y_SENSITIVITY',
]

# Containment-related ablations (theoretically coherent pair)
CONTAINMENT_ABLATIONS = {'NO_CONTAINMENT', 'NO_CLOSE_RECOVERY', 'NO_CROSS_COUPLING'}


# ---------------------------------------------------------------------------
# Load all T0-T4 outputs
# ---------------------------------------------------------------------------
def load_all():
    """Load all Phase 573 outputs."""
    files = {
        't0': 't0_opportunity_normalization.json',
        't1': 't1_mechanism_ablation.json',
        't2': 't2_grammar_strength_forgivingness.json',
        't3': 't3_response_families.json',
        't4': 't4_a2_decomposition.json',
    }
    data = {}
    for key, fname in files.items():
        path = os.path.join(RESULTS_DIR, fname)
        print(f"  Loading {fname}...")
        with open(path, 'r', encoding='utf-8') as f:
            data[key] = json.load(f)
    return data


# ---------------------------------------------------------------------------
# Mechanism verdict
# ---------------------------------------------------------------------------
def determine_mechanism_verdict(t1):
    """Determine how A2's excess forgivingness decomposes across ablation channels."""
    profile_results = t1['profile_results']

    # Find A2 profile
    a2_key = None
    for p in profile_results:
        if 'A2' in p or 'SEALED' in p:
            a2_key = p
            break
    if a2_key is None:
        return 'A2_MECHANISM_UNRESOLVED', {}, 'No A2 profile found in T1 results'

    a2 = profile_results[a2_key]
    ablation_effects = a2['ablation_effects']

    # Collect excess_fi_share per ablation
    shares = {}
    for abl_name in ABLATION_NAMES:
        ae = ablation_effects.get(abl_name, {})
        shares[abl_name] = ae.get('excess_fi_share', 0.0)

    # Sort by absolute share descending
    ranked = sorted(shares.items(), key=lambda x: abs(x[1]), reverse=True)

    top1_name, top1_share = ranked[0]
    top2_name, top2_share = ranked[1] if len(ranked) > 1 else ('', 0.0)

    # Check theoretical coherence of top 2
    top2_coherent = {top1_name, top2_name}.issubset(CONTAINMENT_ABLATIONS)

    # Verdict thresholds (from plan)
    if abs(top1_share) > 0.50:
        verdict = 'A2_MECHANISM_IDENTIFIED_STRONG'
        explanation = (f"Single ablation {top1_name} accounts for {top1_share:.1%} "
                       f"of A2 excess CCS1")
    elif abs(top1_share) + abs(top2_share) > 0.70 and top2_coherent:
        verdict = 'A2_MECHANISM_IDENTIFIED_COMPOSITE'
        explanation = (f"Top 2 ablations ({top1_name}: {top1_share:.1%}, "
                       f"{top2_name}: {top2_share:.1%}) jointly account for "
                       f"{abs(top1_share) + abs(top2_share):.1%} and are "
                       f"theoretically coherent (both containment-related)")
    elif abs(top1_share) > 0.20:
        verdict = 'A2_MECHANISM_PARTIAL'
        explanation = (f"Reproducible profile-specific effect but diffuse. "
                       f"Top channel {top1_name} at {top1_share:.1%}, "
                       f"next {top2_name} at {top2_share:.1%}")
    else:
        verdict = 'A2_MECHANISM_UNRESOLVED'
        explanation = (f"No stable decomposition. Top channel {top1_name} "
                       f"at only {top1_share:.1%}")

    details = {
        'a2_profile': a2_key,
        'ranked_shares': ranked,
        'top1_name': top1_name,
        'top1_share': top1_share,
        'top2_name': top2_name,
        'top2_share': top2_share,
        'top2_coherent': top2_coherent,
        'mean_crr_m1': a2.get('mean_crr_m1', 0.0),
        'mean_crr_m4f': a2.get('mean_crr_m4f', 0.0),
        'mean_nri_m1': a2.get('mean_nri_m1', 0.0),
        'mean_nri_m4f': a2.get('mean_nri_m4f', 0.0),
    }
    return verdict, details, explanation


# ---------------------------------------------------------------------------
# Family verdict
# ---------------------------------------------------------------------------
def determine_family_verdict(t3):
    """Determine whether the apparatus family partition is confirmed."""
    t3a = t3['t3a_response_only']
    t3b = t3['t3b_response_surface']

    best_k_a = t3a.get('best_k', '2')
    best_k_b = t3b.get('best_k', '2')

    # Response-only diagnostics
    best_a = t3a.get(best_k_a, {})
    sil_a = best_a.get('silhouette', 0.0)
    ari_profile_a = best_a.get('ari_vs_profile', 0.0)
    ari_2fam_a = best_a.get('ari_vs_2family', 0.0)
    bootstrap_a = t3a.get('bootstrap_stability', 0.0)

    # Response-surface diagnostics
    best_b = t3b.get(best_k_b, {})
    sil_b = best_b.get('silhouette', 0.0)
    ari_profile_b = best_b.get('ari_vs_profile', 0.0)
    bootstrap_b = t3b.get('bootstrap_stability', 0.0)

    # Best ARI across both layers
    max_ari = max(ari_profile_a, ari_2fam_a, ari_profile_b)

    # Verdict thresholds (from plan)
    if max_ari > 0.50:
        verdict = 'FAMILY_PARTITION_CONFIRMED'
        explanation = (f"Clustering ARI {max_ari:.3f} exceeds 0.50 threshold. "
                       f"Response-only k={best_k_a} (sil={sil_a:.3f}, "
                       f"ARI_profile={ari_profile_a:.3f}, ARI_2fam={ari_2fam_a:.3f}). "
                       f"Response-surface k={best_k_b} (sil={sil_b:.3f}, "
                       f"ARI_profile={ari_profile_b:.3f}).")
    elif 0.15 <= max(sil_a, sil_b) <= 0.50 and max(bootstrap_a, bootstrap_b) >= 0.60:
        verdict = 'FAMILY_PARTITION_GRADIENT'
        explanation = (f"Real structure but gradient-like. "
                       f"Response-only sil={sil_a:.3f}, bootstrap={bootstrap_a:.3f}. "
                       f"Response-surface sil={sil_b:.3f}, bootstrap={bootstrap_b:.3f}. "
                       f"ARI best={max_ari:.3f}.")
    else:
        verdict = 'FAMILY_PARTITION_INCONCLUSIVE'
        explanation = (f"No stable cluster structure. "
                       f"Silhouettes: {sil_a:.3f}, {sil_b:.3f}. "
                       f"Bootstrap: {bootstrap_a:.3f}, {bootstrap_b:.3f}. "
                       f"Best ARI: {max_ari:.3f}.")

    details = {
        'best_k_response': best_k_a,
        'best_k_surface': best_k_b,
        'silhouette_response': sil_a,
        'silhouette_surface': sil_b,
        'ari_profile_response': ari_profile_a,
        'ari_profile_surface': ari_profile_b,
        'ari_2family_response': ari_2fam_a,
        'bootstrap_response': bootstrap_a,
        'bootstrap_surface': bootstrap_b,
        'max_ari': max_ari,
    }
    return verdict, details, explanation


# ---------------------------------------------------------------------------
# Within-A2 verdict
# ---------------------------------------------------------------------------
def determine_a2_structure_verdict(t4):
    """Determine whether A2 is monolithic or internally structured."""
    sub_test = t4.get('sub_profile_test', {})
    section_sig = sub_test.get('section_significant', False)
    f_ratio = sub_test.get('section_f_ratio', 0.0)

    conformity_dist = t4.get('conformity_distribution', {})
    n_core = conformity_dist.get('core_A2', 0)
    n_boundary = sum(conformity_dist.get(k, 0) for k in conformity_dist
                     if 'boundary' in k)
    n_anomalous = conformity_dist.get('anomalous_A2', 0)
    n_total = sum(conformity_dist.values()) if conformity_dist else 1

    boundary_frac = n_boundary / n_total if n_total > 0 else 0.0
    anomalous_frac = n_anomalous / n_total if n_total > 0 else 0.0

    # Section stratification from T4
    section_strat = t4.get('section_stratification', {})
    section_ccs1 = {s: v.get('mean_ccs1', 0.0) for s, v in section_strat.items()}

    if section_sig and (boundary_frac > 0.30 or anomalous_frac > 0.10):
        verdict = 'A2_INTERNALLY_STRUCTURED'
        explanation = (f"Significant section F-ratio={f_ratio:.2f}, "
                       f"boundary folios {boundary_frac:.0%}, "
                       f"anomalous {anomalous_frac:.0%}")
    elif section_sig or boundary_frac > 0.20:
        verdict = 'A2_WEAKLY_STRUCTURED'
        explanation = (f"Section F-ratio={f_ratio:.2f} (sig={section_sig}), "
                       f"boundary {boundary_frac:.0%}, "
                       f"anomalous {anomalous_frac:.0%}. "
                       f"Some internal variation but not enough for sub-profiles")
    else:
        verdict = 'A2_MONOLITHIC'
        explanation = (f"No significant internal structure. "
                       f"F-ratio={f_ratio:.2f}, boundary {boundary_frac:.0%}, "
                       f"core {n_core}/{n_total}")

    details = {
        'f_ratio': f_ratio,
        'section_significant': section_sig,
        'n_core_a2': n_core,
        'n_boundary': n_boundary,
        'n_anomalous': n_anomalous,
        'boundary_fraction': boundary_frac,
        'section_ccs1': section_ccs1,
    }
    return verdict, details, explanation


# ---------------------------------------------------------------------------
# Grammar-forgivingness pattern verdict
# ---------------------------------------------------------------------------
def determine_grammar_verdict(t2):
    """Determine whether A2 forgivingness is uniform or grammar-strength dependent.

    Null events don't carry grammar-strength flags (all land in WEAK band),
    so we compare M1 DYE by grammar band against the OVERALL CCS1.
    The question is: does grammar strength help real events beat the null?
    """
    band_summary = t2.get('band_summary', {})

    # Find A2 profile key
    a2_key = None
    for p in band_summary:
        if 'A2' in p or 'SEALED' in p:
            a2_key = p
            break
    if a2_key is None:
        return 'GRAMMAR_PATTERN_UNRESOLVED', {}, 'No A2 profile found'

    a2_bands = band_summary[a2_key]

    # M1 DYE per grammar strength band
    m1_dye_strong = a2_bands.get('STRONG', {}).get('mean_m1_dye', 0.0)
    m1_dye_medium = a2_bands.get('MEDIUM', {}).get('mean_m1_dye', 0.0)
    m1_dye_weak = a2_bands.get('WEAK', {}).get('mean_m1_dye', 0.0)

    # Overall CCS1 (null DYE) from WEAK band where all nulls land
    overall_ccs1 = a2_bands.get('WEAK', {}).get('mean_m4f_dye', 0.0)

    # Grammar-conditioned advantage = M1_DYE_band - overall_CCS1
    adv_strong = m1_dye_strong - overall_ccs1
    adv_medium = m1_dye_medium - overall_ccs1
    adv_weak = m1_dye_weak - overall_ccs1

    # Counts (M1 events per band)
    n_strong = a2_bands.get('STRONG', {}).get('n_m1', 0)
    n_medium = a2_bands.get('MEDIUM', {}).get('n_m1', 0)
    n_weak = a2_bands.get('WEAK', {}).get('n_m1', 0)

    # Compare non-A2 for reference
    non_a2_keys = [p for p in band_summary if p != a2_key]
    non_a2_strong_m1 = []
    non_a2_weak_m1 = []
    non_a2_ccs1 = []
    for p in non_a2_keys:
        non_a2_strong_m1.append(band_summary[p].get('STRONG', {}).get('mean_m1_dye', 0.0))
        non_a2_weak_m1.append(band_summary[p].get('WEAK', {}).get('mean_m1_dye', 0.0))
        non_a2_ccs1.append(band_summary[p].get('WEAK', {}).get('mean_m4f_dye', 0.0))

    mean_non_a2_strong = (sum(non_a2_strong_m1) / len(non_a2_strong_m1)
                          if non_a2_strong_m1 else 0.0)
    mean_non_a2_weak = (sum(non_a2_weak_m1) / len(non_a2_weak_m1)
                        if non_a2_weak_m1 else 0.0)

    # Decision: does A2's grammar advantage vary by band?
    # If adv_strong ~ adv_weak → uniform forgivingness (grammar strength irrelevant)
    # If adv_strong >> adv_weak → grammar strength matters (only strong events beat null)
    # If adv_weak ~ 0 or negative → weak events can't beat the forgiving null
    if n_strong == 0 and n_weak == 0:
        pattern = 'GRAMMAR_PATTERN_INSUFFICIENT_DATA'
        explanation = f"Insufficient events: STRONG n_m1={n_strong}, WEAK n_m1={n_weak}"
    else:
        # Compare advantage range across bands
        advantages = []
        if n_strong > 0:
            advantages.append(('STRONG', adv_strong, n_strong))
        if n_medium > 0:
            advantages.append(('MEDIUM', adv_medium, n_medium))
        if n_weak > 0:
            advantages.append(('WEAK', adv_weak, n_weak))

        adv_values = [a[1] for a in advantages]
        adv_range = max(adv_values) - min(adv_values) if len(adv_values) > 1 else 0.0
        adv_mean = sum(adv_values) / len(adv_values) if adv_values else 0.0
        relative_range = adv_range / abs(adv_mean) if abs(adv_mean) > 0.001 else 0.0

        if relative_range < 0.50 and adv_range < 0.03:
            pattern = 'GRAMMAR_PATTERN_UNIFORM'
            explanation = (f"A2 grammar advantage is uniform across bands: "
                           f"STRONG adv={adv_strong:+.4f} (n={n_strong}), "
                           f"MEDIUM adv={adv_medium:+.4f} (n={n_medium}), "
                           f"WEAK adv={adv_weak:+.4f} (n={n_weak}). "
                           f"Range={adv_range:.4f}. CCS1={overall_ccs1:.4f}. "
                           f"Grammar strength does not modulate forgivingness.")
        elif adv_strong > adv_weak + 0.02:
            pattern = 'GRAMMAR_PATTERN_STRENGTH_DEPENDENT'
            explanation = (f"A2 grammar advantage varies by strength: "
                           f"STRONG adv={adv_strong:+.4f} (n={n_strong}), "
                           f"WEAK adv={adv_weak:+.4f} (n={n_weak}). "
                           f"Range={adv_range:.4f}, CCS1={overall_ccs1:.4f}. "
                           f"Only strong-grammar events reliably beat the "
                           f"forgiving null. Weak events {'lose' if adv_weak < 0 else 'barely beat'} "
                           f"the null.")
        elif adv_weak > adv_strong + 0.02:
            pattern = 'GRAMMAR_PATTERN_INVERTED'
            explanation = (f"A2 grammar advantage is inverted: "
                           f"WEAK adv={adv_weak:+.4f} > STRONG adv={adv_strong:+.4f}. "
                           f"Range={adv_range:.4f}, CCS1={overall_ccs1:.4f}. "
                           f"Unexpected pattern.")
        else:
            pattern = 'GRAMMAR_PATTERN_MARGINAL'
            explanation = (f"A2 grammar advantage shows marginal band dependence: "
                           f"STRONG adv={adv_strong:+.4f}, "
                           f"WEAK adv={adv_weak:+.4f}. "
                           f"Range={adv_range:.4f}, CCS1={overall_ccs1:.4f}.")

    details = {
        'a2_profile': a2_key,
        'overall_ccs1': overall_ccs1,
        'm1_dye_strong': m1_dye_strong,
        'm1_dye_medium': m1_dye_medium,
        'm1_dye_weak': m1_dye_weak,
        'n_strong': n_strong,
        'n_medium': n_medium,
        'n_weak': n_weak,
        'adv_strong': adv_strong,
        'adv_medium': adv_medium,
        'adv_weak': adv_weak,
        'non_a2_strong_m1_dye': mean_non_a2_strong,
        'non_a2_weak_m1_dye': mean_non_a2_weak,
    }
    return pattern, details, explanation


# ---------------------------------------------------------------------------
# Constraint registration
# ---------------------------------------------------------------------------
def build_constraints(mech_verdict, mech_details, mech_explanation,
                      fam_verdict, fam_details, fam_explanation,
                      a2_verdict, a2_details, a2_explanation,
                      gram_verdict, gram_details, gram_explanation):
    """Build constraint records C1639-C1642."""
    constraints = {}

    # C1639: A2 mechanistic explanation
    constraints['C1639'] = {
        'id': 'C1639',
        'tier': 2,
        'scope': 'B',
        'tags': ['apparatus', 'A2', 'mechanism', 'CCS'],
        'claim': (f"A2_SEALED_RECIRCULATION excess forgivingness mechanism: "
                  f"{mech_verdict}. {mech_explanation}"),
        'verdict': mech_verdict,
        'evidence': {
            'source': 'Phase 573 T1 counterfactual ablation',
            'top_channel': mech_details.get('top1_name', ''),
            'top_share': mech_details.get('top1_share', 0.0),
            'crr_m4f': mech_details.get('mean_crr_m4f', 0.0),
            'nri_m4f': mech_details.get('mean_nri_m4f', 0.0),
        },
        'phase': 573,
    }

    # C1640: Apparatus family partition
    constraints['C1640'] = {
        'id': 'C1640',
        'tier': 2,
        'scope': 'B',
        'tags': ['apparatus', 'clustering', 'family_partition'],
        'claim': (f"Currier B apparatus family partition: {fam_verdict}. "
                  f"{fam_explanation}"),
        'verdict': fam_verdict,
        'evidence': {
            'source': 'Phase 573 T3 two-layer clustering',
            'best_k_response': fam_details.get('best_k_response', ''),
            'silhouette_response': fam_details.get('silhouette_response', 0.0),
            'max_ari': fam_details.get('max_ari', 0.0),
            'bootstrap_response': fam_details.get('bootstrap_response', 0.0),
        },
        'phase': 573,
    }

    # C1641: Within-A2 structure
    constraints['C1641'] = {
        'id': 'C1641',
        'tier': 2,
        'scope': 'B',
        'tags': ['apparatus', 'A2', 'internal_structure'],
        'claim': (f"Within-A2 structure: {a2_verdict}. {a2_explanation}"),
        'verdict': a2_verdict,
        'evidence': {
            'source': 'Phase 573 T4 A2 folio decomposition',
            'f_ratio': a2_details.get('f_ratio', 0.0),
            'boundary_fraction': a2_details.get('boundary_fraction', 0.0),
            'n_core': a2_details.get('n_core_a2', 0),
        },
        'phase': 573,
    }

    # C1642: Grammar-forgivingness pattern
    constraints['C1642'] = {
        'id': 'C1642',
        'tier': 2,
        'scope': 'B',
        'tags': ['apparatus', 'A2', 'grammar', 'forgivingness'],
        'claim': (f"A2 event-type x grammar-strength forgivingness pattern: "
                  f"{gram_verdict}. {gram_explanation}"),
        'verdict': gram_verdict,
        'evidence': {
            'source': 'Phase 573 T2 grammar strength forgivingness',
            'overall_ccs1': gram_details.get('overall_ccs1', 0.0),
            'adv_strong': gram_details.get('adv_strong', 0.0),
            'adv_weak': gram_details.get('adv_weak', 0.0),
            'a2_profile': gram_details.get('a2_profile', ''),
        },
        'phase': 573,
    }

    return constraints


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_report(data, mech_verdict, mech_details, mech_explanation,
                    fam_verdict, fam_details, fam_explanation,
                    a2_verdict, a2_details, a2_explanation,
                    gram_verdict, gram_details, gram_explanation,
                    constraints):
    """Generate REPORT_573.md."""

    t0 = data['t0']
    t1 = data['t1']
    t2 = data['t2']
    t3 = data['t3']
    t4 = data['t4']

    n_folios = t0['metadata']['n_folios']

    # Profile summaries from T1
    profile_results = t1['profile_results']
    profile_names = sorted(profile_results.keys())

    # Best cluster info
    best_k_a = fam_details.get('best_k_response', '2')
    centroids = t3.get('centroids', {})

    lines = []
    lines.append("# Phase 573: A2 Forgivingness Mechanism + Apparatus Family Partition")
    lines.append("")
    lines.append(f"**Mechanism verdict: {mech_verdict}**")
    lines.append(f"**Family verdict: {fam_verdict}**")
    lines.append(f"**Within-A2 verdict: {a2_verdict}**")
    lines.append(f"**Grammar pattern: {gram_verdict}**")
    lines.append(f"**New constraints:** 4 (C1639-C1642)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Summary
    lines.append("## 1. Summary")
    lines.append("")
    lines.append(f"Phase 573 investigates the mechanism behind A2_SEALED_RECIRCULATION's "
                 f"elevated Forgivingness Index (FI = CCS1), which Phase 572 measured "
                 f"as 9x higher than A1. Using counterfactual ablation across 5 physics "
                 f"channels on {n_folios} eligible Currier B folios, the phase identifies "
                 f"which channels cause A2's excess forgivingness and tests whether the "
                 f"76-folio set partitions into natural apparatus-response families.")
    lines.append("")

    # 2. Mechanism ablation
    lines.append("## 2. Mechanism Ablation (T1)")
    lines.append("")
    lines.append(f"**Verdict: {mech_verdict}**")
    lines.append("")
    lines.append(mech_explanation)
    lines.append("")

    # Ablation table
    lines.append("### Ablation Shares by Profile")
    lines.append("")
    header = "| Profile | CCS1 (FI) | CRR_M4f | NRI_M4f |"
    for abl in ABLATION_NAMES:
        short = abl.replace('NO_', '')
        header += f" {short} |"
    lines.append(header)

    sep = "|" + "|".join(["---"] * (4 + len(ABLATION_NAMES))) + "|"
    lines.append(sep)

    for p in profile_names:
        pr = profile_results[p]
        ccs1 = pr.get('mean_m4f_dye', 0.0)
        crr = pr.get('mean_crr_m4f', 0.0)
        nri = pr.get('mean_nri_m4f', 0.0)
        row = f"| {p} | {ccs1:.4f} | {crr:.4f} | {nri:.4f} |"
        for abl in ABLATION_NAMES:
            ae = pr.get('ablation_effects', {}).get(abl, {})
            share = ae.get('excess_fi_share', 0.0)
            row += f" {share:+.1%} |"
        lines.append(row)

    lines.append("")

    # 3. Grammar forgivingness
    lines.append("## 3. Grammar-Strength Forgivingness (T2)")
    lines.append("")
    lines.append(f"**Pattern: {gram_verdict}**")
    lines.append("")
    lines.append(gram_explanation)
    lines.append("")

    # Band table — M1 DYE per band vs overall CCS1
    overall_ccs1 = gram_details.get('overall_ccs1', 0.0)
    lines.append(f"### M1 DYE by Grammar Strength Band (A2, overall CCS1={overall_ccs1:.4f})")
    lines.append("")
    lines.append("| Band | N_m1 | M1_DYE | Adv vs CCS1 |")
    lines.append("|------|------|--------|-------------|")
    for band in ['STRONG', 'MEDIUM', 'WEAK']:
        n = gram_details.get(f'n_{band.lower()}', 0)
        m1_dye = gram_details.get(f'm1_dye_{band.lower()}', 0.0)
        adv = gram_details.get(f'adv_{band.lower()}', 0.0)
        lines.append(f"| {band} | {n} | {m1_dye:.4f} | {adv:+.4f} |")
    lines.append("")

    # Event-count matched comparison
    ec_matched = t2.get('event_count_matched', {})
    if ec_matched:
        lines.append("### Event-Count Matched Comparison (A2 vs non-A2)")
        lines.append("")
        lines.append("| Bin | A2 n | A2 CCS1 | non-A2 n | non-A2 CCS1 | A2 DYE_adv | non-A2 DYE_adv |")
        lines.append("|-----|------|---------|----------|-------------|------------|----------------|")
        for bin_name in sorted(ec_matched.keys()):
            ec = ec_matched[bin_name]
            a2_data = ec.get('A2', {})
            na2_data = ec.get('non_A2', {})
            lines.append(
                f"| {bin_name} "
                f"| {a2_data.get('n', 0)} "
                f"| {a2_data.get('mean_m4f_dye', 0.0):.4f} "
                f"| {na2_data.get('n', 0)} "
                f"| {na2_data.get('mean_m4f_dye', 0.0):.4f} "
                f"| {a2_data.get('mean_dye_adv', 0.0):+.4f} "
                f"| {na2_data.get('mean_dye_adv', 0.0):+.4f} |"
            )
        lines.append("")

    # 4. Family partition
    lines.append("## 4. Apparatus Family Partition (T3)")
    lines.append("")
    lines.append(f"**Verdict: {fam_verdict}**")
    lines.append("")
    lines.append(fam_explanation)
    lines.append("")

    # Clustering summary
    lines.append("### Response-Only Clustering (T3a)")
    lines.append("")
    lines.append("| k | Silhouette | ARI_profile | ARI_2family | Composition |")
    lines.append("|---|-----------|-------------|-------------|-------------|")
    for k in ['2', '3', '4']:
        entry = t3.get('t3a_response_only', {}).get(k, {})
        sil = entry.get('silhouette', 0.0)
        ari_p = entry.get('ari_vs_profile', 0.0)
        ari_2f = entry.get('ari_vs_2family', 0.0)
        comp = entry.get('cluster_composition', {})
        comp_str = '; '.join(f"C{c}: {dict(v)}" for c, v in sorted(comp.items()))
        lines.append(f"| {k} | {sil:.3f} | {ari_p:.3f} | {ari_2f:.3f} | {comp_str} |")
    lines.append("")

    lines.append("### Response-Surface Clustering (T3b)")
    lines.append("")
    lines.append("| k | Silhouette | ARI_profile | Composition |")
    lines.append("|---|-----------|-------------|-------------|")
    for k in ['2', '3', '4']:
        entry = t3.get('t3b_response_surface', {}).get(k, {})
        sil = entry.get('silhouette', 0.0)
        ari_p = entry.get('ari_vs_profile', 0.0)
        comp = entry.get('cluster_composition', {})
        comp_str = '; '.join(f"C{c}: {dict(v)}" for c, v in sorted(comp.items()))
        lines.append(f"| {k} | {sil:.3f} | {ari_p:.3f} | {comp_str} |")
    lines.append("")

    # Supervised sanity check
    t3c = t3.get('t3c_supervised', {})
    if t3c:
        lines.append("### Supervised Sanity Check (T3c)")
        lines.append("")
        lines.append(f"- F-param only accuracy: {t3c.get('fparam_only_accuracy', 0.0):.1%}")
        lines.append(f"- Response-only accuracy: {t3c.get('response_only_accuracy', 0.0):.1%}")
        lines.append(f"- Combined accuracy: {t3c.get('combined_accuracy', 0.0):.1%}")
        pp = t3c.get('profile_prediction', {})
        if pp:
            lines.append(f"- Profile prediction (F-only): {pp.get('fparam_only_accuracy', 0.0):.1%}")
            lines.append(f"- Profile prediction (response): {pp.get('response_only_accuracy', 0.0):.1%}")
            lines.append(f"- Profile prediction (combined): {pp.get('combined_accuracy', 0.0):.1%}")
        lines.append("")

    # Centroid descriptions
    if centroids:
        lines.append("### Cluster Centroids (Response-only, best k)")
        lines.append("")
        for cid in sorted(centroids.keys()):
            c = centroids[cid]
            cent = c.get('centroid', {})
            profiles = c.get('profiles', {})
            lines.append(f"**Cluster {cid}** (n={c.get('n_members', 0)}, "
                          f"profiles: {dict(profiles)})")
            for feat, val in cent.items():
                lines.append(f"  - {feat}: {val:.4f}")
            lines.append("")

    # 5. Within-A2 structure
    lines.append("## 5. Within-A2 Structure (T4)")
    lines.append("")
    lines.append(f"**Verdict: {a2_verdict}**")
    lines.append("")
    lines.append(a2_explanation)
    lines.append("")

    # Section stratification
    section_strat = t4.get('section_stratification', {})
    if section_strat:
        lines.append("### Section Stratification")
        lines.append("")
        lines.append("| Section | N_folios | Mean CCS1 | Mean DYE_adv | Mean EPV |")
        lines.append("|---------|----------|-----------|--------------|----------|")
        for s in sorted(section_strat.keys()):
            ss = section_strat[s]
            lines.append(
                f"| {s} | {ss.get('n_folios', 0)} "
                f"| {ss.get('mean_ccs1', 0.0):.4f} "
                f"| {ss.get('mean_dye_advantage', 0.0):+.4f} "
                f"| {ss.get('mean_epv', 0.0):.4f} |"
            )
        lines.append("")

    # Conformity distribution
    conf_dist = t4.get('conformity_distribution', {})
    if conf_dist:
        lines.append("### Conformity Distribution")
        lines.append("")
        lines.append("| Class | Count |")
        lines.append("|-------|-------|")
        for cls in sorted(conf_dist.keys()):
            lines.append(f"| {cls} | {conf_dist[cls]} |")
        lines.append("")

    # Top/bottom A2 folios
    a2_ranking = t4.get('a2_ranking', [])
    if a2_ranking:
        lines.append("### A2 Folios Ranked by CCS1 (highest = most forgiving)")
        lines.append("")
        lines.append("| Folio | Section | CCS1 | DYE_adv | EPV | Events |")
        lines.append("|-------|---------|------|---------|-----|--------|")
        for r in a2_ranking[:10]:  # top 10
            lines.append(
                f"| {r['folio']} | {r['section']} "
                f"| {r['ccs1']:.4f} "
                f"| {r['dye_advantage']:+.4f} "
                f"| {r.get('epv', 0.0):.4f} "
                f"| {r.get('n_events', 0)} |"
            )
        if len(a2_ranking) > 10:
            lines.append(f"| ... | ... | ... | ... | ... | ... |")
            for r in a2_ranking[-3:]:
                lines.append(
                    f"| {r['folio']} | {r['section']} "
                    f"| {r['ccs1']:.4f} "
                    f"| {r['dye_advantage']:+.4f} "
                    f"| {r.get('epv', 0.0):.4f} "
                    f"| {r.get('n_events', 0)} |"
                )
        lines.append("")

    # Gap analysis
    gap = t4.get('gap_analysis', [])
    failing = [g for g in gap if not g.get('passing', True)]
    if failing:
        lines.append("### Failing A2 Folios (EPV < 0.80)")
        lines.append("")
        lines.append("| Folio | Section | EPV | DYE_adv | CCS1 |")
        lines.append("|-------|---------|-----|---------|------|")
        for g in sorted(failing, key=lambda x: x.get('epv', 0)):
            lines.append(
                f"| {g['folio']} | {g['section']} "
                f"| {g.get('epv', 0.0):.4f} "
                f"| {g.get('dye_advantage', 0.0):+.4f} "
                f"| {g.get('ccs1', 0.0):.4f} |"
            )
        lines.append("")

    # 6. Constraints
    lines.append("## 6. New Constraints")
    lines.append("")
    for cid in sorted(constraints.keys()):
        c = constraints[cid]
        lines.append(f"**{c['id']}** (Tier {c['tier']}, scope {c['scope']})")
        lines.append(f"  {c['claim']}")
        lines.append("")

    # 7. Interpretive synthesis
    lines.append("## 7. Interpretive Synthesis")
    lines.append("")
    lines.append("### A2 Mechanism Story")
    lines.append("")

    # Build interpretive narrative based on verdicts
    if 'STRONG' in mech_verdict or 'COMPOSITE' in mech_verdict:
        top_channel = mech_details.get('top1_name', 'unknown')
        lines.append(f"Phase 573 identifies a specific mechanism for A2's elevated "
                     f"forgivingness: **{top_channel}** is the primary channel through "
                     f"which null events convert disruption into Y. ")
        if 'CONTAINMENT' in top_channel or 'CLOSE_RECOVERY' in top_channel:
            lines.append(f"This supports the containment-mediated energy retention "
                         f"hypothesis: A2's parameter signature (high sensitivity_C, "
                         f"low decay_C, high alpha_XC) creates a regime where energy "
                         f"is retained in containment-related variables and recycled "
                         f"through cross-coupling, eventually feeding Y.")
        lines.append("")
    elif 'PARTIAL' in mech_verdict:
        lines.append("The mechanism is reproducible but distributed across multiple "
                     "channels. No single physics channel dominates A2's excess "
                     "forgivingness, suggesting a distributed parametric regime "
                     "rather than a single pathway.")
        lines.append("")
    else:
        lines.append("The mechanism could not be cleanly decomposed. "
                     "A2's elevated CCS1 may arise from complex interactions "
                     "between channels that are not separable by single-channel ablation.")
        lines.append("")

    # Grammar interpretation
    if 'UNIFORM' in gram_verdict:
        lines.append("The grammar-forgivingness analysis confirms that A2 forgives "
                     "uniformly across grammar strength bands — it grants excess Y to "
                     "nulls regardless of whether the original event was strongly or "
                     "weakly sealed. This rules out soft-closure acceptance and supports "
                     "general recirculatory conversion as the mechanism.")
    elif 'WEAK_CONCENTRATED' in gram_verdict:
        lines.append("A2 forgivingness concentrates in weakly-sealed events, "
                     "suggesting soft-closure acceptance rather than general "
                     "recirculatory conversion.")
    lines.append("")

    # Family interpretation
    if 'CONFIRMED' in fam_verdict:
        lines.append("The family partition confirms that Currier B folios naturally "
                     "cluster into distinct apparatus-response families that align "
                     "with the profile assignments.")
    elif 'GRADIENT' in fam_verdict:
        lines.append("The family partition reveals real but gradient-like structure — "
                     "folios form a continuum rather than crisp clusters, with "
                     "interpretable poles at the extremes.")
    else:
        lines.append("No stable family partition emerged from the clustering analysis.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Generated: {datetime.now(timezone.utc).isoformat()}*")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T5: Integration + Synthesis Report")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    print("\n--- Loading all T0-T4 outputs ---")
    data = load_all()

    # --- Verdicts ---
    print("\n--- Determining verdicts ---")

    print("  Mechanism verdict (T1)...")
    mech_verdict, mech_details, mech_explanation = determine_mechanism_verdict(data['t1'])
    print(f"    {mech_verdict}")
    print(f"    {mech_explanation}")

    print("  Family verdict (T3)...")
    fam_verdict, fam_details, fam_explanation = determine_family_verdict(data['t3'])
    print(f"    {fam_verdict}")
    print(f"    {fam_explanation}")

    print("  Within-A2 verdict (T4)...")
    a2_verdict, a2_details, a2_explanation = determine_a2_structure_verdict(data['t4'])
    print(f"    {a2_verdict}")
    print(f"    {a2_explanation}")

    print("  Grammar-forgivingness verdict (T2)...")
    gram_verdict, gram_details, gram_explanation = determine_grammar_verdict(data['t2'])
    print(f"    {gram_verdict}")
    print(f"    {gram_explanation}")

    # --- Constraints ---
    print("\n--- Registering constraints ---")
    constraints = build_constraints(
        mech_verdict, mech_details, mech_explanation,
        fam_verdict, fam_details, fam_explanation,
        a2_verdict, a2_details, a2_explanation,
        gram_verdict, gram_details, gram_explanation,
    )
    for cid in sorted(constraints):
        print(f"  {cid}: {constraints[cid]['claim'][:80]}...")

    # --- Report ---
    print("\n--- Generating report ---")
    report = generate_report(
        data,
        mech_verdict, mech_details, mech_explanation,
        fam_verdict, fam_details, fam_explanation,
        a2_verdict, a2_details, a2_explanation,
        gram_verdict, gram_details, gram_explanation,
        constraints,
    )
    report_path = os.path.join(PHASE_DIR, 'REPORT_573.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Report: {report_path}")
    print(f"  Size: {os.path.getsize(report_path):,} bytes")

    # --- JSON output ---
    print("\n--- Writing synthesis output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '573',
            'script': 't5_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': time.time() - t_start,
        },
        'verdicts': {
            'mechanism': {
                'verdict': mech_verdict,
                'explanation': mech_explanation,
                'details': {
                    'a2_profile': mech_details.get('a2_profile', ''),
                    'ranked_shares': mech_details.get('ranked_shares', []),
                    'top1_name': mech_details.get('top1_name', ''),
                    'top1_share': mech_details.get('top1_share', 0.0),
                    'top2_name': mech_details.get('top2_name', ''),
                    'top2_share': mech_details.get('top2_share', 0.0),
                    'top2_coherent': mech_details.get('top2_coherent', False),
                    'mean_crr_m4f': mech_details.get('mean_crr_m4f', 0.0),
                    'mean_nri_m4f': mech_details.get('mean_nri_m4f', 0.0),
                },
            },
            'family': {
                'verdict': fam_verdict,
                'explanation': fam_explanation,
                'details': fam_details,
            },
            'a2_structure': {
                'verdict': a2_verdict,
                'explanation': a2_explanation,
                'details': a2_details,
            },
            'grammar_pattern': {
                'verdict': gram_verdict,
                'explanation': gram_explanation,
                'details': {
                    'a2_profile': gram_details.get('a2_profile', ''),
                    'overall_ccs1': gram_details.get('overall_ccs1', 0.0),
                    'm1_dye_strong': gram_details.get('m1_dye_strong', 0.0),
                    'm1_dye_medium': gram_details.get('m1_dye_medium', 0.0),
                    'm1_dye_weak': gram_details.get('m1_dye_weak', 0.0),
                    'adv_strong': gram_details.get('adv_strong', 0.0),
                    'adv_medium': gram_details.get('adv_medium', 0.0),
                    'adv_weak': gram_details.get('adv_weak', 0.0),
                },
            },
        },
        'constraints': constraints,
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)
    print(f"  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")

    elapsed = time.time() - t_start
    print(f"\n  Total time: {elapsed:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
