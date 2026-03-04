#!/usr/bin/env python3
"""
P-C4: c standalone -hy suffix lock

Test the observation that standalone c tokens (MIDDLE = just "c") have
~90% -hy suffix attachment. This makes c one of the most suffix-locked
atoms in the system.

If c = "adjust", the -hy lock means "adjust+watch+end" = a calibration
check that is always completed with monitoring confirmation.

Predictions:
  1. c standalone (MIDDLE == "c") has >= 80% -hy suffix
  2. c tokens at mid-to-late line positions (mean >= 0.40)
  3. Comparison to other standalone atoms (k, h, e, d) shows c is
     uniquely -hy locked

Pass criterion: -hy suffix >= 80% AND mean line position >= 0.40

Method:
  - Collect all tokens where MIDDLE = "c" (standalone, not compound)
  - Check suffix distribution
  - Compute line position (token_index / line_length)
  - Compare to control standalone atoms
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()

    # Target atoms for comparison
    TARGET_ATOMS = ['c', 'k', 'h', 'e', 'd']

    # Collect data: per standalone atom -> suffix dist, positions, macro-states
    atom_suffix_counts = defaultdict(lambda: defaultdict(int))
    atom_totals = defaultdict(int)
    atom_positions = defaultdict(list)  # atom -> list of normalized positions
    atom_macro_states = defaultdict(lambda: defaultdict(int))  # atom -> state -> count
    atom_prefix_dist = defaultdict(lambda: defaultdict(int))  # atom -> prefix -> count
    atom_section_dist = defaultdict(lambda: defaultdict(int))  # atom -> section -> count

    # Need line lengths for position normalization
    # Pre-compute: folio+line -> token count
    line_tokens = defaultdict(list)
    all_b_tokens = []
    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        key = (token.folio, token.line)
        line_tokens[key].append(token)
        all_b_tokens.append(token)

    # Now iterate with position info
    for key, tokens in line_tokens.items():
        line_len = len(tokens)
        if line_len == 0:
            continue

        for idx, token in enumerate(tokens):
            w = token.word
            if not w or '*' in w:
                continue

            m = morph.extract(w)
            if not m.middle:
                continue

            # Only standalone atoms (single char MIDDLE)
            if len(m.middle) != 1:
                continue

            atom = m.middle
            if atom not in TARGET_ATOMS:
                continue

            suffix = m.suffix if m.suffix else 'BARE'
            norm_pos = idx / (line_len - 1) if line_len > 1 else 0.5

            atom_suffix_counts[atom][suffix] += 1
            atom_totals[atom] += 1
            atom_positions[atom].append(norm_pos)
            atom_prefix_dist[atom][m.prefix if m.prefix else 'BARE'] += 1
            atom_section_dist[atom][token.section or 'UNK'] += 1

            # Get macro-state from decoder
            try:
                analysis = decoder.analyze_token(
                    w,
                    line_initial=(idx == 0),
                    line_final=(idx == line_len - 1)
                )
                if analysis and analysis.macro_state:
                    atom_macro_states[atom][analysis.macro_state] += 1
            except Exception:
                pass

    print("=" * 70)
    print("P-C4: c standalone -hy suffix lock")
    print("=" * 70)
    print()

    # ---- TEST 1: Suffix distribution for standalone c ----
    print("-" * 70)
    print("TEST 1: Suffix distribution for standalone c (MIDDLE='c')")
    print("-" * 70)
    print()

    c_total = atom_totals.get('c', 0)
    c_hy = atom_suffix_counts['c'].get('hy', 0)
    c_hy_rate = c_hy / c_total if c_total > 0 else 0

    print(f"  Standalone c tokens: {c_total}")
    print()

    if c_total > 0:
        print(f"  {'Suffix':<10} {'Count':>7} {'%':>8}")
        print("  " + "-" * 28)
        for suffix, count in sorted(atom_suffix_counts['c'].items(),
                                     key=lambda x: -x[1]):
            pct = count / c_total * 100
            marker = " <-- predicted dominant" if suffix == 'hy' else ""
            print(f"  {suffix:<10} {count:>7} {pct:>7.1f}%{marker}")
        print()
        print(f"  -hy suffix rate: {c_hy}/{c_total} = {c_hy_rate*100:.1f}%")

    # ---- TEST 2: Line position distribution ----
    print()
    print("-" * 70)
    print("TEST 2: Line position for standalone c")
    print("-" * 70)
    print()

    c_positions = atom_positions.get('c', [])
    c_mean_pos = sum(c_positions) / len(c_positions) if c_positions else 0

    if c_positions:
        # Quintile distribution
        quintiles = [0] * 5
        for p in c_positions:
            q = min(int(p * 5), 4)
            quintiles[q] += 1

        print(f"  Mean position: {c_mean_pos:.3f}")
        print(f"  N positions:   {len(c_positions)}")
        print()
        print(f"  {'Quintile':<12} {'Range':>12} {'Count':>7} {'%':>8}")
        print("  " + "-" * 42)
        labels = ['Q1 (0.0-0.2)', 'Q2 (0.2-0.4)', 'Q3 (0.4-0.6)',
                  'Q4 (0.6-0.8)', 'Q5 (0.8-1.0)']
        for i, (label, count) in enumerate(zip(labels, quintiles)):
            pct = count / len(c_positions) * 100
            print(f"  {label:<12} {'':>12} {count:>7} {pct:>7.1f}%")

    # ---- TEST 3: Comparison to other standalone atoms ----
    print()
    print("-" * 70)
    print("TEST 3: Comparison -- standalone atoms suffix profiles")
    print("-" * 70)
    print()

    print(f"  {'Atom':<6} {'Total':>6} {'Top suffix':>12} {'Top%':>7} {'-hy%':>7} {'Mean pos':>9}")
    print("  " + "-" * 52)

    for atom in TARGET_ATOMS:
        total = atom_totals.get(atom, 0)
        if total == 0:
            print(f"  {atom:<6} {'N/A':>6}")
            continue

        # Top suffix
        top_suffix = max(atom_suffix_counts[atom], key=atom_suffix_counts[atom].get)
        top_pct = atom_suffix_counts[atom][top_suffix] / total * 100
        hy_pct = atom_suffix_counts[atom].get('hy', 0) / total * 100
        mean_pos = sum(atom_positions[atom]) / len(atom_positions[atom]) if atom_positions[atom] else 0

        marker = " <-- TARGET" if atom == 'c' else ""
        print(f"  {atom:<6} {total:>6} {top_suffix:>12} {top_pct:>6.1f}% {hy_pct:>6.1f}% {mean_pos:>8.3f}{marker}")

    # ---- TEST 4: Macro-state distribution ----
    print()
    print("-" * 70)
    print("TEST 4: Macro-state distribution for standalone c")
    print("-" * 70)
    print()

    c_macro_total = sum(atom_macro_states['c'].values())
    if c_macro_total > 0:
        print(f"  {'Macro-state':<15} {'Count':>7} {'%':>8}")
        print("  " + "-" * 33)
        for state, count in sorted(atom_macro_states['c'].items(),
                                    key=lambda x: -x[1]):
            pct = count / c_macro_total * 100
            print(f"  {state:<15} {count:>7} {pct:>7.1f}%")
    else:
        print("  No macro-state data available")

    # ---- TEST 5: PREFIX distribution for standalone c ----
    print()
    print("-" * 70)
    print("TEST 5: PREFIX distribution for standalone c")
    print("-" * 70)
    print()

    if c_total > 0:
        print(f"  {'PREFIX':<10} {'Count':>7} {'%':>8}")
        print("  " + "-" * 28)
        for pfx, count in sorted(atom_prefix_dist['c'].items(),
                                  key=lambda x: -x[1]):
            pct = count / c_total * 100
            print(f"  {pfx:<10} {count:>7} {pct:>7.1f}%")

    # ---- TEST 6: Section distribution ----
    print()
    print("-" * 70)
    print("TEST 6: Section distribution for standalone c")
    print("-" * 70)
    print()

    if c_total > 0:
        print(f"  {'Section':<10} {'Count':>7} {'%':>8}")
        print("  " + "-" * 28)
        for sec, count in sorted(atom_section_dist['c'].items(),
                                  key=lambda x: -x[1]):
            pct = count / c_total * 100
            print(f"  {sec:<10} {count:>7} {pct:>7.1f}%")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-C4 c standalone -hy suffix lock")
    print("=" * 70)

    pass_hy = c_hy_rate >= 0.80
    pass_position = c_mean_pos >= 0.40

    # Check if c is the most -hy-locked atom
    c_hy_highest = True
    for atom in TARGET_ATOMS:
        if atom == 'c':
            continue
        total = atom_totals.get(atom, 0)
        if total > 0:
            other_hy_rate = atom_suffix_counts[atom].get('hy', 0) / total
            if other_hy_rate >= c_hy_rate:
                c_hy_highest = False
                break

    pass_unique = c_hy_highest

    results = [
        ("-hy suffix >= 80%", pass_hy,
         f"{c_hy_rate*100:.1f}% ({c_hy}/{c_total})"),
        ("Mean line position >= 0.40", pass_position,
         f"{c_mean_pos:.3f}"),
        ("c uniquely -hy locked (highest among controls)", pass_unique,
         f"{'YES' if c_hy_highest else 'NO'}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_hy and pass_position
    print()
    print(f"  PRIMARY CRITERION (-hy >= 80% AND mean pos >= 0.40): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
