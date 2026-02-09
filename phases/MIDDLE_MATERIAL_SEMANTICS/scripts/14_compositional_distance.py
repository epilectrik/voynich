"""
14_compositional_distance.py - Compositional Distance

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 14: Are tail MIDDLEs compositional elaborations or independent identifiers?

Background: C501 predicts distance-1 for 65.9% of B-exclusive MIDDLEs (single char
insertion/substitution). If phase-exclusive tail MIDDLEs are mostly distance-1 from
common MIDDLEs, they're compositional elaborations (operational variants). If
distance >2 dominates, they're independent identifiers (material candidates).

Method:
1. Load Currier B tokens (H track, no labels, no uncertain)
2. Extract MIDDLEs via canonical Morphology
3. Build corpus-wide folio count per MIDDLE
4. Define COMMON middles (>=15 folios) and RARE/TAIL middles (<15 folios)
5. For each folio, assign zones (SETUP/PROCESS/FINISH)
6. Identify zone-exclusive rare middles per folio
7. For each zone-exclusive rare MIDDLE: compute Levenshtein distance to every
   common MIDDLE, take the minimum
8. Do the same for non-zone-exclusive rare middles as a control group
9. Compare distributions: Mann-Whitney U test
10. Report: % at distance 1, % at distance 2, % at distance 3+
11. Also compute: containment (is any common MIDDLE a substring?) as additional measure
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import math
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology
from scipy.stats import mannwhitneyu, chi2_contingency


# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RARITY_THRESHOLD = 15  # folios: <15 = RARE/TAIL, >=15 = COMMON
MIN_FOLIO_OCCURRENCES = 2  # exclude hapax per folio for zone-exclusivity


# ============================================================
# LEVENSHTEIN DISTANCE
# ============================================================
def levenshtein(s1, s2):
    """Standard dynamic programming Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with line/paragraph metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        # Text tokens only (P-prefixed placements)
        if not tok.placement.startswith('P'):
            continue

        m = morph.extract(tok.word)
        if m.middle is None or m.middle == '_EMPTY_':
            continue

        tokens.append({
            'word': tok.word,
            'middle': m.middle,
            'folio': tok.folio,
            'line': tok.line,
            'par_initial': tok.par_initial,
            'line_initial': tok.line_initial,
        })

    return tokens


# ============================================================
# PARAGRAPH BOUNDARY DETECTION
# ============================================================
def assign_paragraphs(folio_tokens):
    """
    Assign paragraph numbers to tokens within a folio.
    par_initial=True on a line-initial token signals paragraph start.
    """
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)

    return para_assignments


