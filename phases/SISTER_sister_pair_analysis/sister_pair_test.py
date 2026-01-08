"""
Sister Pair Test: Do ch/sh and ok/ot behave similarly in Currier B?

If the Currier A prefix groupings reflect real material families,
then sister pairs should:
1. Appear in similar B-program contexts
2. Have similar grammar role distributions
3. Occur near each other (co-occurrence)
4. Appear in similar folio types (regimes)

Tier 4 - Exploratory
"""

import os
from collections import defaultdict, Counter
import math

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def load_currier_b_data():
    """Load Currier B tokens with context."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    data = []
    seen = set()

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            section = parts[3]
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]
            line_init = parts[13]
            line_final = parts[14] if len(parts) > 14 else '0'

            # Filter to Currier B, hand H
            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, token)
                if key not in seen:
                    seen.add(key)
                    data.append({
                        'token': token,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'line_init': line_init == '1',
                        'line_final': line_final == '1'
                    })

    return data

def get_prefix(token):
    """Extract prefix from token."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def analyze_sister_pairs(data):
    """Test if sister pairs behave similarly in B."""

    print("=" * 70)
    print("SISTER PAIR TEST: Do A-groupings predict B-behavior?")
    print("=" * 70)

    # Organize by folio and line
    folio_lines = defaultdict(list)
    for d in data:
        folio_lines[(d['folio'], d['line'])].append(d)

    # === TEST 1: Co-occurrence within lines ===
    print("\n" + "-" * 70)
    print("TEST 1: Co-occurrence within lines")
    print("-" * 70)
    print("(Do sister pairs appear together more often than non-sisters?)")

    # Count how often each prefix pair appears in the same line
    pair_cooccur = defaultdict(int)
    prefix_line_count = defaultdict(int)

    for (folio, line), tokens in folio_lines.items():
        prefixes_in_line = set()
        for t in tokens:
            p = get_prefix(t['token'])
            if p:
                prefixes_in_line.add(p)

        for p in prefixes_in_line:
            prefix_line_count[p] += 1

        # Count co-occurrences
        prefix_list = list(prefixes_in_line)
        for i, p1 in enumerate(prefix_list):
            for p2 in prefix_list[i+1:]:
                key = tuple(sorted([p1, p2]))
                pair_cooccur[key] += 1

    total_lines = len(folio_lines)

    print(f"\nTotal B lines: {total_lines}")
    print("\nCo-occurrence rates (% of lines where both prefixes appear):")

    # Calculate expected vs observed
    print(f"\n{'Pair':<12} {'Observed':<12} {'Expected':<12} {'Ratio':<10} {'Type':<15}")
    print("-" * 60)

    results = []
    for i, p1 in enumerate(PREFIXES):
        for p2 in PREFIXES[i+1:]:
            key = tuple(sorted([p1, p2]))
            observed = pair_cooccur[key]

            # Expected under independence
            rate1 = prefix_line_count[p1] / total_lines
            rate2 = prefix_line_count[p2] / total_lines
            expected = rate1 * rate2 * total_lines

            ratio = observed / expected if expected > 0 else 0

            # Categorize pair
            if (p1, p2) in [('ch', 'sh'), ('sh', 'ch')]:
                pair_type = "SISTER (ch-sh)"
            elif (p1, p2) in [('ok', 'ot'), ('ot', 'ok')]:
                pair_type = "SISTER (ok-ot)"
            elif 'da' in (p1, p2):
                pair_type = "with DA"
            elif 'ct' in (p1, p2):
                pair_type = "with CT"
            else:
                pair_type = "other"

            results.append((p1, p2, observed, expected, ratio, pair_type))

    # Sort by ratio
    results.sort(key=lambda x: -x[4])

    for p1, p2, obs, exp, ratio, ptype in results:
        print(f"{p1}-{p2:<8} {obs:<12} {exp:<12.1f} {ratio:<10.2f} {ptype:<15}")

    # === TEST 2: Sequential adjacency ===
    print("\n" + "-" * 70)
    print("TEST 2: Sequential adjacency (bigrams)")
    print("-" * 70)
    print("(Do sister pairs follow each other more often?)")

    # Build bigrams
    bigram_counts = defaultdict(int)
    prefix_counts = Counter()

    for (folio, line), tokens in folio_lines.items():
        for i in range(len(tokens) - 1):
            p1 = get_prefix(tokens[i]['token'])
            p2 = get_prefix(tokens[i+1]['token'])
            if p1 and p2:
                bigram_counts[(p1, p2)] += 1
                prefix_counts[p1] += 1
        # Count last token
        if tokens:
            p = get_prefix(tokens[-1]['token'])
            if p:
                prefix_counts[p] += 1

    total_bigrams = sum(bigram_counts.values())

    print(f"\nTotal prefix bigrams: {total_bigrams}")
    print("\nBigram enrichment (sister pairs highlighted):")

    print(f"\n{'Bigram':<12} {'Observed':<10} {'Expected':<10} {'Ratio':<10} {'Type':<15}")
    print("-" * 60)

    bigram_results = []
    for p1 in PREFIXES:
        for p2 in PREFIXES:
            if p1 == p2:
                continue
            observed = bigram_counts[(p1, p2)]
            rate1 = prefix_counts[p1] / sum(prefix_counts.values())
            rate2 = prefix_counts[p2] / sum(prefix_counts.values())
            expected = rate1 * rate2 * total_bigrams
            ratio = observed / expected if expected > 0 else 0

            if (p1, p2) in [('ch', 'sh'), ('sh', 'ch')]:
                pair_type = "SISTER ch-sh"
            elif (p1, p2) in [('ok', 'ot'), ('ot', 'ok')]:
                pair_type = "SISTER ok-ot"
            else:
                pair_type = ""

            bigram_results.append((p1, p2, observed, expected, ratio, pair_type))

    # Show sister pairs first, then top others
    sister_bigrams = [r for r in bigram_results if r[5]]
    other_bigrams = [r for r in bigram_results if not r[5]]
    other_bigrams.sort(key=lambda x: -x[4])

    print("\nSISTER PAIR BIGRAMS:")
    for p1, p2, obs, exp, ratio, ptype in sister_bigrams:
        print(f"{p1}->{p2:<8} {obs:<10} {exp:<10.1f} {ratio:<10.2f} {ptype:<15}")

    print("\nTOP 10 OTHER BIGRAMS:")
    for p1, p2, obs, exp, ratio, ptype in other_bigrams[:10]:
        print(f"{p1}->{p2:<8} {obs:<10} {exp:<10.1f} {ratio:<10.2f}")

    # === TEST 3: Folio distribution ===
    print("\n" + "-" * 70)
    print("TEST 3: Folio distribution similarity")
    print("-" * 70)
    print("(Do sister pairs appear in the same folios?)")

    prefix_folios = defaultdict(set)
    for d in data:
        p = get_prefix(d['token'])
        if p:
            prefix_folios[p].add(d['folio'])

    print("\nJaccard similarity of folio sets:")
    print(f"\n{'':8}", end='')
    for p in PREFIXES:
        print(f"{p:>8}", end='')
    print()

    for p1 in PREFIXES:
        print(f"{p1:8}", end='')
        for p2 in PREFIXES:
            if not prefix_folios[p1] or not prefix_folios[p2]:
                print(f"{'N/A':>8}", end='')
            else:
                intersection = len(prefix_folios[p1] & prefix_folios[p2])
                union = len(prefix_folios[p1] | prefix_folios[p2])
                jaccard = intersection / union if union > 0 else 0
                print(f"{jaccard:>8.2f}", end='')
        print()

    # === TEST 4: Position in line ===
    print("\n" + "-" * 70)
    print("TEST 4: Line position patterns")
    print("-" * 70)
    print("(Do sister pairs have similar positional preferences?)")

    prefix_positions = defaultdict(lambda: {'init': 0, 'final': 0, 'mid': 0, 'total': 0})

    for d in data:
        p = get_prefix(d['token'])
        if p:
            prefix_positions[p]['total'] += 1
            if d['line_init']:
                prefix_positions[p]['init'] += 1
            elif d['line_final']:
                prefix_positions[p]['final'] += 1
            else:
                prefix_positions[p]['mid'] += 1

    print(f"\n{'Prefix':<8} {'Initial%':<12} {'Final%':<12} {'Mid%':<12} {'Total':<10}")
    print("-" * 55)

    for p in PREFIXES:
        d = prefix_positions[p]
        if d['total'] > 0:
            init_pct = 100 * d['init'] / d['total']
            final_pct = 100 * d['final'] / d['total']
            mid_pct = 100 * d['mid'] / d['total']
            print(f"{p:<8} {init_pct:<12.1f} {final_pct:<12.1f} {mid_pct:<12.1f} {d['total']:<10}")

    # === TEST 5: Context tokens ===
    print("\n" + "-" * 70)
    print("TEST 5: What tokens appear BEFORE each prefix?")
    print("-" * 70)

    prefix_predecessors = defaultdict(Counter)

    for (folio, line), tokens in folio_lines.items():
        for i in range(1, len(tokens)):
            p = get_prefix(tokens[i]['token'])
            if p:
                prev_token = tokens[i-1]['token']
                prefix_predecessors[p][prev_token] += 1

    print("\nTop 5 predecessors for each prefix:")
    for p in PREFIXES:
        preds = prefix_predecessors[p].most_common(5)
        pred_str = ', '.join(f"{t}({c})" for t, c in preds)
        print(f"  {p}: {pred_str}")

    # === TEST 6: Similarity of predecessor distributions ===
    print("\n" + "-" * 70)
    print("TEST 6: Predecessor distribution similarity (Jensen-Shannon)")
    print("-" * 70)

    def js_divergence(p_counts, q_counts):
        """Calculate Jensen-Shannon divergence between two distributions."""
        all_tokens = set(p_counts.keys()) | set(q_counts.keys())
        p_total = sum(p_counts.values())
        q_total = sum(q_counts.values())

        if p_total == 0 or q_total == 0:
            return 1.0

        # Normalize
        p_dist = {t: p_counts[t] / p_total for t in all_tokens}
        q_dist = {t: q_counts[t] / q_total for t in all_tokens}

        # M = average distribution
        m_dist = {t: (p_dist.get(t, 0) + q_dist.get(t, 0)) / 2 for t in all_tokens}

        # KL divergences
        def kl(p, m):
            total = 0
            for t in p:
                if p[t] > 0 and m[t] > 0:
                    total += p[t] * math.log2(p[t] / m[t])
            return total

        js = (kl(p_dist, m_dist) + kl(q_dist, m_dist)) / 2
        return js

    print("\nJS divergence (lower = more similar):")
    print(f"\n{'':8}", end='')
    for p in PREFIXES:
        print(f"{p:>8}", end='')
    print()

    for p1 in PREFIXES:
        print(f"{p1:8}", end='')
        for p2 in PREFIXES:
            js = js_divergence(prefix_predecessors[p1], prefix_predecessors[p2])
            print(f"{js:>8.3f}", end='')
        print()

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY: Sister Pair Evidence")
    print("=" * 70)

    # Calculate average metrics for sister vs non-sister pairs
    sister_pairs = [('ch', 'sh'), ('ok', 'ot')]

    print("\n1. Co-occurrence enrichment:")
    for p1, p2 in sister_pairs:
        key = tuple(sorted([p1, p2]))
        for r in results:
            if tuple(sorted([r[0], r[1]])) == key:
                print(f"   {p1}-{p2}: {r[4]:.2f}x")

    print("\n2. Folio overlap:")
    for p1, p2 in sister_pairs:
        inter = len(prefix_folios[p1] & prefix_folios[p2])
        union = len(prefix_folios[p1] | prefix_folios[p2])
        print(f"   {p1}-{p2}: {inter}/{union} folios ({100*inter/union:.1f}%)")

    print("\n3. Predecessor JS divergence:")
    for p1, p2 in sister_pairs:
        js = js_divergence(prefix_predecessors[p1], prefix_predecessors[p2])
        print(f"   {p1}-{p2}: {js:.3f}")

if __name__ == '__main__':
    data = load_currier_b_data()
    print(f"Loaded {len(data)} Currier B tokens")
    analyze_sister_pairs(data)
