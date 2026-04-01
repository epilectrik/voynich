#!/usr/bin/env python3
"""
s2_daiin_vs_aiin_split.py — Test whether daiin (da-PREFIX) and bare aiin (a-HEAD)
are functionally distinct tokens across Currier A, B, and AZC.

Phase: AIIN_CROSS_SYSTEM
Purpose: The B-side split is established (C557: daiin 27.7% line-initial;
         C1234: aiin penultimate 1.35x; C816: daiin mean pos 0.413).
         NOVEL question: does this complementary distribution hold in
         Currier A (non-sequential grammar, C240) and AZC?

Uses: scripts/voynich.py canonical library
"""

import sys
import io
import os
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

# Windows stdout encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RESULTS_DIR = REPO_ROOT / 'phases' / 'AIIN_CROSS_SYSTEM' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA LOADING
# ============================================================
def load_data():
    """Load H-track, non-label, non-empty, non-uncertain tokens with positional info."""
    all_tokens = list(tx.all(h_only=True))

    # Filter: non-label, non-empty, non-uncertain
    tokens = [t for t in all_tokens
              if not t.is_label
              and t.word.strip() != ''
              and '*' not in t.word]

    # Build line-level structure: ordered tokens per (folio, line)
    # Tokens arrive in document order from the transcript
    lines = defaultdict(list)
    for t in tokens:
        lines[(t.folio, t.line)].append(t)

    # Assign position index within each line
    # We'll store as list of dicts for easier analysis
    records = []
    for (folio, line_num), line_tokens in lines.items():
        n = len(line_tokens)
        for idx, t in enumerate(line_tokens):
            norm_pos = (idx / (n - 1)) if n > 1 else 0.5
            records.append({
                'word': t.word,
                'folio': folio,
                'line': line_num,
                'language': t.language,
                'placement': t.placement,
                'pos_in_line': idx,  # 0-indexed
                'line_length': n,
                'norm_pos': norm_pos,
                'line_initial': t.line_initial,
                'line_final': t.line_final,
                'par_initial': t.par_initial,
                'par_final': t.par_final,
            })

    return records


def split_by_system(records):
    """Split records into A, B, AZC."""
    a = [r for r in records if r['language'] == 'A']
    b = [r for r in records if r['language'] == 'B']
    azc = [r for r in records if r['language'] == 'NA']
    return {'A': a, 'B': b, 'AZC': azc}


# ============================================================
# STATISTICAL HELPERS
# ============================================================
def chi_squared_2x2(a, b, c, d):
    """Chi-squared test for 2x2 contingency table [[a,b],[c,d]].
    Returns (chi2, p_value_approx). Uses scipy if available, else manual."""
    n = a + b + c + d
    if n == 0:
        return 0.0, 1.0
    expected_a = (a + b) * (a + c) / n
    expected_b = (a + b) * (b + d) / n
    expected_c = (c + d) * (a + c) / n
    expected_d = (c + d) * (b + d) / n

    chi2 = 0.0
    for obs, exp in [(a, expected_a), (b, expected_b), (c, expected_c), (d, expected_d)]:
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp

    # Approximate p-value using chi2 with 1 df
    # Use survival function approximation
    try:
        from scipy.stats import chi2 as chi2_dist
        p = chi2_dist.sf(chi2, 1)
    except ImportError:
        # Rough approximation
        if chi2 > 10.83:
            p = 0.001
        elif chi2 > 6.63:
            p = 0.01
        elif chi2 > 3.84:
            p = 0.05
        else:
            p = 0.5
    return chi2, p


def fisher_exact_2x2(a, b, c, d):
    """Fisher exact test. Falls back to chi-squared if scipy unavailable."""
    try:
        from scipy.stats import fisher_exact
        odds, p = fisher_exact([[a, b], [c, d]])
        return odds, p
    except ImportError:
        chi2, p = chi_squared_2x2(a, b, c, d)
        odds = (a * d) / (b * c) if b * c > 0 else float('inf')
        return odds, p


