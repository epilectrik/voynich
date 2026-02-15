#!/usr/bin/env python3
"""
Phase 378: Galenic Recipe Physics Prediction

3-test battery testing Galenic framework predictions against Voynich structure.

T1: Degree-Hazard Correlation
    Galenic: rare (high-degree) materials are dangerous.
    Test: Do rare MIDDLEs participate more in C109 forbidden transitions?

T2: Quality Opposition Predicts Forbidden Directionality
    Galenic: opposing qualities (hot/cold, dry/humid) produce dangerous transitions.
    Test: Are cross-quality transitions disproportionately forbidden?

T3: Galenic Degree Predicts Recovery Residual
    Galenic: different degrees require different recovery strategies.
    Test: Does Galenic intensity score explain C1035 AXM residual after REGIME?

All Tier 4. Expert-advisor validated.
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, mannwhitneyu, fisher_exact

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS = ROOT / "phases" / "GALENIC_RECIPE_PREDICTION" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# HARDCODED DATA FROM CONSTRAINTS
# ============================================================

# C109: 17 forbidden transition pairs (word-level, from phase18a_forbidden_inventory.json)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
]

# C1000: HUB sub-roles (MIDDLE level)
HAZARD_SOURCE = {'ar', 'dy', 'ey', 'l', 'ol', 'or'}
HAZARD_TARGET = {'aiin', 'al', 'ee', 'o', 'r', 't'}
SAFETY_BUFFER = {'eol', 'k', 'od'}
PURE_CONNECTOR = {'d', 'e', 'eey', 'ek', 'eo', 'iin', 's', 'y'}
HUB_MIDDLES = HAZARD_SOURCE | HAZARD_TARGET | SAFETY_BUFFER | PURE_CONNECTOR

# C1000 T3: 3 non-HUB MIDDLEs also participate in forbidden pairs
NON_HUB_HAZARD = {'c', 'he', 'edy'}

# PREFIX families for quality assignment (from C911, C647)
PREFIX_FAMILIES = {
    'QO': {'qo'},
    'CHSH': {'ch', 'sh'},
    'DA_SA': {'da', 'sa'},
    'OT_OL_OK': {'ot', 'ol', 'ok'},
}

# Quality labels (pre-registered from plan)
QUALITY_MAP = {
    'QO': 'ENERGY',
    'CHSH': 'STABILITY',
    'DA_SA': 'INFRASTRUCTURE',
    'OT_OL_OK': 'PHASE',
}

# Opposition axes (pre-registered: C1057 lane-sister orthogonal axes)
OPPOSITION_PAIRS = [
    ('ENERGY', 'STABILITY'),       # Primary (C1057)
    ('INFRASTRUCTURE', 'PHASE'),   # Secondary
]


# ============================================================
# DATA LOADING
# ============================================================

def load_b_tokens():
    """Load all Currier B tokens with morphological extraction."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
        })
    return tokens


def load_axm_residual_data():
    """Load per-folio AXM residual data from C1035."""
    path = ROOT / "phases" / "AXM_RESIDUAL_DECOMPOSITION" / "results" / "axm_residual_decomposition.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_prefix_family(prefix):
    """Map a prefix to its family."""
    if prefix is None:
        return 'BARE'
    for family, prefixes in PREFIX_FAMILIES.items():
        if prefix in prefixes:
            return family
    return 'OTHER'


# ============================================================
# T1: DEGREE-HAZARD CORRELATION
# ============================================================

