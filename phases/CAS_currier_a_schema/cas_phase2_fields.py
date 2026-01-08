"""
CAS Phase 2: Slot/Field Detection

Question: Are token positions constrained by role?

Tests:
1. Token position entropy (1st, 2nd, last)
2. Prefix/suffix exclusivity by position
3. Mutual exclusion patterns
4. Position-conditioned n-grams

Looking for: POSITIONAL INVARIANTS, not order invariants.

If order is flexible but position isn't, we have a SCHEMA, not grammar.
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent


def load_currier_a_data():
    """Load Currier A tokens with line-level granularity."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6
        section_idx = header.index('section') if 'section' in header else 3

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > lang_idx:
                lang = parts[lang_idx].strip('"').strip()
                if lang == 'A':
                    word = parts[word_idx].strip('"').strip().lower()
                    folio = parts[folio_idx].strip('"').strip() if len(parts) > folio_idx else ''
                    line_num = parts[line_idx].strip('"').strip() if len(parts) > line_idx else ''
                    section = parts[section_idx].strip('"').strip() if len(parts) > section_idx else ''

                    if word:
                        data.append({
                            'token': word,
                            'folio': folio,
                            'line': line_num,
                            'section': section,
                            'folio_line': f"{folio}_{line_num}"
                        })

    return data


def compute_entropy(counter, total):
    """Compute Shannon entropy from a counter."""
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / total
            entropy -= p * np.log2(p)
    return entropy