# ============================================================
# ZONE ASSIGNMENT
# ============================================================
def assign_zones(folio_tokens, para_assignments):
    """
    Assign SETUP/PROCESS/FINISH zones.

    If 3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
    If 1-2 paragraphs: line-based 20/60/20 split
    """
    n_paras = max(para_assignments) if para_assignments else 0

    if n_paras >= 3:
        first_para = 1
        last_para = n_paras
        zones = []
        for p in para_assignments:
            if p == first_para:
                zones.append('SETUP')
            elif p == last_para:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones
    else:
        # Line-based 20/60/20 split
        lines = []
        seen = set()
        for tok in folio_tokens:
            if tok['line'] not in seen:
                lines.append(tok['line'])
                seen.add(tok['line'])

        n_lines = len(lines)
        if n_lines < 3:
            return ['PROCESS'] * len(folio_tokens)

        setup_end = max(1, int(n_lines * 0.2))
        finish_start = n_lines - max(1, int(n_lines * 0.2))

        setup_lines = set(lines[:setup_end])
        finish_lines = set(lines[finish_start:])

        zones = []
        for tok in folio_tokens:
            if tok['line'] in setup_lines:
                zones.append('SETUP')
            elif tok['line'] in finish_lines:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    print("=" * 70)
    print("TEST 14: COMPOSITIONAL DISTANCE")
    print("=" * 70)

    print("\nLoading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)

    print(f"  B folios: {len(folio_groups)}")

    # ---- Pre-compute: corpus-wide MIDDLE folio counts ----
    middle_folios = defaultdict(set)
    for tok in all_tokens:
        middle_folios[tok['middle']].add(tok['folio'])

    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    # Classify COMMON vs RARE/TAIL
    common_middles = {m for m, c in middle_folio_count.items() if c >= RARITY_THRESHOLD}
    rare_middles = {m for m, c in middle_folio_count.items() if c < RARITY_THRESHOLD}

    print(f"\n  COMMON MIDDLEs (>={RARITY_THRESHOLD} folios): {len(common_middles)}")
    print(f"  RARE/TAIL MIDDLEs (<{RARITY_THRESHOLD} folios): {len(rare_middles)}")

    # ---- Per-folio zone analysis to identify zone-exclusive rare middles ----
    # A MIDDLE is zone-exclusive on a given folio if it appears in only 1 zone
    # on that folio AND has 2+ occurrences on that folio (not hapax).
    zone_exclusive_rare = set()  # set of rare MIDDLE strings that are zone-exclusive somewhere
    non_exclusive_rare = set()   # set of rare MIDDLE strings that are non-exclusive somewhere

    # Track per-middle exclusivity status across all folios
    middle_exclusivity = defaultdict(lambda: {'exclusive_count': 0, 'non_exclusive_count': 0})

    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]

        # Assign paragraphs and zones
        para_assignments = assign_paragraphs(ftokens)
        zones = assign_zones(ftokens, para_assignments)

        # Count per-middle zone sets and folio frequency
        middle_zone_sets = defaultdict(set)
        middle_folio_freq = Counter()

        for tok, zone in zip(ftokens, zones):
            mid = tok['middle']
            middle_zone_sets[mid].add(zone)
            middle_folio_freq[mid] += 1

        # Classify each rare middle on this folio
        for mid, freq in middle_folio_freq.items():
            if mid not in rare_middles:
                continue
            if freq < MIN_FOLIO_OCCURRENCES:
                continue  # skip hapax per folio

            zones_present = middle_zone_sets[mid]
            is_exclusive = len(zones_present) == 1

            if is_exclusive:
                zone_exclusive_rare.add(mid)
                middle_exclusivity[mid]['exclusive_count'] += 1
            else:
                non_exclusive_rare.add(mid)
                middle_exclusivity[mid]['non_exclusive_count'] += 1

    # Some middles may be exclusive on some folios and non-exclusive on others.
    # Classify by majority behavior:
    # - "exclusive" = exclusive on more folios than non-exclusive
    # - "non_exclusive" = otherwise
    pure_exclusive = set()
    pure_non_exclusive = set()

    for mid, counts in middle_exclusivity.items():
        if counts['exclusive_count'] > counts['non_exclusive_count']:
            pure_exclusive.add(mid)
        else:
            pure_non_exclusive.add(mid)

    # Also include rare middles that were always hapax (never classified)
    # These are rare middles that never had 2+ occurrences on any single folio
    classified_middles = set(middle_exclusivity.keys())
    unclassified_rare = rare_middles - classified_middles

    print(f"\n  Zone-exclusive rare MIDDLEs (majority exclusive): {len(pure_exclusive)}")
    print(f"  Non-exclusive rare MIDDLEs (majority non-exclusive): {len(pure_non_exclusive)}")
    print(f"  Unclassified rare MIDDLEs (always hapax per folio): {len(unclassified_rare)}")

    # ---- Compute Levenshtein distances ----
    print("\nComputing Levenshtein distances to common MIDDLEs...")

    common_list = sorted(common_middles)  # sorted for reproducibility

    def min_distance_to_common(mid):
        """Compute minimum edit distance from mid to any common MIDDLE."""
        best = float('inf')
        for c in common_list:
            d = levenshtein(mid, c)
            if d < best:
                best = d
                if d == 0:
                    break  # can't do better than 0
        return best

    def is_contained_in_common(mid):
        """Check if any common MIDDLE is a substring of mid, or mid is a substring of common."""
        for c in common_list:
            if c in mid or mid in c:
                return True
        return False

    # Compute for exclusive rare middles
    exclusive_distances = {}
    for mid in sorted(pure_exclusive):
        d = min_distance_to_common(mid)
        contained = is_contained_in_common(mid)
        exclusive_distances[mid] = {'distance': d, 'contained': contained}

    # Compute for non-exclusive rare middles
    non_exclusive_distances = {}
    for mid in sorted(pure_non_exclusive):
        d = min_distance_to_common(mid)
        contained = is_contained_in_common(mid)
        non_exclusive_distances[mid] = {'distance': d, 'contained': contained}

    # Also compute for ALL rare middles (including unclassified) as full picture
    all_rare_distances = {}
    for mid in sorted(rare_middles):
        d = min_distance_to_common(mid)
        contained = is_contained_in_common(mid)
        all_rare_distances[mid] = {'distance': d, 'contained': contained}

    print(f"  Computed distances for {len(exclusive_distances)} exclusive rare MIDDLEs")
    print(f"  Computed distances for {len(non_exclusive_distances)} non-exclusive rare MIDDLEs")
    print(f"  Computed distances for {len(all_rare_distances)} total rare MIDDLEs")

    # ---- Distance distribution analysis ----
    def analyze_distances(dist_dict, label):
        """Analyze a distance dictionary and return summary stats."""
        if not dist_dict:
            return {'n': 0, 'label': label}

        distances = [v['distance'] for v in dist_dict.values()]
        containments = [v['contained'] for v in dist_dict.values()]

        n = len(distances)
        dist_counter = Counter(distances)

        # Distance distribution
        n_dist1 = dist_counter.get(1, 0)
        n_dist2 = dist_counter.get(2, 0)
        n_dist3plus = sum(c for d, c in dist_counter.items() if d >= 3)
        n_dist0 = dist_counter.get(0, 0)

        pct_dist1 = 100 * n_dist1 / n
        pct_dist2 = 100 * n_dist2 / n
        pct_dist3plus = 100 * n_dist3plus / n
        pct_dist0 = 100 * n_dist0 / n

        mean_dist = sum(distances) / n
        median_dist = sorted(distances)[n // 2]

        # Containment rate
        n_contained = sum(containments)
        pct_contained = 100 * n_contained / n

        print(f"\n  --- {label} (n={n}) ---")
        print(f"    Distance 0 (exact match): {n_dist0} ({pct_dist0:.1f}%)")
        print(f"    Distance 1 (elaboration): {n_dist1} ({pct_dist1:.1f}%)")
        print(f"    Distance 2:               {n_dist2} ({pct_dist2:.1f}%)")
        print(f"    Distance 3+:              {n_dist3plus} ({pct_dist3plus:.1f}%)")
        print(f"    Mean distance:            {mean_dist:.2f}")
        print(f"    Median distance:          {median_dist}")
        print(f"    Contained (substring):    {n_contained} ({pct_contained:.1f}%)")

        return {
            'label': label,
            'n': n,
            'n_dist0': n_dist0,
            'n_dist1': n_dist1,
            'n_dist2': n_dist2,
            'n_dist3plus': n_dist3plus,
            'pct_dist0': round(pct_dist0, 2),
            'pct_dist1': round(pct_dist1, 2),
            'pct_dist2': round(pct_dist2, 2),
            'pct_dist3plus': round(pct_dist3plus, 2),
            'mean_distance': round(mean_dist, 4),
            'median_distance': median_dist,
            'n_contained': n_contained,
            'pct_contained': round(pct_contained, 2),
            'distance_distribution': {str(k): v for k, v in sorted(dist_counter.items())},
        }

    print("\n" + "=" * 70)
    print("DISTANCE DISTRIBUTIONS")
    print("=" * 70)

    exclusive_stats = analyze_distances(exclusive_distances, "Zone-Exclusive Rare MIDDLEs")
    non_exclusive_stats = analyze_distances(non_exclusive_distances, "Non-Exclusive Rare MIDDLEs")
    all_rare_stats = analyze_distances(all_rare_distances, "All Rare MIDDLEs")

    # ---- Statistical comparison: exclusive vs non-exclusive ----
    print("\n" + "=" * 70)
    print("STATISTICAL COMPARISON: Exclusive vs Non-Exclusive")
    print("=" * 70)

    excl_dists = [v['distance'] for v in exclusive_distances.values()]
    non_excl_dists = [v['distance'] for v in non_exclusive_distances.values()]

    if len(excl_dists) >= 5 and len(non_excl_dists) >= 5:
        u_stat, p_mw = mannwhitneyu(excl_dists, non_excl_dists, alternative='two-sided')
        print(f"\n  Mann-Whitney U = {u_stat:.1f}")
        print(f"  p-value = {p_mw:.6f}")

        # Effect size (Cohen's d)
        mean_excl = sum(excl_dists) / len(excl_dists)
        mean_non = sum(non_excl_dists) / len(non_excl_dists)
        var_excl = sum((x - mean_excl) ** 2 for x in excl_dists) / max(1, len(excl_dists) - 1)
        var_non = sum((x - mean_non) ** 2 for x in non_excl_dists) / max(1, len(non_excl_dists) - 1)
        pooled_std = math.sqrt(
            ((len(excl_dists) - 1) * var_excl + (len(non_excl_dists) - 1) * var_non)
            / (len(excl_dists) + len(non_excl_dists) - 2)
        )
        effect_d = (mean_excl - mean_non) / pooled_std if pooled_std > 0 else 0
        print(f"  Cohen's d = {effect_d:.4f}")
        print(f"  Mean exclusive: {mean_excl:.3f}, Mean non-exclusive: {mean_non:.3f}")
    else:
        u_stat = None
        p_mw = None
        effect_d = None
        mean_excl = sum(excl_dists) / len(excl_dists) if excl_dists else 0
        mean_non = sum(non_excl_dists) / len(non_excl_dists) if non_excl_dists else 0
        print("\n  Insufficient data for Mann-Whitney U test")

    # ---- Chi-square: elaboration (dist<=1) vs independent (dist>=2) ----
    print("\n  Chi-square: Elaboration (dist<=1) vs Independent (dist>=2)")

    excl_elab = sum(1 for d in excl_dists if d <= 1)
    excl_indep = sum(1 for d in excl_dists if d >= 2)
    non_elab = sum(1 for d in non_excl_dists if d <= 1)
    non_indep = sum(1 for d in non_excl_dists if d >= 2)

    if min(excl_elab, excl_indep, non_elab, non_indep) >= 1:
        table = [[excl_elab, excl_indep], [non_elab, non_indep]]
        # Use chi-square if all cells >= 5, otherwise note low counts
        if min(excl_elab, excl_indep, non_elab, non_indep) >= 5:
            chi2, p_chi, _, _ = chi2_contingency(table)
        else:
            chi2, p_chi, _, _ = chi2_contingency(table, correction=True)
        print(f"  Table: exclusive[elab={excl_elab}, indep={excl_indep}], "
              f"non-exclusive[elab={non_elab}, indep={non_indep}]")
        print(f"  Chi-square = {chi2:.4f}, p = {p_chi:.6f}")
    else:
        chi2 = None
        p_chi = None
        print("  Insufficient data for chi-square test")

    # ---- Containment comparison ----
    excl_contained = sum(1 for v in exclusive_distances.values() if v['contained'])
    non_contained = sum(1 for v in non_exclusive_distances.values() if v['contained'])
    pct_excl_contained = 100 * excl_contained / len(exclusive_distances) if exclusive_distances else 0
    pct_non_contained = 100 * non_contained / len(non_exclusive_distances) if non_exclusive_distances else 0

    print(f"\n  Containment rate (exclusive): {excl_contained}/{len(exclusive_distances)} "
          f"({pct_excl_contained:.1f}%)")
    print(f"  Containment rate (non-exclusive): {non_contained}/{len(non_exclusive_distances)} "
          f"({pct_non_contained:.1f}%)")

    # ---- Top examples ----
    print("\n" + "=" * 70)
    print("EXAMPLES: Zone-Exclusive Rare MIDDLEs")
    print("=" * 70)

    # Show some distance-1 examples (elaborations)
    dist1_examples = [(mid, v) for mid, v in exclusive_distances.items() if v['distance'] == 1]
    if dist1_examples:
        print(f"\n  Distance-1 examples (elaborations, n={len(dist1_examples)}):")
        for mid, v in sorted(dist1_examples)[:10]:
            # Find nearest common
            nearest = min(common_list, key=lambda c: levenshtein(mid, c))
            print(f"    {mid} -> {nearest} (dist=1, contained={v['contained']})")

    # Show some distance-3+ examples (independent)
    dist3_examples = [(mid, v) for mid, v in exclusive_distances.items() if v['distance'] >= 3]
    if dist3_examples:
        print(f"\n  Distance-3+ examples (independent, n={len(dist3_examples)}):")
        for mid, v in sorted(dist3_examples)[:10]:
            nearest = min(common_list, key=lambda c: levenshtein(mid, c))
            print(f"    {mid} -> {nearest} (dist={v['distance']}, contained={v['contained']})")

    # ---- Verdict ----
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    # Classification logic:
    # If >60% of exclusive rare MIDDLEs are distance-1: ELABORATION
    # If >40% of exclusive rare MIDDLEs are distance-3+: INDEPENDENT
    # Otherwise: MIXED

    pct_d1_excl = exclusive_stats.get('pct_dist1', 0) + exclusive_stats.get('pct_dist0', 0)
    pct_d3_excl = exclusive_stats.get('pct_dist3plus', 0)

    if pct_d1_excl > 60:
        verdict = "ELABORATION"
        verdict_detail = (f"Zone-exclusive rare MIDDLEs are predominantly distance-0/1 "
                          f"({pct_d1_excl:.1f}%), indicating compositional elaborations "
                          f"(operational variants of common MIDDLEs)")
    elif pct_d3_excl > 40:
        verdict = "INDEPENDENT"
        verdict_detail = (f"Zone-exclusive rare MIDDLEs are predominantly distance-3+ "
                          f"({pct_d3_excl:.1f}%), indicating independent identifiers "
                          f"(material candidates)")
    else:
        verdict = "MIXED"
        verdict_detail = (f"Zone-exclusive rare MIDDLEs show mixed distances: "
                          f"dist-0/1={pct_d1_excl:.1f}%, dist-3+={pct_d3_excl:.1f}%, "
                          f"indicating partial elaboration with some independent vocabulary")

    # Additional note on exclusive vs non-exclusive comparison
    comparison_note = ""
    if p_mw is not None:
        if p_mw < 0.05:
            comparison_note = (f"Exclusive vs non-exclusive distances differ significantly "
                               f"(p={p_mw:.4f}, d={effect_d:.3f})")
        else:
            comparison_note = (f"Exclusive vs non-exclusive distances do NOT differ significantly "
                               f"(p={p_mw:.4f}, d={effect_d:.3f})")

    notes = f"{verdict_detail}. {comparison_note}"

    print(f"\n  Verdict: {verdict}")
    print(f"  {verdict_detail}")
    if comparison_note:
        print(f"  {comparison_note}")

    # ---- Save results ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "test": "Compositional Distance",
        "question": "Are tail MIDDLEs compositional elaborations or independent identifiers?",
        "n_common_middles": len(common_middles),
        "n_rare_middles": len(rare_middles),
        "rarity_threshold_folios": RARITY_THRESHOLD,
        "n_exclusive_rare": len(pure_exclusive),
        "n_non_exclusive_rare": len(pure_non_exclusive),
        "n_unclassified_rare": len(unclassified_rare),
        "exclusive_distances": exclusive_stats,
        "non_exclusive_distances": non_exclusive_stats,
        "all_rare_distances": all_rare_stats,
        "comparison": {
            "mann_whitney_u": round(u_stat, 2) if u_stat is not None else None,
            "p_value": round(p_mw, 6) if p_mw is not None else None,
            "effect_size_d": round(effect_d, 4) if effect_d is not None else None,
            "mean_exclusive": round(mean_excl, 4),
            "mean_non_exclusive": round(mean_non, 4),
            "chi2_elab_vs_indep": round(chi2, 4) if chi2 is not None else None,
            "chi2_p_value": round(p_chi, 6) if p_chi is not None else None,
            "contingency_table": {
                "exclusive": {"elaboration_d01": excl_elab, "independent_d2plus": excl_indep},
                "non_exclusive": {"elaboration_d01": non_elab, "independent_d2plus": non_indep},
            },
        },
        "containment": {
            "exclusive_rate": round(pct_excl_contained, 2),
            "non_exclusive_rate": round(pct_non_contained, 2),
            "exclusive_n": excl_contained,
            "non_exclusive_n": non_contained,
        },
        "verdict": verdict,
        "notes": notes,
    }

    output_path = RESULTS_DIR / 'compositional_distance.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
