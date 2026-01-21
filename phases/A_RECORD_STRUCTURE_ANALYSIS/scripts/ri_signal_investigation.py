#!/usr/bin/env python3
"""
RI Signal Investigation - All Four Priority Analyses

Uses pre-classified token_data.json from A_INTERNAL_STRATIFICATION.

Priority 1: Line-final RI predecessor analysis
Priority 2: First-line multi-RI propagation test
Priority 3: Line-final vs line-initial RI overlap
Priority 4: f99v.0 pure-RI case study

Includes controls recommended by expert:
- Filter to lines >= 4 tokens
- Report folio count contributing
- Test with top-3 folios removed
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load pre-classified token data from A_INTERNAL_STRATIFICATION."""
    data_path = Path('phases/A_INTERNAL_STRATIFICATION/results/token_data.json')
    with open(data_path, 'r') as f:
        tokens = json.load(f)

    # Group by line (folio.line)
    lines = defaultdict(list)
    for t in tokens:
        line_key = f"{t['folio']}.{t['line']}"
        lines[line_key].append(t)

    # Group lines by folio
    folio_lines = defaultdict(list)
    for line_key in lines.keys():
        folio = line_key.rsplit('.', 1)[0]
        folio_lines[folio].append(line_key)

    # Sort lines within each folio by line number
    for folio in folio_lines:
        def sort_key(lk):
            line_part = lk.rsplit('.', 1)[1]
            # Extract numeric part for sorting
            num = ''.join(c for c in line_part if c.isdigit())
            suffix = ''.join(c for c in line_part if not c.isdigit())
            return (int(num) if num else 0, suffix)
        folio_lines[folio].sort(key=sort_key)

    return tokens, lines, folio_lines

# ============================================================
# PRIORITY 1: LINE-FINAL RI PREDECESSOR ANALYSIS
# ============================================================

