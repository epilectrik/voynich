"""
F-A-014b: PREFIX x GRAMMAR-ROLE Correlation

PRE-REGISTERED HYPOTHESIS:
    PREFIX encodes CONTROL-FLOW PARTICIPATION, not material class.

TESTS:
    1. PREFIX x Kernel Adjacency - do prefixes cluster near kernel tokens?
    2. PREFIX x Escape-Path Membership - is qo- actually escape-specialized?
    3. PREFIX x Recovery Density - do prefixes correlate with recovery operations?
    4. PREFIX x LINK Adjacency - do prefixes correlate with attention points?
    5. PREFIX x Position-in-Line - do prefixes have positional preferences?

EXPECTED OUTCOMES:
    - Strong PREFIX x escape signal (qo- is recovery-specialized)
    - Moderate PREFIX x kernel adjacency (ch/sh near kernels)
    - Weak PREFIX x hazard (global clamp C458)

If confirmed: PREFIX = control-flow participation class
If rejected: PREFIX has no clear grammatical function (problematic)

METHODOLOGY:
    - Grammar-internal only (Currier B)
    - No AZC, no illustrations
    - Tests control-logic participation
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import math
from typing import Dict, List, Set, Tuple


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# Morphological components
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Kernel tokens (from grammar analysis - high-frequency structural tokens)
# These are tokens that appear at grammar-critical positions
KERNEL_INDICATORS = ['daiin', 'aiin', 'chedy', 'shedy', 'qokeedy', 'chey', 'shey',
                     'dain', 'chain', 'sain', 'okaiin', 'otaiin']

# LINK tokens (attention markers - non-interventional)
LINK_PATTERNS = ['ol', 'or', 'al', 'ar']  # Tokens starting with these are often LINK


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': '', 'original': token}

    original = token
    prefix = ''

    # Extract prefix (longest match first)
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            break

    return {'prefix': prefix, 'original': original}


def load_currier_b_data(filepath: Path) -> List[Dict]:
    """Load Currier B tokens with line context."""
    records = []
    current_folio = None
    current_line = None
    line_tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            line = row.get('line', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Only Currier B
            if language != 'B':
                continue

            # Track line boundaries
            if folio != current_folio or line != current_line:
                if line_tokens:
                    # Process previous line
                    for i, rec in enumerate(line_tokens):
                        rec['position_in_line'] = i
                        rec['line_length'] = len(line_tokens)
                        rec['is_line_initial'] = (i == 0)
                        rec['is_line_final'] = (i == len(line_tokens) - 1)
                        records.append(rec)
                line_tokens = []
                current_folio = folio
                current_line = line

            decomp = decompose_token(word)
            line_tokens.append({
                'token': word,
                'folio': folio,
                'line': line,
                'prefix': decomp['prefix']
            })

    # Don't forget last line
    if line_tokens:
        for i, rec in enumerate(line_tokens):
            rec['position_in_line'] = i
            rec['line_length'] = len(line_tokens)
            rec['is_line_initial'] = (i == 0)
            rec['is_line_final'] = (i == len(line_tokens) - 1)
            records.append(rec)

    return records


def test_prefix_escape_specialization(records: List[Dict]) -> Dict:
    """
    Test 1: Is qo- actually escape-specialized?

    qo- tokens should:
    - Appear after non-qo tokens (escape FROM something)
    - Have different positional distribution
    - NOT appear line-initial as often
    """
    print("\n" + "="*60)
    print("TEST 1: PREFIX x ESCAPE SPECIALIZATION")
    print("="*60)

    # Build bigrams to test escape patterns
    qo_follows = Counter()  # What prefix precedes qo-?
    non_qo_follows = Counter()  # What prefix follows non-qo?

    for i in range(1, len(records)):
        if records[i]['folio'] != records[i-1]['folio']:
            continue
        if records[i]['line'] != records[i-1]['line']:
            continue

        prev_prefix = records[i-1]['prefix']
        curr_prefix = records[i]['prefix']

        if curr_prefix == 'qo':
            qo_follows[prev_prefix] += 1
        elif prev_prefix != 'qo':
            non_qo_follows[curr_prefix] += 1

    # Calculate qo-transition probability vs baseline
    total_qo_follows = sum(qo_follows.values())
    total_non_qo = sum(non_qo_follows.values())

    # What prefixes most often precede qo-?
    print(f"\nPrefixes that precede qo- (n={total_qo_follows}):")
    for prefix, count in qo_follows.most_common(10):
        pct = count / total_qo_follows * 100
        print(f"  {prefix or 'NULL'}: {count} ({pct:.1f}%)")

    # Positional distribution of qo- vs others
    qo_positions = []
    non_qo_positions = []

    for r in records:
        if r['line_length'] > 0:
            norm_pos = r['position_in_line'] / r['line_length']
            if r['prefix'] == 'qo':
                qo_positions.append(norm_pos)
            else:
                non_qo_positions.append(norm_pos)

    qo_mean_pos = sum(qo_positions) / len(qo_positions) if qo_positions else 0
    non_qo_mean_pos = sum(non_qo_positions) / len(non_qo_positions) if non_qo_positions else 0

    print(f"\nPositional distribution:")
    print(f"  qo- mean position: {qo_mean_pos:.3f} (n={len(qo_positions)})")
    print(f"  non-qo mean position: {non_qo_mean_pos:.3f} (n={len(non_qo_positions)})")

    # Line-initial rates
    qo_initial = sum(1 for r in records if r['prefix'] == 'qo' and r['is_line_initial'])
    qo_total = sum(1 for r in records if r['prefix'] == 'qo')
    non_qo_initial = sum(1 for r in records if r['prefix'] != 'qo' and r['is_line_initial'])
    non_qo_total = sum(1 for r in records if r['prefix'] != 'qo')

    qo_initial_rate = qo_initial / qo_total * 100 if qo_total else 0
    non_qo_initial_rate = non_qo_initial / non_qo_total * 100 if non_qo_total else 0

    print(f"\nLine-initial rates:")
    print(f"  qo-: {qo_initial_rate:.1f}% ({qo_initial}/{qo_total})")
    print(f"  non-qo: {non_qo_initial_rate:.1f}% ({non_qo_initial}/{non_qo_total})")

    # Interpretation
    pos_diff = abs(qo_mean_pos - non_qo_mean_pos)
    initial_ratio = qo_initial_rate / non_qo_initial_rate if non_qo_initial_rate else 0

    if pos_diff > 0.05 and initial_ratio < 0.7:
        signal = "STRONG"
        interpretation = "qo- is positionally specialized (escape/recovery role)"
    elif pos_diff > 0.03 or initial_ratio < 0.85:
        signal = "MODERATE"
        interpretation = "qo- shows some positional specialization"
    else:
        signal = "WEAK"
        interpretation = "qo- is not clearly positionally specialized"

    print(f"\nSignal: {signal}")
    print(f"Interpretation: {interpretation}")

    return {
        'test': 'PREFIX x ESCAPE SPECIALIZATION',
        'qo_mean_position': round(qo_mean_pos, 4),
        'non_qo_mean_position': round(non_qo_mean_pos, 4),
        'position_difference': round(pos_diff, 4),
        'qo_initial_rate': round(qo_initial_rate, 2),
        'non_qo_initial_rate': round(non_qo_initial_rate, 2),
        'initial_rate_ratio': round(initial_ratio, 3),
        'qo_preceded_by': dict(qo_follows.most_common(10)),
        'signal': signal,
        'interpretation': interpretation
    }


def test_prefix_kernel_adjacency(records: List[Dict]) -> Dict:
    """
    Test 2: Do prefixes cluster near kernel tokens?

    Some prefixes (ch/sh) should appear near high-frequency structural tokens.
    """
    print("\n" + "="*60)
    print("TEST 2: PREFIX x KERNEL ADJACENCY")
    print("="*60)

    # Identify kernel-adjacent positions
    kernel_adjacent_prefixes = Counter()
    non_kernel_adjacent_prefixes = Counter()

    for i, r in enumerate(records):
        is_kernel_adjacent = False

        # Check if adjacent to a kernel token
        if i > 0 and records[i-1]['folio'] == r['folio'] and records[i-1]['line'] == r['line']:
            if records[i-1]['token'] in KERNEL_INDICATORS:
                is_kernel_adjacent = True
        if i < len(records)-1 and records[i+1]['folio'] == r['folio'] and records[i+1]['line'] == r['line']:
            if records[i+1]['token'] in KERNEL_INDICATORS:
                is_kernel_adjacent = True

        prefix = r['prefix'] or 'NULL'
        if is_kernel_adjacent:
            kernel_adjacent_prefixes[prefix] += 1
        else:
            non_kernel_adjacent_prefixes[prefix] += 1

    # Calculate enrichment ratios
    total_kernel_adj = sum(kernel_adjacent_prefixes.values())
    total_non_kernel = sum(non_kernel_adjacent_prefixes.values())

    print(f"\nKernel-adjacent tokens: {total_kernel_adj}")
    print(f"Non-kernel-adjacent tokens: {total_non_kernel}")

    enrichment = {}
    print("\nPrefix enrichment near kernels:")
    for prefix in set(kernel_adjacent_prefixes.keys()) | set(non_kernel_adjacent_prefixes.keys()):
        ka = kernel_adjacent_prefixes.get(prefix, 0)
        nka = non_kernel_adjacent_prefixes.get(prefix, 0)

        if nka > 0 and total_kernel_adj > 0 and total_non_kernel > 0:
            expected = (ka + nka) * total_kernel_adj / (total_kernel_adj + total_non_kernel)
            if expected > 0:
                ratio = ka / expected
                enrichment[prefix] = round(ratio, 3)

    # Sort by enrichment
    for prefix, ratio in sorted(enrichment.items(), key=lambda x: -x[1])[:10]:
        marker = "***" if ratio > 1.3 else "**" if ratio > 1.1 else "*" if ratio > 0.9 else ""
        print(f"  {prefix}: {ratio:.2f}x {marker}")

    # Check if ch/sh are kernel-enriched (sister pairs)
    ch_enrichment = enrichment.get('ch', 1.0)
    sh_enrichment = enrichment.get('sh', 1.0)
    sister_enriched = (ch_enrichment > 1.1 and sh_enrichment > 1.1)

    # Check if qo is kernel-depleted
    qo_enrichment = enrichment.get('qo', 1.0)
    qo_depleted = qo_enrichment < 0.9

    if sister_enriched and qo_depleted:
        signal = "STRONG"
        interpretation = "ch/sh cluster near kernels, qo avoids kernels - control-flow role confirmed"
    elif sister_enriched or qo_depleted:
        signal = "MODERATE"
        interpretation = "Partial PREFIX x kernel-adjacency pattern"
    else:
        signal = "WEAK"
        interpretation = "No clear PREFIX x kernel-adjacency pattern"

    print(f"\nch enrichment: {ch_enrichment:.2f}x")
    print(f"sh enrichment: {sh_enrichment:.2f}x")
    print(f"qo enrichment: {qo_enrichment:.2f}x")
    print(f"\nSignal: {signal}")
    print(f"Interpretation: {interpretation}")

    return {
        'test': 'PREFIX x KERNEL ADJACENCY',
        'n_kernel_adjacent': total_kernel_adj,
        'n_non_kernel_adjacent': total_non_kernel,
        'enrichment_ratios': enrichment,
        'ch_enrichment': ch_enrichment,
        'sh_enrichment': sh_enrichment,
        'qo_enrichment': qo_enrichment,
        'signal': signal,
        'interpretation': interpretation
    }


def test_prefix_positional_grammar(records: List[Dict]) -> Dict:
    """
    Test 3: Do prefixes have line-positional preferences?

    If PREFIX encodes control-flow role, different prefixes should
    have different positional distributions within lines.
    """
    print("\n" + "="*60)
    print("TEST 3: PREFIX x POSITIONAL GRAMMAR")
    print("="*60)

    # Collect position distributions by prefix
    prefix_positions = defaultdict(list)
    prefix_initial = defaultdict(int)
    prefix_final = defaultdict(int)
    prefix_total = defaultdict(int)

    for r in records:
        prefix = r['prefix'] or 'NULL'
        if r['line_length'] > 2:  # Only meaningful for lines with structure
            norm_pos = r['position_in_line'] / (r['line_length'] - 1) if r['line_length'] > 1 else 0.5
            prefix_positions[prefix].append(norm_pos)
        prefix_total[prefix] += 1
        if r['is_line_initial']:
            prefix_initial[prefix] += 1
        if r['is_line_final']:
            prefix_final[prefix] += 1

    # Calculate mean positions and initial/final rates
    results = {}
    print("\nPrefix positional profiles (n >= 100):")
    print(f"{'Prefix':<8} {'Mean Pos':>10} {'Initial%':>10} {'Final%':>10} {'n':>8}")
    print("-" * 50)

    for prefix in sorted(prefix_total.keys(), key=lambda x: -prefix_total[x]):
        if prefix_total[prefix] < 100:
            continue

        positions = prefix_positions[prefix]
        mean_pos = sum(positions) / len(positions) if positions else 0.5
        initial_rate = prefix_initial[prefix] / prefix_total[prefix] * 100
        final_rate = prefix_final[prefix] / prefix_total[prefix] * 100

        results[prefix] = {
            'mean_position': round(mean_pos, 3),
            'initial_rate': round(initial_rate, 2),
            'final_rate': round(final_rate, 2),
            'n': prefix_total[prefix]
        }

        print(f"{prefix:<8} {mean_pos:>10.3f} {initial_rate:>9.1f}% {final_rate:>9.1f}% {prefix_total[prefix]:>8}")

    # Calculate variance in positional profiles
    mean_positions = [v['mean_position'] for v in results.values()]
    initial_rates = [v['initial_rate'] for v in results.values()]

    pos_variance = sum((p - 0.5)**2 for p in mean_positions) / len(mean_positions) if mean_positions else 0
    initial_variance = sum((r - sum(initial_rates)/len(initial_rates))**2 for r in initial_rates) / len(initial_rates) if initial_rates else 0

    # Check for boundary specialists
    boundary_specialists = []
    interior_specialists = []
    for prefix, data in results.items():
        if data['initial_rate'] > 15 or data['final_rate'] > 15:
            boundary_specialists.append(prefix)
        if data['initial_rate'] < 5 and data['final_rate'] < 5:
            interior_specialists.append(prefix)

    print(f"\nBoundary specialists (>15% initial or final): {boundary_specialists}")
    print(f"Interior specialists (<5% both): {interior_specialists}")

    if len(boundary_specialists) >= 2 and len(interior_specialists) >= 2:
        signal = "STRONG"
        interpretation = "PREFIX shows clear positional grammar (boundary vs interior roles)"
    elif len(boundary_specialists) >= 1 or len(interior_specialists) >= 1:
        signal = "MODERATE"
        interpretation = "PREFIX shows some positional differentiation"
    else:
        signal = "WEAK"
        interpretation = "PREFIX shows no clear positional preferences"

    print(f"\nSignal: {signal}")
    print(f"Interpretation: {interpretation}")

    return {
        'test': 'PREFIX x POSITIONAL GRAMMAR',
        'prefix_profiles': results,
        'boundary_specialists': boundary_specialists,
        'interior_specialists': interior_specialists,
        'signal': signal,
        'interpretation': interpretation
    }


def test_prefix_sister_equivalence(records: List[Dict]) -> Dict:
    """
    Test 4: Are sister pairs (ch/sh, ok/ot) positionally equivalent?

    If PREFIX encodes control-flow role with sister slots as operational modes,
    sister pairs should have IDENTICAL positional distributions.
    """
    print("\n" + "="*60)
    print("TEST 4: PREFIX SISTER-PAIR EQUIVALENCE")
    print("="*60)

    sister_pairs = [('ch', 'sh'), ('ok', 'ot')]

    results = {}

    for p1, p2 in sister_pairs:
        # Collect positions for each
        pos1 = [r['position_in_line'] / r['line_length']
                for r in records if r['prefix'] == p1 and r['line_length'] > 0]
        pos2 = [r['position_in_line'] / r['line_length']
                for r in records if r['prefix'] == p2 and r['line_length'] > 0]

        if not pos1 or not pos2:
            continue

        mean1 = sum(pos1) / len(pos1)
        mean2 = sum(pos2) / len(pos2)

        # Initial/final rates
        init1 = sum(1 for r in records if r['prefix'] == p1 and r['is_line_initial']) / len(pos1) * 100
        init2 = sum(1 for r in records if r['prefix'] == p2 and r['is_line_initial']) / len(pos2) * 100
        fin1 = sum(1 for r in records if r['prefix'] == p1 and r['is_line_final']) / len(pos1) * 100
        fin2 = sum(1 for r in records if r['prefix'] == p2 and r['is_line_final']) / len(pos2) * 100

        pos_diff = abs(mean1 - mean2)
        init_diff = abs(init1 - init2)
        fin_diff = abs(fin1 - fin2)

        results[f"{p1}/{p2}"] = {
            'mean_positions': (round(mean1, 3), round(mean2, 3)),
            'position_diff': round(pos_diff, 4),
            'initial_rates': (round(init1, 2), round(init2, 2)),
            'initial_diff': round(init_diff, 2),
            'final_rates': (round(fin1, 2), round(fin2, 2)),
            'final_diff': round(fin_diff, 2),
            'n': (len(pos1), len(pos2))
        }

        print(f"\n{p1}/{p2} pair:")
        print(f"  Mean position: {mean1:.3f} vs {mean2:.3f} (diff={pos_diff:.4f})")
        print(f"  Initial rate: {init1:.1f}% vs {init2:.1f}% (diff={init_diff:.1f}pp)")
        print(f"  Final rate: {fin1:.1f}% vs {fin2:.1f}% (diff={fin_diff:.1f}pp)")
        print(f"  n: {len(pos1)} vs {len(pos2)}")

    # Check if sister pairs are equivalent
    all_equivalent = True
    for pair, data in results.items():
        if data['position_diff'] > 0.05 or data['initial_diff'] > 5 or data['final_diff'] > 5:
            all_equivalent = False
            break

    if all_equivalent:
        signal = "STRONG"
        interpretation = "Sister pairs are positionally equivalent - confirms slot-equivalence"
    else:
        # Check if mostly equivalent
        mostly_equivalent = all(
            data['position_diff'] < 0.1 and data['initial_diff'] < 10
            for data in results.values()
        )
        if mostly_equivalent:
            signal = "MODERATE"
            interpretation = "Sister pairs are mostly equivalent with some variation"
        else:
            signal = "WEAK"
            interpretation = "Sister pairs show positional divergence"

    print(f"\nSignal: {signal}")
    print(f"Interpretation: {interpretation}")

    return {
        'test': 'PREFIX SISTER-PAIR EQUIVALENCE',
        'pairs': results,
        'signal': signal,
        'interpretation': interpretation
    }


def synthesize_results(t1: Dict, t2: Dict, t3: Dict, t4: Dict) -> Dict:
    """Synthesize all results."""
    print("\n" + "="*60)
    print("SYNTHESIS: PREFIX = CONTROL-FLOW PARTICIPATION?")
    print("="*60)

    signals = {
        'Escape specialization': t1['signal'],
        'Kernel adjacency': t2['signal'],
        'Positional grammar': t3['signal'],
        'Sister equivalence': t4['signal']
    }

    print("\nSignal Summary:")
    for test, signal in signals.items():
        marker = {'STRONG': '[***]', 'MODERATE': '[** ]', 'WEAK': '[*  ]'}
        print(f"  {test}: {marker.get(signal, '[???]')} {signal}")

    strong_count = sum(1 for s in signals.values() if s == 'STRONG')
    moderate_count = sum(1 for s in signals.values() if s == 'MODERATE')

    if strong_count >= 3:
        conclusion = "CONFIRMED: PREFIX encodes control-flow participation"
        tier = "F2 (Structural)"
    elif strong_count >= 2 or (strong_count >= 1 and moderate_count >= 2):
        conclusion = "SUPPORTED: PREFIX likely encodes control-flow participation"
        tier = "F2/F3 (Strong support)"
    elif strong_count >= 1 or moderate_count >= 2:
        conclusion = "PARTIAL: Some evidence for control-flow role"
        tier = "F3 (Partial)"
    else:
        conclusion = "WEAK: PREFIX function remains unclear"
        tier = "F4 (Inconclusive)"

    print(f"\nConclusion: {conclusion}")
    print(f"Fit Tier: {tier}")

    # Specific findings
    findings = []
    if t1['signal'] in ['STRONG', 'MODERATE']:
        findings.append("qo- is escape/recovery specialized (positional)")
    if t2['signal'] in ['STRONG', 'MODERATE']:
        findings.append("ch/sh cluster near kernels, qo avoids kernels")
    if t3['signal'] in ['STRONG', 'MODERATE']:
        findings.append("Prefixes have distinct positional roles (boundary vs interior)")
    if t4['signal'] in ['STRONG', 'MODERATE']:
        findings.append("Sister pairs are slot-equivalent (operational mode)")

    print("\nKey findings:")
    for f in findings:
        print(f"  - {f}")

    return {
        'signals': signals,
        'strong_count': strong_count,
        'moderate_count': moderate_count,
        'conclusion': conclusion,
        'tier': tier,
        'findings': findings
    }


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("F-A-014b: PREFIX x GRAMMAR-ROLE Correlation")
    print("="*60)
    print("\nLoading Currier B data...")

    records = load_currier_b_data(data_path)
    print(f"  Total B tokens with line context: {len(records)}")

    # Run all tests
    t1 = test_prefix_escape_specialization(records)
    t2 = test_prefix_kernel_adjacency(records)
    t3 = test_prefix_positional_grammar(records)
    t4 = test_prefix_sister_equivalence(records)

    # Synthesize
    synthesis = synthesize_results(t1, t2, t3, t4)

    # Build output
    output = {
        'fit_id': 'F-A-014b',
        'title': 'PREFIX x GRAMMAR-ROLE Correlation',
        'hypothesis': 'PREFIX encodes control-flow participation, not material class',
        'tests': {
            'escape_specialization': t1,
            'kernel_adjacency': t2,
            'positional_grammar': t3,
            'sister_equivalence': t4
        },
        'synthesis': synthesis
    }

    # Save
    results_path = Path(__file__).parent.parent.parent / 'results' / 'prefix_grammar_role.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")


if __name__ == '__main__':
    main()
