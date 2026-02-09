#!/usr/bin/env python3
"""
Test 14: Paragraph FL State Analysis

Analyzes FL (Flow/Material State) distribution by line position within paragraphs.
Uses C777 FL taxonomy based on MIDDLE morpheme, not 49-class system.

FL Stages (C777):
  INITIAL: ii, i
  EARLY: in
  MEDIAL: r, ar
  LATE: al, l, ol
  FINAL: o, ly, am
  TERMINAL: m, dy, ry, y
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# FL taxonomy from C777
FL_STAGES = {
    'INITIAL': {'ii', 'i'},
    'EARLY': {'in'},
    'MEDIAL': {'r', 'ar'},
    'LATE': {'al', 'l', 'ol'},
    'FINAL': {'o', 'ly', 'am'},
    'TERMINAL': {'m', 'dy', 'ry', 'y'},
}

# Flatten for lookup
FL_MIDDLES = {}
for stage, middles in FL_STAGES.items():
    for m in middles:
        FL_MIDDLES[m] = stage

# Stage order for numerical analysis
STAGE_ORDER = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']
STAGE_NUM = {s: i for i, s in enumerate(STAGE_ORDER)}

def main():
    print("=" * 70)
    print("TEST 14: PARAGRAPH FL STATE ANALYSIS")
    print("=" * 70)
    print("\nFL taxonomy (C777):")
    for stage, middles in FL_STAGES.items():
        print(f"  {stage}: {middles}")

    tx = Transcript()
    morph = Morphology()

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

    # Analyze FL by line ordinal within paragraph
    line_fl_counts = defaultdict(lambda: Counter())  # line_ord -> stage -> count
    line_fl_rate = defaultdict(lambda: {'fl': 0, 'total': 0})  # line_ord -> counts
    line_fl_middles = defaultdict(lambda: Counter())  # line_ord -> middle -> count

    for folio, paras in folio_data.items():
        for para_ord, lines in paras.items():
            for line_ord, tokens in lines.items():
                for token in tokens:
                    m = morph.extract(token.word)
                    if m and m.middle:
                        middle = m.middle
                        line_fl_rate[line_ord]['total'] += 1

                        if middle in FL_MIDDLES:
                            stage = FL_MIDDLES[middle]
                            line_fl_counts[line_ord][stage] += 1
                            line_fl_rate[line_ord]['fl'] += 1
                            line_fl_middles[line_ord][middle] += 1

    # Report FL rate by line ordinal
    print("\n" + "=" * 70)
    print("FL RATE BY LINE ORDINAL WITHIN PARAGRAPH")
    print("=" * 70)

    print("\n| Line | Total | FL Count | FL Rate |")
    print("|------|-------|----------|---------|")

    for line_ord in sorted(line_fl_rate.keys())[:10]:
        data = line_fl_rate[line_ord]
        total = data['total']
        fl_count = data['fl']
        rate = 100 * fl_count / total if total > 0 else 0
        print(f"| {line_ord:4} | {total:5} | {fl_count:8} | {rate:6.1f}% |")

    # Calculate FL rate trend
    x_vals = []
    y_vals = []
    for line_ord in sorted(line_fl_rate.keys())[:8]:
        data = line_fl_rate[line_ord]
        if data['total'] >= 100:
            rate = 100 * data['fl'] / data['total']
            x_vals.append(line_ord)
            y_vals.append(rate)

    if len(x_vals) >= 4:
        rho, p = stats.spearmanr(x_vals, y_vals)
        print(f"\nFL rate trend: rho={rho:+.3f} (p={p:.4f})")

    # Report FL stage distribution by line ordinal
    print("\n" + "=" * 70)
    print("FL STAGE DISTRIBUTION BY LINE ORDINAL")
    print("=" * 70)

    print("\n| Line | INITIAL | EARLY | MEDIAL | LATE | FINAL | TERMINAL |")
    print("|------|---------|-------|--------|------|-------|----------|")

    for line_ord in sorted(line_fl_counts.keys())[:8]:
        stages = line_fl_counts[line_ord]
        total_fl = sum(stages.values())
        row = f"| {line_ord:4} |"
        for stage in STAGE_ORDER:
            count = stages.get(stage, 0)
            pct = 100 * count / total_fl if total_fl > 0 else 0
            row += f" {pct:6.1f}% |"
        print(row)

    # Calculate mean FL stage by line ordinal
    print("\n" + "=" * 70)
    print("MEAN FL STAGE BY LINE ORDINAL")
    print("=" * 70)

    print("\n(0=INITIAL, 1=EARLY, 2=MEDIAL, 3=LATE, 4=FINAL, 5=TERMINAL)")
    print("\n| Line | Mean Stage | Stage Name | N |")
    print("|------|------------|------------|---|")

    mean_stages = []
    for line_ord in sorted(line_fl_counts.keys())[:8]:
        stages = line_fl_counts[line_ord]
        total_fl = sum(stages.values())
        if total_fl >= 50:
            weighted_sum = sum(STAGE_NUM[s] * c for s, c in stages.items())
            mean_stage = weighted_sum / total_fl
            mean_stages.append((line_ord, mean_stage, total_fl))
            stage_name = STAGE_ORDER[int(round(mean_stage))]
            print(f"| {line_ord:4} | {mean_stage:10.2f} | {stage_name:10} | {total_fl:3} |")

    # Calculate mean stage trend
    if len(mean_stages) >= 4:
        x = [m[0] for m in mean_stages]
        y = [m[1] for m in mean_stages]
        rho, p = stats.spearmanr(x, y)
        print(f"\nMean FL stage trend: rho={rho:+.3f} (p={p:.4f})")
        if rho > 0.3:
            print("  -> FL stage INCREASES within paragraph (INITIAL -> TERMINAL)")
        elif rho < -0.3:
            print("  -> FL stage DECREASES within paragraph (TERMINAL -> INITIAL)")
        else:
            print("  -> FL stage FLAT within paragraph")

    # Top FL MIDDLEs by line position
    print("\n" + "=" * 70)
    print("TOP FL MIDDLEs BY LINE POSITION")
    print("=" * 70)

    for line_ord in [1, 2, 3, 4, 5]:
        if line_ord in line_fl_middles and line_fl_middles[line_ord]:
            top5 = line_fl_middles[line_ord].most_common(5)
            total = sum(line_fl_middles[line_ord].values())
            print(f"\nLine {line_ord} (n={total} FL tokens):")
            for middle, count in top5:
                stage = FL_MIDDLES[middle]
                pct = 100 * count / total
                print(f"  {middle:4} ({stage:8}) : {count:4} ({pct:5.1f}%)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: FL WITHIN PARAGRAPH PROGRESSION")
    print("=" * 70)

    l1_data = line_fl_rate[1]
    l1_rate = 100 * l1_data['fl'] / l1_data['total'] if l1_data['total'] > 0 else 0

    late_fl = 0
    late_total = 0
    for line_ord in [4, 5, 6, 7, 8]:
        if line_ord in line_fl_rate:
            late_fl += line_fl_rate[line_ord]['fl']
            late_total += line_fl_rate[line_ord]['total']
    late_rate = 100 * late_fl / late_total if late_total > 0 else 0

    print(f"\nLine 1 FL rate: {l1_rate:.1f}%")
    print(f"Lines 4-8 FL rate: {late_rate:.1f}%")
    print(f"Delta: {late_rate - l1_rate:+.1f}pp")

    # Stage comparison
    l1_stages = line_fl_counts[1]
    l1_total = sum(l1_stages.values())

    late_stages = Counter()
    for line_ord in [4, 5, 6, 7, 8]:
        for stage, count in line_fl_counts[line_ord].items():
            late_stages[stage] += count
    late_stage_total = sum(late_stages.values())

    print("\n| Stage | Line 1 | Lines 4-8 | Delta |")
    print("|-------|--------|-----------|-------|")
    for stage in STAGE_ORDER:
        l1_pct = 100 * l1_stages.get(stage, 0) / l1_total if l1_total > 0 else 0
        late_pct = 100 * late_stages.get(stage, 0) / late_stage_total if late_stage_total > 0 else 0
        print(f"| {stage:9} | {l1_pct:5.1f}% | {late_pct:8.1f}% | {late_pct - l1_pct:+5.1f}pp |")

    # Save results
    output = {
        'fl_rate_by_line': {
            line_ord: {
                'fl_count': data['fl'],
                'total': data['total'],
                'rate': data['fl'] / data['total'] if data['total'] > 0 else 0
            }
            for line_ord, data in line_fl_rate.items()
        },
        'fl_stages_by_line': {
            line_ord: dict(stages)
            for line_ord, stages in line_fl_counts.items()
        }
    }

    output_path = Path(__file__).parent.parent / "results" / "paragraph_fl_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