def test_position_entropy(data):
    """
    Test 1: Token position entropy

    Compare entropy at different positions.
    Low entropy = constrained position
    High entropy = free position
    """
    print("\n" + "=" * 70)
    print("TEST 1: POSITION ENTROPY")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Collect tokens by position (normalized to 0-4 for first 5 positions)
    position_tokens = defaultdict(list)

    for line_tokens in lines.values():
        n = len(line_tokens)
        if n >= 2:
            position_tokens['first'].append(line_tokens[0])
            position_tokens['last'].append(line_tokens[-1])

            if n >= 3:
                position_tokens['second'].append(line_tokens[1])
                position_tokens['penultimate'].append(line_tokens[-2])

            if n >= 5:
                position_tokens['middle'].append(line_tokens[n // 2])

    # Compute entropy for each position
    print(f"\nPosition entropy analysis:")
    print(f"{'Position':<15} {'Count':<10} {'Unique':<10} {'Entropy':<10} {'Concentration':<12}")
    print("-" * 60)

    entropies = {}
    concentrations = {}

    for pos in ['first', 'second', 'middle', 'penultimate', 'last']:
        if position_tokens[pos]:
            counter = Counter(position_tokens[pos])
            total = len(position_tokens[pos])
            unique = len(counter)
            entropy = compute_entropy(counter, total)
            # Top-5 concentration
            top5 = sum(c for _, c in counter.most_common(5)) / total

            entropies[pos] = entropy
            concentrations[pos] = top5

            print(f"{pos:<15} {total:<10} {unique:<10} {entropy:<10.3f} {top5:<12.3f}")

    # Entropy comparison
    print(f"\nEntropy comparison:")
    if 'first' in entropies and 'middle' in entropies:
        ratio = entropies['first'] / entropies['middle'] if entropies['middle'] > 0 else float('inf')
        print(f"  First/Middle ratio: {ratio:.3f}")
        if ratio < 0.9:
            print("  -> First position is MORE CONSTRAINED than middle")
        elif ratio > 1.1:
            print("  -> First position is LESS CONSTRAINED than middle")
        else:
            print("  -> First and middle positions have SIMILAR entropy")

    if 'last' in entropies and 'middle' in entropies:
        ratio = entropies['last'] / entropies['middle'] if entropies['middle'] > 0 else float('inf')
        print(f"  Last/Middle ratio: {ratio:.3f}")
        if ratio < 0.9:
            print("  -> Last position is MORE CONSTRAINED than middle")

    return {
        'entropies': entropies,
        'concentrations': concentrations
    }


def test_prefix_position_binding(data):
    """
    Test 2: Prefix exclusivity by position

    Do certain prefixes only appear in certain positions?
    """
    print("\n" + "=" * 70)
    print("TEST 2: PREFIX-POSITION BINDING")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Extract prefixes by position
    # Use 2-character prefixes
    position_prefixes = defaultdict(lambda: defaultdict(int))

    for line_tokens in lines.values():
        n = len(line_tokens)
        if n >= 2:
            for pos, idx in [('first', 0), ('last', -1)]:
                token = line_tokens[idx]
                if len(token) >= 2:
                    prefix = token[:2]
                    position_prefixes[pos][prefix] += 1

            if n >= 3:
                for idx in range(1, n - 1):
                    token = line_tokens[idx]
                    if len(token) >= 2:
                        prefix = token[:2]
                        position_prefixes['middle'][prefix] += 1

    # Find position-exclusive prefixes
    all_prefixes = set()
    for pos_dict in position_prefixes.values():
        all_prefixes.update(pos_dict.keys())

    print(f"\nTotal unique prefixes: {len(all_prefixes)}")

    # Calculate position preference for each prefix
    print(f"\nTop 10 FIRST-preferring prefixes:")
    first_pref = []
    for prefix in all_prefixes:
        first_count = position_prefixes['first'].get(prefix, 0)
        middle_count = position_prefixes['middle'].get(prefix, 0)
        last_count = position_prefixes['last'].get(prefix, 0)
        total = first_count + middle_count + last_count

        if total >= 10:
            first_ratio = first_count / total
            first_pref.append((prefix, first_ratio, first_count, total))

    first_pref.sort(key=lambda x: x[1], reverse=True)
    for prefix, ratio, count, total in first_pref[:10]:
        print(f"  {prefix}: {ratio:.2f} first ({count}/{total})")

    print(f"\nTop 10 LAST-preferring prefixes:")
    last_pref = []
    for prefix in all_prefixes:
        first_count = position_prefixes['first'].get(prefix, 0)
        middle_count = position_prefixes['middle'].get(prefix, 0)
        last_count = position_prefixes['last'].get(prefix, 0)
        total = first_count + middle_count + last_count

        if total >= 10:
            last_ratio = last_count / total
            last_pref.append((prefix, last_ratio, last_count, total))

    last_pref.sort(key=lambda x: x[1], reverse=True)
    for prefix, ratio, count, total in last_pref[:10]:
        print(f"  {prefix}: {ratio:.2f} last ({count}/{total})")

    # Statistical test: Chi-square for position independence
    print(f"\nChi-square test for position-prefix independence:")
    # Build contingency table for top 20 prefixes
    top_prefixes = [p for p, _, _, t in first_pref[:20] if t >= 20]

    if len(top_prefixes) >= 5:
        observed = []
        for prefix in top_prefixes:
            row = [
                position_prefixes['first'].get(prefix, 0),
                position_prefixes['middle'].get(prefix, 0),
                position_prefixes['last'].get(prefix, 0)
            ]
            observed.append(row)

        observed = np.array(observed)
        chi2, p, dof, expected = sp_stats.chi2_contingency(observed)
        print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p:.6f}")

        if p < 0.01:
            print("  -> STRONG PREFIX-POSITION BINDING (positions are NOT independent)")
        elif p < 0.05:
            print("  -> MODERATE prefix-position binding")
        else:
            print("  -> NO SIGNIFICANT prefix-position binding")

    return {
        'first_preferring': first_pref[:10],
        'last_preferring': last_pref[:10]
    }


def test_suffix_position_binding(data):
    """
    Test 3: Suffix exclusivity by position

    Do certain suffixes only appear in certain positions?
    """
    print("\n" + "=" * 70)
    print("TEST 3: SUFFIX-POSITION BINDING")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Extract suffixes by position
    position_suffixes = defaultdict(lambda: defaultdict(int))

    for line_tokens in lines.values():
        n = len(line_tokens)
        if n >= 2:
            for pos, idx in [('first', 0), ('last', -1)]:
                token = line_tokens[idx]
                if len(token) >= 3:
                    suffix = token[-3:]
                    position_suffixes[pos][suffix] += 1

            if n >= 3:
                for idx in range(1, n - 1):
                    token = line_tokens[idx]
                    if len(token) >= 3:
                        suffix = token[-3:]
                        position_suffixes['middle'][suffix] += 1

    # Find position preference
    all_suffixes = set()
    for pos_dict in position_suffixes.values():
        all_suffixes.update(pos_dict.keys())

    print(f"\nTotal unique suffixes (3-char): {len(all_suffixes)}")

    # Calculate position preference
    print(f"\nTop 10 FIRST-preferring suffixes:")
    first_pref = []
    for suffix in all_suffixes:
        first_count = position_suffixes['first'].get(suffix, 0)
        middle_count = position_suffixes['middle'].get(suffix, 0)
        last_count = position_suffixes['last'].get(suffix, 0)
        total = first_count + middle_count + last_count

        if total >= 10:
            first_ratio = first_count / total
            first_pref.append((suffix, first_ratio, first_count, total))

    first_pref.sort(key=lambda x: x[1], reverse=True)
    for suffix, ratio, count, total in first_pref[:10]:
        print(f"  {suffix}: {ratio:.2f} first ({count}/{total})")

    print(f"\nTop 10 LAST-preferring suffixes:")
    last_pref = []
    for suffix in all_suffixes:
        first_count = position_suffixes['first'].get(suffix, 0)
        middle_count = position_suffixes['middle'].get(suffix, 0)
        last_count = position_suffixes['last'].get(suffix, 0)
        total = first_count + middle_count + last_count

        if total >= 10:
            last_ratio = last_count / total
            last_pref.append((suffix, last_ratio, last_count, total))

    last_pref.sort(key=lambda x: x[1], reverse=True)
    for suffix, ratio, count, total in last_pref[:10]:
        print(f"  {suffix}: {ratio:.2f} last ({count}/{total})")

    # Chi-square test
    print(f"\nChi-square test for position-suffix independence:")
    top_suffixes = [s for s, _, _, t in first_pref[:20] if t >= 20]

    if len(top_suffixes) >= 5:
        observed = []
        for suffix in top_suffixes:
            row = [
                position_suffixes['first'].get(suffix, 0),
                position_suffixes['middle'].get(suffix, 0),
                position_suffixes['last'].get(suffix, 0)
            ]
            observed.append(row)

        observed = np.array(observed)
        chi2, p, dof, expected = sp_stats.chi2_contingency(observed)
        print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p:.6f}")

        if p < 0.01:
            print("  -> STRONG SUFFIX-POSITION BINDING (positions are NOT independent)")
        elif p < 0.05:
            print("  -> MODERATE suffix-position binding")
        else:
            print("  -> NO SIGNIFICANT suffix-position binding")

    return {
        'first_preferring': first_pref[:10],
        'last_preferring': last_pref[:10]
    }