def priority_1_predecessor_analysis(lines):
    """
    Analyze what PP tokens immediately precede line-final RI tokens.

    Tests the "Do X... with Y" hypothesis - does RI at line-end
    have specific PP predecessors?
    """
    print("=" * 70)
    print("PRIORITY 1: LINE-FINAL RI PREDECESSOR ANALYSIS")
    print("=" * 70)
    print()

    # Collect line-final RI tokens and their predecessors
    line_final_ri = []

    for line_key, line_tokens in lines.items():
        if len(line_tokens) < 2:  # Need at least 2 tokens
            continue

        last_token = line_tokens[-1]
        if last_token['middle_class'] == 'exclusive':
            predecessor = line_tokens[-2]
            line_final_ri.append({
                'line_key': line_key,
                'folio': last_token['folio'],
                'ri_token': last_token['token'],
                'ri_middle': last_token['middle'],
                'ri_prefix': last_token['prefix'],
                'pred_token': predecessor['token'],
                'pred_middle': predecessor['middle'],
                'pred_prefix': predecessor['prefix'],
                'pred_class': predecessor['middle_class'],
                'line_length': len(line_tokens)
            })

    print(f"Line-final RI tokens found: {len(line_final_ri)}")
    print()

    # Filter to lines >= 4 tokens (control)
    line_final_ri_4plus = [x for x in line_final_ri if x['line_length'] >= 4]
    print(f"Line-final RI in lines >= 4 tokens: {len(line_final_ri_4plus)}")
    print()

    # Predecessor class distribution
    pred_classes = Counter(x['pred_class'] for x in line_final_ri)
    print("Predecessor class distribution (all line-final RI):")
    for cls, count in pred_classes.most_common():
        pct = 100 * count / len(line_final_ri)
        print(f"  {cls}: {count} ({pct:.1f}%)")
    print()

    # Focus on PP predecessors (most common case)
    pp_predecessors = [x for x in line_final_ri if x['pred_class'] == 'shared']
    print(f"PP predecessors: {len(pp_predecessors)}")
    print()

    # PREFIX distribution of PP predecessors
    pred_prefixes = Counter(x['pred_prefix'] for x in pp_predecessors)
    print("PREFIX distribution of PP predecessors:")
    for prefix, count in pred_prefixes.most_common(15):
        pct = 100 * count / len(pp_predecessors)
        print(f"  {prefix}: {count} ({pct:.1f}%)")
    print()

    # MIDDLE distribution of PP predecessors
    pred_middles = Counter(x['pred_middle'] for x in pp_predecessors)
    print("MIDDLE distribution of PP predecessors (top 15):")
    for middle, count in pred_middles.most_common(15):
        pct = 100 * count / len(pp_predecessors)
        print(f"  {middle}: {count} ({pct:.1f}%)")
    print()

    # Folio distribution (control)
    folios = Counter(x['folio'] for x in line_final_ri)
    print(f"Distinct folios contributing: {len(folios)}")
    print("Top 5 folios:")
    for folio, count in folios.most_common(5):
        print(f"  {folio}: {count}")
    print()

    # Control: Remove top 3 folios and re-check
    top_3_folios = set(f for f, _ in folios.most_common(3))
    line_final_ri_no_top3 = [x for x in line_final_ri if x['folio'] not in top_3_folios]
    print(f"After removing top 3 folios: {len(line_final_ri_no_top3)} line-final RI")

    if line_final_ri_no_top3:
        pp_pred_no_top3 = [x for x in line_final_ri_no_top3 if x['pred_class'] == 'shared']
        if pp_pred_no_top3:
            pred_prefixes_no_top3 = Counter(x['pred_prefix'] for x in pp_pred_no_top3)
            print("PREFIX distribution (top 3 folios removed):")
            for prefix, count in pred_prefixes_no_top3.most_common(10):
                pct = 100 * count / len(pp_pred_no_top3)
                print(f"  {prefix}: {count} ({pct:.1f}%)")
    print()

    # Specific line-final RI MIDDLEs and their predecessors
    print("Line-final RI MIDDLEs (ho, hod, hol, mo, oro, tod) - predecessors:")
    target_middles = ['ho', 'hod', 'hol', 'mo', 'oro', 'tod']
    for target in target_middles:
        matches = [x for x in line_final_ri if x['ri_middle'] == target]
        if matches:
            preds = Counter(x['pred_middle'] for x in matches)
            pred_list = ', '.join(f"{m}({c})" for m, c in preds.most_common(5))
            print(f"  {target} (n={len(matches)}): {pred_list}")
    print()

    return {
        'total_line_final_ri': len(line_final_ri),
        'lines_4plus': len(line_final_ri_4plus),
        'pp_predecessors': len(pp_predecessors),
        'distinct_folios': len(folios),
        'pred_prefix_dist': dict(pred_prefixes.most_common(10)),
        'pred_middle_dist': dict(pred_middles.most_common(10)),
    }


# ============================================================
# PRIORITY 2: FIRST-LINE MULTI-RI PROPAGATION TEST
# ============================================================

