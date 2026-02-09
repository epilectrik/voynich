"""
12_fl_state_vs_material_discriminator.py - FL State vs Material Identity

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 12

Question: Are finish-zone exclusive MIDDLEs FL state markers or material identifiers?

Background: C771/C777 identifies FL (First-Line / Final-Line) state markers as tokens
enriched for characters {a, d, i, l, m, n, o, r, y}. If finish-zone exclusive MIDDLEs
are enriched for these characters, they're operational (FL state markers). If NOT enriched,
they're more likely to be material identifiers.

Method:
1. Identify finish-zone exclusive MIDDLEs across all B folios
2. Compute rate of FL-characteristic characters (a, d, i, l, m, n, o, r, y) in these MIDDLEs
3. Compare with baseline rate across ALL middles
4. Also compare with non-finish-exclusive MIDDLEs as control
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
FL_CHARS = set('adilmnory')
MIN_FOLIO_OCCURRENCES = 2  # exclude hapax from zone-exclusivity determination


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with morphology and metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
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
# PARAGRAPH AND ZONE ASSIGNMENT (reused from test 01)
# ============================================================
def assign_paragraphs(folio_tokens):
    """Assign paragraph numbers to tokens within a folio."""
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)

    return para_assignments


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
# FL CHARACTER RATE COMPUTATION
# ============================================================
def fl_char_rate(middle_str):
    """Compute fraction of characters in a MIDDLE that are FL chars."""
    if not middle_str:
        return 0.0
    n_fl = sum(1 for c in middle_str if c in FL_CHARS)
    return n_fl / len(middle_str)


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    print("Loading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)

    print(f"  B folios: {len(folio_groups)}")

    # ---- Assign zones to all tokens ----
    all_with_zone = []
    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]
        para_assignments = assign_paragraphs(ftokens)
        zones = assign_zones(ftokens, para_assignments)
        for tok, zone in zip(ftokens, zones):
            tok_with_zone = dict(tok)
            tok_with_zone['zone'] = zone
            all_with_zone.append(tok_with_zone)

    print(f"  Tokens with zone assignment: {len(all_with_zone)}")

    # Zone distribution
    zone_counts = Counter(t['zone'] for t in all_with_zone)
    print(f"  Zone distribution: {dict(zone_counts)}")

    # ---- Per-folio: identify zone-exclusive MIDDLEs ----
    # For each (folio, middle) pair with 2+ occurrences,
    # determine which zones it appears in
    folio_middle_zones = defaultdict(lambda: defaultdict(set))   # folio -> middle -> set of zones
    folio_middle_count = defaultdict(lambda: defaultdict(int))   # folio -> middle -> count

    for t in all_with_zone:
        folio_middle_zones[t['folio']][t['middle']].add(t['zone'])
        folio_middle_count[t['folio']][t['middle']] += 1

    # Classify each MIDDLE across all folios where it has 2+ occurrences
    # A MIDDLE is "finish-exclusive" if, on EVERY folio where it has 2+ occurrences,
    # it appears ONLY in the FINISH zone.
    # More practically: collect all (middle, folio) pairs that are finish-exclusive
    # and identify MIDDLEs that are finish-exclusive on at least one folio.

    # Approach: collect zone-exclusivity per (folio, middle) pair
    finish_exclusive_middles = set()    # MIDDLEs that are finish-exclusive on at least one folio
    setup_exclusive_middles = set()     # MIDDLEs that are setup-exclusive on at least one folio
    process_only_middles = set()        # MIDDLEs that are process-exclusive on at least one folio

    # Also track: MIDDLEs that are finish-exclusive ACROSS ALL folios where they appear
    # (global finish exclusivity)
    middle_all_folios_zones = defaultdict(set)  # middle -> union of zones across all folios

    for folio in folio_middle_zones:
        for mid, zones in folio_middle_zones[folio].items():
            count = folio_middle_count[folio][mid]
            if count < MIN_FOLIO_OCCURRENCES:
                continue  # skip hapax

            middle_all_folios_zones[mid].update(zones)

            if zones == {'FINISH'}:
                finish_exclusive_middles.add(mid)
            elif zones == {'SETUP'}:
                setup_exclusive_middles.add(mid)
            elif zones == {'PROCESS'}:
                process_only_middles.add(mid)

    # Global finish-exclusive: MIDDLEs where ALL non-hapax appearances are in FINISH zone
    global_finish_exclusive = set()
    for mid, zones in middle_all_folios_zones.items():
        if zones == {'FINISH'}:
            global_finish_exclusive.add(mid)

    print(f"\n=== Zone-Exclusive MIDDLE Counts ===")
    print(f"  Finish-exclusive (any folio): {len(finish_exclusive_middles)}")
    print(f"  Finish-exclusive (global):    {len(global_finish_exclusive)}")
    print(f"  Setup-exclusive (any folio):  {len(setup_exclusive_middles)}")
    print(f"  Process-only (any folio):     {len(process_only_middles)}")
    print(f"  Total unique MIDDLEs (2+ occ): {len(middle_all_folios_zones)}")

    # ---- Compute FL character rates for each group ----
    # Group 1: Finish-exclusive MIDDLEs (any folio)
    finish_excl_fl_rates = [fl_char_rate(m) for m in finish_exclusive_middles]

    # Group 2: Setup-exclusive MIDDLEs (any folio)
    setup_excl_fl_rates = [fl_char_rate(m) for m in setup_exclusive_middles]

    # Group 3: Process-only MIDDLEs (any folio)
    process_only_fl_rates = [fl_char_rate(m) for m in process_only_middles]

    # Group 4: All MIDDLEs (baseline)
    all_middles = set(t['middle'] for t in all_with_zone)
    all_fl_rates = [fl_char_rate(m) for m in all_middles]

    # Group 5: Non-finish MIDDLEs (everything NOT in finish_exclusive_middles)
    non_finish_middles = all_middles - finish_exclusive_middles
    non_finish_fl_rates = [fl_char_rate(m) for m in non_finish_middles]

    # Group 6: Global finish-exclusive
    global_finish_fl_rates = [fl_char_rate(m) for m in global_finish_exclusive]

    def safe_mean(values):
        return sum(values) / len(values) if values else 0.0

    def safe_median(values):
        if not values:
            return 0.0
        s = sorted(values)
        n = len(s)
        if n % 2 == 1:
            return s[n // 2]
        return (s[n // 2 - 1] + s[n // 2]) / 2

    def safe_std(values):
        if len(values) < 2:
            return 0.0
        m = safe_mean(values)
        return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))

    print(f"\n=== FL Character Rates (C771 chars: a,d,i,l,m,n,o,r,y) ===")
    groups = {
        'finish_exclusive': finish_excl_fl_rates,
        'setup_exclusive': setup_excl_fl_rates,
        'process_only': process_only_fl_rates,
        'all_middles': all_fl_rates,
        'non_finish': non_finish_fl_rates,
        'global_finish_exclusive': global_finish_fl_rates,
    }

    group_stats = {}
    for name, rates in groups.items():
        mean = safe_mean(rates)
        median = safe_median(rates)
        std = safe_std(rates)
        n = len(rates)
        print(f"  {name:30s}: n={n:4d}, mean={mean:.4f}, median={median:.4f}, std={std:.4f}")
        group_stats[name] = {
            'n': n,
            'mean': round(mean, 4),
            'median': round(median, 4),
            'std': round(std, 4),
        }

    # ---- Statistical tests ----
    # Test 1: Mann-Whitney U: finish-exclusive FL rates vs all_middles FL rates
    # (alternative='greater' tests if finish-exclusive is enriched)
    print(f"\n=== Statistical Tests ===")

    test_results = {}

    # Test A: finish-exclusive vs all middles
    if len(finish_excl_fl_rates) >= 5 and len(all_fl_rates) >= 5:
        u_stat, p_val = mannwhitneyu(finish_excl_fl_rates, all_fl_rates, alternative='greater')
        print(f"  Finish-exclusive vs ALL middles:  U={u_stat:.1f}, p={p_val:.6f} (one-sided greater)")
        test_results['finish_vs_all'] = {
            'u_statistic': round(u_stat, 2),
            'p_value': round(p_val, 6),
            'direction': 'finish > all' if safe_mean(finish_excl_fl_rates) > safe_mean(all_fl_rates) else 'finish <= all',
        }
    else:
        print(f"  Finish-exclusive vs ALL middles:  INSUFFICIENT DATA (n_finish={len(finish_excl_fl_rates)})")
        test_results['finish_vs_all'] = {'p_value': None, 'note': 'insufficient data'}

    # Test B: finish-exclusive vs non-finish
    if len(finish_excl_fl_rates) >= 5 and len(non_finish_fl_rates) >= 5:
        u_stat, p_val = mannwhitneyu(finish_excl_fl_rates, non_finish_fl_rates, alternative='greater')
        print(f"  Finish-exclusive vs non-finish:   U={u_stat:.1f}, p={p_val:.6f} (one-sided greater)")
        test_results['finish_vs_non_finish'] = {
            'u_statistic': round(u_stat, 2),
            'p_value': round(p_val, 6),
            'direction': 'finish > non-finish' if safe_mean(finish_excl_fl_rates) > safe_mean(non_finish_fl_rates) else 'finish <= non-finish',
        }
    else:
        print(f"  Finish-exclusive vs non-finish:   INSUFFICIENT DATA")
        test_results['finish_vs_non_finish'] = {'p_value': None, 'note': 'insufficient data'}

    # Test C: finish-exclusive vs setup-exclusive
    if len(finish_excl_fl_rates) >= 5 and len(setup_excl_fl_rates) >= 5:
        u_stat, p_val = mannwhitneyu(finish_excl_fl_rates, setup_excl_fl_rates, alternative='two-sided')
        print(f"  Finish-exclusive vs setup-excl:   U={u_stat:.1f}, p={p_val:.6f} (two-sided)")
        test_results['finish_vs_setup'] = {
            'u_statistic': round(u_stat, 2),
            'p_value': round(p_val, 6),
            'direction': 'finish > setup' if safe_mean(finish_excl_fl_rates) > safe_mean(setup_excl_fl_rates) else 'finish <= setup',
        }
    else:
        print(f"  Finish-exclusive vs setup-excl:   INSUFFICIENT DATA (n_setup={len(setup_excl_fl_rates)})")
        test_results['finish_vs_setup'] = {'p_value': None, 'note': 'insufficient data'}

    # Test D: finish-exclusive vs process-only
    if len(finish_excl_fl_rates) >= 5 and len(process_only_fl_rates) >= 5:
        u_stat, p_val = mannwhitneyu(finish_excl_fl_rates, process_only_fl_rates, alternative='two-sided')
        print(f"  Finish-exclusive vs process-only: U={u_stat:.1f}, p={p_val:.6f} (two-sided)")
        test_results['finish_vs_process'] = {
            'u_statistic': round(u_stat, 2),
            'p_value': round(p_val, 6),
            'direction': 'finish > process' if safe_mean(finish_excl_fl_rates) > safe_mean(process_only_fl_rates) else 'finish <= process',
        }
    else:
        print(f"  Finish-exclusive vs process-only: INSUFFICIENT DATA (n_process={len(process_only_fl_rates)})")
        test_results['finish_vs_process'] = {'p_value': None, 'note': 'insufficient data'}

    # ---- Effect size: Cohen's d for finish-exclusive vs all ----
    if len(finish_excl_fl_rates) >= 2 and len(all_fl_rates) >= 2:
        m1 = safe_mean(finish_excl_fl_rates)
        m2 = safe_mean(all_fl_rates)
        s1 = safe_std(finish_excl_fl_rates)
        s2 = safe_std(all_fl_rates)
        n1 = len(finish_excl_fl_rates)
        n2 = len(all_fl_rates)
        pooled_std = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
        cohens_d = (m1 - m2) / pooled_std if pooled_std > 0 else 0.0
        print(f"\n  Cohen's d (finish vs all): {cohens_d:.4f}")
    else:
        cohens_d = None

    # ---- Character-level analysis ----
    # Detailed character frequency in finish-exclusive vs non-finish MIDDLEs
    print(f"\n=== Character-Level Analysis ===")

    def char_frequency(middles_set):
        """Compute character frequency distribution for a set of MIDDLEs."""
        char_counts = Counter()
        total_chars = 0
        for m in middles_set:
            for c in m:
                char_counts[c] += 1
                total_chars += 1
        return {c: round(cnt / total_chars, 4) if total_chars > 0 else 0
                for c, cnt in char_counts.most_common()}, total_chars

    finish_char_freq, finish_total_chars = char_frequency(finish_exclusive_middles)
    all_char_freq, all_total_chars = char_frequency(all_middles)
    non_finish_char_freq, non_finish_total_chars = char_frequency(non_finish_middles)

    print(f"  Finish-exclusive MIDDLEs ({len(finish_exclusive_middles)} types, {finish_total_chars} chars):")
    fl_char_total_finish = 0
    for c, rate in sorted(finish_char_freq.items(), key=lambda x: -x[1]):
        is_fl = c in FL_CHARS
        marker = " [FL]" if is_fl else ""
        print(f"    {c}: {rate:.4f}{marker}")
        if is_fl:
            fl_char_total_finish += rate

    print(f"  Non-finish MIDDLEs ({len(non_finish_middles)} types, {non_finish_total_chars} chars):")
    fl_char_total_non_finish = 0
    for c, rate in sorted(non_finish_char_freq.items(), key=lambda x: -x[1]):
        is_fl = c in FL_CHARS
        marker = " [FL]" if is_fl else ""
        print(f"    {c}: {rate:.4f}{marker}")
        if is_fl:
            fl_char_total_non_finish += rate

    print(f"\n  FL char fraction in finish-exclusive: {fl_char_total_finish:.4f}")
    print(f"  FL char fraction in non-finish:       {fl_char_total_non_finish:.4f}")
    print(f"  FL char fraction in all middles:       {sum(r for c, r in all_char_freq.items() if c in FL_CHARS):.4f}")

    # ---- Chi-square test on FL vs non-FL character composition ----
    # Contingency table: [finish-exclusive, non-finish] x [FL chars, non-FL chars]
    finish_fl_count = sum(1 for m in finish_exclusive_middles for c in m if c in FL_CHARS)
    finish_nonfl_count = finish_total_chars - finish_fl_count
    nonfinish_fl_count = sum(1 for m in non_finish_middles for c in m if c in FL_CHARS)
    nonfinish_nonfl_count = non_finish_total_chars - nonfinish_fl_count

    chi2_table = [[finish_fl_count, finish_nonfl_count],
                  [nonfinish_fl_count, nonfinish_nonfl_count]]

    print(f"\n  Chi-square contingency table (FL chars vs non-FL chars):")
    print(f"    Finish-excl:  FL={finish_fl_count}, non-FL={finish_nonfl_count}")
    print(f"    Non-finish:   FL={nonfinish_fl_count}, non-FL={nonfinish_nonfl_count}")

    if min(finish_fl_count, finish_nonfl_count, nonfinish_fl_count, nonfinish_nonfl_count) >= 5:
        chi2, chi2_p, dof, expected = chi2_contingency(chi2_table)
        print(f"    Chi2={chi2:.4f}, p={chi2_p:.6f}, dof={dof}")
    else:
        chi2, chi2_p, dof = 0.0, 1.0, 1
        print(f"    Insufficient counts for chi-square")

    chi2_result = {
        'chi2': round(chi2, 4),
        'p_value': round(chi2_p, 6),
        'finish_fl': finish_fl_count,
        'finish_nonfl': finish_nonfl_count,
        'nonfinish_fl': nonfinish_fl_count,
        'nonfinish_nonfl': nonfinish_nonfl_count,
    }

    # ---- List the actual finish-exclusive MIDDLEs ----
    print(f"\n=== Finish-Exclusive MIDDLEs (any folio, 2+ occ) ===")
    finish_excl_detail = []
    for m in sorted(finish_exclusive_middles):
        rate = fl_char_rate(m)
        # Count how many folios this middle appears in
        folio_set = set(t['folio'] for t in all_with_zone if t['middle'] == m)
        finish_excl_detail.append({
            'middle': m,
            'fl_char_rate': round(rate, 4),
            'length': len(m),
            'n_folios': len(folio_set),
            'fl_chars_in_middle': ''.join(c for c in m if c in FL_CHARS),
            'non_fl_chars_in_middle': ''.join(c for c in m if c not in FL_CHARS),
        })
        print(f"  {m:20s}  fl_rate={rate:.4f}  len={len(m)}  folios={len(folio_set)}")

    # Global finish-exclusive detail
    print(f"\n=== Global Finish-Exclusive MIDDLEs (ALL folios, 2+ occ) ===")
    global_finish_detail = []
    for m in sorted(global_finish_exclusive):
        rate = fl_char_rate(m)
        folio_set = set(t['folio'] for t in all_with_zone if t['middle'] == m)
        global_finish_detail.append({
            'middle': m,
            'fl_char_rate': round(rate, 4),
            'length': len(m),
            'n_folios': len(folio_set),
        })
        print(f"  {m:20s}  fl_rate={rate:.4f}  len={len(m)}  folios={len(folio_set)}")

    # ---- VERDICT ----
    # Primary test: Mann-Whitney U of finish-exclusive FL rates vs all-middles FL rates
    # OPERATIONAL if finish-exclusive significantly > baseline (p < 0.05 one-sided)
    # MATERIAL if NOT significantly > baseline
    # INDETERMINATE if data insufficient or marginal
    finish_vs_all_p = test_results.get('finish_vs_all', {}).get('p_value')
    finish_vs_nonfinish_p = test_results.get('finish_vs_non_finish', {}).get('p_value')

    finish_mean = safe_mean(finish_excl_fl_rates)
    all_mean = safe_mean(all_fl_rates)

    print(f"\n{'='*60}")
    if finish_vs_all_p is None:
        verdict = "INDETERMINATE"
        interpretation = "Insufficient data for statistical test"
    elif finish_vs_all_p < 0.05 and finish_mean > all_mean:
        verdict = "OPERATIONAL"
        interpretation = (
            f"Finish-exclusive MIDDLEs are significantly enriched for FL characters "
            f"(mean={finish_mean:.4f} vs baseline={all_mean:.4f}, p={finish_vs_all_p:.6f}). "
            f"This suggests they function as FL state markers (operational role per C777), "
            f"NOT as material identifiers."
        )
    elif finish_vs_all_p >= 0.05 and abs(finish_mean - all_mean) < 0.05:
        verdict = "INDETERMINATE"
        interpretation = (
            f"Finish-exclusive MIDDLEs show FL character rate similar to baseline "
            f"(mean={finish_mean:.4f} vs baseline={all_mean:.4f}, p={finish_vs_all_p:.6f}). "
            f"Cannot discriminate between operational and material identity."
        )
    else:
        verdict = "MATERIAL"
        interpretation = (
            f"Finish-exclusive MIDDLEs are NOT significantly enriched for FL characters "
            f"(mean={finish_mean:.4f} vs baseline={all_mean:.4f}, p={finish_vs_all_p:.6f}). "
            f"Their zone restriction is NOT explained by FL state marking (C777), "
            f"consistent with material identity."
        )

    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")
    print(f"Interpretation: {interpretation}")

    # ---- Save results ----
    results = {
        'test': 'FL State vs Material Identity Discriminator',
        'test_number': 12,
        'phase': 'MIDDLE_MATERIAL_SEMANTICS',
        'question': 'Are finish-zone exclusive MIDDLEs FL state markers or material identifiers?',
        'fl_characters': sorted(FL_CHARS),
        'counts': {
            'total_b_tokens': len(all_tokens),
            'total_unique_middles': len(all_middles),
            'finish_exclusive_middles': len(finish_exclusive_middles),
            'global_finish_exclusive_middles': len(global_finish_exclusive),
            'setup_exclusive_middles': len(setup_exclusive_middles),
            'process_only_middles': len(process_only_middles),
            'non_finish_middles': len(non_finish_middles),
            'total_middles_with_zones': len(middle_all_folios_zones),
        },
        'fl_char_rates': group_stats,
        'statistical_tests': test_results,
        'chi_square_composition': chi2_result,
        'effect_size_cohens_d': round(cohens_d, 4) if cohens_d is not None else None,
        'character_frequencies': {
            'finish_exclusive': finish_char_freq,
            'non_finish': non_finish_char_freq,
            'all_middles': all_char_freq,
        },
        'fl_char_fraction': {
            'finish_exclusive': round(fl_char_total_finish, 4),
            'non_finish': round(fl_char_total_non_finish, 4),
            'all_middles': round(sum(r for c, r in all_char_freq.items() if c in FL_CHARS), 4),
        },
        'finish_exclusive_detail': sorted(finish_excl_detail, key=lambda x: x['fl_char_rate']),
        'global_finish_exclusive_detail': sorted(global_finish_detail, key=lambda x: x['fl_char_rate']),
        'verdict': verdict,
        'interpretation': interpretation,
        'notes': (
            f"FL chars = {{a,d,i,l,m,n,o,r,y}} per C771/C777. "
            f"Finish-exclusive = MIDDLE appears ONLY in FINISH zone on at least one folio (2+ occ, hapax excluded). "
            f"Global finish-exclusive = FINISH zone only across ALL folios. "
            f"Zone assignment: paragraph-based (3+ paras) or line-based 20/60/20 (1-2 paras). "
            f"OPERATIONAL = FL-enriched (state markers). MATERIAL = not FL-enriched (material IDs). "
            f"Mann-Whitney U one-sided greater test; chi-square on character composition."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'fl_state_vs_material.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
