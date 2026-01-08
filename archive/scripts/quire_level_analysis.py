"""
Phase QLA: Quire-Level Analysis

Investigates how structural boundaries (sections, Currier A/B, regimes)
align with physical quire boundaries.

Prior knowledge:
- Constraint 156: "Detected sections match codicology"
- Constraint 155: "Piecewise-sequential geometry (PC1 rho=-0.624)"
- 18 quires identified (A-T, missing P, R)
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import random

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
REGIME_FILE = BASE / "phases" / "OPS2_control_strategy_clustering" / "ops2_folio_cluster_assignments.json"

def load_data():
    """Load transcription and regime data."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)

    try:
        with open(REGIME_FILE, 'r') as f:
            regimes = json.load(f)['assignments']
    except:
        regimes = {}

    return data, regimes

def get_quire_structure(data):
    """Build quire -> folio -> tokens structure."""
    quire_data = defaultdict(lambda: defaultdict(list))

    for row in data:
        quire = row.get('quire', '')
        folio = row['folio']
        if quire and row.get('transcriber') == 'H':
            quire_data[quire][folio].append(row)

    return dict(quire_data)

def test_qla1_ab_segregation(data):
    """
    QLA-1: Do Currier A and B segregate into different quires?
    """
    print("\n" + "="*70)
    print("QLA-1: CURRIER A/B QUIRE SEGREGATION")
    print("="*70)
    print("\nQuestion: Do Currier A and B segregate into different quires?")

    # Count A/B tokens per quire
    quire_lang = defaultdict(lambda: {'A': 0, 'B': 0, 'NA': 0})

    for row in data:
        quire = row.get('quire', '')
        lang = row.get('language', 'NA')
        if quire and row.get('transcriber') == 'H':
            if lang in ['A', 'B']:
                quire_lang[quire][lang] += 1
            else:
                quire_lang[quire]['NA'] += 1

    # Calculate purity for each quire
    print("\nQuire composition (A/B tokens):")
    pure_a = 0
    pure_b = 0
    mixed = 0
    pure_na = 0

    quire_purities = []

    for q in sorted(quire_lang.keys()):
        counts = quire_lang[q]
        total_ab = counts['A'] + counts['B']
        total = total_ab + counts['NA']

        if total_ab == 0:
            purity = 1.0  # Pure NA (AZC)
            label = "PURE_AZC"
            pure_na += 1
        else:
            a_frac = counts['A'] / total_ab
            b_frac = counts['B'] / total_ab
            purity = max(a_frac, b_frac)

            if purity >= 0.95:
                if a_frac > b_frac:
                    label = "PURE_A"
                    pure_a += 1
                else:
                    label = "PURE_B"
                    pure_b += 1
            else:
                label = f"MIXED ({a_frac:.0%}A/{b_frac:.0%}B)"
                mixed += 1

        quire_purities.append(purity)
        print(f"  {q}: A={counts['A']:5}, B={counts['B']:5}, NA={counts['NA']:5} -> {label}")

    print(f"\nSummary:")
    print(f"  Pure A quires: {pure_a}")
    print(f"  Pure B quires: {pure_b}")
    print(f"  Pure AZC quires: {pure_na}")
    print(f"  Mixed quires: {mixed}")
    print(f"  Mean purity: {np.mean(quire_purities):.3f}")

    # Statistical test: compare observed mixing to random
    # Null: if A/B were randomly distributed across quires
    total_a = sum(quire_lang[q]['A'] for q in quire_lang)
    total_b = sum(quire_lang[q]['B'] for q in quire_lang)
    total_ab = total_a + total_b

    if total_ab > 0:
        expected_purity = max(total_a, total_b) / total_ab
        observed_purity = np.mean([p for p in quire_purities if p < 1.0])  # Exclude pure AZC

        print(f"\n  Expected purity (random): {expected_purity:.3f}")
        print(f"  Observed purity (A/B quires): {observed_purity:.3f}")

        ratio = observed_purity / expected_purity if expected_purity > 0 else 1

        if observed_purity > 0.9:
            verdict = "SIGNAL"
            interp = f"Strong A/B segregation by quire ({pure_a} pure A, {pure_b} pure B, {mixed} mixed)"
        elif mixed == 0:
            verdict = "SIGNAL"
            interp = "Complete A/B segregation - no mixed quires"
        else:
            verdict = "NULL"
            interp = f"Moderate mixing ({mixed} mixed quires)"
    else:
        verdict = "NULL"
        interp = "No A/B content"
        ratio = 1
        observed_purity = 0

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'QLA-1',
        'pure_a': pure_a,
        'pure_b': pure_b,
        'pure_na': pure_na,
        'mixed': mixed,
        'mean_purity': np.mean(quire_purities),
        'verdict': verdict
    }

