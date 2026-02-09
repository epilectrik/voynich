#!/usr/bin/env python3
"""
Test: Does AZC position predict B grammar behavior?

We established:
1. AZC positions have different MIDDLE inventories
2. Different MIDDLEs prefer different PREFIXes
3. "Escape rate" is just PREFIX frequency

Question: Does AZC position predict anything about B behavior
BEYOND what MIDDLE composition already determines?

Tests:
1. Do MIDDLEs from different AZC positions have different B-side class distributions?
2. Do MIDDLEs from different AZC positions have different hazard involvement?
3. Do MIDDLEs from different AZC positions appear in different REGIMEs?
4. After controlling for MIDDLE, does position add predictive power?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np
import json

def load_azc_tokens():
    """Load AZC tokens with position and MIDDLE."""
    sys.path.insert(0, str(Path('C:/git/voynich/archive/scripts')))
    from archive.scripts.currier_a_token_generator import decompose_token

    filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        middle = result[1] if result[1] else ''
                        if middle:
                            tokens.append({
                                'token': token,
                                'folio': folio,
                                'placement': placement,
                                'middle': middle
                            })
    return tokens

def load_b_tokens_with_class():
    """Load B tokens with their 49-class assignments."""
    from scripts.voynich import Transcript, Morphology

    # Load class map
    class_map_path = Path('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
    with open(class_map_path) as f:
        class_data = json.load(f)

    # Build token -> class mapping
    token_to_class = {}
    # The JSON has structure {"token_to_class": {token: class, ...}}
    if "token_to_class" in class_data:
        for token, class_id in class_data["token_to_class"].items():
            token_to_class[token.lower()] = int(class_id)
    else:
        # Fallback: assume {class_id: [tokens]}
        for class_id, tokens in class_data.items():
            for token in tokens:
                token_to_class[token.lower()] = int(class_id)

    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        if not t.word.strip():
            continue
        m = morph.extract(t.word)
        if m.middle:
            token_class = token_to_class.get(t.word.lower())
            tokens.append({
                'token': t.word.lower(),
                'folio': t.folio,
                'middle': m.middle,
                'class': token_class
            })

    return tokens

def load_regime_assignments():
    """Load folio -> REGIME mapping."""
    # From OPS-2 cluster profiles
    regime_map = {}

    # REGIME_1
    for f in ['f103v', 'f104r', 'f106r', 'f106v', 'f107v', 'f108r', 'f108v',
              'f111r', 'f111v', 'f112r', 'f112v', 'f113r', 'f114r', 'f66r',
              'f75r', 'f75v', 'f76r', 'f76v', 'f77v', 'f78r', 'f78v', 'f79r',
              'f79v', 'f80r', 'f80v', 'f81v', 'f82r', 'f82v', 'f83r', 'f84r', 'f84v']:
        regime_map[f] = 1

    # REGIME_2
    for f in ['f105r', 'f105v', 'f107r', 'f113v', 'f115v', 'f26v', 'f48r',
              'f48v', 'f85v2', 'f86v3', 'f86v5']:
        regime_map[f] = 2

    # REGIME_3
    for f in ['f103r', 'f104v', 'f114v', 'f115r', 'f116r', 'f31r', 'f33r',
              'f33v', 'f39r', 'f46r', 'f77r', 'f81r', 'f83v', 'f86v4', 'f95r1', 'f95r2']:
        regime_map[f] = 3

    # REGIME_4
    for f in ['f26r', 'f31v', 'f34r', 'f34v', 'f39v', 'f40r', 'f40v', 'f41r',
              'f41v', 'f43r', 'f43v', 'f46v', 'f50r', 'f50v', 'f55r', 'f55v',
              'f57r', 'f66v', 'f85r1', 'f85r2', 'f86v6', 'f94r', 'f94v', 'f95v1', 'f95v2']:
        regime_map[f] = 4

    return regime_map

def main():
    print("=" * 70)
    print("TEST: Does AZC Position Predict B Grammar Behavior?")
    print("=" * 70)
    print()

    # Load data
    print("Loading AZC tokens...")
    azc_tokens = load_azc_tokens()
    print(f"  {len(azc_tokens)} AZC tokens")

    print("Loading B tokens with class assignments...")
    b_tokens = load_b_tokens_with_class()
    print(f"  {len(b_tokens)} B tokens")

    regime_map = load_regime_assignments()

    # Build MIDDLE -> AZC position mapping
    middle_to_positions = defaultdict(set)
    middle_position_counts = defaultdict(lambda: defaultdict(int))

    for t in azc_tokens:
        middle_to_positions[t['middle']].add(t['placement'])
        middle_position_counts[t['middle']][t['placement']] += 1

    # Assign each MIDDLE a "primary" AZC position (most common)
    middle_primary_position = {}
    for middle, pos_counts in middle_position_counts.items():
        primary = max(pos_counts.items(), key=lambda x: x[1])[0]
        middle_primary_position[middle] = primary

    print(f"\nMIDDLEs with AZC position mapping: {len(middle_primary_position)}")

    # ===========================================
    # TEST 1: Position vs B-side Class Distribution
    # ===========================================
    print()
    print("=" * 70)
    print("TEST 1: AZC Position vs B-side Class Distribution")
    print("=" * 70)
    print()

    # Group B tokens by their MIDDLE's AZC position
    position_classes = defaultdict(list)

    for t in b_tokens:
        if t['middle'] in middle_primary_position and t['class'] is not None:
            pos = middle_primary_position[t['middle']]
            position_classes[pos].append(t['class'])

    # Show class distribution by position
    print(f"{'Position':<10} {'N tokens':>10} {'Top classes':>40}")
    print("-" * 62)

    for pos in sorted(position_classes.keys()):
        classes = position_classes[pos]
        if len(classes) < 50:
            continue
        class_counts = Counter(classes)
        top3 = class_counts.most_common(3)
        top_str = ", ".join([f"C{c}:{n}" for c, n in top3])
        print(f"{pos:<10} {len(classes):>10} {top_str:>40}")

    # Chi-squared test: Position x Class (top positions x top classes)
    top_positions = [p for p, c in position_classes.items() if len(c) >= 100]
    if len(top_positions) >= 2:
        # Build contingency table
        all_classes_flat = [c for p in top_positions for c in position_classes[p]]
        top_classes = [c for c, _ in Counter(all_classes_flat).most_common(10)]

        matrix = []
        for pos in top_positions:
            row = [position_classes[pos].count(c) for c in top_classes]
            matrix.append(row)

        matrix = np.array(matrix)
        if matrix.min() >= 0 and matrix.sum() > 0:
            chi2, p, dof, expected = stats.chi2_contingency(matrix)
            print()
            print(f"Chi-squared (Position x Class): chi2={chi2:.1f}, p={p:.2e}, dof={dof}")
            if p < 0.001:
                print("SIGNIFICANT: Position predicts class distribution")
            else:
                print("NOT SIGNIFICANT: Position does not predict class")

    # ===========================================
    # TEST 2: Position vs REGIME Distribution
    # ===========================================
    print()
    print("=" * 70)
    print("TEST 2: AZC Position vs REGIME Distribution")
    print("=" * 70)
    print()

    position_regimes = defaultdict(list)

    for t in b_tokens:
        if t['middle'] in middle_primary_position:
            pos = middle_primary_position[t['middle']]
            regime = regime_map.get(t['folio'])
            if regime:
                position_regimes[pos].append(regime)

    print(f"{'Position':<10} {'N':>8} {'R1%':>8} {'R2%':>8} {'R3%':>8} {'R4%':>8}")
    print("-" * 52)

    for pos in sorted(position_regimes.keys()):
        regimes = position_regimes[pos]
        if len(regimes) < 50:
            continue
        regime_counts = Counter(regimes)
        total = len(regimes)
        r1 = regime_counts.get(1, 0) / total * 100
        r2 = regime_counts.get(2, 0) / total * 100
        r3 = regime_counts.get(3, 0) / total * 100
        r4 = regime_counts.get(4, 0) / total * 100
        print(f"{pos:<10} {total:>8} {r1:>7.1f}% {r2:>7.1f}% {r3:>7.1f}% {r4:>7.1f}%")

    # Chi-squared for position x regime
    top_positions = [p for p, r in position_regimes.items() if len(r) >= 100]
    if len(top_positions) >= 2:
        matrix = []
        for pos in top_positions:
            row = [position_regimes[pos].count(r) for r in [1, 2, 3, 4]]
            matrix.append(row)

        matrix = np.array(matrix)
        chi2, p, dof, expected = stats.chi2_contingency(matrix)
        print()
        print(f"Chi-squared (Position x REGIME): chi2={chi2:.1f}, p={p:.2e}, dof={dof}")

    # ===========================================
    # TEST 3: Position vs Hazard Class Membership
    # ===========================================
    print()
    print("=" * 70)
    print("TEST 3: AZC Position vs Hazard Class Membership")
    print("=" * 70)
    print()

    # Hazard-involved classes from our earlier findings
    hazard_classes = {7, 8, 9, 11, 23, 30, 31, 33, 41}

    position_hazard = defaultdict(lambda: {'hazard': 0, 'safe': 0})

    for t in b_tokens:
        if t['middle'] in middle_primary_position and t['class'] is not None:
            pos = middle_primary_position[t['middle']]
            if t['class'] in hazard_classes:
                position_hazard[pos]['hazard'] += 1
            else:
                position_hazard[pos]['safe'] += 1

    print(f"{'Position':<10} {'Total':>10} {'Hazard%':>10} {'Safe%':>10}")
    print("-" * 42)

    for pos in sorted(position_hazard.keys()):
        h = position_hazard[pos]['hazard']
        s = position_hazard[pos]['safe']
        total = h + s
        if total < 50:
            continue
        print(f"{pos:<10} {total:>10} {h/total*100:>9.1f}% {s/total*100:>9.1f}%")

    # Chi-squared for position x hazard
    top_positions = [p for p, d in position_hazard.items() if d['hazard'] + d['safe'] >= 100]
    if len(top_positions) >= 2:
        matrix = [[position_hazard[p]['hazard'], position_hazard[p]['safe']] for p in top_positions]
        matrix = np.array(matrix)
        chi2, p, dof, expected = stats.chi2_contingency(matrix)
        print()
        print(f"Chi-squared (Position x Hazard): chi2={chi2:.1f}, p={p:.2e}, dof={dof}")

    # ===========================================
    # TEST 4: Does Position Add to MIDDLE?
    # ===========================================
    print()
    print("=" * 70)
    print("TEST 4: Does Position Add Predictive Power Beyond MIDDLE?")
    print("=" * 70)
    print()

    # For MIDDLEs that appear at multiple AZC positions,
    # does position predict different B behavior?

    multi_position_middles = [m for m, positions in middle_to_positions.items()
                              if len(positions) >= 2]

    print(f"MIDDLEs appearing at 2+ AZC positions: {len(multi_position_middles)}")

    # For each such MIDDLE, check if B behavior differs by position
    significant_cases = 0
    tested_cases = 0

    for middle in multi_position_middles:
        # Get B tokens for this MIDDLE, grouped by AZC position
        position_b_classes = defaultdict(list)

        for t in b_tokens:
            if t['middle'] == middle and t['class'] is not None:
                # Determine which AZC position this token's MIDDLE came from
                # (This is tricky - we can only use the most common position)
                # Actually, we need to check if this MIDDLE appears at multiple positions
                for pos in middle_to_positions[middle]:
                    if middle_position_counts[middle][pos] >= 5:
                        position_b_classes[pos].append(t['class'])

        # If we have multiple positions with enough data, test
        valid_positions = [p for p, classes in position_b_classes.items() if len(classes) >= 10]

        if len(valid_positions) >= 2:
            # Compare class distributions across positions
            try:
                groups = [position_b_classes[p] for p in valid_positions]
                h_stat, p_val = stats.kruskal(*groups)
                tested_cases += 1
                if p_val < 0.05:
                    significant_cases += 1
            except:
                pass

    if tested_cases > 0:
        print(f"MIDDLEs tested: {tested_cases}")
        print(f"Significant position effect: {significant_cases} ({significant_cases/tested_cases*100:.1f}%)")
    else:
        print("Insufficient data to test position effect controlling for MIDDLE")

    # ===========================================
    # SUMMARY
    # ===========================================
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Note: All position effects are CONFOUNDED with MIDDLE composition.")
    print("Different positions have different MIDDLEs, so position effects")
    print("may be entirely explained by vocabulary composition.")
    print()
    print("To show position has INDEPENDENT effect, we need MIDDLEs that")
    print("appear at multiple positions to behave differently by position.")
    print("Our Test 4 attempts this but has limited data.")

if __name__ == "__main__":
    main()
