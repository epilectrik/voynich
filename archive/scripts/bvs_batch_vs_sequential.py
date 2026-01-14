"""
Phase BvS: Batch vs Sequential Processing Test

Research Question: Do multiple items in a Currier A line get processed
together (batch) or separately (sequential)?

Test Logic:
- If BATCH: B procedure structure should be INVARIANT to A line length
- If SEQUENTIAL: B procedure structure should SCALE with A line length

Thresholds (per expert guidance):
- p < 0.01: REJECT batch model
- p > 0.10: SUPPORT batch model
- 0.01-0.10: INCONCLUSIVE

Tests:
1. A line length vs B line length
2. A line length vs B transition entropy
3. A line length vs B instruction class diversity
4. Within-folio control
"""

import csv
import json
import math
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT = BASE / "results" / "bvs_batch_vs_sequential.json"


def load_transcription_data():
    """Load all token data with line information."""
    a_lines = defaultdict(list)  # (folio, line_num) -> [tokens]
    b_lines = defaultdict(list)  # (folio, line_num) -> [tokens]
    a_folio_tokens = defaultdict(set)  # folio -> set of tokens
    b_folio_tokens = defaultdict(set)  # folio -> set of tokens
    token_a_folios = defaultdict(set)  # token -> set of A folios
    token_b_folios = defaultdict(set)  # token -> set of B folios

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            lang = row.get('language', '')
            line_num = row.get('line_number', '0')

            try:
                line_num = int(line_num)
            except:
                line_num = 0

            if lang == 'A':
                a_lines[(folio, line_num)].append(token)
                a_folio_tokens[folio].add(token)
                token_a_folios[token].add(folio)
            elif lang == 'B':
                b_lines[(folio, line_num)].append(token)
                b_folio_tokens[folio].add(token)
                token_b_folios[token].add(folio)

    return a_lines, b_lines, a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios


def compute_a_line_lengths(a_lines):
    """Compute length statistics for A lines."""
    lengths = []
    for (folio, line_num), tokens in a_lines.items():
        lengths.append({
            'folio': folio,
            'line_num': line_num,
            'length': len(tokens),
            'tokens': tokens
        })
    return lengths


def categorize_a_lines(a_line_lengths):
    """Categorize A lines into SHORT/MEDIUM/LONG."""
    categories = {'SHORT': [], 'MEDIUM': [], 'LONG': []}

    for entry in a_line_lengths:
        length = entry['length']
        if length <= 3:
            categories['SHORT'].append(entry)
        elif length <= 7:
            categories['MEDIUM'].append(entry)
        else:
            categories['LONG'].append(entry)

    return categories


def build_a_b_mapping(a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios):
    """Build A-to-B folio mapping via rare token overlap."""
    # Identify rare shared tokens (<=3 A folios, <=5 B folios)
    all_a_tokens = set(token_a_folios.keys())
    all_b_tokens = set(token_b_folios.keys())
    shared_tokens = all_a_tokens & all_b_tokens

    rare_tokens = set()
    for token in shared_tokens:
        if len(token_a_folios[token]) <= 3 and len(token_b_folios[token]) <= 5:
            rare_tokens.add(token)

    # Build overlap counts
    a_b_overlap = defaultdict(Counter)
    for token in rare_tokens:
        a_fols = token_a_folios[token]
        b_fols = token_b_folios[token]
        for a_f in a_fols:
            for b_f in b_fols:
                a_b_overlap[a_f][b_f] += 1

    return a_b_overlap, len(rare_tokens)