def test_qla2_section_alignment(data):
    """
    QLA-2: Do manuscript sections align with quire boundaries?
    """
    print("\n" + "="*70)
    print("QLA-2: SECTION-QUIRE ALIGNMENT")
    print("="*70)
    print("\nQuestion: Do sections align with quire boundaries?")

    # Count sections per quire
    quire_sections = defaultdict(lambda: defaultdict(int))

    for row in data:
        quire = row.get('quire', '')
        section = row.get('section', '')
        if quire and section and row.get('transcriber') == 'H':
            quire_sections[quire][section] += 1

    # Calculate section homogeneity per quire
    print("\nQuire-section distribution:")
    homogeneities = []

    for q in sorted(quire_sections.keys()):
        sections = quire_sections[q]
        total = sum(sections.values())
        dominant = max(sections.values())
        homogeneity = dominant / total if total > 0 else 0
        homogeneities.append(homogeneity)

        section_str = ", ".join(f"{s}:{c}" for s, c in sorted(sections.items(), key=lambda x: -x[1]))
        n_sections = len(sections)
        print(f"  {q}: {n_sections} section(s), homogeneity={homogeneity:.2f} [{section_str}]")

    mean_homogeneity = np.mean(homogeneities)

    # How many quires have only 1 section?
    single_section = sum(1 for q in quire_sections if len(quire_sections[q]) == 1)
    multi_section = len(quire_sections) - single_section

    print(f"\nSummary:")
    print(f"  Single-section quires: {single_section}/{len(quire_sections)}")
    print(f"  Multi-section quires: {multi_section}/{len(quire_sections)}")
    print(f"  Mean homogeneity: {mean_homogeneity:.3f}")

    # Null model: random section assignment
    all_sections = []
    for row in data:
        if row.get('transcriber') == 'H' and row.get('section'):
            all_sections.append(row['section'])

    section_counts = Counter(all_sections)
    total_tokens = len(all_sections)

    # Expected homogeneity if random
    expected_hom = sum((c/total_tokens)**2 for c in section_counts.values())

    print(f"\n  Expected homogeneity (random): {expected_hom:.3f}")
    print(f"  Observed homogeneity: {mean_homogeneity:.3f}")

    ratio = mean_homogeneity / expected_hom if expected_hom > 0 else 1

    if mean_homogeneity > 0.9:
        verdict = "SIGNAL"
        interp = f"Strong section-quire alignment ({single_section} pure quires, {ratio:.1f}x random)"
    elif mean_homogeneity > 0.7:
        verdict = "SIGNAL"
        interp = f"Moderate section-quire alignment ({ratio:.1f}x random)"
    else:
        verdict = "NULL"
        interp = "Weak section-quire alignment"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'QLA-2',
        'single_section_quires': single_section,
        'multi_section_quires': multi_section,
        'mean_homogeneity': mean_homogeneity,
        'expected_homogeneity': expected_hom,
        'ratio': ratio,
        'verdict': verdict
    }

