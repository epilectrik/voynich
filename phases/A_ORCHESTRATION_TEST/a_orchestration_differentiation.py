"""
A-ORCHESTRATION DIFFERENTIATION TEST

Refined question: Does token position within A entries differentiate
which REGIMEs get used - even if not monotonically ordered?

Test: Kruskal-Wallis across positions - do different positions have
significantly different REGIME distributions?
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent

REGIME_ORDINAL = {
    'REGIME_2': 1,
    'REGIME_1': 2,
    'REGIME_4': 3,
    'REGIME_3': 4,
}


def load_data():
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''
                transcriber = parts[12].strip('"').strip()
                line_number = parts[11].strip('"') if len(parts) > 11 else ''
                if transcriber == 'H' and word and folio:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'currier': language,
                        'line_number': line_number
                    })
    return data


def load_regime_mapping():
    filepath = project_root / 'results' / 'regime_folio_mapping.json'
    with open(filepath, 'r') as f:
        regime_folios = json.load(f)
    folio_to_regime = {}
    for regime, folios in regime_folios.items():
        for folio in folios:
            folio_to_regime[folio] = regime
    return folio_to_regime


def main():
    print("=" * 70)
    print("A-ORCHESTRATION DIFFERENTIATION TEST")
    print("Do different positions map to different REGIME distributions?")
    print("=" * 70)

    data = load_data()
    folio_to_regime = load_regime_mapping()

    # Build A entries
    a_data = [d for d in data if d['currier'] == 'A']
    entries = defaultdict(list)
    for d in a_data:
        key = (d['folio'], d['line_number'])
        entries[key].append(d['token'])
    entries = {k: v for k, v in entries.items() if len(v) >= 3}

    # Build B vocab -> REGIME mapping
    b_data = [d for d in data if d['currier'] == 'B']
    token_to_regimes = defaultdict(list)
    for d in b_data:
        folio = d['folio']
        regime = folio_to_regime.get(folio)
        if regime:
            token_to_regimes[d['token']].append(regime)

    # Get REGIME distribution per position
    position_regimes = defaultdict(list)  # position -> list of REGIME ordinals
    position_regime_counts = defaultdict(Counter)  # position -> Counter of REGIMEs

    for (folio, line), tokens in entries.items():
        for pos, token in enumerate(tokens, 1):
            regimes = token_to_regimes.get(token, [])
            for regime in regimes:
                if regime in REGIME_ORDINAL:
                    position_regimes[pos].append(REGIME_ORDINAL[regime])
                    position_regime_counts[pos][regime] += 1

    # Kruskal-Wallis test: do positions differ?
    print("\n[1] Kruskal-Wallis test across positions 1-10:")
    groups = [position_regimes[p] for p in range(1, 11) if len(position_regimes[p]) > 10]

    if len(groups) >= 2:
        stat, p_value = stats.kruskal(*groups)
        print(f"    H-statistic: {stat:.4f}")
        print(f"    p-value: {p_value:.6f}")

        if p_value < 0.01:
            print("    -> Positions have SIGNIFICANTLY different distributions")
        else:
            print("    -> Positions do NOT have significantly different distributions")

    # Show REGIME distribution per position
    print("\n[2] REGIME distribution by position (positions 1-10):")
    print(f"    {'Pos':<5} {'R1':<8} {'R2':<8} {'R3':<8} {'R4':<8} {'Total':<8}")
    print("    " + "-" * 45)

    for pos in range(1, 11):
        counts = position_regime_counts[pos]
        total = sum(counts.values())
        if total > 0:
            r1 = counts.get('REGIME_1', 0)
            r2 = counts.get('REGIME_2', 0)
            r3 = counts.get('REGIME_3', 0)
            r4 = counts.get('REGIME_4', 0)
            print(f"    {pos:<5} {r1:<8} {r2:<8} {r3:<8} {r4:<8} {total:<8}")

    # Show percentages
    print("\n[3] REGIME distribution by position (percentages):")
    print(f"    {'Pos':<5} {'R1%':<8} {'R2%':<8} {'R3%':<8} {'R4%':<8}")
    print("    " + "-" * 40)

    for pos in range(1, 11):
        counts = position_regime_counts[pos]
        total = sum(counts.values())
        if total > 0:
            r1 = 100 * counts.get('REGIME_1', 0) / total
            r2 = 100 * counts.get('REGIME_2', 0) / total
            r3 = 100 * counts.get('REGIME_3', 0) / total
            r4 = 100 * counts.get('REGIME_4', 0) / total
            print(f"    {pos:<5} {r1:<8.1f} {r2:<8.1f} {r3:<8.1f} {r4:<8.1f}")

    # Chi-squared test on contingency table
    print("\n[4] Chi-squared test on position × REGIME contingency table:")

    # Build contingency table for positions 1-10
    contingency = []
    for pos in range(1, 11):
        counts = position_regime_counts[pos]
        row = [
            counts.get('REGIME_1', 0),
            counts.get('REGIME_2', 0),
            counts.get('REGIME_3', 0),
            counts.get('REGIME_4', 0)
        ]
        contingency.append(row)

    contingency = np.array(contingency)
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)

    print(f"    Chi-squared: {chi2:.4f}")
    print(f"    Degrees of freedom: {dof}")
    print(f"    p-value: {p_chi:.6f}")

    if p_chi < 0.01:
        print("    -> REGIME distribution DEPENDS on position")
    else:
        print("    -> REGIME distribution is INDEPENDENT of position")

    # Effect size (Cramer's V)
    n = contingency.sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim))
    print(f"    Cramer's V: {cramers_v:.4f}")

    if cramers_v < 0.1:
        print("    -> Effect size: NEGLIGIBLE")
    elif cramers_v < 0.3:
        print("    -> Effect size: SMALL")
    else:
        print("    -> Effect size: MODERATE or larger")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if p_chi >= 0.01:
        print("\n    Result: FALSIFIED")
        print("    Position does NOT differentiate REGIME usage")
    elif cramers_v < 0.1:
        print("\n    Result: FALSIFIED (negligible effect)")
        print("    Statistically significant but practically meaningless")
    else:
        print("\n    Result: POSSIBLE EFFECT")
        print(f"    Cramer's V = {cramers_v:.4f} suggests position may matter")


if __name__ == '__main__':
    main()