def compute_b_metrics(b_lines, b_folios):
    """Compute B metrics for a set of B folios."""
    if not b_folios:
        return None

    # Filter B lines to only those in the target folios
    relevant_lines = [(k, v) for k, v in b_lines.items() if k[0] in b_folios]

    if not relevant_lines:
        return None

    # Metric 1: Line lengths
    line_lengths = [len(tokens) for _, tokens in relevant_lines]

    # Metric 2: Transition entropy (bigram entropy)
    all_tokens = []
    for _, tokens in relevant_lines:
        all_tokens.extend(tokens)

    if len(all_tokens) < 2:
        bigram_entropy = 0
    else:
        bigrams = [(all_tokens[i], all_tokens[i+1]) for i in range(len(all_tokens)-1)]
        bigram_counts = Counter(bigrams)
        total = sum(bigram_counts.values())
        probs = [c/total for c in bigram_counts.values()]
        bigram_entropy = -sum(p * math.log2(p) for p in probs if p > 0)

    # Metric 3: Token type diversity (proxy for class diversity)
    unique_types = set(all_tokens)
    type_token_ratio = len(unique_types) / len(all_tokens) if all_tokens else 0

    return {
        'n_lines': len(relevant_lines),
        'n_tokens': len(all_tokens),
        'mean_line_length': np.mean(line_lengths) if line_lengths else 0,
        'std_line_length': np.std(line_lengths) if line_lengths else 0,
        'bigram_entropy': bigram_entropy,
        'unique_types': len(unique_types),
        'type_token_ratio': type_token_ratio
    }


def get_associated_b_folios(a_folios, a_b_overlap, min_overlap=1):
    """Get B folios associated with a set of A folios."""
    b_folios = set()
    total_overlap = 0

    for a_f in a_folios:
        if a_f in a_b_overlap:
            for b_f, count in a_b_overlap[a_f].items():
                if count >= min_overlap:
                    b_folios.add(b_f)
                    total_overlap += count

    return b_folios, total_overlap


def run_test_1(categories, a_b_overlap, b_lines):
    """Test 1: A line length vs B line length."""
    print("\n" + "="*70)
    print("TEST 1: A LINE LENGTH VS B LINE LENGTH")
    print("="*70)

    category_metrics = {}
    category_b_lengths = {}

    for cat_name, entries in categories.items():
        # Get A folios in this category
        a_folios = set(e['folio'] for e in entries)

        # Get associated B folios
        b_folios, overlap = get_associated_b_folios(a_folios, a_b_overlap)

        # Compute B metrics
        metrics = compute_b_metrics(b_lines, b_folios)

        if metrics:
            category_metrics[cat_name] = metrics
            # Get individual B line lengths for statistical test
            relevant_lines = [(k, v) for k, v in b_lines.items() if k[0] in b_folios]
            category_b_lengths[cat_name] = [len(tokens) for _, tokens in relevant_lines]

        print(f"\n{cat_name} A lines ({len(entries)} lines, {len(a_folios)} folios):")
        print(f"  Associated B folios: {len(b_folios)}")
        print(f"  Rare token overlap: {overlap}")
        if metrics:
            print(f"  B mean line length: {metrics['mean_line_length']:.2f} ± {metrics['std_line_length']:.2f}")

    # Statistical test: Kruskal-Wallis across categories
    if len(category_b_lengths) >= 2:
        groups = [category_b_lengths[c] for c in ['SHORT', 'MEDIUM', 'LONG'] if c in category_b_lengths]
        if all(len(g) > 0 for g in groups):
            stat, p_value = stats.kruskal(*groups)
            print(f"\nKruskal-Wallis test: H={stat:.3f}, p={p_value:.4f}")

            return {
                'test': 'A line length vs B line length',
                'metrics': category_metrics,
                'kruskal_wallis_H': stat,
                'p_value': p_value,
                'interpretation': interpret_p_value(p_value)
            }

    return {'test': 'A line length vs B line length', 'metrics': category_metrics, 'error': 'insufficient data'}