def priority_2_first_line_propagation(lines, folio_lines):
    """
    Test if first-line multi-RI entries "set up" vocabulary for later lines.

    Do RI MIDDLEs from folio's first line reappear in subsequent lines?
    """
    print("=" * 70)
    print("PRIORITY 2: FIRST-LINE MULTI-RI PROPAGATION TEST")
    print("=" * 70)
    print()

    # Find folios where first line has 2+ RI
    first_line_multi_ri = []

    for folio, line_keys in folio_lines.items():
        if len(line_keys) < 2:  # Need subsequent lines
            continue

        first_line_key = line_keys[0]
        first_line_tokens = lines[first_line_key]

        ri_middles = [t['middle'] for t in first_line_tokens
                      if t['middle_class'] == 'exclusive']

        if len(ri_middles) >= 2:
            # Get RI middles from subsequent lines
            subsequent_ri = set()
            for lk in line_keys[1:]:
                for t in lines[lk]:
                    if t['middle_class'] == 'exclusive':
                        subsequent_ri.add(t['middle'])

            propagated = set(ri_middles) & subsequent_ri

            first_line_multi_ri.append({
                'folio': folio,
                'first_line': first_line_key,
                'ri_middles': ri_middles,
                'n_subsequent_lines': len(line_keys) - 1,
                'subsequent_ri': subsequent_ri,
                'propagated': propagated,
                'propagation_rate': len(propagated) / len(ri_middles) if ri_middles else 0
            })

    print(f"Folios with first-line multi-RI: {len(first_line_multi_ri)}")
    print()

    if not first_line_multi_ri:
        print("No folios with multi-RI first lines found.")
        return {}

    # Propagation statistics
    prop_rates = [x['propagation_rate'] for x in first_line_multi_ri]
    mean_prop = sum(prop_rates) / len(prop_rates)
    any_prop = sum(1 for x in first_line_multi_ri if x['propagation_rate'] > 0)

    print(f"Mean propagation rate: {100*mean_prop:.1f}%")
    print(f"Folios with ANY propagation: {any_prop}/{len(first_line_multi_ri)} ({100*any_prop/len(first_line_multi_ri):.1f}%)")
    print()

    # Show examples
    print("Examples:")
    for entry in first_line_multi_ri[:10]:
        prop_str = ', '.join(entry['propagated']) if entry['propagated'] else 'NONE'
        print(f"  {entry['folio']}: first-line RI = {entry['ri_middles']}")
        print(f"    Propagated to subsequent lines: {prop_str}")
        print(f"    Rate: {100*entry['propagation_rate']:.0f}%")
        print()

    # Control: Compare to non-first-line multi-RI
    print("-" * 50)
    print("CONTROL: Non-first-line multi-RI propagation")
    print()

    non_first_multi_ri = []
    for folio, line_keys in folio_lines.items():
        if len(line_keys) < 3:  # Need lines before and after
            continue

        # Look at middle lines (not first, not last)
        for i, lk in enumerate(line_keys[1:-1], start=1):
            line_tokens = lines[lk]
            ri_middles = [t['middle'] for t in line_tokens
                          if t['middle_class'] == 'exclusive']

            if len(ri_middles) >= 2:
                # Get RI from subsequent lines only
                subsequent_ri = set()
                for subsequent_lk in line_keys[i+1:]:
                    for t in lines[subsequent_lk]:
                        if t['middle_class'] == 'exclusive':
                            subsequent_ri.add(t['middle'])

                propagated = set(ri_middles) & subsequent_ri

                non_first_multi_ri.append({
                    'folio': folio,
                    'line': lk,
                    'ri_middles': ri_middles,
                    'propagated': propagated,
                    'propagation_rate': len(propagated) / len(ri_middles) if ri_middles else 0
                })

    if non_first_multi_ri:
        control_rates = [x['propagation_rate'] for x in non_first_multi_ri]
        control_mean = sum(control_rates) / len(control_rates)
        control_any = sum(1 for x in non_first_multi_ri if x['propagation_rate'] > 0)

        print(f"Non-first-line multi-RI entries: {len(non_first_multi_ri)}")
        print(f"Mean propagation rate: {100*control_mean:.1f}%")
        print(f"Any propagation: {control_any}/{len(non_first_multi_ri)} ({100*control_any/len(non_first_multi_ri):.1f}%)")
        print()
        print(f"COMPARISON: First-line = {100*mean_prop:.1f}% vs Non-first = {100*control_mean:.1f}%")
    else:
        print("No non-first-line multi-RI found for control.")
        control_mean = 0

    print()

    return {
        'first_line_multi_ri_count': len(first_line_multi_ri),
        'mean_propagation_rate': mean_prop,
        'any_propagation_count': any_prop,
        'control_mean_rate': control_mean if non_first_multi_ri else None,
    }


# ============================================================
# PRIORITY 3: LINE-FINAL VS LINE-INITIAL RI OVERLAP
# ============================================================