def run_t1(tokens):
    """
    Galenic prediction: rare (high-degree) MIDDLEs are dangerous.
    Test: rank MIDDLEs by within-channel frequency, check if rare ones
    participate more in C109 forbidden transitions.

    Expected: FAIL. Hazard is hub-mediated (C1000), not degree-based.
    """
    print("\n" + "=" * 60)
    print("T1: Degree-Hazard Correlation")
    print("=" * 60)

    # Build per-channel (PREFIX) frequency counts for MIDDLEs
    # Channel = PREFIX value (including None for bare tokens)
    channel_middle_counts = defaultdict(Counter)
    for t in tokens:
        if t['middle']:
            channel = t['prefix'] if t['prefix'] else '_BARE_'
            channel_middle_counts[channel][t['middle']] += 1

    print(f"  Channels: {len(channel_middle_counts)}")
    print(f"  Channel sizes: {', '.join(f'{ch}={len(counts)}' for ch, counts in sorted(channel_middle_counts.items()))}")

    # Rank MIDDLEs within each channel (1 = most frequent = "degree 1")
    channel_ranks = {}
    for channel, counts in channel_middle_counts.items():
        n = len(counts)
        ranked = counts.most_common()
        channel_ranks[channel] = {}
        for rank, (mid, _) in enumerate(ranked, 1):
            # Normalize: 0 = most frequent, 1 = rarest
            channel_ranks[channel][mid] = (rank - 1) / max(n - 1, 1)

    # Compute weighted mean normalized rank per MIDDLE (across all channels)
    middle_rank_entries = defaultdict(list)
    for channel, ranks in channel_ranks.items():
        for mid, norm_rank in ranks.items():
            count = channel_middle_counts[channel][mid]
            middle_rank_entries[mid].append((norm_rank, count))

    middle_mean_rank = {}
    for mid, entries in middle_rank_entries.items():
        total_tokens = sum(c for _, c in entries)
        if total_tokens > 0:
            middle_mean_rank[mid] = sum(r * c for r, c in entries) / total_tokens

    # Classify into degree quartiles (across ALL MIDDLEs)
    all_ranks = sorted(middle_mean_rank.values())
    q25 = float(np.percentile(all_ranks, 25))
    q50 = float(np.percentile(all_ranks, 50))
    q75 = float(np.percentile(all_ranks, 75))

    def quartile(rank):
        if rank <= q25:
            return 1  # Most frequent = "degree 1"
        elif rank <= q50:
            return 2
        elif rank <= q75:
            return 3
        else:
            return 4  # Rarest = "degree 4"

    # Build HUB MIDDLE analysis table
    hazard_middles = HAZARD_SOURCE | HAZARD_TARGET
    hub_results = []
    for mid in sorted(HUB_MIDDLES):
        if mid in middle_mean_rank:
            is_hazard = mid in hazard_middles
            sub_role = (
                'HAZARD_SOURCE' if mid in HAZARD_SOURCE else
                'HAZARD_TARGET' if mid in HAZARD_TARGET else
                'SAFETY_BUFFER' if mid in SAFETY_BUFFER else
                'PURE_CONNECTOR'
            )
            hub_results.append({
                'middle': mid,
                'quartile': quartile(middle_mean_rank[mid]),
                'mean_rank': round(middle_mean_rank[mid], 4),
                'hazard': is_hazard,
                'sub_role': sub_role,
            })

    print(f"\n  HUB MIDDLEs analyzed: {len(hub_results)}")

    # Print detail table
    print(f"\n  {'MIDDLE':8s} {'Q':3s} {'Rank':6s} {'Hazard':7s} {'Sub-Role'}")
    print(f"  {'-'*8} {'-'*3} {'-'*6} {'-'*7} {'-'*16}")
    for r in sorted(hub_results, key=lambda x: x['mean_rank']):
        print(f"  {r['middle']:8s} Q{r['quartile']}  {r['mean_rank']:.4f} {'YES' if r['hazard'] else 'no':7s} {r['sub_role']}")

    # Test: Are hazard MIDDLEs concentrated in Q4 (rarest)?
    hazard_quartiles = [r['quartile'] for r in hub_results if r['hazard']]
    non_hazard_quartiles = [r['quartile'] for r in hub_results if not r['hazard']]

    hazard_mean_q = float(np.mean(hazard_quartiles))
    non_hazard_mean_q = float(np.mean(non_hazard_quartiles))
    print(f"\n  Hazard MIDDLEs (n={len(hazard_quartiles)}): mean quartile = {hazard_mean_q:.2f}")
    print(f"  Non-hazard HUB (n={len(non_hazard_quartiles)}): mean quartile = {non_hazard_mean_q:.2f}")

    # Mann-Whitney U: are hazard MIDDLEs in HIGHER quartiles (rarer)?
    u_stat, u_pval = mannwhitneyu(hazard_quartiles, non_hazard_quartiles, alternative='greater')
    print(f"  Mann-Whitney U (hazard > non-hazard): U={u_stat:.1f}, p={u_pval:.4f}")

    # Fisher exact: Q4 enrichment in hazard vs non-hazard
    q4_hazard = sum(1 for r in hub_results if r['hazard'] and r['quartile'] == 4)
    q4_nonhaz = sum(1 for r in hub_results if not r['hazard'] and r['quartile'] == 4)
    nq4_hazard = sum(1 for r in hub_results if r['hazard'] and r['quartile'] != 4)
    nq4_nonhaz = sum(1 for r in hub_results if not r['hazard'] and r['quartile'] != 4)

    table_2x2 = [[q4_hazard, q4_nonhaz], [nq4_hazard, nq4_nonhaz]]
    fisher_or, fisher_p = fisher_exact(table_2x2, alternative='greater')
    print(f"  Fisher exact (Q4 enrichment): OR={fisher_or:.2f}, p={fisher_p:.4f}")
    print(f"    [[Q4_haz={q4_hazard}, Q4_nonhaz={q4_nonhaz}], [notQ4_haz={nq4_hazard}, notQ4_nonhaz={nq4_nonhaz}]]")

    # Also check reverse: are hazard MIDDLEs in Q1 (most frequent)?
    q1_hazard = sum(1 for r in hub_results if r['hazard'] and r['quartile'] == 1)
    q1_nonhaz = sum(1 for r in hub_results if not r['hazard'] and r['quartile'] == 1)
    nq1_hazard = sum(1 for r in hub_results if r['hazard'] and r['quartile'] != 1)
    nq1_nonhaz = sum(1 for r in hub_results if not r['hazard'] and r['quartile'] != 1)

    table_q1 = [[q1_hazard, q1_nonhaz], [nq1_hazard, nq1_nonhaz]]
    fisher_q1_or, fisher_q1_p = fisher_exact(table_q1, alternative='greater')
    print(f"  Fisher exact (Q1 enrichment): OR={fisher_q1_or:.2f}, p={fisher_q1_p:.4f}")
    print(f"    [[Q1_haz={q1_hazard}, Q1_nonhaz={q1_nonhaz}], [notQ1_haz={nq1_hazard}, notQ1_nonhaz={nq1_nonhaz}]]")

    # Verdict (pre-registered criteria)
    q4_rate_haz = q4_hazard / max(q4_hazard + nq4_hazard, 1)
    nq4_rate_haz = nq4_hazard / max(nq4_hazard + q4_hazard, 1)
    # Wait: rate = what fraction of Q4 MIDDLEs are hazard vs what fraction of non-Q4 are hazard
    total_q4 = q4_hazard + q4_nonhaz
    total_nq4 = nq4_hazard + nq4_nonhaz
    q4_hazard_rate = q4_hazard / max(total_q4, 1)
    nq4_hazard_rate = nq4_hazard / max(total_nq4, 1)

    if u_pval < 0.05 and q4_hazard_rate > 2 * nq4_hazard_rate:
        verdict = "PASS"
    elif u_pval < 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Q4 hazard rate: {q4_hazard_rate:.3f} ({q4_hazard}/{total_q4})")
    print(f"  Non-Q4 hazard rate: {nq4_hazard_rate:.3f} ({nq4_hazard}/{total_nq4})")
    print(f"\n  >>> VERDICT: {verdict}")

    result = {
        'test': 'T1_degree_hazard_correlation',
        'hypothesis': 'Rare (high-degree) MIDDLEs participate more in forbidden transitions',
        'galenic_prediction': 'Degree 4 (rare, extreme) materials are dangerous',
        'verdict': verdict,
        'n_hub_middles_analyzed': len(hub_results),
        'hazard_mean_quartile': round(hazard_mean_q, 4),
        'non_hazard_mean_quartile': round(non_hazard_mean_q, 4),
        'mann_whitney': {
            'U': float(u_stat),
            'p': round(float(u_pval), 6),
            'alternative': 'hazard > non-hazard (one-sided)',
        },
        'fisher_q4_enrichment': {
            'OR': round(float(fisher_or), 4),
            'p': round(float(fisher_p), 6),
            'table': table_2x2,
        },
        'fisher_q1_enrichment': {
            'OR': round(float(fisher_q1_or), 4),
            'p': round(float(fisher_q1_p), 6),
            'table': table_q1,
        },
        'q4_hazard_rate': round(q4_hazard_rate, 4),
        'not_q4_hazard_rate': round(nq4_hazard_rate, 4),
        'quartile_thresholds': {'q25': q25, 'q50': q50, 'q75': q75},
        'hub_middle_details': hub_results,
        'interpretation': (
            'Galenic degree predicts hazard participation' if verdict == 'PASS' else
            'Hazard is topological (hub-mediated), not scalar (degree-based). '
            'HUB MIDDLEs are the MOST frequent vocabulary, not the rarest. '
            'This confirms the Galenic degree analogy breaks at the hazard level.'
            if verdict == 'FAIL' else
            'Some evidence for degree-hazard correlation but below pre-registered threshold.'
        ),
        'constraints_referenced': ['C109', 'C1000', 'C541', 'C623'],
    }

    return result