def test_qla3_regime_quire(data, regimes):
    """
    QLA-3: Do control regimes cluster within quires? (B only)
    """
    print("\n" + "="*70)
    print("QLA-3: REGIME-QUIRE ASSOCIATION (Currier B only)")
    print("="*70)
    print("\nQuestion: Do control regimes cluster within quires?")

    if not regimes:
        print("\nNo regime data available")
        return {'test': 'QLA-3', 'verdict': 'SKIP'}

    # Get quire -> folio mapping for B only
    quire_folios = defaultdict(list)
    folio_quire = {}

    for row in data:
        quire = row.get('quire', '')
        folio = row['folio']
        lang = row.get('language', '')
        if quire and lang == 'B' and row.get('transcriber') == 'H':
            if folio not in folio_quire:
                folio_quire[folio] = quire
                quire_folios[quire].append(folio)

    # Get regime for each B folio
    quire_regimes = defaultdict(list)
    for folio, quire in folio_quire.items():
        if folio in regimes:
            regime = regimes[folio].get('cluster_id', 'UNKNOWN')
            quire_regimes[quire].append(regime)

    print("\nQuire-regime distribution (Currier B folios):")

    homogeneities = []
    for q in sorted(quire_regimes.keys()):
        regime_list = quire_regimes[q]
        if not regime_list:
            continue
        regime_counts = Counter(regime_list)
        total = len(regime_list)
        dominant = max(regime_counts.values())
        homogeneity = dominant / total if total > 0 else 0
        homogeneities.append(homogeneity)

        regime_str = ", ".join(f"{r}:{c}" for r, c in sorted(regime_counts.items()))
        print(f"  {q}: {len(regime_list)} B folios, homogeneity={homogeneity:.2f} [{regime_str}]")

    if not homogeneities:
        print("\nNo B folios with regime data in quires")
        return {'test': 'QLA-3', 'verdict': 'SKIP'}

    mean_homogeneity = np.mean(homogeneities)

    # Compare within-quire vs between-quire regime similarity
    within_same = 0
    within_total = 0
    between_same = 0
    between_total = 0

    quires = list(quire_regimes.keys())
    for i, q1 in enumerate(quires):
        regimes1 = quire_regimes[q1]
        # Within-quire pairs
        for j in range(len(regimes1)):
            for k in range(j+1, len(regimes1)):
                within_total += 1
                if regimes1[j] == regimes1[k]:
                    within_same += 1

        # Between-quire pairs
        for q2 in quires[i+1:]:
            regimes2 = quire_regimes[q2]
            for r1 in regimes1:
                for r2 in regimes2:
                    between_total += 1
                    if r1 == r2:
                        between_same += 1

    within_rate = within_same / within_total if within_total > 0 else 0
    between_rate = between_same / between_total if between_total > 0 else 0

    print(f"\nWithin-quire same-regime rate: {within_rate:.3f} ({within_same}/{within_total})")
    print(f"Between-quire same-regime rate: {between_rate:.3f} ({between_same}/{between_total})")

    ratio = within_rate / between_rate if between_rate > 0 else 1

    if ratio > 1.5 and within_rate > between_rate:
        verdict = "SIGNAL"
        interp = f"Regimes cluster within quires ({ratio:.2f}x within/between)"
    else:
        verdict = "NULL"
        interp = f"No regime-quire clustering ({ratio:.2f}x)"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'QLA-3',
        'mean_homogeneity': mean_homogeneity,
        'within_rate': within_rate,
        'between_rate': between_rate,
        'ratio': ratio,
        'verdict': verdict
    }

