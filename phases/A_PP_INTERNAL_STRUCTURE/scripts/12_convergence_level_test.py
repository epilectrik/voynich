#!/usr/bin/env python3
"""
Test 12: Convergence Level Analysis

Question: Does the hysteresis loop tightening occur at:
- FOLIO level (line position within folio)
- PARAGRAPH level (line position within paragraph)
- BOTH levels

Measures:
1. Hazard proximity trajectory
2. Lane balance (QO fraction) trajectory
3. Line complexity trajectory

At two levels:
- Within-paragraph: line ordinal within paragraph (1st, 2nd, 3rd line of paragraph)
- Across-paragraph: paragraph ordinal within folio (1st, 2nd, 3rd paragraph)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# Load B grammar for class identification
BCSC_PATH = Path(__file__).parent.parent.parent.parent / "context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml"

def load_class_map():
    """Load MIDDLE -> class mapping from BCSC."""
    import yaml
    with open(BCSC_PATH) as f:
        bcsc = yaml.safe_load(f)

    class_map = {}
    for cls in bcsc.get('instruction_classes', []):
        cls_id = cls['id']
        for member in cls.get('members', []):
            class_map[member] = cls_id
    return class_map

def get_hazard_classes():
    """Return set of hazard-participating class IDs."""
    # From BCSC: hazard classes are 7, 8, 30, 31 plus FL hazard classes
    return {7, 8, 30, 31}

def get_hazard_middles(class_map, hazard_classes):
    """Get set of MIDDLEs that belong to hazard classes."""
    return {m for m, c in class_map.items() if c in hazard_classes}

def get_lane(middle, class_map):
    """Determine lane (QO or CHSH) from MIDDLE's initial character."""
    if not middle:
        return None
    first_char = middle[0]
    if first_char in 'qo':
        return 'QO'
    elif first_char in 'chs':
        return 'CHSH'
    return None

def analyze_line(tokens, class_map, morph, hazard_classes):
    """Analyze a single line for convergence metrics."""
    if len(tokens) < 2:
        return None

    middles = []
    classes = []
    lanes = []

    for token in tokens:
        m = morph.extract(token.word)
        if m and m.middle:
            middles.append(m.middle)
            cls = class_map.get(m.middle)
            classes.append(cls)
            lanes.append(get_lane(m.middle, class_map))

    if len(middles) < 2:
        return None

    # 1. Hazard proximity: mean distance to nearest hazard-class token
    hazard_positions = [i for i, c in enumerate(classes) if c in hazard_classes]
    if hazard_positions:
        distances = []
        for i, c in enumerate(classes):
            if c not in hazard_classes:
                min_dist = min(abs(i - hp) for hp in hazard_positions)
                distances.append(min_dist)
        hazard_proximity = np.mean(distances) if distances else None
    else:
        hazard_proximity = None

    # 2. Lane balance: QO fraction among EN tokens with lane
    lane_tokens = [l for l in lanes if l is not None]
    if lane_tokens:
        qo_fraction = sum(1 for l in lane_tokens if l == 'QO') / len(lane_tokens)
    else:
        qo_fraction = None

    # 3. Line complexity: unique MIDDLE count
    unique_middles = len(set(middles))

    return {
        'hazard_proximity': hazard_proximity,
        'qo_fraction': qo_fraction,
        'unique_middles': unique_middles,
        'token_count': len(middles)
    }