# ============================================================
# T2: QUALITY OPPOSITION PREDICTS FORBIDDEN DIRECTIONALITY
# ============================================================

def run_t2(tokens, morph):
    """
    Galenic prediction: opposing qualities produce dangerous transitions.
    Test: assign HUB MIDDLEs quality by PREFIX affiliation, check if
    cross-quality transitions are disproportionately forbidden.

    Quality assignment is PRE-REGISTERED before examining directionality.
    """
    print("\n" + "=" * 60)
    print("T2: Quality Opposition Predicts Forbidden Directionality")
    print("=" * 60)

    # Step 1: Assign each HUB MIDDLE a dominant quality
    # Count tokens by PREFIX family for each MIDDLE
    middle_prefix_profile = defaultdict(Counter)
    for t in tokens:
        if t['middle'] in HUB_MIDDLES:
            family = get_prefix_family(t['prefix'])
            middle_prefix_profile[t['middle']][family] += 1

    # Assign dominant quality
    quality_families = ['QO', 'CHSH', 'DA_SA', 'OT_OL_OK']
    middle_quality = {}
    quality_details = {}

    print("\n  PRE-REGISTERED QUALITY ASSIGNMENTS (before examining directionality):")
    print(f"  {'MIDDLE':8s} {'Quality':16s} {'Dominant':10s} {'Total':6s} {'QO%':6s} {'CHSH%':6s} {'DA%':6s} {'OT%':6s} {'BARE%':6s}")
    print(f"  {'-'*8} {'-'*16} {'-'*10} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")

    for mid in sorted(HUB_MIDDLES):
        profile = middle_prefix_profile.get(mid, Counter())
        total = sum(profile.values())
        if total == 0:
            continue

        fractions = {}
        for fam in quality_families + ['BARE', 'OTHER']:
            fractions[fam] = profile.get(fam, 0) / total

        # Assign based on quality-family counts (excluding BARE and OTHER)
        prefixed_total = sum(profile.get(f, 0) for f in quality_families)
        if prefixed_total > 0:
            dominant_family = max(quality_families, key=lambda f: profile.get(f, 0))
            quality = QUALITY_MAP[dominant_family]
        else:
            dominant_family = 'BARE'
            quality = 'UNASSIGNED'

        middle_quality[mid] = quality
        quality_details[mid] = {
            'middle': mid,
            'total_tokens': total,
            'profile': {k: round(v, 4) for k, v in fractions.items()},
            'dominant_family': dominant_family,
            'quality': quality,
            'prefixed_total': prefixed_total,
        }

        print(f"  {mid:8s} {quality:16s} {dominant_family:10s} {total:6d} "
              f"{fractions.get('QO', 0):5.1%} {fractions.get('CHSH', 0):5.1%} "
              f"{fractions.get('DA_SA', 0):5.1%} {fractions.get('OT_OL_OK', 0):5.1%} "
              f"{fractions.get('BARE', 0):5.1%}")

    quality_group_sizes = Counter(q for q in middle_quality.values() if q != 'UNASSIGNED')
    print(f"\n  Quality group sizes: {dict(quality_group_sizes)}")

    # Step 2: Classify each forbidden pair by source/target quality
    print("\n  FORBIDDEN PAIR CLASSIFICATION:")
    pair_classifications = []

    for source_word, target_word in FORBIDDEN_PAIRS:
        src_m = morph.extract(source_word)
        tgt_m = morph.extract(target_word)

        src_mid = src_m.middle
        tgt_mid = tgt_m.middle

        src_quality = middle_quality.get(src_mid, 'UNKNOWN')
        tgt_quality = middle_quality.get(tgt_mid, 'UNKNOWN')

        valid_qualities = set(QUALITY_MAP.values())
        src_valid = src_quality in valid_qualities
        tgt_valid = tgt_quality in valid_qualities

        is_cross_quality = (src_valid and tgt_valid and src_quality != tgt_quality)

        # Check opposition
        is_opposition = False
        opposition_axis = None
        if is_cross_quality:
            for q1, q2 in OPPOSITION_PAIRS:
                if {src_quality, tgt_quality} == {q1, q2}:
                    is_opposition = True
                    opposition_axis = f"{q1}<>{q2}"
                    break

        pair_classifications.append({
            'source_word': source_word,
            'target_word': target_word,
            'source_middle': src_mid,
            'target_middle': tgt_mid,
            'source_quality': src_quality,
            'target_quality': tgt_quality,
            'is_cross_quality': is_cross_quality,
            'is_opposition': is_opposition,
            'opposition_axis': opposition_axis,
        })

        marker = "CROSS" if is_cross_quality else ("same" if (src_valid and tgt_valid) else "???")
        opp = f" [{opposition_axis}]" if is_opposition else ""
        print(f"    {source_word:8s} -> {target_word:8s}  "
              f"({src_mid}->{tgt_mid})  "
              f"{src_quality:16s} -> {tgt_quality:16s}  {marker}{opp}")

    # Step 3: Count cross-quality vs same-quality
    valid_pairs = [p for p in pair_classifications
                   if p['source_quality'] in set(QUALITY_MAP.values())
                   and p['target_quality'] in set(QUALITY_MAP.values())]

    cross_count = sum(1 for p in valid_pairs if p['is_cross_quality'])
    same_count = sum(1 for p in valid_pairs if not p['is_cross_quality'])
    opp_count = sum(1 for p in valid_pairs if p['is_opposition'])
    total_valid = len(valid_pairs)
    cross_frac = cross_count / max(total_valid, 1)

    print(f"\n  Valid pairs (both qualities assigned): {total_valid}/{len(FORBIDDEN_PAIRS)}")
    print(f"  Cross-quality: {cross_count} ({cross_frac:.1%})")
    print(f"  Same-quality: {same_count} ({1 - cross_frac:.1%})")
    print(f"  Opposition crossings: {opp_count}")

    # Step 4: Permutation test
    n_perm = 10000
    hub_list = [mid for mid, q in middle_quality.items() if q in set(QUALITY_MAP.values())]
    quality_list = [middle_quality[mid] for mid in hub_list]

    rng = np.random.default_rng(42)
    perm_cross_counts = np.zeros(n_perm, dtype=int)

    for i in range(n_perm):
        perm_qs = quality_list.copy()
        rng.shuffle(perm_qs)
        perm_map = dict(zip(hub_list, perm_qs))

        count = 0
        for p in valid_pairs:
            src_q = perm_map.get(p['source_middle'], 'UNKNOWN')
            tgt_q = perm_map.get(p['target_middle'], 'UNKNOWN')
            if (src_q in set(QUALITY_MAP.values()) and
                tgt_q in set(QUALITY_MAP.values()) and
                src_q != tgt_q):
                count += 1
        perm_cross_counts[i] = count

    perm_p = float(np.mean(perm_cross_counts >= cross_count))
    perm_mean = float(np.mean(perm_cross_counts))
    perm_95 = float(np.percentile(perm_cross_counts, 95))

    print(f"\n  Permutation test ({n_perm} permutations):")
    print(f"    Observed cross-quality: {cross_count}")
    print(f"    Null mean: {perm_mean:.2f}")
    print(f"    Null 95th percentile: {perm_95:.1f}")
    print(f"    p-value: {perm_p:.4f}")

    # Step 5: Directional analysis (among cross-quality pairs)
    direction_counts = Counter()
    for p in valid_pairs:
        if p['is_cross_quality']:
            direction = f"{p['source_quality']}->{p['target_quality']}"
            direction_counts[direction] += 1

    print(f"\n  Directional breakdown (cross-quality):")
    for direction, count in direction_counts.most_common():
        print(f"    {direction}: {count}")

    # Verdict
    if perm_p < 0.05 and opp_count > cross_count / 2:
        verdict = "PASS"
    elif perm_p < 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  >>> VERDICT: {verdict}")

    result = {
        'test': 'T2_quality_opposition_directionality',
        'hypothesis': 'Cross-quality transitions are disproportionately forbidden',
        'galenic_prediction': 'Opposing qualities (hot/cold, dry/humid) produce dangerous transitions',
        'verdict': verdict,
        'n_valid_pairs': total_valid,
        'n_total_pairs': len(FORBIDDEN_PAIRS),
        'cross_quality_count': cross_count,
        'same_quality_count': same_count,
        'cross_quality_fraction': round(cross_frac, 4),
        'opposition_count': opp_count,
        'permutation_test': {
            'n_permutations': n_perm,
            'observed': cross_count,
            'null_mean': round(perm_mean, 2),
            'null_95th': round(perm_95, 2),
            'p_value': round(perm_p, 6),
        },
        'direction_counts': dict(direction_counts),
        'quality_assignments': quality_details,
        'pair_classifications': pair_classifications,
        'quality_group_sizes': dict(quality_group_sizes),
        'interpretation': (
            'Quality opposition predicts forbidden directionality' if verdict == 'PASS' else
            'Cross-quality transitions enriched but opposition axis does not dominate.'
            if verdict == 'PARTIAL' else
            'Quality assignment based on PREFIX affiliation does not predict which '
            'transitions are forbidden. The Galenic quality-opposition analogy does not '
            'map onto the forbidden transition topology.'
        ),
        'constraints_referenced': ['C109', 'C625', 'C911', 'C1000', 'C1057'],
    }

    return result


