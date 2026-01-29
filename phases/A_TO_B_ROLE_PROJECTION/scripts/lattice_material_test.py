#!/usr/bin/env python3
"""
lattice_material_test.py - A Record Co-occurrence Lattice & Material Consistency

Builds the PP-PP co-occurrence lattice from A records and tests:
(1) Whether legal PP pairs preferentially combine different B roles (heterogeneity)
(2) Whether A records show material class consistency (all-ANIMAL or all-HERB)
Both tests use 10,000-iteration permutation tests.

Sections:
1. Load dependencies
2. Build PP-PP co-occurrence lattice
3. Role heterogeneity of legal pairs (permutation test)
4. Material class consistency (permutation test)
5. Summary and save
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from math import lgamma

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


ROLE_CORRECTIONS = {'17': 'CORE_CONTROL'}
ROLE_NAMES = ['AUXILIARY', 'CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR']
ROLE_SHORT = {'AUXILIARY': 'AX', 'CORE_CONTROL': 'CC', 'ENERGY_OPERATOR': 'EN',
              'FLOW_OPERATOR': 'FL', 'FREQUENT_OPERATOR': 'FQ'}

N_PERMUTATIONS = 10000


def chi2_sf(x, df):
    """Chi-squared survival function."""
    if x <= 0 or df <= 0:
        return 1.0
    a = df / 2.0
    z = x / 2.0
    return 1.0 - regularized_gamma_p(a, z)


def regularized_gamma_p(a, x):
    if x <= 0:
        return 0.0
    if x < a + 1:
        return gamma_series(a, x)
    else:
        return 1.0 - gamma_cf(a, x)


def gamma_series(a, x):
    from math import exp
    if x == 0:
        return 0.0
    ap = a
    s = 1.0 / a
    delta = s
    for n in range(1, 300):
        ap += 1
        delta *= x / ap
        s += delta
        if abs(delta) < abs(s) * 1e-12:
            break
    return s * exp(-x + a * np.log(x) - lgamma(a))


def gamma_cf(a, x):
    from math import exp
    b_val = x + 1 - a
    c = 1e30
    d = 1.0 / b_val if b_val != 0 else 1e30
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b_val += 2
        d = an * d + b_val
        if abs(d) < 1e-30:
            d = 1e-30
        c = b_val + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return exp(-x + a * np.log(x) - lgamma(a)) * h


def main():
    print("=" * 70)
    print("LATTICE & MATERIAL TEST")
    print("Phase: A_TO_B_ROLE_PROJECTION | Script 3 of 3")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / 'results'
    rng = np.random.RandomState(42)

    # ================================================================
    # SECTION 1: Load Dependencies
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: Load Dependencies")
    print("=" * 70)

    # Load Script 1 results
    s1_path = results_dir / 'pp_role_foundation.json'
    with open(s1_path, 'r', encoding='utf-8') as f:
        s1 = json.load(f)
    pp_role_map = s1['pp_role_map']

    azc_med_set = set(s1['azc_split']['azc_mediated'])
    b_native_set = set(s1['azc_split']['b_native'])
    print(f"PP role map: {len(pp_role_map)} MIDDLEs")
    print(f"AZC-Mediated: {len(azc_med_set)}, B-Native: {len(b_native_set)}")

    # Load PP classification
    ppc_path = PROJECT_ROOT / 'phases' / 'PP_CLASSIFICATION' / 'results' / 'pp_classification.json'
    with open(ppc_path, 'r', encoding='utf-8') as f:
        ppc_data = json.load(f)
    pp_material = {}
    for mid, info in ppc_data.get('pp_classification', {}).items():
        pp_material[mid] = info.get('material_class', 'UNKNOWN')
    print(f"PP material classifications: {len(pp_material)}")

    # Load PP/RI MIDDLE lists
    mc_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes_v2_backup.json'
    with open(mc_path, 'r', encoding='utf-8') as f:
        mc_data = json.load(f)
    pp_middles = set(mc_data['a_shared_middles'])
    ri_middles = set(mc_data['a_exclusive_middles'])

    # Initialize transcript and morphology
    tx = Transcript()
    morph = Morphology()

    # Pre-compute role and pathway for each PP MIDDLE
    mid_dominant_role = {}
    mid_pathway = {}
    for mid in pp_middles:
        data = pp_role_map.get(mid, {})
        mid_dominant_role[mid] = data.get('dominant_role')  # None if unmatched
        if mid in azc_med_set:
            mid_pathway[mid] = 'AZC_MED'
        elif mid in b_native_set:
            mid_pathway[mid] = 'B_NATIVE'
        else:
            mid_pathway[mid] = 'UNKNOWN'

    # ================================================================
    # SECTION 2: Build PP-PP Co-occurrence Lattice
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: Build PP-PP Co-occurrence Lattice")
    print("=" * 70)

    # Single-pass over A tokens: group by folio+line, extract PP MIDDLEs per record
    a_records = defaultdict(list)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if not m.middle:
            continue
        key = (token.folio, token.line)
        a_records[key].append({
            'middle': m.middle,
            'is_pp': m.middle in pp_middles,
            'is_ri': m.middle in ri_middles,
        })

    print(f"\nA records: {len(a_records)}")

    # Extract PP MIDDLEs per record and build co-occurrence pairs
    active_pp = set()
    legal_pairs = set()  # frozenset({m1, m2})
    record_pp_lists = []  # for later use in Section 4
    pair_count = Counter()  # how many records each pair co-occurs in

    for (folio, line), tokens in sorted(a_records.items()):
        pp_mids = sorted(set(t['middle'] for t in tokens if t['is_pp']))
        if len(pp_mids) < 2:
            if len(pp_mids) == 1:
                active_pp.add(pp_mids[0])
            record_pp_lists.append({
                'folio': folio, 'line': line,
                'pp_middles': pp_mids,
                'n_pp': len(pp_mids),
                'n_total': len(tokens),
            })
            continue

        active_pp.update(pp_mids)
        record_pp_lists.append({
            'folio': folio, 'line': line,
            'pp_middles': pp_mids,
            'n_pp': len(pp_mids),
            'n_total': len(tokens),
        })

        # Record all pairs
        for i in range(len(pp_mids)):
            for j in range(i + 1, len(pp_mids)):
                pair = frozenset({pp_mids[i], pp_mids[j]})
                legal_pairs.add(pair)
                pair_count[pair] += 1

    n_active = len(active_pp)
    total_possible = n_active * (n_active - 1) // 2
    n_legal = len(legal_pairs)
    incompatibility_rate = 1.0 - n_legal / total_possible if total_possible > 0 else 0.0
    density = n_legal / total_possible if total_possible > 0 else 0.0

    records_with_2plus = sum(1 for r in record_pp_lists if r['n_pp'] >= 2)

    print(f"Active PP MIDDLEs (appear in A records): {n_active}")
    print(f"Records with 2+ PP: {records_with_2plus}")
    print(f"Total possible pairs: {total_possible}")
    print(f"Legal (observed) pairs: {n_legal}")
    print(f"Incompatibility rate: {incompatibility_rate:.4f} ({incompatibility_rate*100:.1f}%)")
    print(f"Lattice density: {density:.4f} ({density*100:.1f}%)")

    # Pair recurrence stats
    pair_counts_list = list(pair_count.values())
    mean_recur = np.mean(pair_counts_list) if pair_counts_list else 0
    max_recur = max(pair_counts_list) if pair_counts_list else 0
    single_occurrence = sum(1 for c in pair_counts_list if c == 1)
    print(f"Mean pair recurrence: {mean_recur:.2f}")
    print(f"Max pair recurrence: {max_recur}")
    print(f"Single-occurrence pairs: {single_occurrence}/{n_legal} ({single_occurrence/n_legal*100:.1f}%)")

    lattice_results = {
        'n_active_pp': n_active,
        'n_records_2plus_pp': records_with_2plus,
        'total_possible_pairs': total_possible,
        'n_legal_pairs': n_legal,
        'incompatibility_rate': incompatibility_rate,
        'density': density,
        'mean_pair_recurrence': float(mean_recur),
        'max_pair_recurrence': int(max_recur),
        'single_occurrence_pairs': single_occurrence,
    }

    # ================================================================
    # SECTION 3: Role Heterogeneity of Legal Pairs (Permutation Test)
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: Role Heterogeneity of Legal Pairs")
    print("=" * 70)

    # For each legal pair where BOTH MIDDLEs have a dominant_role, check SAME vs DIFFERENT
    role_pairs = []
    pathway_pairs = []

    for pair in legal_pairs:
        m1, m2 = sorted(pair)
        r1 = mid_dominant_role.get(m1)
        r2 = mid_dominant_role.get(m2)
        if r1 is not None and r2 is not None:
            role_pairs.append((m1, m2, r1, r2))
        p1 = mid_pathway.get(m1, 'UNKNOWN')
        p2 = mid_pathway.get(m2, 'UNKNOWN')
        pathway_pairs.append((m1, m2, p1, p2))

    print(f"\nLegal pairs with both MIDDLEs role-assigned: {len(role_pairs)}")

    if len(role_pairs) >= 10:
        # Observed heterogeneity
        n_different = sum(1 for _, _, r1, r2 in role_pairs if r1 != r2)
        n_same = len(role_pairs) - n_different
        obs_heterogeneity = n_different / len(role_pairs)

        print(f"Observed: {n_different} different, {n_same} same")
        print(f"Observed heterogeneity rate: {obs_heterogeneity:.4f} ({obs_heterogeneity*100:.1f}%)")

        # Permutation test: shuffle role assignments among the MIDDLEs that appear in pairs
        # Get unique MIDDLEs in role_pairs
        pair_middles = sorted(set(m for m1, m2, _, _ in role_pairs for m in (m1, m2)))
        middle_roles = np.array([mid_dominant_role[m] for m in pair_middles])
        middle_to_idx = {m: i for i, m in enumerate(pair_middles)}

        # Pre-compute pair index arrays for fast permutation
        pair_idx1 = np.array([middle_to_idx[m1] for m1, m2, _, _ in role_pairs])
        pair_idx2 = np.array([middle_to_idx[m2] for m1, m2, _, _ in role_pairs])

        perm_heterogeneity = np.empty(N_PERMUTATIONS)
        for perm_i in range(N_PERMUTATIONS):
            shuffled = rng.permutation(middle_roles)
            r1s = shuffled[pair_idx1]
            r2s = shuffled[pair_idx2]
            n_diff = np.sum(r1s != r2s)
            perm_heterogeneity[perm_i] = n_diff / len(role_pairs)

        perm_mean = float(np.mean(perm_heterogeneity))
        perm_std = float(np.std(perm_heterogeneity))

        # Two-tailed p-value
        p_high = np.mean(perm_heterogeneity >= obs_heterogeneity)
        p_low = np.mean(perm_heterogeneity <= obs_heterogeneity)
        p_val = 2.0 * min(p_high, p_low)
        p_val = min(p_val, 1.0)

        if obs_heterogeneity > perm_mean:
            direction = 'MORE_HETEROGENEOUS'
        elif obs_heterogeneity < perm_mean:
            direction = 'LESS_HETEROGENEOUS'
        else:
            direction = 'AS_EXPECTED'

        print(f"Permutation mean: {perm_mean:.4f} (std={perm_std:.4f})")
        print(f"p-value (two-tailed): {p_val:.4f}")
        print(f"Direction: {direction}")

        heterogeneity_results = {
            'n_pairs': len(role_pairs),
            'n_different': int(n_different),
            'n_same': int(n_same),
            'obs_heterogeneity': obs_heterogeneity,
            'perm_mean': perm_mean,
            'perm_std': perm_std,
            'p_value': float(p_val),
            'direction': direction,
            'significant': p_val < 0.05,
            'n_permutations': N_PERMUTATIONS,
        }

        # Stratify by pathway
        print("\n--- Stratified by Pathway ---")
        pathway_strata = {
            'AZC_x_AZC': [],
            'BN_x_BN': [],
            'CROSS': [],
        }
        for m1, m2, r1, r2 in role_pairs:
            p1 = mid_pathway.get(m1, 'UNKNOWN')
            p2 = mid_pathway.get(m2, 'UNKNOWN')
            if p1 == 'AZC_MED' and p2 == 'AZC_MED':
                pathway_strata['AZC_x_AZC'].append((r1, r2))
            elif p1 == 'B_NATIVE' and p2 == 'B_NATIVE':
                pathway_strata['BN_x_BN'].append((r1, r2))
            else:
                pathway_strata['CROSS'].append((r1, r2))

        strata_results = {}
        for stratum, pairs in pathway_strata.items():
            if len(pairs) > 0:
                n_diff_s = sum(1 for r1, r2 in pairs if r1 != r2)
                het_s = n_diff_s / len(pairs)
                strata_results[stratum] = {
                    'n_pairs': len(pairs),
                    'n_different': n_diff_s,
                    'heterogeneity': het_s,
                }
                print(f"  {stratum}: {len(pairs)} pairs, {n_diff_s} different ({het_s*100:.1f}%)")
            else:
                strata_results[stratum] = {'n_pairs': 0}
                print(f"  {stratum}: 0 pairs")

        heterogeneity_results['pathway_strata'] = strata_results

        # Record-level role coverage: mean distinct roles per record
        record_role_counts = []
        for rec in record_pp_lists:
            if rec['n_pp'] < 2:
                continue
            roles_in_record = set()
            for mid in rec['pp_middles']:
                r = mid_dominant_role.get(mid)
                if r is not None:
                    roles_in_record.add(r)
            if roles_in_record:
                record_role_counts.append(len(roles_in_record))

        if record_role_counts:
            mean_roles = float(np.mean(record_role_counts))
            print(f"\n  Mean distinct roles per record (2+ PP): {mean_roles:.2f} "
                  f"(n={len(record_role_counts)} records)")

            # Permutation baseline for record-level coverage
            perm_role_means = np.empty(N_PERMUTATIONS)
            # Build arrays for fast permutation
            all_rec_middles = []  # list of lists of middle indices
            for rec in record_pp_lists:
                if rec['n_pp'] < 2:
                    continue
                mids_with_role = [middle_to_idx.get(m) for m in rec['pp_middles']
                                  if m in middle_to_idx]
                mids_with_role = [x for x in mids_with_role if x is not None]
                if mids_with_role:
                    all_rec_middles.append(mids_with_role)

            for perm_i in range(N_PERMUTATIONS):
                shuffled = rng.permutation(middle_roles)
                total_roles = 0
                for rec_indices in all_rec_middles:
                    roles = set(shuffled[idx] for idx in rec_indices)
                    total_roles += len(roles)
                perm_role_means[perm_i] = total_roles / len(all_rec_middles) if all_rec_middles else 0

            perm_role_mean = float(np.mean(perm_role_means))
            p_role_high = float(np.mean(perm_role_means >= mean_roles))
            p_role_low = float(np.mean(perm_role_means <= mean_roles))
            p_role = 2.0 * min(p_role_high, p_role_low)
            p_role = min(p_role, 1.0)

            heterogeneity_results['record_role_coverage'] = {
                'mean_roles_per_record': mean_roles,
                'n_records': len(record_role_counts),
                'perm_mean': perm_role_mean,
                'p_value': p_role,
                'significant': p_role < 0.05,
            }
            sig = "*" if p_role < 0.05 else ""
            print(f"  Permutation baseline: {perm_role_mean:.2f}")
            print(f"  p-value: {p_role:.4f} {sig}")
    else:
        heterogeneity_results = {'verdict': 'INSUFFICIENT_ROLE_PAIRS', 'n_pairs': len(role_pairs)}
        print("  Insufficient role-assigned pairs for permutation test")

    # ================================================================
    # SECTION 4: Material Class Consistency (Permutation Test)
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: Material Class Consistency")
    print("=" * 70)

    # For each A record, collect material classes of PP MIDDLEs
    # Classify: ALL_ANIMAL, ALL_HERB, MIXED, NEUTRAL_ONLY
    # Require 2+ non-neutral PP for classification
    classified_records = []
    material_per_record = []

    for rec in record_pp_lists:
        if rec['n_pp'] < 2:
            continue

        mat_list = []
        for mid in rec['pp_middles']:
            mat = pp_material.get(mid, 'UNKNOWN')
            if mat not in ('NEUTRAL', 'UNKNOWN'):
                mat_list.append(mat)

        if len(mat_list) < 2:
            continue

        unique_mats = set(mat_list)
        if unique_mats == {'ANIMAL'}:
            consistency = 'ALL_ANIMAL'
        elif unique_mats == {'HERB'}:
            consistency = 'ALL_HERB'
        elif unique_mats == {'MIXED'}:
            consistency = 'ALL_MIXED'
        else:
            consistency = 'HETEROGENEOUS'

        classified_records.append({
            'folio': rec['folio'],
            'line': rec['line'],
            'n_pp': rec['n_pp'],
            'materials': mat_list,
            'consistency': consistency,
        })
        material_per_record.append(mat_list)

    n_classified = len(classified_records)
    consistency_counts = Counter(r['consistency'] for r in classified_records)
    n_consistent = consistency_counts.get('ALL_ANIMAL', 0) + consistency_counts.get('ALL_HERB', 0)
    obs_consistency = n_consistent / n_classified if n_classified > 0 else 0

    print(f"\nRecords with 2+ non-neutral PP: {n_classified}")
    for cat, count in sorted(consistency_counts.items()):
        print(f"  {cat}: {count} ({count/n_classified*100:.1f}%)")
    print(f"Observed consistency rate: {obs_consistency:.4f} ({obs_consistency*100:.1f}%)")

    # Permutation test: shuffle material class assignments among PP MIDDLEs
    if n_classified >= 10:
        # Get all unique PP MIDDLEs that appear in classified records
        all_mats_in_records = set()
        for rec in classified_records:
            for mid in rec.get('materials', []):
                pass  # We need middles, not materials

        # Rebuild: for each classified record, we need the PP middles and their material classes
        # Re-extract from record_pp_lists
        classified_with_middles = []
        for rec in record_pp_lists:
            if rec['n_pp'] < 2:
                continue
            non_neutral_mids = []
            for mid in rec['pp_middles']:
                mat = pp_material.get(mid, 'UNKNOWN')
                if mat not in ('NEUTRAL', 'UNKNOWN'):
                    non_neutral_mids.append(mid)
            if len(non_neutral_mids) >= 2:
                classified_with_middles.append(non_neutral_mids)

        # Build mapping: unique PP MIDDLEs with non-neutral material -> material class
        non_neutral_pp = sorted(set(mid for mids in classified_with_middles for mid in mids))
        pp_mat_array = np.array([pp_material.get(mid, 'UNKNOWN') for mid in non_neutral_pp])
        pp_to_idx = {mid: i for i, mid in enumerate(non_neutral_pp)}

        # Pre-compute record index arrays
        record_idx_lists = []
        for mids in classified_with_middles:
            indices = [pp_to_idx[mid] for mid in mids if mid in pp_to_idx]
            if len(indices) >= 2:
                record_idx_lists.append(indices)

        def compute_consistency(mat_array):
            """Count records where all non-neutral PP have same material class."""
            n_cons = 0
            for indices in record_idx_lists:
                mats = set(mat_array[idx] for idx in indices)
                if len(mats) == 1 and ('ANIMAL' in mats or 'HERB' in mats):
                    n_cons += 1
            return n_cons

        obs_n_consistent = compute_consistency(pp_mat_array)
        obs_rate = obs_n_consistent / len(record_idx_lists) if record_idx_lists else 0

        print(f"\nPermutation test (n={N_PERMUTATIONS})...")
        perm_consistencies = np.empty(N_PERMUTATIONS)
        for perm_i in range(N_PERMUTATIONS):
            shuffled = rng.permutation(pp_mat_array)
            perm_consistencies[perm_i] = compute_consistency(shuffled)

        perm_mean = float(np.mean(perm_consistencies))
        perm_std = float(np.std(perm_consistencies))
        perm_rate_mean = perm_mean / len(record_idx_lists) if record_idx_lists else 0

        # One-tailed: is observed consistency HIGHER than expected?
        p_high = float(np.mean(perm_consistencies >= obs_n_consistent))
        # Also compute two-tailed
        p_low = float(np.mean(perm_consistencies <= obs_n_consistent))
        p_two = 2.0 * min(p_high, p_low)
        p_two = min(p_two, 1.0)

        if obs_rate > perm_rate_mean:
            direction = 'MORE_CONSISTENT'
        elif obs_rate < perm_rate_mean:
            direction = 'LESS_CONSISTENT'
        else:
            direction = 'AS_EXPECTED'

        print(f"Observed consistent records: {obs_n_consistent}/{len(record_idx_lists)} ({obs_rate*100:.1f}%)")
        print(f"Permutation mean: {perm_mean:.1f} ({perm_rate_mean*100:.1f}%)")
        print(f"Permutation std: {perm_std:.2f}")
        print(f"p-value (one-tailed, obs >= perm): {p_high:.4f}")
        print(f"p-value (two-tailed): {p_two:.4f}")
        print(f"Direction: {direction}")

        material_results = {
            'n_classified_records': n_classified,
            'consistency_distribution': dict(consistency_counts),
            'obs_consistent': obs_n_consistent,
            'obs_rate': obs_rate,
            'n_records_tested': len(record_idx_lists),
            'perm_mean': perm_mean,
            'perm_std': perm_std,
            'perm_rate_mean': perm_rate_mean,
            'p_one_tailed': p_high,
            'p_two_tailed': p_two,
            'direction': direction,
            'significant_one_tailed': p_high < 0.05,
            'significant_two_tailed': p_two < 0.05,
            'n_permutations': N_PERMUTATIONS,
            'n_unique_non_neutral_pp': len(non_neutral_pp),
        }

        # Stratify by section (from folio name)
        # Currier A sections: extract section from folio
        # A sections mapping is complex; use folio ranges as proxy
        # For now, report per-folio consistency
        folio_consistency = defaultdict(lambda: {'consistent': 0, 'total': 0})
        for rec in classified_records:
            folio = rec['folio']
            folio_consistency[folio]['total'] += 1
            if rec['consistency'] in ('ALL_ANIMAL', 'ALL_HERB'):
                folio_consistency[folio]['consistent'] += 1

        folio_rates = {}
        for folio, counts in sorted(folio_consistency.items()):
            if counts['total'] >= 3:
                rate = counts['consistent'] / counts['total']
                folio_rates[folio] = {
                    'consistent': counts['consistent'],
                    'total': counts['total'],
                    'rate': rate,
                }

        material_results['per_folio_consistency'] = folio_rates
        if folio_rates:
            rates_list = [v['rate'] for v in folio_rates.values()]
            print(f"\nPer-folio consistency (folios with 3+ records):")
            print(f"  N folios: {len(folio_rates)}")
            print(f"  Mean rate: {np.mean(rates_list):.3f}")
            print(f"  Min: {min(rates_list):.3f}, Max: {max(rates_list):.3f}")

        # Cross-tabulate material_class x dominant_role (chi-squared, Cramer's V)
        print("\n--- Material x Role Cross-Tabulation ---")
        mat_role_table = defaultdict(Counter)
        for mid in non_neutral_pp:
            mat = pp_material.get(mid, 'UNKNOWN')
            role = mid_dominant_role.get(mid)
            if role is not None and mat not in ('NEUTRAL', 'UNKNOWN'):
                mat_role_table[mat][role] += 1

        materials_present = sorted(mat_role_table.keys())
        roles_present = sorted(set(r for counts in mat_role_table.values() for r in counts.keys()))

        if len(materials_present) >= 2 and len(roles_present) >= 2:
            # Build contingency table
            table = []
            for mat in materials_present:
                row = [mat_role_table[mat].get(r, 0) for r in roles_present]
                table.append(row)
            table = np.array(table, dtype=float)

            # Chi-squared test
            row_totals = table.sum(axis=1)
            col_totals = table.sum(axis=0)
            grand_total = table.sum()

            expected = np.outer(row_totals, col_totals) / grand_total
            # Mask cells with expected < 1
            valid = expected >= 1.0
            if valid.sum() >= 4:
                chi2 = np.sum((table[valid] - expected[valid])**2 / expected[valid])
                df = (len(materials_present) - 1) * (len(roles_present) - 1)
                p_chi2 = chi2_sf(float(chi2), df)
                k = min(len(materials_present), len(roles_present))
                cramers_v = np.sqrt(chi2 / (grand_total * (k - 1))) if grand_total * (k - 1) > 0 else 0

                material_results['material_role_crosstab'] = {
                    'materials': materials_present,
                    'roles': roles_present,
                    'table': table.tolist(),
                    'chi2': float(chi2),
                    'df': df,
                    'p': float(p_chi2),
                    'cramers_v': float(cramers_v),
                    'significant': p_chi2 < 0.05,
                    'warning': 'Some expected counts < 5' if np.any(expected < 5) else None,
                }

                print(f"  Materials: {materials_present}")
                print(f"  Roles: {[ROLE_SHORT.get(r, r) for r in roles_present]}")
                for i, mat in enumerate(materials_present):
                    print(f"    {mat}: {[int(x) for x in table[i]]}")
                print(f"  Chi2={chi2:.2f}, df={df}, p={p_chi2:.4f}, Cramer's V={cramers_v:.3f}")
                if np.any(expected < 5):
                    print("  WARNING: Some expected counts < 5")
            else:
                material_results['material_role_crosstab'] = {'verdict': 'TOO_SPARSE'}
                print("  Too sparse for chi-squared test")
        else:
            material_results['material_role_crosstab'] = {'verdict': 'INSUFFICIENT_CATEGORIES'}
            print("  Insufficient categories for cross-tabulation")
    else:
        material_results = {
            'verdict': 'INSUFFICIENT_DATA',
            'n_classified_records': n_classified,
        }
        print("  Insufficient classified records for permutation test")

    # ================================================================
    # SECTION 5: Summary and Save
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Lattice verdict
    if density < 0.05:
        lattice_verdict = 'VERY_SPARSE'
    elif density < 0.20:
        lattice_verdict = 'SPARSE'
    elif density < 0.50:
        lattice_verdict = 'MODERATE'
    else:
        lattice_verdict = 'DENSE'

    # Heterogeneity verdict
    het_sig = heterogeneity_results.get('significant', False)
    het_dir = heterogeneity_results.get('direction', 'UNKNOWN')
    if het_sig and het_dir == 'MORE_HETEROGENEOUS':
        het_verdict = 'RECORDS_PREFER_ROLE_MIXING'
    elif het_sig and het_dir == 'LESS_HETEROGENEOUS':
        het_verdict = 'RECORDS_PREFER_ROLE_HOMOGENEITY'
    elif not het_sig:
        het_verdict = 'ROLE_MIXING_AS_EXPECTED'
    else:
        het_verdict = 'INCONCLUSIVE'

    # Material verdict
    mat_sig = material_results.get('significant_one_tailed', False)
    mat_dir = material_results.get('direction', 'UNKNOWN')
    if mat_sig and mat_dir == 'MORE_CONSISTENT':
        mat_verdict = 'MATERIAL_CONSISTENCY_ABOVE_CHANCE'
    elif mat_sig and mat_dir == 'LESS_CONSISTENT':
        mat_verdict = 'MATERIAL_CONSISTENCY_BELOW_CHANCE'
    else:
        mat_verdict = 'MATERIAL_CONSISTENCY_AT_CHANCE'

    summary = {
        'lattice_density': f"{density:.4f} ({lattice_verdict})",
        'n_legal_pairs': n_legal,
        'n_active_pp': n_active,
        'role_heterogeneity_verdict': het_verdict,
        'material_consistency_verdict': mat_verdict,
    }

    for k, v in summary.items():
        print(f"  {k}: {v}")

    results = {
        'metadata': {
            'phase': 'A_TO_B_ROLE_PROJECTION',
            'script': 'lattice_material_test.py',
            'description': 'PP-PP co-occurrence lattice and material consistency in A records',
            'n_permutations': N_PERMUTATIONS,
        },
        'lattice': lattice_results,
        'role_heterogeneity': heterogeneity_results,
        'material_consistency': material_results,
        'summary': summary,
    }

    out_path = results_dir / 'lattice_material_test.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")

    print("\n" + "=" * 70)
    print("Script 3 complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