def test_qla4_vocabulary_continuity(data):
    """
    QLA-4: Do folios within the same quire share more vocabulary?
    """
    print("\n" + "="*70)
    print("QLA-4: VOCABULARY CONTINUITY WITHIN QUIRES")
    print("="*70)
    print("\nQuestion: Do folios in the same quire share more vocabulary?")

    # Build folio -> vocabulary, folio -> quire
    folio_vocab = defaultdict(set)
    folio_quire = {}

    for row in data:
        quire = row.get('quire', '')
        folio = row['folio']
        word = row.get('word', '')
        if quire and word and row.get('transcriber') == 'H':
            folio_vocab[folio].add(word)
            folio_quire[folio] = quire

    # Calculate Jaccard similarity
    def jaccard(s1, s2):
        if not s1 or not s2:
            return 0
        return len(s1 & s2) / len(s1 | s2)

    # Within-quire vs between-quire similarity
    within_sims = []
    between_sims = []

    folios = list(folio_vocab.keys())

    for i, f1 in enumerate(folios):
        for f2 in folios[i+1:]:
            sim = jaccard(folio_vocab[f1], folio_vocab[f2])
            if folio_quire.get(f1) == folio_quire.get(f2):
                within_sims.append(sim)
            else:
                between_sims.append(sim)

    within_mean = np.mean(within_sims) if within_sims else 0
    between_mean = np.mean(between_sims) if between_sims else 0

    print(f"\nWithin-quire pairs: {len(within_sims)}")
    print(f"Between-quire pairs: {len(between_sims)}")
    print(f"\nWithin-quire mean Jaccard: {within_mean:.4f}")
    print(f"Between-quire mean Jaccard: {between_mean:.4f}")

    ratio = within_mean / between_mean if between_mean > 0 else 1
    print(f"Ratio: {ratio:.2f}x")

    # Statistical test
    if within_sims and between_sims:
        stat, p_value = stats.mannwhitneyu(within_sims, between_sims, alternative='greater')
        print(f"Mann-Whitney U p-value: {p_value:.6f}")
    else:
        p_value = 1

    if p_value < 0.001 and ratio > 1.2:
        verdict = "SIGNAL"
        interp = f"Within-quire vocabulary sharing {ratio:.2f}x higher (p<0.001)"
    elif p_value < 0.05:
        verdict = "SIGNAL"
        interp = f"Moderate within-quire vocabulary effect ({ratio:.2f}x, p={p_value:.4f})"
    else:
        verdict = "NULL"
        interp = f"No significant within-quire vocabulary effect"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'QLA-4',
        'within_pairs': len(within_sims),
        'between_pairs': len(between_sims),
        'within_mean': within_mean,
        'between_mean': between_mean,
        'ratio': ratio,
        'p_value': p_value,
        'verdict': verdict
    }

def test_qla5_boundary_discontinuity(data):
    """
    QLA-5: Are there structural discontinuities at quire boundaries?
    """
    print("\n" + "="*70)
    print("QLA-5: QUIRE BOUNDARY DISCONTINUITY")
    print("="*70)
    print("\nQuestion: Are there structural discontinuities at quire boundaries?")

    # Build ordered list of folios with quires
    folio_order = []
    folio_quire = {}
    folio_vocab = defaultdict(set)
    folio_section = {}
    folio_lang = {}

    seen_folios = set()
    for row in data:
        quire = row.get('quire', '')
        folio = row['folio']
        word = row.get('word', '')
        if quire and row.get('transcriber') == 'H':
            if folio not in seen_folios:
                folio_order.append(folio)
                seen_folios.add(folio)
            folio_quire[folio] = quire
            if word:
                folio_vocab[folio].add(word)
            folio_section[folio] = row.get('section', '')
            folio_lang[folio] = row.get('language', '')

    # Calculate Jaccard for adjacent pairs
    def jaccard(s1, s2):
        if not s1 or not s2:
            return 0
        return len(s1 & s2) / len(s1 | s2)

    within_quire_sims = []
    cross_quire_sims = []

    for i in range(len(folio_order) - 1):
        f1, f2 = folio_order[i], folio_order[i+1]
        sim = jaccard(folio_vocab[f1], folio_vocab[f2])

        if folio_quire.get(f1) == folio_quire.get(f2):
            within_quire_sims.append(sim)
        else:
            cross_quire_sims.append(sim)

    print(f"\nAdjacent pairs within quire: {len(within_quire_sims)}")
    print(f"Adjacent pairs crossing quire boundary: {len(cross_quire_sims)}")

    within_mean = np.mean(within_quire_sims) if within_quire_sims else 0
    cross_mean = np.mean(cross_quire_sims) if cross_quire_sims else 0

    print(f"\nWithin-quire adjacent mean Jaccard: {within_mean:.4f}")
    print(f"Cross-quire adjacent mean Jaccard: {cross_mean:.4f}")

    ratio = within_mean / cross_mean if cross_mean > 0 else 1
    print(f"Discontinuity ratio: {ratio:.2f}x")

    # Count section/language changes at boundaries
    quire_boundaries = 0
    section_changes_at_boundary = 0
    lang_changes_at_boundary = 0

    for i in range(len(folio_order) - 1):
        f1, f2 = folio_order[i], folio_order[i+1]
        if folio_quire.get(f1) != folio_quire.get(f2):
            quire_boundaries += 1
            if folio_section.get(f1) != folio_section.get(f2):
                section_changes_at_boundary += 1
            if folio_lang.get(f1) != folio_lang.get(f2):
                lang_changes_at_boundary += 1

    section_rate = section_changes_at_boundary / quire_boundaries if quire_boundaries > 0 else 0
    lang_rate = lang_changes_at_boundary / quire_boundaries if quire_boundaries > 0 else 0

    print(f"\nQuire boundaries: {quire_boundaries}")
    print(f"Section changes at boundaries: {section_changes_at_boundary} ({section_rate:.1%})")
    print(f"Language changes at boundaries: {lang_changes_at_boundary} ({lang_rate:.1%})")

    if ratio > 1.3 or section_rate > 0.5:
        verdict = "SIGNAL"
        interp = f"Discontinuity at quire boundaries (vocab {ratio:.2f}x, {section_rate:.0%} section changes)"
    else:
        verdict = "NULL"
        interp = "No significant discontinuity at quire boundaries"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'QLA-5',
        'within_mean': within_mean,
        'cross_mean': cross_mean,
        'ratio': ratio,
        'quire_boundaries': quire_boundaries,
        'section_change_rate': section_rate,
        'lang_change_rate': lang_rate,
        'verdict': verdict
    }