def priority_3_positional_overlap(lines):
    """
    Test if line-final and line-initial RI MIDDLEs are distinct subsets.

    If disjoint: RI has sub-roles (openers vs closers)
    If overlapping: position is structural, not role-based
    """
    print("=" * 70)
    print("PRIORITY 3: LINE-FINAL VS LINE-INITIAL RI OVERLAP")
    print("=" * 70)
    print()

    line_initial_ri = set()
    line_final_ri = set()
    line_middle_ri = set()

    # Also track by token for frequency
    initial_counts = Counter()
    final_counts = Counter()
    middle_counts = Counter()

    for line_key, line_tokens in lines.items():
        if len(line_tokens) < 2:
            continue

        for i, t in enumerate(line_tokens):
            if t['middle_class'] == 'exclusive':
                middle = t['middle']
                if i == 0:
                    line_initial_ri.add(middle)
                    initial_counts[middle] += 1
                elif i == len(line_tokens) - 1:
                    line_final_ri.add(middle)
                    final_counts[middle] += 1
                else:
                    line_middle_ri.add(middle)
                    middle_counts[middle] += 1

    print(f"Line-INITIAL RI MIDDLEs: {len(line_initial_ri)} types")
    print(f"Line-FINAL RI MIDDLEs: {len(line_final_ri)} types")
    print(f"Line-MIDDLE RI MIDDLEs: {len(line_middle_ri)} types")
    print()

    # Overlaps
    initial_final_overlap = line_initial_ri & line_final_ri
    initial_only = line_initial_ri - line_final_ri - line_middle_ri
    final_only = line_final_ri - line_initial_ri - line_middle_ri

    all_positional = line_initial_ri | line_final_ri | line_middle_ri

    print(f"Initial-Final overlap: {len(initial_final_overlap)} MIDDLEs")
    print(f"Initial-ONLY: {len(initial_only)} MIDDLEs")
    print(f"Final-ONLY: {len(final_only)} MIDDLEs")
    print()

    # Jaccard similarity
    if line_initial_ri | line_final_ri:
        jaccard = len(initial_final_overlap) / len(line_initial_ri | line_final_ri)
        print(f"Jaccard similarity (initial vs final): {jaccard:.3f}")
    print()

    # Show initial-only MIDDLEs
    print("INITIAL-ONLY MIDDLEs (never appear at end):")
    for middle in sorted(initial_only)[:15]:
        print(f"  {middle} (n={initial_counts[middle]})")
    print()

    # Show final-only MIDDLEs
    print("FINAL-ONLY MIDDLEs (never appear at start):")
    for middle in sorted(final_only)[:15]:
        print(f"  {middle} (n={final_counts[middle]})")
    print()

    # MIDDLEs that appear in both
    print("MIDDLEs appearing BOTH initial and final:")
    for middle in sorted(initial_final_overlap):
        init_n = initial_counts[middle]
        final_n = final_counts[middle]
        ratio = final_n / init_n if init_n > 0 else float('inf')
        print(f"  {middle}: initial={init_n}, final={final_n}, ratio={ratio:.2f}")
    print()

    # Positional preference score
    print("POSITIONAL PREFERENCE (MIDDLEs appearing 3+ times at boundary):")
    all_boundary = set(m for m, c in initial_counts.items() if c >= 3) | \
                   set(m for m, c in final_counts.items() if c >= 3)

    for middle in sorted(all_boundary):
        init_n = initial_counts[middle]
        final_n = final_counts[middle]
        total = init_n + final_n
        if total >= 3:
            pref = (final_n - init_n) / total  # -1 = all initial, +1 = all final
            pref_label = "FINAL" if pref > 0.3 else ("INITIAL" if pref < -0.3 else "NEUTRAL")
            print(f"  {middle}: init={init_n}, final={final_n}, pref={pref:+.2f} ({pref_label})")
    print()

    return {
        'initial_types': len(line_initial_ri),
        'final_types': len(line_final_ri),
        'overlap_types': len(initial_final_overlap),
        'initial_only': len(initial_only),
        'final_only': len(final_only),
        'jaccard': jaccard if (line_initial_ri | line_final_ri) else 0,
    }


