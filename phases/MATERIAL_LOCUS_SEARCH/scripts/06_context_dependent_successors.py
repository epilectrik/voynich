#!/usr/bin/env python3
"""
Test 6: Context-Dependent MIDDLE Successor Profiles

Question: Does the same MIDDLE show different successors in different
paragraph positions / sections?

Method:
  1. Load Currier B tokens (H track, no labels, no uncertain).
  2. For each common MIDDLE (200+ occurrences), compute successor MIDDLE
     distributions stratified by:
       - SECTION (B, H, S, T, C)
       - PARAGRAPH POSITION (EARLY / MID / LATE thirds)
  3. Per MIDDLE, chi-square test of successor distribution x section
     (Bonferroni-corrected) and successor distribution x position.
  4. KL divergence between section-stratified and position-stratified
     successor distributions.
  5. Compare: does section KL > position KL?

Pass: >30% MIDDLEs significant by section after Bonferroni,
      section KL > position KL.
Fail: Successors independent of context.

Phase: MATERIAL_LOCUS_SEARCH
"""

import sys
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================
MIN_MIDDLE_COUNT = 200          # MIDDLE must appear 200+ times in B
ALPHA = 0.05                    # significance level before Bonferroni
EPSILON = 1e-10                 # smoothing for KL divergence
MIN_SUCCESSOR_COUNT = 5         # minimum total successors per stratum

SCRIPT_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/scripts')
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
OUTPUT_PATH = RESULTS_DIR / 'context_dependent_successors.json'


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def chi2_contingency_manual(contingency_dict, row_keys, col_keys):
    """
    Manual chi-square test of independence on a contingency table.

    contingency_dict: {(row, col): count}
    row_keys: list of row categories
    col_keys: list of col categories

    Returns (chi2_stat, p_value, dof)
    Uses scipy for p-value from chi2 distribution.
    """
    from scipy.stats import chi2 as chi2_dist

    # Build marginals
    row_totals = {}
    col_totals = {}
    grand_total = 0
    for r in row_keys:
        row_totals[r] = sum(contingency_dict.get((r, c), 0) for c in col_keys)
    for c in col_keys:
        col_totals[c] = sum(contingency_dict.get((r, c), 0) for r in row_keys)
    grand_total = sum(row_totals.values())

    if grand_total == 0:
        return 0.0, 1.0, 0

    # Chi-square statistic
    chi2_stat = 0.0
    for r in row_keys:
        for c in col_keys:
            observed = contingency_dict.get((r, c), 0)
            expected = (row_totals[r] * col_totals[c]) / grand_total if grand_total > 0 else 0
            if expected > 0:
                chi2_stat += (observed - expected) ** 2 / expected

    dof = (len(row_keys) - 1) * (len(col_keys) - 1)
    if dof <= 0:
        return chi2_stat, 1.0, dof

    p_value = 1.0 - chi2_dist.cdf(chi2_stat, dof)
    return chi2_stat, p_value, dof


def kl_divergence(p_dict, q_dict, all_keys, epsilon=EPSILON):
    """
    Compute KL(P || Q) with epsilon smoothing.

    p_dict, q_dict: {key: count}
    all_keys: set of all possible keys
    Returns KL divergence in nats.
    """
    p_total = sum(p_dict.get(k, 0) for k in all_keys) + epsilon * len(all_keys)
    q_total = sum(q_dict.get(k, 0) for k in all_keys) + epsilon * len(all_keys)

    kl = 0.0
    for k in all_keys:
        p_prob = (p_dict.get(k, 0) + epsilon) / p_total
        q_prob = (q_dict.get(k, 0) + epsilon) / q_total
        kl += p_prob * math.log(p_prob / q_prob)
    return kl


def symmetric_kl(p_dict, q_dict, all_keys, epsilon=EPSILON):
    """Symmetric KL divergence = (KL(P||Q) + KL(Q||P)) / 2."""
    return (kl_divergence(p_dict, q_dict, all_keys, epsilon) +
            kl_divergence(q_dict, p_dict, all_keys, epsilon)) / 2.0