def main():
    print("=" * 70)
    print("TEST 12: CONVERGENCE LEVEL ANALYSIS")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    class_map = load_class_map()
    hazard_classes = get_hazard_classes()
    hazard_middles = get_hazard_middles(class_map, hazard_classes)
    print(f"\nHazard classes: {hazard_classes}")
    print(f"Hazard MIDDLEs: {len(hazard_middles)} types")
    print(f"Examples: {list(hazard_middles)[:10]}")

    # Organize tokens by folio -> paragraph -> line
    # Build paragraph structure from par_initial flags
    folio_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    current_para = defaultdict(int)  # folio -> current paragraph number
    current_line = defaultdict(lambda: defaultdict(int))  # folio -> para -> current line

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

    # Counters for debugging
    lines_with_hazard = 0
    total_lines = 0

    # Analyze each line
    results = {
        'within_paragraph': {  # line ordinal within paragraph
            'hazard_proximity': defaultdict(list),
            'qo_fraction': defaultdict(list),
            'unique_middles': defaultdict(list)
        },
        'across_paragraph': {  # paragraph ordinal within folio
            'hazard_proximity': defaultdict(list),
            'qo_fraction': defaultdict(list),
            'unique_middles': defaultdict(list)
        },
        'folio_level': {  # line ordinal within folio (for comparison)
            'hazard_proximity': defaultdict(list),
            'qo_fraction': defaultdict(list),
            'unique_middles': defaultdict(list)
        }
    }

    for folio, paras in folio_data.items():
        folio_line_ordinal = 0

        for para_ord, lines in sorted(paras.items()):
            para_metrics = []

            for line_ord, tokens in sorted(lines.items()):
                folio_line_ordinal += 1
                metrics = analyze_line(tokens, class_map, morph, hazard_classes)
                total_lines += 1

                if metrics:
                    if metrics['hazard_proximity'] is not None:
                        lines_with_hazard += 1
                    para_metrics.append(metrics)

                    # Within-paragraph: by line ordinal within paragraph
                    if metrics['hazard_proximity'] is not None:
                        results['within_paragraph']['hazard_proximity'][line_ord].append(metrics['hazard_proximity'])
                    if metrics['qo_fraction'] is not None:
                        results['within_paragraph']['qo_fraction'][line_ord].append(metrics['qo_fraction'])
                    results['within_paragraph']['unique_middles'][line_ord].append(metrics['unique_middles'])

                    # Folio-level: by line ordinal within folio (normalized to quartile)
                    if metrics['hazard_proximity'] is not None:
                        results['folio_level']['hazard_proximity'][folio_line_ordinal].append(metrics['hazard_proximity'])
                    if metrics['qo_fraction'] is not None:
                        results['folio_level']['qo_fraction'][folio_line_ordinal].append(metrics['qo_fraction'])
                    results['folio_level']['unique_middles'][folio_line_ordinal].append(metrics['unique_middles'])

            # Across-paragraph: aggregate paragraph metrics
            if para_metrics:
                mean_hp = np.mean([m['hazard_proximity'] for m in para_metrics if m['hazard_proximity'] is not None]) if any(m['hazard_proximity'] is not None for m in para_metrics) else None
                mean_qo = np.mean([m['qo_fraction'] for m in para_metrics if m['qo_fraction'] is not None]) if any(m['qo_fraction'] is not None for m in para_metrics) else None
                mean_um = np.mean([m['unique_middles'] for m in para_metrics])

                if mean_hp is not None:
                    results['across_paragraph']['hazard_proximity'][para_ord].append(mean_hp)
                if mean_qo is not None:
                    results['across_paragraph']['qo_fraction'][para_ord].append(mean_qo)
                results['across_paragraph']['unique_middles'][para_ord].append(mean_um)

    print(f"\nTotal lines analyzed: {total_lines}")
    print(f"Lines with hazard tokens: {lines_with_hazard} ({100*lines_with_hazard/total_lines:.1f}%)")

    # Analyze trajectories
    print("\n" + "=" * 70)
    print("WITHIN-PARAGRAPH TRAJECTORY (line ordinal within paragraph)")
    print("=" * 70)

    for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']:
        data = results['within_paragraph'][metric]
        # Limit to first 8 line ordinals (most paragraphs are short)
        ordinals = sorted([o for o in data.keys() if o <= 8])

        if len(ordinals) >= 3:
            # Compute correlation with ordinal
            all_x = []
            all_y = []
            for o in ordinals:
                for v in data[o]:
                    all_x.append(o)
                    all_y.append(v)

            if len(all_x) > 10:
                rho, p = stats.spearmanr(all_x, all_y)

                print(f"\n{metric}:")
                print(f"  Spearman rho = {rho:.3f}, p = {p:.4g}")
                print(f"  Line 1: {np.mean(data[1]):.3f} (n={len(data[1])})")
                if 4 in data and data[4]:
                    print(f"  Line 4: {np.mean(data[4]):.3f} (n={len(data[4])})")
                if 8 in data and data[8]:
                    print(f"  Line 8: {np.mean(data[8]):.3f} (n={len(data[8])})")

    print("\n" + "=" * 70)
    print("ACROSS-PARAGRAPH TRAJECTORY (paragraph ordinal within folio)")
    print("=" * 70)

    for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']:
        data = results['across_paragraph'][metric]
        # Limit to first 10 paragraph ordinals
        ordinals = sorted([o for o in data.keys() if o <= 10])

        if len(ordinals) >= 3:
            all_x = []
            all_y = []
            for o in ordinals:
                for v in data[o]:
                    all_x.append(o)
                    all_y.append(v)

            if len(all_x) > 10:
                rho, p = stats.spearmanr(all_x, all_y)

                print(f"\n{metric}:")
                print(f"  Spearman rho = {rho:.3f}, p = {p:.4g}")
                print(f"  Para 1: {np.mean(data[1]):.3f} (n={len(data[1])})")
                if 5 in data and data[5]:
                    print(f"  Para 5: {np.mean(data[5]):.3f} (n={len(data[5])})")
                if 10 in data and data[10]:
                    print(f"  Para 10: {np.mean(data[10]):.3f} (n={len(data[10])})")

    print("\n" + "=" * 70)
    print("FOLIO-LEVEL TRAJECTORY (for comparison with C668/C669/C677)")
    print("=" * 70)

    for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']:
        data = results['folio_level'][metric]
        ordinals = sorted(data.keys())

        if len(ordinals) >= 4:
            all_x = []
            all_y = []
            for o in ordinals:
                for v in data[o]:
                    all_x.append(o)
                    all_y.append(v)

            if len(all_x) > 10:
                rho, p = stats.spearmanr(all_x, all_y)

                # Compute quartile means
                q1_ord = ordinals[:len(ordinals)//4]
                q4_ord = ordinals[3*len(ordinals)//4:]

                q1_vals = [v for o in q1_ord for v in data[o]]
                q4_vals = [v for o in q4_ord for v in data[o]]

                print(f"\n{metric}:")
                print(f"  Spearman rho = {rho:.3f}, p = {p:.4g}")
                if q1_vals:
                    print(f"  Q1 mean: {np.mean(q1_vals):.3f}")
                if q4_vals:
                    print(f"  Q4 mean: {np.mean(q4_vals):.3f}")

    print("\n" + "=" * 70)
    print("SUMMARY: WHERE DOES CONVERGENCE OCCUR?")
    print("=" * 70)

    # Collect all correlations for summary
    summary = {}

    for level in ['within_paragraph', 'across_paragraph', 'folio_level']:
        summary[level] = {}
        for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']:
            data = results[level][metric]
            if level == 'within_paragraph':
                ordinals = sorted([o for o in data.keys() if o <= 8])
            elif level == 'across_paragraph':
                ordinals = sorted([o for o in data.keys() if o <= 10])
            else:
                ordinals = sorted(data.keys())

            if len(ordinals) >= 3:
                all_x = []
                all_y = []
                for o in ordinals:
                    for v in data[o]:
                        all_x.append(o)
                        all_y.append(v)

                if len(all_x) > 10:
                    rho, p = stats.spearmanr(all_x, all_y)
                    summary[level][metric] = {'rho': rho, 'p': p}

    print("\n| Level | Hazard Prox | QO Fraction | Unique MIDDLEs |")
    print("|-------|-------------|-------------|----------------|")

    for level in ['within_paragraph', 'across_paragraph', 'folio_level']:
        row = f"| {level:18} |"
        for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']:
            if metric in summary[level]:
                rho = summary[level][metric]['rho']
                p = summary[level][metric]['p']
                sig = "**" if p < 0.01 else "*" if p < 0.05 else ""
                row += f" {rho:+.3f}{sig:2} |"
            else:
                row += " N/A |"
        print(row)

    print("\n** p<0.01, * p<0.05")
    print("\nNegative correlation = tightening (closer hazard, less QO, fewer MIDDLEs)")

    # Save results
    output = {
        'summary': {
            level: {
                metric: summary[level].get(metric, {})
                for metric in ['hazard_proximity', 'qo_fraction', 'unique_middles']
            }
            for level in ['within_paragraph', 'across_paragraph', 'folio_level']
        }
    }

    output_path = Path(__file__).parent.parent / "results" / "convergence_level_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