def run_test_2(categories, a_b_overlap, b_lines):
    """Test 2: A line length vs B transition entropy."""
    print("\n" + "="*70)
    print("TEST 2: A LINE LENGTH VS B TRANSITION ENTROPY")
    print("="*70)

    category_entropies = {}

    for cat_name, entries in categories.items():
        a_folios = set(e['folio'] for e in entries)
        b_folios, _ = get_associated_b_folios(a_folios, a_b_overlap)

        # Compute entropy per B folio
        folio_entropies = []
        for b_f in b_folios:
            folio_lines = [(k, v) for k, v in b_lines.items() if k[0] == b_f]
            tokens = []
            for _, toks in folio_lines:
                tokens.extend(toks)

            if len(tokens) >= 2:
                bigrams = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
                bigram_counts = Counter(bigrams)
                total = sum(bigram_counts.values())
                probs = [c/total for c in bigram_counts.values()]
                entropy = -sum(p * math.log2(p) for p in probs if p > 0)
                folio_entropies.append(entropy)

        if folio_entropies:
            category_entropies[cat_name] = folio_entropies
            print(f"\n{cat_name}: mean entropy = {np.mean(folio_entropies):.3f} ± {np.std(folio_entropies):.3f} (n={len(folio_entropies)})")

    # Statistical test
    if len(category_entropies) >= 2:
        groups = [category_entropies[c] for c in ['SHORT', 'MEDIUM', 'LONG'] if c in category_entropies]
        if all(len(g) > 0 for g in groups):
            stat, p_value = stats.kruskal(*groups)
            print(f"\nKruskal-Wallis test: H={stat:.3f}, p={p_value:.4f}")

            return {
                'test': 'A line length vs B transition entropy',
                'category_means': {k: float(np.mean(v)) for k, v in category_entropies.items()},
                'kruskal_wallis_H': stat,
                'p_value': p_value,
                'interpretation': interpret_p_value(p_value)
            }

    return {'test': 'A line length vs B transition entropy', 'error': 'insufficient data'}


def run_test_3(categories, a_b_overlap, b_lines):
    """Test 3: A line length vs B type diversity."""
    print("\n" + "="*70)
    print("TEST 3: A LINE LENGTH VS B TYPE DIVERSITY")
    print("="*70)

    category_diversity = {}

    for cat_name, entries in categories.items():
        a_folios = set(e['folio'] for e in entries)
        b_folios, _ = get_associated_b_folios(a_folios, a_b_overlap)

        # Compute type-token ratio per B folio
        folio_ttrs = []
        for b_f in b_folios:
            folio_lines = [(k, v) for k, v in b_lines.items() if k[0] == b_f]
            tokens = []
            for _, toks in folio_lines:
                tokens.extend(toks)

            if tokens:
                ttr = len(set(tokens)) / len(tokens)
                folio_ttrs.append(ttr)

        if folio_ttrs:
            category_diversity[cat_name] = folio_ttrs
            print(f"\n{cat_name}: mean TTR = {np.mean(folio_ttrs):.3f} ± {np.std(folio_ttrs):.3f} (n={len(folio_ttrs)})")

    # Statistical test
    if len(category_diversity) >= 2:
        groups = [category_diversity[c] for c in ['SHORT', 'MEDIUM', 'LONG'] if c in category_diversity]
        if all(len(g) > 0 for g in groups):
            stat, p_value = stats.kruskal(*groups)
            print(f"\nKruskal-Wallis test: H={stat:.3f}, p={p_value:.4f}")

            return {
                'test': 'A line length vs B type diversity',
                'category_means': {k: float(np.mean(v)) for k, v in category_diversity.items()},
                'kruskal_wallis_H': stat,
                'p_value': p_value,
                'interpretation': interpret_p_value(p_value)
            }

    return {'test': 'A line length vs B type diversity', 'error': 'insufficient data'}


def run_test_4(a_lines, a_b_overlap):
    """Test 4: Within-folio control - do different length lines in same A folio map to same B?"""
    print("\n" + "="*70)
    print("TEST 4: WITHIN-FOLIO CONTROL")
    print("="*70)

    # Group A lines by folio
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in a_lines.items():
        folio_lines[folio].append({'line_num': line_num, 'length': len(tokens)})

    # Find folios with both short and long lines
    mixed_folios = []
    for folio, lines in folio_lines.items():
        lengths = [l['length'] for l in lines]
        if min(lengths) <= 3 and max(lengths) >= 8:
            mixed_folios.append({
                'folio': folio,
                'min_length': min(lengths),
                'max_length': max(lengths),
                'n_lines': len(lines)
            })

    print(f"\nA folios with both SHORT (<=3) and LONG (>=8) lines: {len(mixed_folios)}")

    if mixed_folios:
        # For each mixed folio, check if it maps to same B folios regardless of line length
        consistency_scores = []

        for mf in mixed_folios[:10]:  # Sample
            folio = mf['folio']
            if folio in a_b_overlap:
                b_counts = a_b_overlap[folio]
                # Check concentration - if batch, should be highly concentrated
                total = sum(b_counts.values())
                top_b = b_counts.most_common(1)[0][1] if b_counts else 0
                concentration = top_b / total if total > 0 else 0
                consistency_scores.append(concentration)

                print(f"  {folio}: lines={mf['n_lines']}, length range={mf['min_length']}-{mf['max_length']}, "
                      f"B folios={len(b_counts)}, concentration={concentration:.2%}")

        if consistency_scores:
            mean_conc = np.mean(consistency_scores)
            print(f"\nMean B-folio concentration for mixed A folios: {mean_conc:.2%}")

            return {
                'test': 'Within-folio control',
                'mixed_folios': len(mixed_folios),
                'mean_concentration': mean_conc,
                'interpretation': 'HIGH concentration supports BATCH (same B regardless of A line length)'
            }

    return {'test': 'Within-folio control', 'mixed_folios': 0, 'error': 'no mixed folios found'}