def main():
    print("="*70)
    print("PHASE QLA: QUIRE-LEVEL ANALYSIS")
    print("="*70)
    print("\nCore Question: How do structural boundaries align with physical quires?")

    data, regimes = load_data()

    print(f"\nLoaded {len(data)} tokens")

    # Run tests
    results = {}

    results['qla1'] = test_qla1_ab_segregation(data)
    results['qla2'] = test_qla2_section_alignment(data)
    results['qla3'] = test_qla3_regime_quire(data, regimes)
    results['qla4'] = test_qla4_vocabulary_continuity(data)
    results['qla5'] = test_qla5_boundary_discontinuity(data)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    signal_count = sum(1 for r in results.values() if r.get('verdict') == 'SIGNAL')
    null_count = sum(1 for r in results.values() if r.get('verdict') == 'NULL')
    skip_count = sum(1 for r in results.values() if r.get('verdict') == 'SKIP')

    print(f"\nResults: {signal_count} SIGNAL, {null_count} NULL, {skip_count} SKIP")

    print("\n| Test | Finding | Verdict |")
    print("|------|---------|---------|")

    for key, r in results.items():
        test_name = r.get('test', key)
        verdict = r.get('verdict', 'UNKNOWN')

        if key == 'qla1':
            finding = f"{r.get('pure_a',0)} pure A, {r.get('pure_b',0)} pure B, {r.get('mixed',0)} mixed"
        elif key == 'qla2':
            finding = f"Homogeneity {r.get('mean_homogeneity',0):.2f} ({r.get('ratio',1):.1f}x random)"
        elif key == 'qla3':
            if verdict == 'SKIP':
                finding = "No data"
            else:
                finding = f"Within/between ratio {r.get('ratio',1):.2f}x"
        elif key == 'qla4':
            finding = f"Within/between {r.get('ratio',1):.2f}x (p={r.get('p_value',1):.2e})"
        elif key == 'qla5':
            finding = f"Discontinuity {r.get('ratio',1):.2f}x, {r.get('section_change_rate',0):.0%} section changes"
        else:
            finding = "See details"

        print(f"| {test_name} | {finding} | **{verdict}** |")

    # Save results
    output_file = BASE / "archive" / "reports" / "quire_level_analysis.json"

    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    with open(output_file, 'w') as f:
        json.dump(convert(results), f, indent=2)

    print(f"\nResults saved to {output_file}")

if __name__ == '__main__':
    main()