# ============================================================
# ANALYSIS 1: KNOWN ANCHORS (B-side validation)
# ============================================================
def analysis_1_b_anchors(systems):
    """Validate known B-side constraints for daiin and aiin."""
    print("=" * 70)
    print("ANALYSIS 1: KNOWN B-SIDE ANCHORS")
    print("=" * 70)

    b = systems['B']
    daiin_b = [r for r in b if r['word'] == 'daiin']
    aiin_b = [r for r in b if r['word'] == 'aiin']

    # C557: daiin line-initial rate ~27.7%
    daiin_li = sum(1 for r in daiin_b if r['pos_in_line'] == 0)
    daiin_li_rate = daiin_li / len(daiin_b) if daiin_b else 0
    print(f"\ndaiin in B: {len(daiin_b)} tokens")
    print(f"  Line-initial: {daiin_li} ({daiin_li_rate:.1%}) [expected ~27.7%, C557]")

    # C816: daiin mean position ~0.413
    daiin_mean_pos = sum(r['norm_pos'] for r in daiin_b) / len(daiin_b) if daiin_b else 0
    print(f"  Mean norm position: {daiin_mean_pos:.3f} [expected ~0.413, C816]")

    # C1234: aiin penultimate enrichment ~1.35x
    aiin_penult = sum(1 for r in aiin_b if r['line_length'] > 1 and r['pos_in_line'] == r['line_length'] - 2)
    aiin_penult_rate = aiin_penult / len(aiin_b) if aiin_b else 0
    # Expected penultimate rate under uniformity = 1/mean_line_length
    b_mean_line_len = sum(r['line_length'] for r in aiin_b) / len(aiin_b) if aiin_b else 1
    expected_penult = 1 / b_mean_line_len if b_mean_line_len > 0 else 0
    enrichment = aiin_penult_rate / expected_penult if expected_penult > 0 else 0
    print(f"\naiin in B: {len(aiin_b)} tokens")
    print(f"  Penultimate rate: {aiin_penult_rate:.3%}")
    print(f"  Expected under uniformity: {expected_penult:.3%}")
    print(f"  Enrichment: {enrichment:.2f}x [expected ~1.35x, C1234]")

    return {
        'daiin_B_count': len(daiin_b),
        'daiin_B_line_initial_rate': round(daiin_li_rate, 4),
        'daiin_B_line_initial_expected': 0.277,
        'daiin_B_mean_norm_pos': round(daiin_mean_pos, 4),
        'daiin_B_mean_pos_expected': 0.413,
        'aiin_B_count': len(aiin_b),
        'aiin_B_penultimate_rate': round(aiin_penult_rate, 4),
        'aiin_B_penultimate_enrichment': round(enrichment, 3),
        'aiin_B_penultimate_enrichment_expected': 1.35,
    }


