"""
Phase S1: Single-Token A Line Positional & Codicological Anchoring

Question: What transitions do single-token A lines coincide with?

If they are registry-level operators, they should align with:
- quire/folio boundaries
- section breaks
- coverage trajectory inflections
- prefix regime shifts

Tests:
S1.1 - Boundary Proximity
S1.2 - Coverage Trajectory Breaks
S1.3 - Prefix Regime Shifts
S1.4 - HT Response Check (negative test)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# The 10 single-token line tokens
SINGLE_TOKEN_LINES = [
    ('f1r', 6, 'ydaraishy'),
    ('f1r', 28, 'dchaiin'),
    ('f8r', 13, 'okokchodm'),
    ('f8v', 11, 'sorain'),
    ('f24r', 20, 'samchorly'),
    ('f27r', 13, 'okchodeey'),
    ('f37v', 13, 'sotoiiin'),
    ('f88v', 0, 'daramdal'),
    ('f89r1', 0, 'ykyd'),
    ('f102v1', 0, 'ker'),
]


def load_full_data():
    """Load all data with metadata."""
    lines_by_folio = defaultdict(list)  # folio -> [(line_num, tokens, section, quire)]
    folio_metadata = {}  # folio -> {section, quire, max_line}

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            lang = row.get('language', '')
            if lang != 'A':
                continue

            folio = row['folio']
            section = row.get('section', '')
            quire = row.get('quire', '')
            line_str = row.get('line_number', '0')

            try:
                line_num = int(line_str)
            except ValueError:
                line_num = int(''.join(c for c in line_str if c.isdigit()) or '0')

            lines_by_folio[folio].append((line_num, token, section, quire))

            if folio not in folio_metadata:
                folio_metadata[folio] = {'section': section, 'quire': quire, 'max_line': 0}
            folio_metadata[folio]['max_line'] = max(folio_metadata[folio]['max_line'], line_num)

    # Consolidate to line-level
    line_data = {}  # (folio, line_num) -> {tokens: [], section, quire}
    for folio, entries in lines_by_folio.items():
        by_line = defaultdict(list)
        for line_num, token, section, quire in entries:
            by_line[line_num].append((token, section, quire))

        for line_num, token_list in by_line.items():
            tokens = [t[0] for t in token_list]
            section = token_list[0][1]
            quire = token_list[0][2]
            line_data[(folio, line_num)] = {
                'tokens': tokens,
                'section': section,
                'quire': quire,
                'folio': folio
            }

    return line_data, folio_metadata


def test_s1_1_boundary_proximity(line_data, folio_metadata):
    """S1.1: Test proximity to boundaries."""
    print("="*70)
    print("S1.1: BOUNDARY PROXIMITY")
    print("="*70)

    single_distances = []
    random_distances = []

    # Calculate distances for single-token lines
    print(f"\nSingle-token line boundary distances:")
    print(f"{'Folio':<10} {'Line':<6} {'Max':<6} {'From Start':<12} {'From End':<12} {'Normalized':<12}")
    print("-"*65)

    for folio, line_num, token in SINGLE_TOKEN_LINES:
        if folio in folio_metadata:
            max_line = folio_metadata[folio]['max_line']
            from_start = line_num
            from_end = max_line - line_num
            min_distance = min(from_start, from_end)
            normalized = min_distance / max_line if max_line > 0 else 0

            single_distances.append({
                'folio': folio,
                'line': line_num,
                'from_start': from_start,
                'from_end': from_end,
                'min_distance': min_distance,
                'normalized': normalized
            })

            print(f"{folio:<10} {line_num:<6} {max_line:<6} {from_start:<12} {from_end:<12} {normalized:.3f}")

    # Calculate for random sample of A lines
    all_lines = [(f, ln) for (f, ln) in line_data.keys()]
    np.random.seed(42)
    sample_indices = np.random.choice(len(all_lines), min(200, len(all_lines)), replace=False)

    for idx in sample_indices:
        folio, line_num = all_lines[idx]
        if folio in folio_metadata:
            max_line = folio_metadata[folio]['max_line']
            from_start = line_num
            from_end = max_line - line_num
            min_distance = min(from_start, from_end)
            normalized = min_distance / max_line if max_line > 0 else 0
            random_distances.append(normalized)

    # Statistical comparison
    single_norm = [d['normalized'] for d in single_distances]

    print(f"\nBoundary proximity (normalized min distance):")
    print(f"  Single-token lines: mean={np.mean(single_norm):.3f} ± {np.std(single_norm):.3f}")
    print(f"  Random A lines:     mean={np.mean(random_distances):.3f} ± {np.std(random_distances):.3f}")

    # Lower normalized distance = closer to boundary
    stat, p = stats.mannwhitneyu(single_norm, random_distances, alternative='less')
    print(f"\n  Mann-Whitney U (single < random): p = {p:.4f}")
    print(f"  Interpretation: {'BOUNDARY ENRICHED' if p < 0.05 else 'NOT BOUNDARY ENRICHED'}")

    # Count at exact boundaries
    at_start = sum(1 for d in single_distances if d['from_start'] <= 1)
    at_end = sum(1 for d in single_distances if d['from_end'] <= 1)

    print(f"\n  At folio start (line 0-1): {at_start}/10 ({100*at_start/10:.0f}%)")
    print(f"  At folio end (last 2 lines): {at_end}/10 ({100*at_end/10:.0f}%)")

    return single_distances


def test_s1_2_coverage_trajectory(line_data, folio_metadata):
    """S1.2: Test if single-token lines occur at coverage trajectory breaks."""
    print("\n" + "="*70)
    print("S1.2: COVERAGE TRAJECTORY BREAKS")
    print("="*70)

    # For each folio with a single-token line, analyze MIDDLE introduction rate
    # before vs after the single-token line

    def get_middle(token):
        if len(token) >= 4:
            return token[2:-2] if len(token) > 4 else token[2:-1]
        return token

    results = []

    for folio, single_line, token in SINGLE_TOKEN_LINES:
        # Get all lines in this folio
        folio_lines = [(ln, data) for (f, ln), data in line_data.items() if f == folio]
        folio_lines.sort(key=lambda x: x[0])

        if len(folio_lines) < 5:
            continue

        # Split into before and after single-token line
        before_middles = set()
        after_middles = set()

        for ln, data in folio_lines:
            for tok in data['tokens']:
                middle = get_middle(tok)
                if ln < single_line:
                    before_middles.add(middle)
                elif ln > single_line:
                    after_middles.add(middle)

        # New MIDDLEs introduced after
        new_after = after_middles - before_middles

        results.append({
            'folio': folio,
            'single_line': single_line,
            'before_middles': len(before_middles),
            'after_middles': len(after_middles),
            'new_after': len(new_after),
            'novelty_rate': len(new_after) / len(after_middles) if after_middles else 0
        })

    print(f"\nMIDDLE introduction around single-token lines:")
    print(f"{'Folio':<10} {'Line':<6} {'Before':<8} {'After':<8} {'New':<8} {'Novelty':<10}")
    print("-"*55)

    for r in results:
        print(f"{r['folio']:<10} {r['single_line']:<6} {r['before_middles']:<8} "
              f"{r['after_middles']:<8} {r['new_after']:<8} {r['novelty_rate']:.2%}")

    if results:
        avg_novelty = np.mean([r['novelty_rate'] for r in results])
        print(f"\nMean novelty rate after single-token lines: {avg_novelty:.1%}")

        # Compare to random split points
        random_novelties = []
        for folio in set(f for f, _, _ in SINGLE_TOKEN_LINES):
            folio_lines = [(ln, data) for (f, ln), data in line_data.items() if f == folio]
            folio_lines.sort(key=lambda x: x[0])

            if len(folio_lines) < 10:
                continue

            # Random split point
            split_point = folio_lines[len(folio_lines)//2][0]

            before_m = set()
            after_m = set()
            for ln, data in folio_lines:
                for tok in data['tokens']:
                    middle = get_middle(tok)
                    if ln < split_point:
                        before_m.add(middle)
                    else:
                        after_m.add(middle)

            new_m = after_m - before_m
            if after_m:
                random_novelties.append(len(new_m) / len(after_m))

        if random_novelties:
            print(f"Mean novelty rate at random splits: {np.mean(random_novelties):.1%}")

    return results


def test_s1_3_prefix_regime_shifts(line_data, folio_metadata):
    """S1.3: Test if prefix distribution changes around single-token lines."""
    print("\n" + "="*70)
    print("S1.3: PREFIX REGIME SHIFTS")
    print("="*70)

    def get_prefix(token):
        return token[:2] if len(token) >= 2 else token

    results = []

    for folio, single_line, token in SINGLE_TOKEN_LINES:
        folio_lines = [(ln, data) for (f, ln), data in line_data.items() if f == folio]
        folio_lines.sort(key=lambda x: x[0])

        if len(folio_lines) < 5:
            continue

        before_prefixes = []
        after_prefixes = []

        for ln, data in folio_lines:
            for tok in data['tokens']:
                prefix = get_prefix(tok)
                if ln < single_line:
                    before_prefixes.append(prefix)
                elif ln > single_line:
                    after_prefixes.append(prefix)

        if not before_prefixes or not after_prefixes:
            continue

        # Compare prefix distributions
        before_counts = Counter(before_prefixes)
        after_counts = Counter(after_prefixes)

        # Calculate entropy
        def entropy(counts):
            total = sum(counts.values())
            probs = [c/total for c in counts.values()]
            return -sum(p * np.log2(p) for p in probs if p > 0)

        before_ent = entropy(before_counts)
        after_ent = entropy(after_counts)

        # Top prefix changes
        all_prefixes = set(before_counts.keys()) | set(after_counts.keys())
        before_total = sum(before_counts.values())
        after_total = sum(after_counts.values())

        shifts = []
        for p in all_prefixes:
            before_pct = before_counts.get(p, 0) / before_total
            after_pct = after_counts.get(p, 0) / after_total
            shift = after_pct - before_pct
            if abs(shift) > 0.03:  # 3% threshold
                shifts.append((p, before_pct, after_pct, shift))

        results.append({
            'folio': folio,
            'single_line': single_line,
            'before_entropy': before_ent,
            'after_entropy': after_ent,
            'entropy_change': after_ent - before_ent,
            'major_shifts': shifts
        })

    print(f"\nPrefix entropy changes around single-token lines:")
    print(f"{'Folio':<10} {'Line':<6} {'Before H':<10} {'After H':<10} {'Change':<10}")
    print("-"*50)

    for r in results:
        print(f"{r['folio']:<10} {r['single_line']:<6} {r['before_entropy']:.3f}     "
              f"{r['after_entropy']:.3f}     {r['entropy_change']:+.3f}")

    # Show major shifts
    print(f"\nMajor prefix shifts (>3%):")
    for r in results:
        if r['major_shifts']:
            print(f"\n  {r['folio']} line {r['single_line']}:")
            for prefix, before, after, shift in sorted(r['major_shifts'], key=lambda x: -abs(x[3])):
                direction = "+" if shift > 0 else "-"
                print(f"    {prefix}: {before:.1%} -> {after:.1%} ({direction}{abs(shift):.1%})")

    if results:
        avg_entropy_change = np.mean([abs(r['entropy_change']) for r in results])
        print(f"\nMean absolute entropy change: {avg_entropy_change:.3f}")

    return results


def test_s1_4_ht_response(line_data):
    """S1.4: Negative test - expect NO HT clustering at single-token lines."""
    print("\n" + "="*70)
    print("S1.4: HT RESPONSE CHECK (NEGATIVE TEST)")
    print("="*70)

    # HT tokens are rare in pure-A folios (we already know AZC=0 for these)
    # But let's check if there's any HT-like behavior in adjacent lines

    # HT-associated prefixes (from context)
    ht_prefixes = {'s', 'd', 'y', 'o', 'q', 'l', 'r', 'p', 'f', 'm', 'n'}

    results = []

    for folio, single_line, token in SINGLE_TOKEN_LINES:
        folio_lines = [(ln, data) for (f, ln), data in line_data.items() if f == folio]
        folio_lines.sort(key=lambda x: x[0])

        # Check 3 lines before and after
        adjacent_tokens = []
        for ln, data in folio_lines:
            if abs(ln - single_line) <= 3 and ln != single_line:
                adjacent_tokens.extend(data['tokens'])

        # Count single-char tokens (potential HT markers)
        single_char = sum(1 for t in adjacent_tokens if len(t) == 1)
        single_char_rate = single_char / len(adjacent_tokens) if adjacent_tokens else 0

        results.append({
            'folio': folio,
            'line': single_line,
            'adjacent_tokens': len(adjacent_tokens),
            'single_char': single_char,
            'single_char_rate': single_char_rate
        })

    print(f"\nSingle-character token rate near single-token lines:")
    print(f"{'Folio':<10} {'Line':<6} {'Adjacent':<10} {'Single-char':<12} {'Rate':<10}")
    print("-"*55)

    for r in results:
        print(f"{r['folio']:<10} {r['line']:<6} {r['adjacent_tokens']:<10} "
              f"{r['single_char']:<12} {r['single_char_rate']:.1%}")

    if results:
        avg_rate = np.mean([r['single_char_rate'] for r in results])
        print(f"\nMean single-char rate near single-token lines: {avg_rate:.1%}")
        print(f"(Low rate supports HT non-involvement)")

    return results


def main():
    print("Loading data...")
    line_data, folio_metadata = load_full_data()
    print(f"Loaded {len(line_data)} A lines across {len(folio_metadata)} folios")

    # Run S1 tests
    s1_1 = test_s1_1_boundary_proximity(line_data, folio_metadata)
    s1_2 = test_s1_2_coverage_trajectory(line_data, folio_metadata)
    s1_3 = test_s1_3_prefix_regime_shifts(line_data, folio_metadata)
    s1_4 = test_s1_4_ht_response(line_data)

    # Summary
    print("\n" + "="*70)
    print("PHASE S1 SUMMARY")
    print("="*70)

    signals = []

    # S1.1 summary
    at_boundary = sum(1 for d in s1_1 if d['normalized'] < 0.1)
    if at_boundary >= 5:
        signals.append("BOUNDARY_ANCHORED")
        print(f"\n[✓] S1.1: {at_boundary}/10 within 10% of folio boundary → BOUNDARY ANCHORED")
    else:
        print(f"\n[ ] S1.1: {at_boundary}/10 within 10% of boundary → Not strongly anchored")

    # S1.2 summary
    if s1_2:
        high_novelty = sum(1 for r in s1_2 if r['novelty_rate'] > 0.3)
        if high_novelty >= 3:
            signals.append("TRAJECTORY_BREAK")
            print(f"[✓] S1.2: {high_novelty}/{len(s1_2)} show >30% novelty → TRAJECTORY BREAKS")
        else:
            print(f"[ ] S1.2: {high_novelty}/{len(s1_2)} show >30% novelty → Weak trajectory signal")

    # S1.3 summary
    if s1_3:
        with_shifts = sum(1 for r in s1_3 if len(r['major_shifts']) >= 2)
        if with_shifts >= 3:
            signals.append("PREFIX_REGIME_SHIFT")
            print(f"[✓] S1.3: {with_shifts}/{len(s1_3)} show ≥2 major prefix shifts → REGIME SHIFTS")
        else:
            print(f"[ ] S1.3: {with_shifts}/{len(s1_3)} show ≥2 major prefix shifts → Weak regime signal")

    # S1.4 summary
    if s1_4:
        low_ht = sum(1 for r in s1_4 if r['single_char_rate'] < 0.05)
        if low_ht >= 7:
            signals.append("HT_NON_INVOLVEMENT")
            print(f"[✓] S1.4: {low_ht}/10 show <5% single-char → HT NON-INVOLVEMENT confirmed")
        else:
            print(f"[ ] S1.4: {low_ht}/10 show <5% single-char → HT involvement unclear")

    print(f"\n{'='*70}")
    if len(signals) >= 3:
        print("VERDICT: Single-token lines are REGISTRY CONTROL OPERATORS")
        print(f"         Signals: {', '.join(signals)}")
    elif len(signals) >= 2:
        print("VERDICT: Strong evidence for registry control function")
        print(f"         Signals: {', '.join(signals)}")
    else:
        print("VERDICT: Evidence inconclusive - may be structural punctuation")
    print("="*70)


if __name__ == '__main__':
    main()