# ============================================================
# T3: GALENIC DEGREE PREDICTS RECOVERY RESIDUAL
# ============================================================

def run_t3(tokens):
    """
    Galenic prediction: materials of different degree require different recovery.
    Test: does per-folio Galenic intensity score explain C1035 AXM residual
    after controlling for REGIME?

    Expected: FAIL. Galenic degree ~ REGIME (both measure intensity).
    C634 shows recovery not regime-stratified (all KW p > 0.40).
    """
    print("\n" + "=" * 60)
    print("T3: Galenic Degree Predicts Recovery Residual")
    print("=" * 60)

    # Load AXM residual data
    axm_data = load_axm_residual_data()
    folio_data = axm_data.get('folio_data', {})
    print(f"  AXM data: {len(folio_data)} folios")

    # Build per-channel frequency counts and ranks
    channel_middle_counts = defaultdict(Counter)
    folio_channel_middles = defaultdict(lambda: defaultdict(list))

    for t in tokens:
        if t['middle']:
            channel = t['prefix'] if t['prefix'] else '_BARE_'
            channel_middle_counts[channel][t['middle']] += 1
            folio_channel_middles[t['folio']][channel].append(t['middle'])

    # Rank within each channel (normalized: 0=most frequent, 1=rarest)
    channel_ranks = {}
    for channel, counts in channel_middle_counts.items():
        n = len(counts)
        ranked = counts.most_common()
        channel_ranks[channel] = {
            mid: (rank - 1) / max(n - 1, 1)
            for rank, (mid, _) in enumerate(ranked, 1)
        }

    # Compute per-folio Galenic intensity score
    # Mean within-channel normalized rank, weighted by token count per channel
    folio_galenic = {}
    for folio, channel_mids in folio_channel_middles.items():
        total_w = 0
        weighted_sum = 0.0
        for channel, middles in channel_mids.items():
            ranks = channel_ranks.get(channel, {})
            for mid in middles:
                if mid in ranks:
                    weighted_sum += ranks[mid]
                    total_w += 1
        if total_w > 0:
            folio_galenic[folio] = weighted_sum / total_w

    print(f"  Galenic scores computed: {len(folio_galenic)} folios")

    # Match with AXM residual data
    matched = []
    for folio in sorted(folio_galenic.keys()):
        if folio in folio_data:
            fd = folio_data[folio]
            if fd.get('c1017_residual') is not None:
                matched.append({
                    'folio': folio,
                    'galenic_score': folio_galenic[folio],
                    'axm_residual': fd['c1017_residual'],
                    'axm_self': fd.get('axm_self'),
                    'regime': fd.get('regime'),
                    'section': fd.get('section'),
                })

    n = len(matched)
    print(f"  Matched folios: {n}")

    if n < 10:
        print("  ERROR: Too few matched folios")
        return {'test': 'T3_galenic_degree_recovery_residual',
                'verdict': 'ERROR', 'error': f'Only {n} matched folios'}

    galenic = np.array([m['galenic_score'] for m in matched])
    residuals = np.array([m['axm_residual'] for m in matched])
    regimes = [m['regime'] for m in matched]

    print(f"  Galenic score: mean={np.mean(galenic):.4f}, std={np.std(galenic):.4f}, "
          f"range=[{np.min(galenic):.4f}, {np.max(galenic):.4f}]")
    print(f"  AXM residual: mean={np.mean(residuals):.4f}, std={np.std(residuals):.4f}")

    # Raw Spearman correlation
    rho_raw, p_raw = spearmanr(galenic, residuals)
    print(f"\n  Raw Spearman(galenic, residual): rho={rho_raw:.4f}, p={p_raw:.4f}")

    # Partial correlation controlling for REGIME
    # Residualize both variables against REGIME dummies
    unique_regimes = sorted(set(regimes))
    regime_dummies = np.zeros((n, len(unique_regimes)))
    for i, r in enumerate(regimes):
        regime_dummies[i, unique_regimes.index(r)] = 1

    # Drop first column for identifiability, add intercept
    X = np.column_stack([np.ones(n), regime_dummies[:, 1:]])

    # Residualize galenic score
    beta_g = np.linalg.lstsq(X, galenic, rcond=None)[0]
    galenic_resid = galenic - X @ beta_g

    # Residualize AXM residual
    beta_a = np.linalg.lstsq(X, residuals, rcond=None)[0]
    axm_resid_ctrl = residuals - X @ beta_a

    rho_partial, p_partial = spearmanr(galenic_resid, axm_resid_ctrl)
    print(f"  Partial Spearman(galenic, residual | REGIME): rho={rho_partial:.4f}, p={p_partial:.4f}")

    # Galenic score ~ REGIME correlation (checking for confounding)
    regime_numeric = np.array([unique_regimes.index(r) for r in regimes], dtype=float)
    rho_regime, p_regime = spearmanr(galenic, regime_numeric)
    print(f"\n  Galenic ~ REGIME: rho={rho_regime:.4f}, p={p_regime:.4f}")

    # Per-regime means
    regime_means = {}
    for r in unique_regimes:
        mask = np.array([reg == r for reg in regimes])
        if mask.sum() > 0:
            regime_means[r] = {
                'n': int(mask.sum()),
                'mean_galenic': round(float(np.mean(galenic[mask])), 4),
                'std_galenic': round(float(np.std(galenic[mask])), 4),
            }
    print(f"  Per-regime Galenic:")
    for r, stats in sorted(regime_means.items()):
        print(f"    {r}: n={stats['n']}, mean={stats['mean_galenic']:.4f} +/- {stats['std_galenic']:.4f}")

    # Verdict (pre-registered criteria)
    if p_partial < 0.05 and abs(rho_partial) > 0.25:
        verdict = "PASS"
    elif p_partial < 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  >>> VERDICT: {verdict}")

    result = {
        'test': 'T3_galenic_degree_recovery_residual',
        'hypothesis': 'Galenic intensity score explains AXM residual after controlling for REGIME',
        'galenic_prediction': 'Different degrees require different recovery strategies',
        'verdict': verdict,
        'n_folios': n,
        'galenic_score_stats': {
            'mean': round(float(np.mean(galenic)), 4),
            'std': round(float(np.std(galenic)), 4),
            'min': round(float(np.min(galenic)), 4),
            'max': round(float(np.max(galenic)), 4),
        },
        'raw_spearman': {
            'rho': round(float(rho_raw), 4),
            'p': round(float(p_raw), 6),
        },
        'partial_spearman_controlling_regime': {
            'rho': round(float(rho_partial), 4),
            'p': round(float(p_partial), 6),
        },
        'galenic_regime_correlation': {
            'rho': round(float(rho_regime), 4),
            'p': round(float(p_regime), 6),
        },
        'per_regime_stats': regime_means,
        'folio_details': matched,
        'interpretation': (
            'Galenic intensity score explains recovery residual beyond REGIME' if verdict == 'PASS' else
            'Galenic degree is mechanically correlated with REGIME. Since REGIME does not '
            'predict recovery (C634: all KW p > 0.40), neither does Galenic degree. '
            'The Galenic degree analogy is absorbed by the existing REGIME classification.'
            if verdict == 'FAIL' else
            'Weak signal: Galenic score has marginal partial correlation with residual.'
        ),
        'constraints_referenced': ['C634', 'C1017', 'C1035'],
    }

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 378: Galenic Recipe Physics Prediction")
    print("3-test battery | Tier 4 throughout")
    print("=" * 60)

    morph = Morphology()

    print("\nLoading Currier B tokens...")
    tokens = load_b_tokens()
    print(f"  Tokens: {len(tokens)}")

    # Run 3-test battery
    t1 = run_t1(tokens)
    t2 = run_t2(tokens, morph)
    t3 = run_t3(tokens)

    # Save individual results
    for name, result in [('t1_degree_hazard', t1),
                         ('t2_quality_directionality', t2),
                         ('t3_degree_recovery', t3)]:
        path = RESULTS / f'{name}.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nSaved: {path}")

    # Combined summary
    verdicts = [t1['verdict'], t2['verdict'], t3['verdict']]
    n_pass = sum(1 for v in verdicts if v == 'PASS')
    n_partial = sum(1 for v in verdicts if v == 'PARTIAL')
    n_fail = sum(1 for v in verdicts if v == 'FAIL')

    summary = {
        'phase': 378,
        'name': 'GALENIC_RECIPE_PREDICTION',
        'description': '3-test battery testing Galenic framework predictions against Voynich structure',
        'tier': 4,
        'tests': [
            {'id': 'T1', 'name': 'Degree-Hazard Correlation', 'verdict': t1['verdict']},
            {'id': 'T2', 'name': 'Quality Opposition Directionality', 'verdict': t2['verdict']},
            {'id': 'T3', 'name': 'Galenic Degree Recovery Residual', 'verdict': t3['verdict']},
        ],
        'overall': f"{n_pass}/3 PASS, {n_partial}/3 PARTIAL, {n_fail}/3 FAIL",
        'constraints_referenced': sorted(set(
            t1.get('constraints_referenced', []) +
            t2.get('constraints_referenced', []) +
            t3.get('constraints_referenced', [])
        )),
    }

    with open(RESULTS / 'galenic_recipe_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {RESULTS / 'galenic_recipe_summary.json'}")

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {summary['overall']}")
    for t in summary['tests']:
        print(f"  {t['id']}: {t['name']} -> {t['verdict']}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
