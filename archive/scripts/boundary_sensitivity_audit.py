"""
BOUNDARY SENSITIVITY AUDIT

Question: Are hazard-related tokens depleted near structural boundaries?

If hazards are avoided near line/folio/quire boundaries, this suggests:
- Grammar has human-factors awareness
- Boundaries serve as "safe zones"
- Connects hazard topology to organizational structure

Tests:
1. Line boundaries: Are hazard sources/targets depleted at line start/end?
2. Folio boundaries: Are hazard sources/targets depleted at folio start/end?
3. Quire boundaries: Same for quire boundaries
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

def load_forbidden_transitions():
    """Load forbidden transitions from canonical grammar."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    forbidden = set()
    constraints = data.get('constraints', {})
    samples = constraints.get('sample', [])

    for item in samples:
        if item.get('type') == 'FORBIDDEN':
            pattern = item.get('pattern', '')
            parts = pattern.split(' -> ')
            if len(parts) == 2:
                forbidden.add((parts[0].strip(), parts[1].strip()))

    return forbidden

def load_sequences_with_positions():
    """Load Currier B tokens with full position information."""
    data = []

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            # Handle line numbers like '4a' by extracting numeric part
            line_str = row.get('line_number', '0')
            try:
                line_num = int(''.join(c for c in line_str if c.isdigit()) or '0')
            except:
                line_num = 0

            data.append({
                'folio': row['folio'],
                'line': line_num,
                'line_str': line_str,  # Keep original for grouping
                'token': token,
                'line_initial': row.get('line_initial', '0') == '1',
                'line_final': row.get('line_final', '0') == '1',
                'quire': row.get('quire', '')
            })

    return data

def identify_boundary_positions(data):
    """Identify tokens at various boundary positions."""
    # Group by folio to identify folio boundaries
    by_folio = defaultdict(list)
    for i, item in enumerate(data):
        by_folio[item['folio']].append(i)

    # Group by quire
    by_quire = defaultdict(list)
    for i, item in enumerate(data):
        if item['quire']:
            by_quire[item['quire']].append(i)

    boundaries = {
        'line_initial': set(),
        'line_final': set(),
        'folio_initial': set(),
        'folio_final': set(),
        'quire_initial': set(),
        'quire_final': set(),
        'mid_line': set(),
        'mid_folio': set()
    }

    for i, item in enumerate(data):
        if item['line_initial']:
            boundaries['line_initial'].add(i)
        elif item['line_final']:
            boundaries['line_final'].add(i)
        else:
            boundaries['mid_line'].add(i)

    for folio, indices in by_folio.items():
        if indices:
            boundaries['folio_initial'].add(indices[0])
            boundaries['folio_final'].add(indices[-1])
            for idx in indices[1:-1]:
                boundaries['mid_folio'].add(idx)

    for quire, indices in by_quire.items():
        if indices:
            boundaries['quire_initial'].add(indices[0])
            boundaries['quire_final'].add(indices[-1])

    return boundaries

def identify_hazard_tokens(forbidden):
    """Get sets of hazard source and target tokens."""
    sources = set(t1 for t1, t2 in forbidden)
    targets = set(t2 for t1, t2 in forbidden)
    return sources, targets

def analyze_boundary_hazard_depletion(data, boundaries, sources, targets):
    """Check if hazard tokens are depleted at boundaries."""
    print("="*70)
    print("BOUNDARY SENSITIVITY AUDIT")
    print("="*70)

    print(f"\nHazard sources: {sources}")
    print(f"Hazard targets: {targets}")

    # Count hazard tokens at each boundary type
    results = {}

    for boundary_type in ['line_initial', 'line_final', 'folio_initial', 'folio_final']:
        boundary_indices = boundaries[boundary_type]

        if boundary_type.startswith('line'):
            non_boundary = boundaries['mid_line']
        else:
            non_boundary = boundaries['mid_folio']

        # Count sources and targets at boundary vs non-boundary
        source_at_boundary = sum(1 for i in boundary_indices if data[i]['token'] in sources)
        source_not_boundary = sum(1 for i in non_boundary if data[i]['token'] in sources)

        target_at_boundary = sum(1 for i in boundary_indices if data[i]['token'] in targets)
        target_not_boundary = sum(1 for i in non_boundary if data[i]['token'] in targets)

        total_boundary = len(boundary_indices)
        total_non_boundary = len(non_boundary)

        results[boundary_type] = {
            'source_boundary': source_at_boundary,
            'source_non_boundary': source_not_boundary,
            'target_boundary': target_at_boundary,
            'target_non_boundary': target_not_boundary,
            'total_boundary': total_boundary,
            'total_non_boundary': total_non_boundary
        }

    return results