# ============================================================
# ANALYSIS 2: POSITIONAL DISTRIBUTIONS PER SYSTEM
# ============================================================
def positional_profile(records, word):
    """Compute positional metrics for a target word in a set of records."""
    hits = [r for r in records if r['word'] == word]
    n = len(hits)
    if n == 0:
        return {'count': 0, 'line_initial_rate': None, 'line_final_rate': None,
                'mean_norm_pos': None, 'median_norm_pos': None}

    li = sum(1 for r in hits if r['pos_in_line'] == 0)
    lf = sum(1 for r in hits if r['pos_in_line'] == r['line_length'] - 1)
    positions = sorted(r['norm_pos'] for r in hits)
    mean_pos = sum(positions) / n
    median_pos = positions[n // 2] if n % 2 == 1 else (positions[n // 2 - 1] + positions[n // 2]) / 2

    return {
        'count': n,
        'line_initial_count': li,
        'line_initial_rate': round(li / n, 4),
        'line_final_count': lf,
        'line_final_rate': round(lf / n, 4),
        'mean_norm_pos': round(mean_pos, 4),
        'median_norm_pos': round(median_pos, 4),
        'pos_variance': round(sum((p - mean_pos) ** 2 for p in positions) / n, 6) if n > 1 else 0,
    }


def analysis_2_positional(systems):
    """Positional distributions of daiin vs aiin across systems."""
    print("\n" + "=" * 70)
    print("ANALYSIS 2: POSITIONAL DISTRIBUTIONS PER SYSTEM")
    print("=" * 70)

    results = {}
    for sys_name, records in systems.items():
        print(f"\n--- {sys_name} ---")
        total_lines = len(set((r['folio'], r['line']) for r in records))
        total_tokens = len(records)
        mean_line_len = total_tokens / total_lines if total_lines > 0 else 0
        print(f"  Total tokens: {total_tokens}, Lines: {total_lines}, Mean line length: {mean_line_len:.1f}")

        base_initial_rate = 1 / mean_line_len if mean_line_len > 0 else 0

        for word in ['daiin', 'aiin']:
            prof = positional_profile(records, word)
            print(f"\n  {word}: {prof['count']} tokens")
            if prof['count'] > 0:
                print(f"    Line-initial: {prof['line_initial_count']} ({prof['line_initial_rate']:.1%}) "
                      f"[base rate: {base_initial_rate:.1%}]")
                print(f"    Line-final:   {prof['line_final_count']} ({prof['line_final_rate']:.1%})")
                print(f"    Mean norm pos: {prof['mean_norm_pos']:.4f}")
                print(f"    Median norm pos: {prof['median_norm_pos']:.4f}")
                print(f"    Position variance: {prof['pos_variance']:.6f}")

                # Chi-squared for line-initial enrichment vs base rate
                if prof['count'] >= 5:
                    expected_li = prof['count'] * base_initial_rate
                    observed_li = prof['line_initial_count']
                    observed_not_li = prof['count'] - observed_li
                    # Compare to total system: line-initial tokens vs not
                    total_li = sum(1 for r in records if r['pos_in_line'] == 0)
                    total_not_li = total_tokens - total_li
                    word_not_li = prof['count'] - observed_li
                    other_li = total_li - observed_li
                    other_not_li = total_not_li - word_not_li
                    chi2, p = chi_squared_2x2(observed_li, word_not_li, other_li, other_not_li)
                    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                    print(f"    Line-initial chi2: {chi2:.2f}, p={p:.4g} {sig}")

            prof['base_initial_rate'] = round(base_initial_rate, 4)
            results[f"{word}_{sys_name}"] = prof

        # Direct daiin vs aiin comparison within system
        d_prof = results.get(f"daiin_{sys_name}", {})
        a_prof = results.get(f"aiin_{sys_name}", {})
        if d_prof.get('count', 0) > 0 and a_prof.get('count', 0) > 0:
            print(f"\n  daiin vs aiin comparison ({sys_name}):")
            print(f"    Mean pos: daiin={d_prof['mean_norm_pos']:.4f} vs aiin={a_prof['mean_norm_pos']:.4f}")
            print(f"    Variance: daiin={d_prof['pos_variance']:.6f} vs aiin={a_prof['pos_variance']:.6f}")
            print(f"    LI rate:  daiin={d_prof['line_initial_rate']:.1%} vs aiin={a_prof['line_initial_rate']:.1%}")

    return results


# ============================================================
# ANALYSIS 3: PARAGRAPH-LEVEL POSITION (B only)
# ============================================================
def analysis_3_paragraph(systems):
    """Paragraph-level analysis for B tokens using par_initial/par_final flags."""
    print("\n" + "=" * 70)
    print("ANALYSIS 3: PARAGRAPH-LEVEL POSITION (B only)")
    print("=" * 70)

    b = systems['B']

    # Use par_initial flag to identify paragraph-initial lines
    # Group B tokens by folio+line to find paragraph boundaries
    lines_by_key = defaultdict(list)
    for r in b:
        lines_by_key[(r['folio'], r['line'])].append(r)

    # Identify paragraph-initial lines (any token on that line has par_initial)
    par_initial_lines = set()
    par_final_lines = set()
    for (folio, line_num), recs in lines_by_key.items():
        if any(r['par_initial'] for r in recs):
            par_initial_lines.add((folio, line_num))
        if any(r['par_final'] for r in recs):
            par_final_lines.add((folio, line_num))

    # Build paragraph structure: assign paragraph ID to each line
    # Sort lines by folio, then line number
    folio_lines = defaultdict(list)
    for key in lines_by_key:
        folio_lines[key[0]].append(key)
    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: int(x[1]) if x[1].isdigit() else 0)

    # Assign paragraph IDs and positions within paragraph
    line_para_info = {}
    for folio, lines_list in folio_lines.items():
        para_id = 0
        lines_in_para = []
        for lkey in lines_list:
            if lkey in par_initial_lines and lines_in_para:
                # Flush previous paragraph
                n_lines = len(lines_in_para)
                for idx, lk in enumerate(lines_in_para):
                    third = 0 if idx < n_lines / 3 else (2 if idx >= 2 * n_lines / 3 else 1)
                    line_para_info[lk] = {'para_id': para_id, 'para_pos': idx, 'para_len': n_lines, 'third': third}
                para_id += 1
                lines_in_para = [lkey]
            else:
                if not lines_in_para and lkey not in par_initial_lines:
                    pass  # first line of folio, not marked as par_initial
                lines_in_para.append(lkey)
        # Flush last paragraph
        if lines_in_para:
            n_lines = len(lines_in_para)
            for idx, lk in enumerate(lines_in_para):
                third = 0 if idx < n_lines / 3 else (2 if idx >= 2 * n_lines / 3 else 1)
                line_para_info[lk] = {'para_id': para_id, 'para_pos': idx, 'para_len': n_lines, 'third': third}

    results = {}
    for word in ['daiin', 'aiin']:
        hits = [r for r in b if r['word'] == word]
        n = len(hits)
        if n == 0:
            continue

        # Paragraph-initial line
        on_par_initial = sum(1 for r in hits if (r['folio'], r['line']) in par_initial_lines and r['pos_in_line'] == 0)
        on_par_initial_line = sum(1 for r in hits if (r['folio'], r['line']) in par_initial_lines)
        on_par_final_line = sum(1 for r in hits if (r['folio'], r['line']) in par_final_lines)

        # Density by thirds
        thirds = [0, 0, 0]
        thirds_total = [0, 0, 0]
        for r in b:
            key = (r['folio'], r['line'])
            if key in line_para_info:
                t = line_para_info[key]['third']
                thirds_total[t] += 1
                if r['word'] == word:
                    thirds[t] += 1

        third_rates = [thirds[i] / thirds_total[i] if thirds_total[i] > 0 else 0 for i in range(3)]

        print(f"\n  {word} ({n} tokens):")
        print(f"    On paragraph-initial line: {on_par_initial_line} ({on_par_initial_line/n:.1%})")
        print(f"    On paragraph-initial line AND line-initial: {on_par_initial}")
        print(f"    On paragraph-final line: {on_par_final_line} ({on_par_final_line/n:.1%})")
        print(f"    Density by paragraph third:")
        print(f"      First third:  {thirds[0]}/{thirds_total[0]} = {third_rates[0]:.4%}")
        print(f"      Middle third: {thirds[1]}/{thirds_total[1]} = {third_rates[1]:.4%}")
        print(f"      Final third:  {thirds[2]}/{thirds_total[2]} = {third_rates[2]:.4%}")

        results[word] = {
            'count': n,
            'on_par_initial_line': on_par_initial_line,
            'on_par_initial_line_rate': round(on_par_initial_line / n, 4),
            'par_initial_and_line_initial': on_par_initial,
            'on_par_final_line': on_par_final_line,
            'on_par_final_line_rate': round(on_par_final_line / n, 4),
            'density_first_third': round(third_rates[0], 6),
            'density_middle_third': round(third_rates[1], 6),
            'density_final_third': round(third_rates[2], 6),
        }

    return results