def test_mutual_exclusion(data):
    """
    Test 4: Mutual exclusion patterns

    Do certain tokens/prefixes never co-occur in the same entry?
    """
    print("\n" + "=" * 70)
    print("TEST 4: MUTUAL EXCLUSION PATTERNS")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Get top prefixes
    all_prefixes = Counter()
    for line_tokens in lines.values():
        for token in line_tokens:
            if len(token) >= 2:
                all_prefixes[token[:2]] += 1

    top_prefixes = [p for p, _ in all_prefixes.most_common(20)]

    # Build co-occurrence matrix
    cooccurrence = defaultdict(lambda: defaultdict(int))
    prefix_totals = defaultdict(int)

    for line_tokens in lines.values():
        line_prefixes = set()
        for token in line_tokens:
            if len(token) >= 2:
                line_prefixes.add(token[:2])

        for p in line_prefixes:
            prefix_totals[p] += 1
            for q in line_prefixes:
                if p <= q:  # Avoid double counting
                    cooccurrence[p][q] += 1

    print(f"\nCo-occurrence analysis (top 10 prefixes):")
    print(f"\nExpected vs Observed co-occurrence:")

    # Calculate expected (if independent)
    total_lines = len(lines)
    exclusion_pairs = []

    for i, p1 in enumerate(top_prefixes[:10]):
        for p2 in top_prefixes[i+1:10]:
            p1_prob = prefix_totals[p1] / total_lines
            p2_prob = prefix_totals[p2] / total_lines
            expected = p1_prob * p2_prob * total_lines

            observed = cooccurrence[min(p1, p2)][max(p1, p2)]

            ratio = observed / expected if expected > 0 else float('inf')

            if ratio < 0.3 and expected > 5:
                exclusion_pairs.append((p1, p2, observed, expected, ratio))

    if exclusion_pairs:
        print(f"\nPotential MUTUALLY EXCLUSIVE prefix pairs:")
        for p1, p2, obs, exp, ratio in sorted(exclusion_pairs, key=lambda x: x[4])[:10]:
            print(f"  {p1} / {p2}: observed={obs}, expected={exp:.1f}, ratio={ratio:.3f}")
    else:
        print(f"\nNo strong mutual exclusion patterns detected")

    # Also check for high co-occurrence (always together)
    association_pairs = []
    for i, p1 in enumerate(top_prefixes[:10]):
        for p2 in top_prefixes[i+1:10]:
            p1_prob = prefix_totals[p1] / total_lines
            p2_prob = prefix_totals[p2] / total_lines
            expected = p1_prob * p2_prob * total_lines

            observed = cooccurrence[min(p1, p2)][max(p1, p2)]

            ratio = observed / expected if expected > 0 else 0

            if ratio > 2.0 and observed > 10:
                association_pairs.append((p1, p2, observed, expected, ratio))

    if association_pairs:
        print(f"\nStrong POSITIVE ASSOCIATION pairs:")
        for p1, p2, obs, exp, ratio in sorted(association_pairs, key=lambda x: -x[4])[:10]:
            print(f"  {p1} + {p2}: observed={obs}, expected={exp:.1f}, ratio={ratio:.2f}x")
    else:
        print(f"\nNo strong positive associations detected")

    return {
        'exclusion_pairs': exclusion_pairs,
        'association_pairs': association_pairs
    }


