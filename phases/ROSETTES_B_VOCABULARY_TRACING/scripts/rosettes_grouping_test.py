"""Phase 401 Final Test: Rosette Grouping and Exhaustion

Three-part battery to exhaust the Rosettes-B vocabulary investigation:
  Part A: Rosette pairing affinity matrix (which rosettes share B-folio vocabulary?)
  Part B: Grouped section discrimination (T-targeting vs S-targeting groups)
  Part C: PREFIX+MIDDLE exhaustion check (any signal beyond individual MIDDLEs?)

Groups based on T3 section targeting results:
  T-targeting: CENTER (8) + NORTH (3) + NW (4) = 15 informative MIDDLEs
  S-targeting: WEST (5) + SW (4) = 9 informative MIDDLEs
  Depleted: SOUTH (2) + NE (0) + SE (0) = too sparse

References: C1091, C1098, C1109, Phase 401 T1-T6 results
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, RosettesAnalyzer

RESULTS_DIR = PROJECT / 'phases' / 'ROSETTES_B_VOCABULARY_TRACING' / 'results'

# Section-targeting groups from T3 results
T_GROUP = ['CENTER', 'NORTH', 'NW']  # → Section T (pharma/recipe)
S_GROUP = ['WEST', 'SW']             # → Section S (Stars/pharma)


def jaccard(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def load_data():
    """Load from Phase 401 results + raw data."""
    # Load T1 results for informative MIDDLE lists
    t1_path = RESULTS_DIR / 'rosettes_b_tracing_results.json'
    with open(t1_path) as f:
        prior = json.load(f)
    informative_lists = prior['t1']['informative_lists']

    # Load bridge set
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # Load per-rosette MIDDLE lists (full, including bridges)
    prof_path = PROJECT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results' / 'rosettes_functional_profiling.json'
    with open(prof_path) as f:
        prof_data = json.load(f)
    rosette_middles = {k: set(v) for k, v in prof_data['rosette_middles'].items()}

    # B corpus data
    tx = Transcript()
    morph = Morphology()

    b_folio_middles = defaultdict(set)
    b_folio_prefix_middles = defaultdict(set)  # PREFIX+MIDDLE combinations
    folio_section = {}

    for tok in tx.currier_b():
        word = tok.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle != '_EMPTY_':
            b_folio_middles[tok.folio].add(m.middle)
            pm_combo = f"{m.prefix or 'BARE'}+{m.middle}"
            b_folio_prefix_middles[tok.folio].add(pm_combo)
        folio_section[tok.folio] = tok.section

    # Build rosette PREFIX+MIDDLE sets from raw tokens
    ra = RosettesAnalyzer()
    rosette_prefix_middles = defaultdict(set)
    rosette_regions = prof_data['rosette_regions']

    for ros_name, regions in rosette_regions.items():
        for region_code in regions:
            tokens = ra.get_tokens('f85v2', region=region_code)
            for tok in tokens:
                word = tok.word.strip() if tok.word else ''
                if not word or '*' in word:
                    continue
                m = morph.extract(word)
                if m.middle and m.middle != '_EMPTY_':
                    pm = f"{m.prefix or 'BARE'}+{m.middle}"
                    rosette_prefix_middles[ros_name].add(pm)

    b_corpus_middles = set()
    for ms in b_folio_middles.values():
        b_corpus_middles |= ms

    b_corpus_pm = set()
    for pms in b_folio_prefix_middles.values():
        b_corpus_pm |= pms

    print(f"Loaded: {len(informative_lists)} rosettes, {len(b_folio_middles)} B folios")

    return {
        'informative_lists': informative_lists,
        'rosette_middles': rosette_middles,
        'rosette_prefix_middles': dict(rosette_prefix_middles),
        'bridge_set': bridge_set,
        'b_folio_middles': dict(b_folio_middles),
        'b_folio_prefix_middles': dict(b_folio_prefix_middles),
        'b_corpus_middles': b_corpus_middles,
        'b_corpus_pm': b_corpus_pm,
        'folio_section': folio_section,
        'morph': morph,
    }


# ---------------------------------------------------------------------------
# Part A: Rosette Pairing Affinity Matrix
# ---------------------------------------------------------------------------

def part_a_pairing_affinity(data):
    """Pairwise Jaccard of informative vocabularies + B-folio overlap affinity."""
    print("\n=== Part A: Rosette Pairing Affinity ===")

    informative_lists = data['informative_lists']
    b_folio_middles = data['b_folio_middles']

    rosettes = sorted(informative_lists.keys())

    # 1. Pairwise Jaccard of INFORMATIVE vocabulary
    print("\n  Informative vocabulary pairwise Jaccard:")
    vocab_matrix = {}
    for r1 in rosettes:
        vocab_matrix[r1] = {}
        for r2 in rosettes:
            s1 = set(informative_lists[r1])
            s2 = set(informative_lists[r2])
            vocab_matrix[r1][r2] = round(jaccard(s1, s2), 3)

    # Print matrix
    header = "          " + " ".join(f"{r:>8s}" for r in rosettes)
    print(f"  {header}")
    for r1 in rosettes:
        row = f"  {r1:8s}  " + " ".join(f"{vocab_matrix[r1][r2]:8.3f}" for r2 in rosettes)
        print(row)

    # 2. B-folio overlap affinity: for each pair of rosettes, how many B folios
    #    share informative vocabulary with BOTH?
    print("\n  B-folio co-targeting (folios sharing informative vocab with both rosettes):")
    cotarget_matrix = {}
    for r1 in rosettes:
        cotarget_matrix[r1] = {}
        s1 = set(informative_lists[r1])
        for r2 in rosettes:
            s2 = set(informative_lists[r2])
            if not s1 or not s2:
                cotarget_matrix[r1][r2] = 0
                continue
            n_both = sum(1 for f, mids in b_folio_middles.items()
                         if (mids & s1) and (mids & s2))
            cotarget_matrix[r1][r2] = n_both

    header = "          " + " ".join(f"{r:>8s}" for r in rosettes)
    print(f"  {header}")
    for r1 in rosettes:
        row = f"  {r1:8s}  " + " ".join(f"{cotarget_matrix[r1][r2]:8d}" for r2 in rosettes)
        print(row)

    # 3. Identify natural clusters
    # Compute mean within-group vs between-group affinity for T-group and S-group
    t_set = set(T_GROUP) & set(rosettes)
    s_set = set(S_GROUP) & set(rosettes)

    within_t = []
    within_s = []
    between_ts = []
    for r1 in rosettes:
        for r2 in rosettes:
            if r1 >= r2:
                continue
            j = vocab_matrix[r1][r2]
            if r1 in t_set and r2 in t_set:
                within_t.append(j)
            elif r1 in s_set and r2 in s_set:
                within_s.append(j)
            elif (r1 in t_set and r2 in s_set) or (r1 in s_set and r2 in t_set):
                between_ts.append(j)

    mean_within_t = sum(within_t) / len(within_t) if within_t else 0
    mean_within_s = sum(within_s) / len(within_s) if within_s else 0
    mean_between = sum(between_ts) / len(between_ts) if between_ts else 0

    print(f"\n  Cluster coherence:")
    print(f"    T-group ({', '.join(sorted(t_set))}): mean within Jaccard = {mean_within_t:.3f}")
    print(f"    S-group ({', '.join(sorted(s_set))}): mean within Jaccard = {mean_within_s:.3f}")
    print(f"    Between T/S groups: mean Jaccard = {mean_between:.3f}")

    # Identify strongest pairs
    pairs = []
    for r1 in rosettes:
        for r2 in rosettes:
            if r1 < r2:
                j = vocab_matrix[r1][r2]
                if j > 0:
                    pairs.append((r1, r2, j))
    pairs.sort(key=lambda x: -x[2])

    print(f"\n  Strongest rosette pairs (by informative vocabulary Jaccard):")
    for r1, r2, j in pairs[:10]:
        shared = set(informative_lists[r1]) & set(informative_lists[r2])
        print(f"    {r1:8s} + {r2:8s}: Jaccard={j:.3f}  shared={sorted(shared)}")

    return {
        'vocab_jaccard_matrix': vocab_matrix,
        'cotarget_matrix': {r1: {r2: v for r2, v in row.items()} for r1, row in cotarget_matrix.items()},
        'cluster_coherence': {
            't_group_within': round(mean_within_t, 4),
            's_group_within': round(mean_within_s, 4),
            'between_groups': round(mean_between, 4),
        },
        'top_pairs': [(r1, r2, round(j, 3)) for r1, r2, j in pairs[:10]],
    }


# ---------------------------------------------------------------------------
# Part B: Grouped Section Discrimination
# ---------------------------------------------------------------------------

def part_b_grouped_discrimination(data):
    """Pool T-group and S-group informative MIDDLEs, test section discrimination."""
    print("\n=== Part B: Grouped Section Discrimination ===")

    informative_lists = data['informative_lists']
    b_folio_middles = data['b_folio_middles']
    folio_section = data['folio_section']

    # Pool informative MIDDLEs by group
    t_pool = set()
    for ros in T_GROUP:
        if ros in informative_lists:
            t_pool.update(informative_lists[ros])

    s_pool = set()
    for ros in S_GROUP:
        if ros in informative_lists:
            s_pool.update(informative_lists[ros])

    print(f"  T-group pool ({', '.join(T_GROUP)}): {len(t_pool)} informative MIDDLEs")
    print(f"    MIDDLEs: {sorted(t_pool)}")
    print(f"  S-group pool ({', '.join(S_GROUP)}): {len(s_pool)} informative MIDDLEs")
    print(f"    MIDDLEs: {sorted(s_pool)}")
    print(f"  Overlap: {sorted(t_pool & s_pool)}")

    random.seed(42)
    group_results = {}

    for group_name, pool in [('T_GROUP', t_pool), ('S_GROUP', s_pool)]:
        if not pool:
            continue

        # Per-section overlap
        section_overlaps = defaultdict(list)
        for folio, middles in b_folio_middles.items():
            sec = folio_section.get(folio)
            if not sec:
                continue
            n_shared = len(middles & pool)
            section_overlaps[sec].append(n_shared)

        # ANOVA
        all_vals = []
        for sec, vals in section_overlaps.items():
            all_vals.extend(vals)
        grand_mean = sum(all_vals) / len(all_vals) if all_vals else 0
        k = len(section_overlaps)
        n_total = len(all_vals)

        ss_between = sum(len(vals) * (sum(vals)/len(vals) - grand_mean)**2
                         for vals in section_overlaps.values())
        ss_within = sum(sum((v - sum(vals)/len(vals))**2 for v in vals)
                        for vals in section_overlaps.values())
        df_b = k - 1
        df_w = n_total - k

        if df_w > 0 and ss_within > 0:
            f_ratio = (ss_between / df_b) / (ss_within / df_w)
        else:
            f_ratio = 0

        # Permutation p-value
        n_perm = 1000
        perm_f_count = 0
        for _ in range(n_perm):
            shuffled = all_vals[:]
            random.shuffle(shuffled)
            perm_groups = defaultdict(list)
            idx = 0
            for sec, vals in section_overlaps.items():
                for _ in vals:
                    perm_groups[sec].append(shuffled[idx])
                    idx += 1
            perm_gm = sum(shuffled) / len(shuffled)
            perm_ssb = sum(len(perm_groups[s]) * (sum(perm_groups[s])/len(perm_groups[s]) - perm_gm)**2
                           for s in perm_groups)
            perm_ssw = sum(sum((v - sum(perm_groups[s])/len(perm_groups[s]))**2 for v in perm_groups[s])
                           for s in perm_groups)
            if perm_ssw > 0:
                perm_f = (perm_ssb / df_b) / (perm_ssw / df_w)
                if perm_f >= f_ratio:
                    perm_f_count += 1
        perm_p = perm_f_count / n_perm

        section_means = {s: round(sum(v)/len(v), 3) for s, v in sorted(section_overlaps.items())}
        top_section = max(section_means, key=section_means.get)

        print(f"\n  {group_name}: F={f_ratio:.2f}, perm_p={perm_p:.4f}, "
              f"top_section={top_section}")
        print(f"    Section means: {section_means}")

        # Per-section enrichment ratio vs grand mean
        enrichment = {s: round(m / grand_mean, 2) if grand_mean > 0 else 0
                      for s, m in section_means.items()}
        print(f"    Enrichment vs mean: {enrichment}")

        group_results[group_name] = {
            'n_pool': len(pool),
            'pool_middles': sorted(pool),
            'f_ratio': round(f_ratio, 3),
            'perm_p': round(perm_p, 4),
            'top_section': top_section,
            'section_means': section_means,
            'enrichment': enrichment,
            'significant': perm_p < 0.05,
        }

    # Verdict
    t_sig = group_results.get('T_GROUP', {}).get('significant', False)
    s_sig = group_results.get('S_GROUP', {}).get('significant', False)
    t_top = group_results.get('T_GROUP', {}).get('top_section', '')
    s_top = group_results.get('S_GROUP', {}).get('top_section', '')

    if t_sig and s_sig and t_top != s_top:
        verdict = 'DUAL_SECTION_TARGETING_CONFIRMED'
    elif t_sig or s_sig:
        verdict = 'PARTIAL_SECTION_TARGETING'
    else:
        verdict = 'NO_GROUPED_DISCRIMINATION'

    print(f"\n  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'group_results': group_results,
    }


# ---------------------------------------------------------------------------
# Part C: PREFIX+MIDDLE Exhaustion Check
# ---------------------------------------------------------------------------

def part_c_prefix_middle_exhaustion(data):
    """Test whether PREFIX+MIDDLE combinations provide additional discrimination."""
    print("\n=== Part C: PREFIX+MIDDLE Exhaustion Check ===")

    rosette_pm = data['rosette_prefix_middles']
    b_folio_pm = data['b_folio_prefix_middles']
    bridge_set = data['bridge_set']
    b_corpus_pm = data['b_corpus_pm']
    folio_section = data['folio_section']

    # Build per-rosette informative PREFIX+MIDDLE set
    # First get Rosettes-exclusive PMs (not in any B folio)
    all_ros_pm = set()
    for pms in rosette_pm.values():
        all_ros_pm |= pms

    exclusive_pm = all_ros_pm - b_corpus_pm

    # Informative PMs: in rosette AND in B AND not bridge-based
    # A PM is "bridge-based" if its MIDDLE component is a bridge MIDDLE
    def is_bridge_pm(pm):
        parts = pm.split('+', 1)
        if len(parts) == 2:
            return parts[1] in bridge_set
        return False

    rosette_informative_pm = {}
    total_informative_pm = set()
    for ros_name, pms in sorted(rosette_pm.items()):
        in_b = pms & b_corpus_pm
        informative = {pm for pm in in_b if not is_bridge_pm(pm)}
        rosette_informative_pm[ros_name] = informative
        total_informative_pm |= informative

    print(f"  Total Rosettes PREFIX+MIDDLE combos: {len(all_ros_pm)}")
    print(f"  Exclusive (not in B): {len(exclusive_pm)}")
    print(f"  Informative (in B, non-bridge): {len(total_informative_pm)}")

    # Per-rosette informative PM counts
    for ros in sorted(rosette_informative_pm):
        n = len(rosette_informative_pm[ros])
        print(f"    {ros:8s}: {n} informative PMs")

    # Compare to MIDDLE-only: does PM resolution add any discriminative MIDDLEs?
    # A PM adds value if the same MIDDLE appears with different PREFIXes in
    # different rosettes, allowing finer discrimination
    pm_middles = set()
    for pm in total_informative_pm:
        parts = pm.split('+', 1)
        if len(parts) == 2:
            pm_middles.add(parts[1])

    # Load prior informative MIDDLE set
    informative_lists = data['informative_lists']
    prior_inf = set()
    for middles in informative_lists.values():
        prior_inf.update(middles)

    new_middles = pm_middles - prior_inf
    print(f"\n  MIDDLEs reachable via PM but not via MIDDLE-only: {len(new_middles)}")
    if new_middles:
        print(f"    New MIDDLEs: {sorted(new_middles)}")

    # Test: do informative PMs discriminate sections better than informative MIDDLEs?
    random.seed(42)

    # Pool all informative PMs and test section ANOVA
    if total_informative_pm:
        section_overlaps = defaultdict(list)
        for folio, pms in b_folio_pm.items():
            sec = folio_section.get(folio)
            if not sec:
                continue
            n_shared = len(pms & total_informative_pm)
            section_overlaps[sec].append(n_shared)

        all_vals = []
        for vals in section_overlaps.values():
            all_vals.extend(vals)
        grand_mean = sum(all_vals) / len(all_vals) if all_vals else 0
        k = len(section_overlaps)
        n_total = len(all_vals)

        ss_between = sum(len(vals) * (sum(vals)/len(vals) - grand_mean)**2
                         for vals in section_overlaps.values())
        ss_within = sum(sum((v - sum(vals)/len(vals))**2 for v in vals)
                        for vals in section_overlaps.values())
        df_b = k - 1
        df_w = n_total - k

        if df_w > 0 and ss_within > 0:
            f_ratio_pm = (ss_between / df_b) / (ss_within / df_w)
        else:
            f_ratio_pm = 0

        # Compare with MIDDLE-only F-ratio (approximate from T3 results)
        # Pool all informative MIDDLEs for section test
        section_mid_overlaps = defaultdict(list)
        b_folio_middles = data['b_folio_middles']
        for folio, mids in b_folio_middles.items():
            sec = folio_section.get(folio)
            if not sec:
                continue
            n_shared = len(mids & prior_inf)
            section_mid_overlaps[sec].append(n_shared)

        all_mid_vals = []
        for vals in section_mid_overlaps.values():
            all_mid_vals.extend(vals)
        gm_mid = sum(all_mid_vals) / len(all_mid_vals) if all_mid_vals else 0

        ssb_mid = sum(len(vals) * (sum(vals)/len(vals) - gm_mid)**2
                       for vals in section_mid_overlaps.values())
        ssw_mid = sum(sum((v - sum(vals)/len(vals))**2 for v in vals)
                       for vals in section_mid_overlaps.values())

        if df_w > 0 and ssw_mid > 0:
            f_ratio_mid = (ssb_mid / df_b) / (ssw_mid / df_w)
        else:
            f_ratio_mid = 0

        section_pm_means = {s: round(sum(v)/len(v), 3) for s, v in sorted(section_overlaps.items())}

        print(f"\n  Section ANOVA:")
        print(f"    PREFIX+MIDDLE F-ratio: {f_ratio_pm:.2f}")
        print(f"    MIDDLE-only F-ratio:   {f_ratio_mid:.2f}")
        print(f"    PM section means: {section_pm_means}")

        improvement = f_ratio_pm / f_ratio_mid if f_ratio_mid > 0 else 0
        print(f"    PM/MIDDLE F-ratio ratio: {improvement:.2f}x")

        if improvement > 1.5:
            verdict = 'PM_ADDS_DISCRIMINATION'
        else:
            verdict = 'PM_NO_ADDITIONAL_SIGNAL'
    else:
        f_ratio_pm = 0
        f_ratio_mid = 0
        improvement = 0
        verdict = 'NO_INFORMATIVE_PMS'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_ros_pm_total': len(all_ros_pm),
        'n_exclusive_pm': len(exclusive_pm),
        'n_informative_pm': len(total_informative_pm),
        'n_new_middles_via_pm': len(new_middles),
        'new_middles': sorted(new_middles) if new_middles else [],
        'f_ratio_pm': round(f_ratio_pm, 3),
        'f_ratio_mid_only': round(f_ratio_mid, 3) if f_ratio_mid else 0,
        'improvement_ratio': round(improvement, 3),
    }


# ---------------------------------------------------------------------------
# Overall
# ---------------------------------------------------------------------------

def overall_verdict(part_a, part_b, part_c):
    print("\n" + "=" * 60)
    print("FINAL VERDICT: ROSETTES-B VOCABULARY TRACING")
    print("=" * 60)

    print(f"\n  Part A (Pairing): T-group coherence={part_a['cluster_coherence']['t_group_within']:.3f}, "
          f"S-group={part_a['cluster_coherence']['s_group_within']:.3f}, "
          f"between={part_a['cluster_coherence']['between_groups']:.3f}")
    print(f"  Part B (Grouped discrimination): {part_b['verdict']}")
    print(f"  Part C (PREFIX+MIDDLE exhaustion): {part_c['verdict']}")

    dual_targeting = part_b['verdict'] == 'DUAL_SECTION_TARGETING_CONFIRMED'
    pm_adds = part_c['verdict'] == 'PM_ADDS_DISCRIMINATION'
    clusters_coherent = (part_a['cluster_coherence']['t_group_within'] >
                         part_a['cluster_coherence']['between_groups'])

    if dual_targeting and clusters_coherent:
        overall = 'SECTION_CATEGORICAL_INDEX_CONFIRMED'
        reasoning = ('Rosettes decomposes into coherent section-targeting groups. '
                     'T-group and S-group vocabularies discriminate distinct manuscript sections. '
                     'The indexing operates at section-category level, not individual-folio level.')
    elif dual_targeting or clusters_coherent:
        overall = 'PARTIAL_CATEGORICAL_INDEX'
        reasoning = ('Some evidence for section-categorical indexing but not fully coherent.')
    else:
        overall = 'BRIDGE_MEDIATED_GENERIC_INDEX'
        reasoning = ('No section-categorical structure survives grouping. '
                     'Rosettes-B connection is entirely bridge-mediated.')

    if pm_adds:
        overall += '_WITH_PM_SIGNAL'
        reasoning += ' PREFIX+MIDDLE resolution adds discrimination beyond individual MIDDLEs.'
    else:
        reasoning += ' PREFIX+MIDDLE resolution adds no signal — investigation exhausted.'

    print(f"\n  OVERALL: {overall}")
    print(f"  Reasoning: {reasoning}")

    return {
        'overall': overall,
        'reasoning': reasoning,
    }


def main():
    print("Phase 401 Final Test: Rosette Grouping and Exhaustion")
    print("=" * 55)

    data = load_data()

    part_a = part_a_pairing_affinity(data)
    part_b = part_b_grouped_discrimination(data)
    part_c = part_c_prefix_middle_exhaustion(data)
    final = overall_verdict(part_a, part_b, part_c)

    results = {
        'part_a_pairing': part_a,
        'part_b_grouped': part_b,
        'part_c_exhaustion': part_c,
        'final_verdict': final,
    }

    output_path = RESULTS_DIR / 'rosettes_grouping_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