# ============================================================
# ANALYSIS 4: CO-OCCURRENCE WITHIN LINES
# ============================================================
def analysis_4_cooccurrence(systems):
    """Co-occurrence of daiin and aiin within lines."""
    print("\n" + "=" * 70)
    print("ANALYSIS 4: CO-OCCURRENCE WITHIN LINES")
    print("=" * 70)

    results = {}
    for sys_name, records in systems.items():
        # Group by line
        lines = defaultdict(list)
        for r in records:
            lines[(r['folio'], r['line'])].append(r)

        n_lines = len(lines)
        lines_with_daiin = 0
        lines_with_aiin = 0
        lines_with_both = 0
        daiin_before_aiin = 0
        aiin_before_daiin = 0

        for key, line_tokens in lines.items():
            words = [r['word'] for r in line_tokens]
            has_daiin = 'daiin' in words
            has_aiin = 'aiin' in words
            if has_daiin:
                lines_with_daiin += 1
            if has_aiin:
                lines_with_aiin += 1
            if has_daiin and has_aiin:
                lines_with_both += 1
                # Order: find first occurrence of each
                first_daiin = words.index('daiin')
                first_aiin = words.index('aiin')
                if first_daiin < first_aiin:
                    daiin_before_aiin += 1
                else:
                    aiin_before_daiin += 1

        p_daiin = lines_with_daiin / n_lines if n_lines > 0 else 0
        p_aiin = lines_with_aiin / n_lines if n_lines > 0 else 0
        expected_both = p_daiin * p_aiin * n_lines
        observed_both = lines_with_both

        print(f"\n--- {sys_name} ({n_lines} lines) ---")
        print(f"  Lines with daiin: {lines_with_daiin} ({p_daiin:.1%})")
        print(f"  Lines with aiin:  {lines_with_aiin} ({p_aiin:.1%})")
        print(f"  Lines with BOTH:  {observed_both} (expected under independence: {expected_both:.1f})")
        ratio = observed_both / expected_both if expected_both > 0 else 0
        print(f"  Observed/Expected ratio: {ratio:.2f} ({'attraction' if ratio > 1 else 'repulsion' if ratio < 1 else 'neutral'})")

        if lines_with_both > 0:
            print(f"  When co-occurring: daiin first {daiin_before_aiin}/{lines_with_both} "
                  f"({daiin_before_aiin/lines_with_both:.0%}), "
                  f"aiin first {aiin_before_daiin}/{lines_with_both} "
                  f"({aiin_before_daiin/lines_with_both:.0%})")

        # Chi-squared for co-occurrence
        # 2x2: [both, daiin_only], [aiin_only, neither]
        a = observed_both
        b = lines_with_daiin - observed_both
        c = lines_with_aiin - observed_both
        d = n_lines - lines_with_daiin - lines_with_aiin + observed_both
        chi2, p = chi_squared_2x2(a, b, c, d)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  Co-occurrence chi2: {chi2:.2f}, p={p:.4g} {sig}")

        # Fisher exact
        odds, fp = fisher_exact_2x2(a, b, c, d)
        print(f"  Fisher exact: OR={odds:.2f}, p={fp:.4g}")

        results[sys_name] = {
            'n_lines': n_lines,
            'lines_with_daiin': lines_with_daiin,
            'lines_with_aiin': lines_with_aiin,
            'lines_with_both': observed_both,
            'expected_both': round(expected_both, 2),
            'obs_exp_ratio': round(ratio, 3),
            'daiin_before_aiin': daiin_before_aiin,
            'aiin_before_daiin': aiin_before_daiin,
            'chi2': round(chi2, 3),
            'fisher_OR': round(odds, 3) if odds != float('inf') else 'inf',
        }

    return results