def test_field_structure(data):
    """
    Test 5: Field structure detection

    Do multi-token entries show consistent field patterns?
    """
    print("\n" + "=" * 70)
    print("TEST 5: FIELD STRUCTURE DETECTION")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Analyze 3-token lines (simplest multi-field case)
    three_token_lines = [v for v in lines.values() if len(v) == 3]

    print(f"\n3-token lines (simplest multi-field): {len(three_token_lines)}")

    if len(three_token_lines) < 50:
        print("  Insufficient data for field analysis")
        return {}

    # Extract position-specific patterns
    pos1_prefixes = Counter()
    pos2_prefixes = Counter()
    pos3_prefixes = Counter()

    for tokens in three_token_lines:
        for i, token in enumerate(tokens):
            if len(token) >= 2:
                prefix = token[:2]
                if i == 0:
                    pos1_prefixes[prefix] += 1
                elif i == 1:
                    pos2_prefixes[prefix] += 1
                else:
                    pos3_prefixes[prefix] += 1

    # Entropy by position
    n = len(three_token_lines)
    e1 = compute_entropy(pos1_prefixes, n)
    e2 = compute_entropy(pos2_prefixes, n)
    e3 = compute_entropy(pos3_prefixes, n)

    print(f"\nEntropy by position in 3-token lines:")
    print(f"  Position 1: {e1:.3f} bits")
    print(f"  Position 2: {e2:.3f} bits")
    print(f"  Position 3: {e3:.3f} bits")

    # Top prefixes by position
    print(f"\nTop 5 prefixes by position:")
    print(f"  Pos 1: {pos1_prefixes.most_common(5)}")
    print(f"  Pos 2: {pos2_prefixes.most_common(5)}")
    print(f"  Pos 3: {pos3_prefixes.most_common(5)}")

    # Field discrimination test
    # Are positions distinguishable by their prefix distributions?
    pos1_vec = np.array([pos1_prefixes.get(p, 0) for p in set(pos1_prefixes) | set(pos2_prefixes) | set(pos3_prefixes)])
    pos2_vec = np.array([pos2_prefixes.get(p, 0) for p in set(pos1_prefixes) | set(pos2_prefixes) | set(pos3_prefixes)])
    pos3_vec = np.array([pos3_prefixes.get(p, 0) for p in set(pos1_prefixes) | set(pos2_prefixes) | set(pos3_prefixes)])

    # Normalize
    pos1_vec = pos1_vec / (pos1_vec.sum() + 1e-10)
    pos2_vec = pos2_vec / (pos2_vec.sum() + 1e-10)
    pos3_vec = pos3_vec / (pos3_vec.sum() + 1e-10)

    # Jensen-Shannon divergence
    from scipy.spatial.distance import jensenshannon

    js_12 = jensenshannon(pos1_vec, pos2_vec)
    js_13 = jensenshannon(pos1_vec, pos3_vec)
    js_23 = jensenshannon(pos2_vec, pos3_vec)

    print(f"\nJensen-Shannon divergence between positions:")
    print(f"  Pos1 vs Pos2: {js_12:.4f}")
    print(f"  Pos1 vs Pos3: {js_13:.4f}")
    print(f"  Pos2 vs Pos3: {js_23:.4f}")

    mean_js = (js_12 + js_13 + js_23) / 3

    if mean_js > 0.3:
        print(f"\n  -> STRONG FIELD DIFFERENTIATION (positions have distinct distributions)")
    elif mean_js > 0.15:
        print(f"\n  -> MODERATE field differentiation")
    else:
        print(f"\n  -> WEAK field differentiation (positions look similar)")

    return {
        'entropy_pos1': e1,
        'entropy_pos2': e2,
        'entropy_pos3': e3,
        'js_12': js_12,
        'js_13': js_13,
        'js_23': js_23,
        'mean_js': mean_js
    }


