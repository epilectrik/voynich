#!/usr/bin/env python3
"""
Test 13: Paragraph Line Role Analysis

Question: What roles and interventions occur at each line position within paragraphs?

Analyzes:
1. Role distribution by line ordinal (EN, CC, AX, FQ, FL)
2. Class enrichment by line ordinal
3. Specific MIDDLE patterns by position
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# Role definitions from BCSC
ROLE_CLASSES = {
    'CC': {10, 11, 12, 17},  # CORE_CONTROL
    'EN': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},  # ENERGY
    'AX': {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},  # AUXILIARY
    'FQ': {9, 13, 14, 23},  # FREQUENT
    'FL': {7, 30, 38, 40},  # FLOW (includes hazard FL)
}

# Load class map
def load_class_map():
    """Load MIDDLE -> class mapping."""
    class_map_path = Path(__file__).parent.parent.parent.parent / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"

    if class_map_path.exists():
        with open(class_map_path) as f:
            data = json.load(f)
            # Build middle->class from token data
            middle_to_class = {}
            for token, cls_id in data.get('token_to_class', {}).items():
                middle = data.get('token_to_middle', {}).get(token)
                if middle:
                    middle_to_class[middle] = cls_id
            return middle_to_class, data.get('token_to_class', {}), data.get('token_to_role', {})

    return {}, {}, {}

def get_role(cls_id):
    """Get role name for a class ID."""
    for role, classes in ROLE_CLASSES.items():
        if cls_id in classes:
            return role
    return 'HT'  # Unclassified = HT

def main():
    print("=" * 70)
    print("TEST 13: PARAGRAPH LINE ROLE ANALYSIS")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    middle_to_class, token_to_class, token_to_role = load_class_map()

    print(f"\nLoaded class map with {len(middle_to_class)} MIDDLEs, {len(token_to_class)} tokens")

    # Build paragraph structure
    folio_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    current_para = defaultdict(int)
    current_line = defaultdict(lambda: defaultdict(int))

    for token in tx.currier_b():
        folio = token.folio
        if token.par_initial:
            current_para[folio] += 1
            current_line[folio][current_para[folio]] = 0
        if token.line_initial:
            current_line[folio][current_para[folio]] += 1

        para = current_para[folio]
        line = current_line[folio][para]
        if para > 0 and line > 0:
            folio_data[folio][para][line].append(token)

    # Analyze by line ordinal within paragraph
    line_roles = defaultdict(lambda: Counter())  # line_ord -> role -> count
    line_classes = defaultdict(lambda: Counter())  # line_ord -> class -> count
    line_middles = defaultdict(lambda: Counter())  # line_ord -> middle -> count
    line_totals = defaultdict(int)  # line_ord -> total tokens

    for folio, paras in folio_data.items():
        for para_ord, lines in paras.items():
            for line_ord, tokens in lines.items():
                for token in tokens:
                    word = token.word
                    m = morph.extract(word)
                    if m and m.middle:
                        middle = m.middle

                        # Try to get role from token_to_role first (more accurate)
                        role = token_to_role.get(word)
                        cls_id = token_to_class.get(word)

                        # Fallback to middle-based lookup
                        if role is None:
                            cls_id = middle_to_class.get(middle)
                            if cls_id is not None:
                                role = get_role(int(cls_id))

                        if role:
                            line_roles[line_ord][role] += 1
                            if cls_id is not None:
                                line_classes[line_ord][int(cls_id)] += 1
                        else:
                            line_roles[line_ord]['HT'] += 1

                        line_middles[line_ord][middle] += 1
                        line_totals[line_ord] += 1

    # Report role distribution by line ordinal
    print("\n" + "=" * 70)
    print("ROLE DISTRIBUTION BY LINE ORDINAL WITHIN PARAGRAPH")
    print("=" * 70)

    print("\n| Line | Total | CC% | EN% | AX% | FQ% | FL% | HT% |")
    print("|------|-------|-----|-----|-----|-----|-----|-----|")

    for line_ord in sorted(line_roles.keys())[:10]:  # First 10 lines
        total = line_totals[line_ord]
        roles = line_roles[line_ord]

        row = f"| {line_ord:4} | {total:5} |"
        for role in ['CC', 'EN', 'AX', 'FQ', 'FL', 'HT']:
            pct = 100 * roles[role] / total if total > 0 else 0
            row += f" {pct:4.1f}|"
        print(row)

    # Calculate role trends
    print("\n" + "=" * 70)
    print("ROLE TRENDS (Spearman correlation with line ordinal)")
    print("=" * 70)

    for role in ['CC', 'EN', 'AX', 'FQ', 'FL', 'HT']:
        x_vals = []
        y_vals = []
        for line_ord in sorted(line_roles.keys())[:8]:  # Use first 8 lines
            total = line_totals[line_ord]
            if total >= 50:  # Minimum sample
                pct = 100 * line_roles[line_ord][role] / total
                x_vals.append(line_ord)
                y_vals.append(pct)

        if len(x_vals) >= 4:
            rho, p = stats.spearmanr(x_vals, y_vals)
            sig = "**" if p < 0.01 else "*" if p < 0.05 else ""
            direction = "INCREASES" if rho > 0.3 else "DECREASES" if rho < -0.3 else "FLAT"
            print(f"  {role}: rho={rho:+.3f} (p={p:.3f}) {sig} -> {direction}")

    # Top MIDDLEs by line position
    print("\n" + "=" * 70)
    print("TOP 5 MIDDLEs BY LINE POSITION")
    print("=" * 70)

    for line_ord in [1, 2, 3, 4, 5]:
        if line_ord in line_middles:
            top5 = line_middles[line_ord].most_common(5)
            total = line_totals[line_ord]
            print(f"\nLine {line_ord} (n={total}):")
            for middle, count in top5:
                cls_id = middle_to_class.get(middle)
                role = get_role(int(cls_id)) if cls_id else 'HT'
                pct = 100 * count / total
                print(f"  {middle:12} ({role:2}) : {count:4} ({pct:5.1f}%)")

    # Class enrichment analysis
    print("\n" + "=" * 70)
    print("CLASS ENRICHMENT BY LINE POSITION")
    print("=" * 70)

    # Calculate baseline class rates
    total_by_class = Counter()
    grand_total = 0
    for line_ord, classes in line_classes.items():
        if line_ord <= 8:
            for cls_id, count in classes.items():
                total_by_class[cls_id] += count
                grand_total += count

    baseline_rates = {cls_id: count/grand_total for cls_id, count in total_by_class.items()}

    # Find enriched classes at each position
    for line_ord in [1, 2, 3, 4, 5]:
        if line_ord in line_classes:
            line_total = sum(line_classes[line_ord].values())

            enrichments = []
            for cls_id, count in line_classes[line_ord].items():
                if baseline_rates.get(cls_id, 0) > 0 and count >= 10:
                    obs_rate = count / line_total
                    exp_rate = baseline_rates[cls_id]
                    enrichment = obs_rate / exp_rate
                    if enrichment > 1.3 or enrichment < 0.7:  # >30% deviation
                        enrichments.append((cls_id, enrichment, count))

            enrichments.sort(key=lambda x: -x[1])

            print(f"\nLine {line_ord} - Enriched classes (>1.3x or <0.7x baseline):")
            for cls_id, enrich, count in enrichments[:5]:
                role = get_role(cls_id)
                direction = "UP" if enrich > 1 else "DOWN"
                print(f"  Class {cls_id:2} ({role:2}): {enrich:.2f}x {direction} (n={count})")

    # Semantic interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION: PARAGRAPH LINE PROGRESSION")
    print("=" * 70)

    # Get line 1 vs line 4+ comparison
    l1_roles = line_roles[1]
    l1_total = line_totals[1]

    late_roles = Counter()
    late_total = 0
    for line_ord in [4, 5, 6, 7, 8]:
        if line_ord in line_roles:
            for role, count in line_roles[line_ord].items():
                late_roles[role] += count
            late_total += line_totals[line_ord]

    print("\nLine 1 (paragraph start) vs Lines 4-8 (paragraph body):")
    print("\n| Role | Line 1 | Lines 4-8 | Delta |")
    print("|------|--------|-----------|-------|")

    for role in ['CC', 'EN', 'AX', 'FQ', 'FL', 'HT']:
        l1_pct = 100 * l1_roles[role] / l1_total if l1_total > 0 else 0
        late_pct = 100 * late_roles[role] / late_total if late_total > 0 else 0
        delta = late_pct - l1_pct
        print(f"| {role:4} | {l1_pct:5.1f}% | {late_pct:8.1f}% | {delta:+5.1f}pp |")

    # Save results
    output = {
        'role_by_line': {
            line_ord: {role: count for role, count in roles.items()}
            for line_ord, roles in line_roles.items()
        },
        'line_totals': dict(line_totals),
        'top_middles_by_line': {
            line_ord: middles.most_common(10)
            for line_ord, middles in line_middles.items()
        }
    }

    output_path = Path(__file__).parent.parent / "results" / "paragraph_line_role_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