# ============================================================
# ANALYSIS 5: OTHER PREFIXED FORMS
# ============================================================
def analysis_5_other_forms(systems):
    """Positional profiles of other aiin-family members."""
    print("\n" + "=" * 70)
    print("ANALYSIS 5: OTHER PREFIXED -AIIN FORMS")
    print("=" * 70)

    # Find top aiin-family tokens (ending in 'aiin' but not 'daiin' or bare 'aiin')
    all_records = []
    for recs in systems.values():
        all_records.extend(recs)

    aiin_family = Counter()
    for r in all_records:
        w = r['word']
        if w.endswith('aiin') and w != 'daiin' and w != 'aiin' and len(w) > 4:
            aiin_family[w] += 1

    top5 = aiin_family.most_common(5)
    print(f"\n  Top 5 non-da, non-bare aiin-family tokens:")
    for w, c in top5:
        print(f"    {w}: {c}")

    results = {}
    # Also include daiin and aiin as reference
    target_words = ['daiin', 'aiin'] + [w for w, _ in top5]

    for sys_name, records in systems.items():
        if sys_name == 'AZC':
            continue  # AZC too sparse for most forms
        print(f"\n--- {sys_name} ---")
        print(f"  {'Token':15s} {'N':>5s} {'LI rate':>8s} {'LF rate':>8s} {'Mean pos':>9s} {'Variance':>10s}")
        print(f"  {'-'*15} {'-'*5} {'-'*8} {'-'*8} {'-'*9} {'-'*10}")
        for word in target_words:
            prof = positional_profile(records, word)
            if prof['count'] > 0:
                print(f"  {word:15s} {prof['count']:5d} "
                      f"{prof['line_initial_rate']:8.1%} "
                      f"{prof['line_final_rate']:8.1%} "
                      f"{prof['mean_norm_pos']:9.4f} "
                      f"{prof['pos_variance']:10.6f}")
                results[f"{word}_{sys_name}"] = prof

    return results