def mean_pairwise_kl(distributions, all_keys, epsilon=EPSILON):
    """
    Mean pairwise symmetric KL divergence across a set of distributions.

    distributions: list of {key: count} dicts
    Returns mean symmetric KL over all pairs.
    """
    if len(distributions) < 2:
        return 0.0
    total_kl = 0.0
    n_pairs = 0
    for i in range(len(distributions)):
        for j in range(i + 1, len(distributions)):
            total_kl += symmetric_kl(distributions[i], distributions[j], all_keys, epsilon)
            n_pairs += 1
    return total_kl / n_pairs if n_pairs > 0 else 0.0


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    print("Test 6: Context-Dependent MIDDLE Successor Profiles")
    print("=" * 65)

    tx = Transcript()
    morph = Morphology()

    # ----------------------------------------------------------
    # Step 1: Load all Currier B tokens, extract MIDDLEs
    # ----------------------------------------------------------
    print("\nLoading Currier B tokens...")

    # Collect tokens preserving ordering within lines
    # Key structure: list of dicts with word, folio, line, section, middle,
    #                par_initial, par_final
    all_tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        mid = m.middle if m.middle and m.middle != '_EMPTY_' else None
        all_tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'middle': mid,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
        })

    total_tokens = len(all_tokens)
    print(f"  Total Currier B tokens: {total_tokens}")

    # ----------------------------------------------------------
    # Step 2: Assign paragraph IDs and relative position
    # ----------------------------------------------------------
    # Build paragraph assignments using par_initial boundaries
    par_id = 0
    par_assignments = []   # parallel to all_tokens: paragraph_id for each token
    current_folio = None

    for t in all_tokens:
        if t['folio'] != current_folio:
            # New folio => new paragraph
            par_id += 1
            current_folio = t['folio']
        elif t['par_initial']:
            par_id += 1
        par_assignments.append(par_id)

    # Count tokens per paragraph
    par_token_counts = Counter(par_assignments)

    # Compute position within paragraph for each token
    par_token_index = defaultdict(int)  # par_id -> running index
    position_labels = []  # EARLY, MID, LATE for each token

    for i, pid in enumerate(par_assignments):
        idx = par_token_index[pid]
        par_token_index[pid] += 1
        n_tokens_in_par = par_token_counts[pid]

        if n_tokens_in_par < 3:
            # Too small to divide into thirds meaningfully
            position_labels.append('MID')
        else:
            # Divide into thirds
            third = n_tokens_in_par / 3.0
            if idx < third:
                position_labels.append('EARLY')
            elif idx < 2 * third:
                position_labels.append('MID')
            else:
                position_labels.append('LATE')

    print(f"  Paragraphs identified: {par_id}")
    pos_counts = Counter(position_labels)
    print(f"  Position distribution: EARLY={pos_counts.get('EARLY',0)}, "
          f"MID={pos_counts.get('MID',0)}, LATE={pos_counts.get('LATE',0)}")

    # ----------------------------------------------------------
    # Step 3: Build successor pairs
    # ----------------------------------------------------------
    # For consecutive tokens on the same line with valid MIDDLEs,
    # record (current_middle, next_middle, section, position)
    successor_pairs = []

    for i in range(len(all_tokens) - 1):
        t_curr = all_tokens[i]
        t_next = all_tokens[i + 1]

        # Must be on same line (same folio + same line number)
        if t_curr['folio'] != t_next['folio'] or t_curr['line'] != t_next['line']:
            continue

        # Both must have valid MIDDLEs
        if t_curr['middle'] is None or t_next['middle'] is None:
            continue

        successor_pairs.append({
            'current_middle': t_curr['middle'],
            'successor_middle': t_next['middle'],
            'section': t_curr['section'],
            'position': position_labels[i],
        })

    print(f"  Successor pairs: {len(successor_pairs)}")

    # ----------------------------------------------------------
    # Step 4: Count MIDDLEs, filter to common ones (200+)
    # ----------------------------------------------------------
    middle_counts = Counter(p['current_middle'] for p in successor_pairs)
    common_middles = sorted([m for m, c in middle_counts.items() if c >= MIN_MIDDLE_COUNT])
    common_middles_set = set(common_middles)

    print(f"  Common MIDDLEs (>= {MIN_MIDDLE_COUNT} successor pairs): {len(common_middles)}")

    # ----------------------------------------------------------
    # Step 5: Pre-compute per-MIDDLE stratified successor distributions
    # ----------------------------------------------------------
    # For each common MIDDLE, build:
    #   section_successors[middle][section] = Counter of successor MIDDLEs
    #   position_successors[middle][position] = Counter of successor MIDDLEs
    section_successors = defaultdict(lambda: defaultdict(Counter))
    position_successors = defaultdict(lambda: defaultdict(Counter))

    for p in successor_pairs:
        mid = p['current_middle']
        if mid not in common_middles_set:
            continue
        section_successors[mid][p['section']][p['successor_middle']] += 1
        position_successors[mid][p['position']][p['successor_middle']] += 1

    # ----------------------------------------------------------
    # Step 6: Chi-square tests per MIDDLE
    # ----------------------------------------------------------
    n_tests = len(common_middles)
    bonferroni_alpha = ALPHA / n_tests if n_tests > 0 else ALPHA

    per_middle_results = []
    section_sig_count = 0
    position_sig_count = 0

    for mid in common_middles:
        # --- Section chi-square ---
        sec_data = section_successors[mid]
        # Get all sections and all successor MIDDLEs for this MIDDLE
        sec_keys = sorted(sec_data.keys())
        all_successors_sec = set()
        for s in sec_keys:
            all_successors_sec.update(sec_data[s].keys())
        all_successors_sec = sorted(all_successors_sec)

        # Filter: need at least 2 sections with MIN_SUCCESSOR_COUNT successors
        usable_sections = [s for s in sec_keys
                          if sum(sec_data[s].values()) >= MIN_SUCCESSOR_COUNT]

        if len(usable_sections) >= 2 and len(all_successors_sec) >= 2:
            # Build contingency dict: (successor, section) -> count
            sec_contingency = {}
            for s in usable_sections:
                for succ in all_successors_sec:
                    sec_contingency[(succ, s)] = sec_data[s].get(succ, 0)

            sec_chi2, sec_p, sec_dof = chi2_contingency_manual(
                sec_contingency, all_successors_sec, usable_sections)
            sec_significant = bool(sec_p < bonferroni_alpha)
        else:
            sec_chi2, sec_p, sec_dof = 0.0, 1.0, 0
            sec_significant = False

        if sec_significant:
            section_sig_count += 1

        # --- Position chi-square ---
        pos_data = position_successors[mid]
        pos_keys = sorted(pos_data.keys())
        all_successors_pos = set()
        for p in pos_keys:
            all_successors_pos.update(pos_data[p].keys())
        all_successors_pos = sorted(all_successors_pos)

        usable_positions = [p for p in pos_keys
                           if sum(pos_data[p].values()) >= MIN_SUCCESSOR_COUNT]

        if len(usable_positions) >= 2 and len(all_successors_pos) >= 2:
            pos_contingency = {}
            for p in usable_positions:
                for succ in all_successors_pos:
                    pos_contingency[(succ, p)] = pos_data[p].get(succ, 0)

            pos_chi2, pos_p, pos_dof = chi2_contingency_manual(
                pos_contingency, all_successors_pos, usable_positions)
            pos_significant = bool(pos_p < bonferroni_alpha)
        else:
            pos_chi2, pos_p, pos_dof = 0.0, 1.0, 0
            pos_significant = False

        if pos_significant:
            position_sig_count += 1

        # --- KL divergences ---
        # Section KL: mean pairwise symmetric KL across section distributions
        sec_dists = [dict(sec_data[s]) for s in usable_sections]
        all_succ_keys = set()
        for d in sec_dists:
            all_succ_keys.update(d.keys())

        sec_kl = mean_pairwise_kl(sec_dists, all_succ_keys) if len(sec_dists) >= 2 else 0.0

        # Position KL: mean pairwise symmetric KL across position distributions
        pos_dists = [dict(pos_data[p]) for p in usable_positions]
        all_succ_keys_pos = set()
        for d in pos_dists:
            all_succ_keys_pos.update(d.keys())

        pos_kl = mean_pairwise_kl(pos_dists, all_succ_keys_pos) if len(pos_dists) >= 2 else 0.0

        per_middle_results.append({
            'middle': mid,
            'total_successor_pairs': middle_counts[mid],
            'n_usable_sections': len(usable_sections),
            'n_usable_positions': len(usable_positions),
            'section_chi2': round(sec_chi2, 2),
            'section_p': float(f'{sec_p:.6e}'),
            'section_dof': sec_dof,
            'section_significant': sec_significant,
            'position_chi2': round(pos_chi2, 2),
            'position_p': float(f'{pos_p:.6e}'),
            'position_dof': pos_dof,
            'position_significant': pos_significant,
            'section_kl': round(sec_kl, 6),
            'position_kl': round(pos_kl, 6),
            'section_kl_gt_position_kl': bool(sec_kl > pos_kl),
        })

    # ----------------------------------------------------------
    # Step 7: Aggregate statistics
    # ----------------------------------------------------------
    section_sig_frac = section_sig_count / n_tests if n_tests > 0 else 0
    position_sig_frac = position_sig_count / n_tests if n_tests > 0 else 0

    # Count how many MIDDLEs have section KL > position KL
    sec_gt_pos_count = sum(1 for r in per_middle_results if r['section_kl_gt_position_kl'])
    sec_gt_pos_frac = sec_gt_pos_count / n_tests if n_tests > 0 else 0

    # Mean KL values
    mean_sec_kl = sum(r['section_kl'] for r in per_middle_results) / n_tests if n_tests > 0 else 0
    mean_pos_kl = sum(r['position_kl'] for r in per_middle_results) / n_tests if n_tests > 0 else 0

    # Median KL values
    sorted_sec_kl = sorted(r['section_kl'] for r in per_middle_results)
    sorted_pos_kl = sorted(r['position_kl'] for r in per_middle_results)
    median_sec_kl = sorted_sec_kl[len(sorted_sec_kl) // 2] if sorted_sec_kl else 0
    median_pos_kl = sorted_pos_kl[len(sorted_pos_kl) // 2] if sorted_pos_kl else 0

    # ----------------------------------------------------------
    # Step 8: Print results
    # ----------------------------------------------------------
    print(f"\n--- Section Stratification ---")
    print(f"  MIDDLEs significant (Bonferroni {bonferroni_alpha:.6f}): "
          f"{section_sig_count}/{n_tests} ({section_sig_frac:.1%})")
    print(f"  Mean section KL: {mean_sec_kl:.6f}")
    print(f"  Median section KL: {median_sec_kl:.6f}")

    print(f"\n--- Position Stratification ---")
    print(f"  MIDDLEs significant (Bonferroni {bonferroni_alpha:.6f}): "
          f"{position_sig_count}/{n_tests} ({position_sig_frac:.1%})")
    print(f"  Mean position KL: {mean_pos_kl:.6f}")
    print(f"  Median position KL: {median_pos_kl:.6f}")

    print(f"\n--- KL Comparison ---")
    print(f"  MIDDLEs with section KL > position KL: "
          f"{sec_gt_pos_count}/{n_tests} ({sec_gt_pos_frac:.1%})")
    print(f"  Mean section KL / Mean position KL: "
          f"{mean_sec_kl / mean_pos_kl:.2f}" if mean_pos_kl > 0 else "  N/A")

    # Top 10 by section KL
    print(f"\n--- Top 10 MIDDLEs by Section KL ---")
    for r in sorted(per_middle_results, key=lambda x: x['section_kl'], reverse=True)[:10]:
        print(f"  {r['middle']:15s}  sec_KL={r['section_kl']:.4f}  "
              f"pos_KL={r['position_kl']:.4f}  "
              f"sec_sig={r['section_significant']}  "
              f"n={r['total_successor_pairs']}")

    # ----------------------------------------------------------
    # Step 9: Verdict
    # ----------------------------------------------------------
    pass_section_sig = section_sig_frac > 0.30
    pass_kl_comparison = mean_sec_kl > mean_pos_kl

    if pass_section_sig and pass_kl_comparison:
        verdict = 'PASS'
        verdict_detail = (
            f"{section_sig_frac:.1%} of MIDDLEs show significant section-dependent "
            f"successor distributions (threshold: >30%). "
            f"Section KL ({mean_sec_kl:.4f}) > position KL ({mean_pos_kl:.4f}), "
            f"confirming that MIDDLE successors are shaped more by section identity "
            f"(material domain) than by paragraph position (operational phase)."
        )
    elif pass_section_sig and not pass_kl_comparison:
        verdict = 'PARTIAL_PASS'
        verdict_detail = (
            f"{section_sig_frac:.1%} of MIDDLEs significant by section (>30% threshold met), "
            f"but position KL ({mean_pos_kl:.4f}) >= section KL ({mean_sec_kl:.4f}). "
            f"Context dependency exists but position (operational phase) dominates over "
            f"section (material domain)."
        )
    elif not pass_section_sig and pass_kl_comparison:
        verdict = 'PARTIAL_PASS'
        verdict_detail = (
            f"Only {section_sig_frac:.1%} of MIDDLEs significant by section "
            f"(below 30% threshold), but section KL ({mean_sec_kl:.4f}) > "
            f"position KL ({mean_pos_kl:.4f}). Weak but directionally correct signal."
        )
    else:
        verdict = 'FAIL'
        verdict_detail = (
            f"Only {section_sig_frac:.1%} of MIDDLEs significant by section "
            f"(below 30% threshold) and position KL ({mean_pos_kl:.4f}) >= "
            f"section KL ({mean_sec_kl:.4f}). Successor distributions are largely "
            f"independent of context."
        )

    print(f"\n{'=' * 65}")
    print(f"VERDICT: {verdict}")
    print(f"  {verdict_detail}")

    # ----------------------------------------------------------
    # Step 10: Output JSON
    # ----------------------------------------------------------
    output = {
        'test': 'context_dependent_middle_successors',
        'phase': 'MATERIAL_LOCUS_SEARCH',
        'test_number': 6,
        'question': (
            'Does the same MIDDLE show different successor MIDDLE distributions '
            'in different sections vs paragraph positions?'
        ),
        'method': {
            'description': (
                'For each common MIDDLE (200+ occurrences), compute successor MIDDLE '
                'distributions stratified by section and by paragraph position '
                '(EARLY/MID/LATE). Chi-square tests with Bonferroni correction for '
                'section and position independence. Mean pairwise symmetric KL '
                'divergence to compare section vs position context effects.'
            ),
            'min_middle_count': MIN_MIDDLE_COUNT,
            'alpha_before_bonferroni': ALPHA,
            'bonferroni_alpha': round(bonferroni_alpha, 8),
            'n_middles_tested': n_tests,
            'epsilon_kl': EPSILON,
            'min_successor_count_per_stratum': MIN_SUCCESSOR_COUNT,
        },
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'summary': {
            'total_currier_b_tokens': total_tokens,
            'total_successor_pairs': len(successor_pairs),
            'common_middles_tested': n_tests,
            'section_analysis': {
                'significant_count': section_sig_count,
                'significant_fraction': round(section_sig_frac, 4),
                'mean_kl': round(mean_sec_kl, 6),
                'median_kl': round(median_sec_kl, 6),
            },
            'position_analysis': {
                'significant_count': position_sig_count,
                'significant_fraction': round(position_sig_frac, 4),
                'mean_kl': round(mean_pos_kl, 6),
                'median_kl': round(median_pos_kl, 6),
            },
            'kl_comparison': {
                'section_kl_gt_position_kl_count': sec_gt_pos_count,
                'section_kl_gt_position_kl_fraction': round(sec_gt_pos_frac, 4),
                'mean_section_over_mean_position': round(mean_sec_kl / mean_pos_kl, 4) if mean_pos_kl > 0 else None,
            },
        },
        'per_middle_top15_by_section_kl': sorted(
            per_middle_results,
            key=lambda x: x['section_kl'],
            reverse=True
        )[:15],
        'per_middle_top15_by_position_kl': sorted(
            per_middle_results,
            key=lambda x: x['position_kl'],
            reverse=True
        )[:15],
        'all_middles': sorted(per_middle_results, key=lambda x: x['middle']),
        'pass_criteria': {
            'section_significance_threshold': '>30% MIDDLEs significant by section after Bonferroni',
            'kl_comparison': 'mean section KL > mean position KL',
        },
        'references': ['C293', 'C475', 'C697', 'C728', 'C730', 'C827'],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