def synthesize_fields(results):
    """Synthesize field detection results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: FIELD STRUCTURE DETERMINATION")
    print("=" * 70)

    scores = {
        'FIELD_STRUCTURED': 0,
        'POSITION_FREE': 0
    }

    # Test 1: Position entropy
    if 'entropies' in results['entropy']:
        entropies = results['entropy']['entropies']
        if 'first' in entropies and 'middle' in entropies:
            if entropies['first'] < entropies['middle'] * 0.9:
                scores['FIELD_STRUCTURED'] += 1
                print("[+] First position has lower entropy -> FIELD_STRUCTURED")
            else:
                scores['POSITION_FREE'] += 1
                print("[-] First position has similar entropy to middle -> POSITION_FREE")

    # Test 2-3: Prefix/suffix binding (check if chi-square showed dependence)
    # We'll use the presence of position-preferring morphemes
    if results['prefix']:
        top_first = results['prefix'].get('first_preferring', [])
        if top_first and top_first[0][1] > 0.5:  # >50% first-preferring
            scores['FIELD_STRUCTURED'] += 1
            print(f"[+] Strong first-preferring prefix ({top_first[0][0]}={top_first[0][1]:.2f}) -> FIELD_STRUCTURED")

    if results['suffix']:
        top_last = results['suffix'].get('last_preferring', [])
        if top_last and top_last[0][1] > 0.5:
            scores['FIELD_STRUCTURED'] += 1
            print(f"[+] Strong last-preferring suffix ({top_last[0][0]}={top_last[0][1]:.2f}) -> FIELD_STRUCTURED")

    # Test 4: Mutual exclusion
    if results['exclusion'].get('exclusion_pairs'):
        scores['FIELD_STRUCTURED'] += 1
        print("[+] Mutual exclusion pairs detected -> FIELD_STRUCTURED")

    # Test 5: Field structure
    if results['fields'].get('mean_js', 0) > 0.2:
        scores['FIELD_STRUCTURED'] += 1
        print(f"[+] High JS divergence between positions ({results['fields']['mean_js']:.3f}) -> FIELD_STRUCTURED")

    print(f"\nScores: FIELD_STRUCTURED={scores['FIELD_STRUCTURED']}, POSITION_FREE={scores['POSITION_FREE']}")

    if scores['FIELD_STRUCTURED'] >= 3:
        verdict = 'FIELD_STRUCTURED'
        interpretation = "Currier A shows positional constraints. Entries have distinct field slots."
    elif scores['FIELD_STRUCTURED'] >= 2:
        verdict = 'WEAKLY_STRUCTURED'
        interpretation = "Currier A shows some positional patterns but weak field boundaries."
    else:
        verdict = 'POSITION_FREE'
        interpretation = "Currier A does not show clear positional constraints. Tokens appear freely across positions."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(f"\n{interpretation}")

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 2: SLOT/FIELD DETECTION")
    print("=" * 70)
    print("\nQuestion: Are token positions constrained by role?")

    data = load_currier_a_data()
    print(f"\nLoaded {len(data)} Currier A tokens")

    results = {
        'entropy': test_position_entropy(data),
        'prefix': test_prefix_position_binding(data),
        'suffix': test_suffix_position_binding(data),
        'exclusion': test_mutual_exclusion(data),
        'fields': test_field_structure(data)
    }

    verdict, interpretation = synthesize_fields(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase2_results.json'

    # Convert tuples to lists for JSON
    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