def test_depletion(results):
    """Statistical test for depletion at boundaries."""
    print("\n" + "-"*70)
    print("HAZARD TOKEN BOUNDARY DEPLETION TEST")
    print("-"*70)

    for boundary_type, counts in results.items():
        print(f"\n{boundary_type.upper()}:")

        # Source tokens
        source_rate_boundary = counts['source_boundary'] / counts['total_boundary'] * 100
        source_rate_non = counts['source_non_boundary'] / counts['total_non_boundary'] * 100

        # Create 2x2 contingency table for sources
        # [boundary_source, boundary_other], [non_boundary_source, non_boundary_other]
        table_source = [
            [counts['source_boundary'], counts['total_boundary'] - counts['source_boundary']],
            [counts['source_non_boundary'], counts['total_non_boundary'] - counts['source_non_boundary']]
        ]

        if min(counts['source_boundary'], counts['source_non_boundary']) < 5:
            _, p_source = fisher_exact(table_source)
            test_type = "Fisher"
        else:
            chi2, p_source, _, _ = chi2_contingency(table_source)
            test_type = "Chi2"

        ratio_source = source_rate_boundary / source_rate_non if source_rate_non > 0 else float('inf')

        print(f"  SOURCE tokens:")
        print(f"    At boundary: {counts['source_boundary']}/{counts['total_boundary']} ({source_rate_boundary:.2f}%)")
        print(f"    Non-boundary: {counts['source_non_boundary']}/{counts['total_non_boundary']} ({source_rate_non:.2f}%)")
        print(f"    Ratio: {ratio_source:.2f}x ({test_type} p={p_source:.4f})")

        # Target tokens
        target_rate_boundary = counts['target_boundary'] / counts['total_boundary'] * 100
        target_rate_non = counts['target_non_boundary'] / counts['total_non_boundary'] * 100

        table_target = [
            [counts['target_boundary'], counts['total_boundary'] - counts['target_boundary']],
            [counts['target_non_boundary'], counts['total_non_boundary'] - counts['target_non_boundary']]
        ]

        if min(counts['target_boundary'], counts['target_non_boundary']) < 5:
            _, p_target = fisher_exact(table_target)
            test_type = "Fisher"
        else:
            chi2, p_target, _, _ = chi2_contingency(table_target)
            test_type = "Chi2"

        ratio_target = target_rate_boundary / target_rate_non if target_rate_non > 0 else float('inf')

        print(f"  TARGET tokens:")
        print(f"    At boundary: {counts['target_boundary']}/{counts['total_boundary']} ({target_rate_boundary:.2f}%)")
        print(f"    Non-boundary: {counts['target_non_boundary']}/{counts['total_non_boundary']} ({target_rate_non:.2f}%)")
        print(f"    Ratio: {ratio_target:.2f}x ({test_type} p={p_target:.4f})")