# ============================================================
# PRIORITY 4: f99v.0 PURE-RI CASE STUDY
# ============================================================

def priority_4_pure_ri_case_study(lines, folio_lines):
    """
    Case study of f99v.0 (pure-RI line) and similar entries.

    Does the vocabulary appear in subsequent lines?
    """
    print("=" * 70)
    print("PRIORITY 4: PURE-RI LINE CASE STUDY")
    print("=" * 70)
    print()

    # Find all pure-RI lines (100% exclusive)
    pure_ri_lines = []
    for line_key, line_tokens in lines.items():
        if len(line_tokens) == 0:
            continue
        ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
        if ri_count == len(line_tokens):
            pure_ri_lines.append({
                'line_key': line_key,
                'folio': line_tokens[0]['folio'],
                'tokens': [t['token'] for t in line_tokens],
                'middles': [t['middle'] for t in line_tokens],
                'length': len(line_tokens)
            })

    print(f"Pure-RI lines found: {len(pure_ri_lines)}")
    print()

    for entry in pure_ri_lines:
        print(f"Line: {entry['line_key']}")
        print(f"  Tokens: {' '.join(entry['tokens'])}")
        print(f"  MIDDLEs: {entry['middles']}")
        print()

        # Check if these MIDDLEs appear elsewhere in the folio
        folio = entry['folio']
        if folio in folio_lines:
            other_lines = [lk for lk in folio_lines[folio] if lk != entry['line_key']]

            for middle in entry['middles']:
                appearances = []
                for lk in other_lines:
                    for t in lines[lk]:
                        if t['middle'] == middle:
                            appearances.append(lk)

                if appearances:
                    print(f"  {middle} appears in: {appearances}")
                else:
                    print(f"  {middle} appears NOWHERE else in {folio}")
            print()

    # Focus on f99v.0 specifically
    print("-" * 50)
    print("FOCUS: f99v.0")
    print()

    if 'f99v.0' in lines:
        f99v0 = lines['f99v.0']
        print(f"Tokens: {[t['token'] for t in f99v0]}")
        print(f"MIDDLEs: {[t['middle'] for t in f99v0]}")
        print()

        # What follows f99v.0?
        if 'f99v' in folio_lines:
            f99v_lines = folio_lines['f99v']
            print(f"All f99v lines: {f99v_lines}")
            print()

            for lk in f99v_lines:
                line_tokens = lines[lk]
                ri_tokens = [t for t in line_tokens if t['middle_class'] == 'exclusive']
                pp_tokens = [t for t in line_tokens if t['middle_class'] == 'shared']

                ri_str = ' '.join(t['token'] for t in ri_tokens) if ri_tokens else '-'
                pp_str = ' '.join(t['token'] for t in pp_tokens) if pp_tokens else '-'

                print(f"  {lk}: RI=[{ri_str}] PP=[{pp_str}]")
    else:
        print("f99v.0 not found in data")

    print()

    return {
        'pure_ri_lines': len(pure_ri_lines),
        'pure_ri_details': pure_ri_lines
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("RI SIGNAL INVESTIGATION")
    print("=" * 70)
    print()

    # Load data
    print("Loading data from token_data.json...")
    tokens, lines, folio_lines = load_data()
    print(f"  Tokens: {len(tokens)}")
    print(f"  Lines: {len(lines)}")
    print(f"  Folios: {len(folio_lines)}")
    print()

    results = {}

    # Run all four priorities
    results['priority_1'] = priority_1_predecessor_analysis(lines)
    results['priority_2'] = priority_2_first_line_propagation(lines, folio_lines)
    results['priority_3'] = priority_3_positional_overlap(lines)
    results['priority_4'] = priority_4_pure_ri_case_study(lines, folio_lines)

    # Save results
    output_path = Path('phases/A_RECORD_STRUCTURE_ANALYSIS/results/ri_signal_investigation.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("=" * 70)
    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    main()