def interpret_p_value(p):
    """Interpret p-value per expert thresholds."""
    if p < 0.01:
        return "REJECT_BATCH (p < 0.01)"
    elif p > 0.10:
        return "SUPPORT_BATCH (p > 0.10)"
    else:
        return "INCONCLUSIVE (0.01 < p < 0.10)"


def main():
    print("="*70)
    print("PHASE BvS: BATCH VS SEQUENTIAL PROCESSING TEST")
    print("="*70)

    # Load data
    print("\nLoading transcription data...")
    a_lines, b_lines, a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios = load_transcription_data()

    print(f"A lines: {len(a_lines)}")
    print(f"B lines: {len(b_lines)}")
    print(f"A folios: {len(a_folio_tokens)}")
    print(f"B folios: {len(b_folio_tokens)}")

    # Compute A line lengths and categorize
    a_line_lengths = compute_a_line_lengths(a_lines)
    categories = categorize_a_lines(a_line_lengths)

    print(f"\nA line length distribution:")
    for cat, entries in categories.items():
        lengths = [e['length'] for e in entries]
        print(f"  {cat}: {len(entries)} lines, mean={np.mean(lengths):.1f}, range={min(lengths)}-{max(lengths)}")

    # Build A-B mapping
    a_b_overlap, n_rare = build_a_b_mapping(a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios)
    print(f"\nA-B mapping built using {n_rare} rare tokens")
    print(f"A folios with B overlap: {len(a_b_overlap)}")

    # Run tests
    results = {
        'phase': 'BvS',
        'question': 'Batch vs Sequential processing',
        'h0': 'B complexity independent of A line length (batch)',
        'h1': 'B complexity scales with A line length (sequential)',
        'thresholds': {
            'reject_batch': 'p < 0.01',
            'support_batch': 'p > 0.10',
            'inconclusive': '0.01 < p < 0.10'
        },
        'tests': []
    }

    test1 = run_test_1(categories, a_b_overlap, b_lines)
    results['tests'].append(test1)

    test2 = run_test_2(categories, a_b_overlap, b_lines)
    results['tests'].append(test2)

    test3 = run_test_3(categories, a_b_overlap, b_lines)
    results['tests'].append(test3)

    test4 = run_test_4(a_lines, a_b_overlap)
    results['tests'].append(test4)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    interpretations = []
    for t in results['tests']:
        if 'interpretation' in t:
            interpretations.append(t['interpretation'])
            print(f"{t['test']}: {t['interpretation']}")

    # Overall verdict
    batch_support = sum(1 for i in interpretations if 'SUPPORT_BATCH' in i)
    batch_reject = sum(1 for i in interpretations if 'REJECT_BATCH' in i)

    if batch_reject > 0:
        verdict = "SEQUENTIAL_MODEL_SUPPORTED"
    elif batch_support >= 2:
        verdict = "BATCH_MODEL_CONFIRMED"
    else:
        verdict = "INCONCLUSIVE"

    results['verdict'] = verdict
    print(f"\nOVERALL VERDICT: {verdict}")

    # Save results
    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {OUTPUT}")

    return results


if __name__ == '__main__':
    main()