def analyze_near_boundary(data, boundaries, sources, targets, window=2):
    """Check if hazard tokens are depleted NEAR boundaries (within window)."""
    print("\n" + "-"*70)
    print(f"NEAR-BOUNDARY ANALYSIS (window={window})")
    print("-"*70)

    # Create sets of positions near boundaries
    near_line_start = set()
    near_line_end = set()

    for i in boundaries['line_initial']:
        for j in range(i, min(i + window, len(data))):
            near_line_start.add(j)

    for i in boundaries['line_final']:
        for j in range(max(0, i - window + 1), i + 1):
            near_line_end.add(j)

    mid_positions = set(range(len(data))) - near_line_start - near_line_end

    # Count
    for token_set, name in [(sources, "SOURCE"), (targets, "TARGET")]:
        count_near_start = sum(1 for i in near_line_start if data[i]['token'] in token_set)
        count_near_end = sum(1 for i in near_line_end if data[i]['token'] in token_set)
        count_mid = sum(1 for i in mid_positions if data[i]['token'] in token_set)

        rate_start = count_near_start / len(near_line_start) * 100 if near_line_start else 0
        rate_end = count_near_end / len(near_line_end) * 100 if near_line_end else 0
        rate_mid = count_mid / len(mid_positions) * 100 if mid_positions else 0

        print(f"\n{name} tokens:")
        print(f"  Near line start: {count_near_start}/{len(near_line_start)} ({rate_start:.2f}%)")
        print(f"  Near line end:   {count_near_end}/{len(near_line_end)} ({rate_end:.2f}%)")
        print(f"  Mid-line:        {count_mid}/{len(mid_positions)} ({rate_mid:.2f}%)")

        if rate_mid > 0:
            print(f"  Start/mid ratio: {rate_start/rate_mid:.2f}x")
            print(f"  End/mid ratio:   {rate_end/rate_mid:.2f}x")

def analyze_transition_positions(data, forbidden):
    """Check where in lines forbidden transition PAIRS would occur if they existed."""
    print("\n" + "-"*70)
    print("POTENTIAL TRANSITION POSITION ANALYSIS")
    print("-"*70)

    sources, targets = identify_hazard_tokens(forbidden)

    # Find all bigrams involving source followed by target (not forbidden, just source->anything or anything->target)
    source_positions = []  # positions where source tokens appear
    target_positions = []  # positions where target tokens appear

    for i, item in enumerate(data):
        if item['token'] in sources:
            source_positions.append(i)
        if item['token'] in targets:
            target_positions.append(i)

    # Analyze line positions of source and target tokens
    source_line_positions = []
    target_line_positions = []

    # Group by line to get relative position
    by_line = defaultdict(list)
    for i, item in enumerate(data):
        key = (item['folio'], item.get('line_str', item['line']))
        by_line[key].append(i)

    for key, indices in by_line.items():
        line_len = len(indices)
        for pos, idx in enumerate(indices):
            rel_pos = pos / (line_len - 1) if line_len > 1 else 0.5
            if data[idx]['token'] in sources:
                source_line_positions.append(rel_pos)
            if data[idx]['token'] in targets:
                target_line_positions.append(rel_pos)

    if source_line_positions:
        print(f"\nSource token line positions (0=start, 1=end):")
        print(f"  Mean: {np.mean(source_line_positions):.3f}")
        print(f"  Std:  {np.std(source_line_positions):.3f}")
        print(f"  Count: {len(source_line_positions)}")

    if target_line_positions:
        print(f"\nTarget token line positions (0=start, 1=end):")
        print(f"  Mean: {np.mean(target_line_positions):.3f}")
        print(f"  Std:  {np.std(target_line_positions):.3f}")
        print(f"  Count: {len(target_line_positions)}")

def summarize():
    """Summary of findings."""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
If hazard tokens are DEPLETED at boundaries:
  -> Grammar has human-factors awareness
  -> Boundaries serve as "safe zones"
  -> Supports ergonomic design hypothesis

If hazard tokens are UNIFORM:
  -> No human-factors signal at boundary level
  -> Hazard avoidance is local (token-to-token), not structural

If hazard tokens are ENRICHED at boundaries:
  -> Boundaries might be "hazard concentration" points
  -> Would contradict ergonomic hypothesis
""")

def main():
    forbidden = load_forbidden_transitions()
    data = load_sequences_with_positions()
    boundaries = identify_boundary_positions(data)
    sources, targets = identify_hazard_tokens(forbidden)

    print(f"Loaded {len(forbidden)} forbidden transitions")
    print(f"Loaded {len(data)} Currier B tokens with positions")
    print(f"Hazard sources: {len(sources)}, targets: {len(targets)}")

    print(f"\nBoundary counts:")
    for btype, indices in boundaries.items():
        print(f"  {btype}: {len(indices)}")

    results = analyze_boundary_hazard_depletion(data, boundaries, sources, targets)
    test_depletion(results)
    analyze_near_boundary(data, boundaries, sources, targets)
    analyze_transition_positions(data, forbidden)
    summarize()

if __name__ == '__main__':
    main()