# ============================================================
# ANALYSIS 6: A-SIDE SPECIAL ANALYSIS
# ============================================================
def analysis_6_a_special(systems):
    """Test whether positional grammar exists in Currier A (C240: non-sequential)."""
    print("\n" + "=" * 70)
    print("ANALYSIS 6: A-SIDE SPECIAL ANALYSIS (C240 non-sequential test)")
    print("=" * 70)

    a = systems['A']
    b = systems['B']

    # Base rate: 1/mean_tokens_per_line
    a_lines = defaultdict(list)
    for r in a:
        a_lines[(r['folio'], r['line'])].append(r)
    a_mean_line_len = sum(len(v) for v in a_lines.values()) / len(a_lines) if a_lines else 1
    a_base_rate = 1 / a_mean_line_len

    b_lines = defaultdict(list)
    for r in b:
        b_lines[(r['folio'], r['line'])].append(r)
    b_mean_line_len = sum(len(v) for v in b_lines.values()) / len(b_lines) if b_lines else 1
    b_base_rate = 1 / b_mean_line_len

    print(f"\n  A: mean line length = {a_mean_line_len:.1f}, base LI rate = {a_base_rate:.1%}")
    print(f"  B: mean line length = {b_mean_line_len:.1f}, base LI rate = {b_base_rate:.1%}")

    results = {}
    for word in ['daiin', 'aiin']:
        print(f"\n  --- {word} ---")
        a_prof = positional_profile(a, word)
        b_prof = positional_profile(b, word)

        for sys_name, prof, base_rate in [('A', a_prof, a_base_rate), ('B', b_prof, b_base_rate)]:
            if prof['count'] == 0:
                print(f"    {sys_name}: no tokens")
                continue
            # Test LI rate against base rate
            li_excess = prof['line_initial_rate'] / base_rate if base_rate > 0 else 0
            print(f"    {sys_name}: n={prof['count']}, LI={prof['line_initial_rate']:.1%} "
                  f"(base={base_rate:.1%}, enrichment={li_excess:.2f}x), "
                  f"var={prof['pos_variance']:.6f}")

        # Compare variance between A and B
        if a_prof['count'] > 1 and b_prof['count'] > 1:
            var_ratio = a_prof['pos_variance'] / b_prof['pos_variance'] if b_prof['pos_variance'] > 0 else float('inf')
            print(f"    A/B variance ratio: {var_ratio:.3f} "
                  f"({'A more dispersed' if var_ratio > 1 else 'B more dispersed'})")
            # If A is truly position-free, variance should be higher (closer to uniform)
            # Uniform on [0,1] has variance = 1/12 = 0.0833
            print(f"    [Uniform variance reference: 0.0833]")
            results[f"{word}_var_ratio_A_over_B"] = round(var_ratio, 4)

        results[f"{word}_A"] = a_prof
        results[f"{word}_B"] = b_prof

    # Additional: is daiin LI rate in A significantly different from base rate?
    print("\n  Statistical tests (A-side):")
    for word in ['daiin', 'aiin']:
        a_hits = [r for r in a if r['word'] == word]
        n = len(a_hits)
        if n < 5:
            print(f"    {word}: too few tokens in A (n={n})")
            continue
        li_count = sum(1 for r in a_hits if r['pos_in_line'] == 0)
        # Binomial test approximation: compare to base rate
        expected = n * a_base_rate
        # Use total system counts for chi-squared
        total_li_a = sum(1 for r in a if r['pos_in_line'] == 0)
        total_not_li_a = len(a) - total_li_a
        word_not_li = n - li_count
        other_li = total_li_a - li_count
        other_not_li = total_not_li_a - word_not_li
        chi2, p = chi_squared_2x2(li_count, word_not_li, other_li, other_not_li)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"    {word}: LI {li_count}/{n} vs expected {expected:.1f}, chi2={chi2:.2f}, p={p:.4g} {sig}")

    return results


# ============================================================
# ANALYSIS 7: AZC POSITIONAL ANALYSIS
# ============================================================
def analysis_7_azc(systems):
    """AZC ring/placement analysis for daiin and aiin."""
    print("\n" + "=" * 70)
    print("ANALYSIS 7: AZC POSITIONAL ANALYSIS")
    print("=" * 70)

    azc = systems['AZC']
    results = {}

    for word in ['daiin', 'aiin']:
        hits = [r for r in azc if r['word'] == word]
        print(f"\n  {word} in AZC: {len(hits)} tokens")
        if hits:
            # Count by placement prefix (R=ring, C=circle, S=star, P=paragraph)
            placement_counts = Counter()
            folio_counts = Counter()
            for r in hits:
                # Extract placement type (first char or first 2 chars)
                pl = r['placement']
                if pl:
                    # Get the prefix (e.g., R1, R2, S1, C1, P1)
                    placement_counts[pl] += 1
                folio_counts[r['folio']] += 1

            print(f"    By placement:")
            for pl, c in sorted(placement_counts.items(), key=lambda x: -x[1]):
                print(f"      {pl}: {c}")
            print(f"    By folio (top 10):")
            for folio, c in folio_counts.most_common(10):
                print(f"      {folio}: {c}")

            results[word] = {
                'count': len(hits),
                'placements': dict(placement_counts),
                'top_folios': dict(folio_counts.most_common(10)),
            }
        else:
            results[word] = {'count': 0}

    # Also check broader aiin-family in AZC
    aiin_family_azc = Counter()
    for r in azc:
        if r['word'].endswith('aiin'):
            aiin_family_azc[r['word']] += 1
    if aiin_family_azc:
        print(f"\n  All -aiin family tokens in AZC:")
        for w, c in aiin_family_azc.most_common(15):
            print(f"    {w}: {c}")
        results['all_aiin_family'] = dict(aiin_family_azc.most_common(15))

    return results


# ============================================================
# MAIN
# ============================================================
def main():
    print("Loading transcript data...")
    records = load_data()
    systems = split_by_system(records)

    print(f"Records: A={len(systems['A'])}, B={len(systems['B'])}, AZC={len(systems['AZC'])}")
    print(f"Total: {sum(len(v) for v in systems.values())}")

    all_results = {}

    all_results['anchors'] = analysis_1_b_anchors(systems)
    all_results['positional'] = analysis_2_positional(systems)
    all_results['paragraph'] = analysis_3_paragraph(systems)
    all_results['cooccurrence'] = analysis_4_cooccurrence(systems)
    all_results['other_forms'] = analysis_5_other_forms(systems)
    all_results['a_special'] = analysis_6_a_special(systems)
    all_results['azc'] = analysis_7_azc(systems)

    # Save results
    out_path = RESULTS_DIR / 's2_daiin_vs_aiin_split.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n{'='*70}")
    print(f"Results saved to {out_path}")


if __name__ == '__main__':
    main()
