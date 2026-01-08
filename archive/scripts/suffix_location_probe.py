"""
Suffix Location Hypothesis Probe

Test if SUFFIX encodes location (bin/shelf) rather than form/state.

If suffix = location:
1. Same PREFIX+MIDDLE should appear with multiple suffixes (same item, different locations)
2. Suffix should cluster by folio/position (physical organization)
3. Suffix distribution should be systematic by section (different rooms have different bins)

Tier 4 - Exploratory (do not document unless significant)
"""

from collections import defaultdict, Counter
import math

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def load_currier_a_tokens():
    """Load Currier A tokens with context."""
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

            if currier == 'A' and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, token)
                if key not in seen:
                    seen.add(key)
                    data.append({
                        'token': token,
                        'folio': folio,
                        'section': section,
                        'line': line_num
                    })

    return data

def get_prefix(token):
    """Extract prefix from token."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def decompose_token(token):
    """Decompose token into prefix, middle, suffix."""
    prefix = get_prefix(token)
    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Common suffixes (from prior analysis)
    SUFFIXES = ['aiin', 'ain', 'edy', 'eedy', 'dy', 'ey', 'eey', 'ol', 'eol',
                'or', 'ar', 'al', 'y', 'o', 'am', 'chy', 'cthy', 'ckhy']

    suffix = None
    middle = remainder

    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            middle = remainder[:-len(s)]
            break

    if suffix is None and len(remainder) > 0:
        # Last 1-2 chars as suffix
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        else:
            suffix = remainder
            middle = ''

    return prefix, middle, suffix

def test_multi_suffix_stems(data):
    """Test if same PREFIX+MIDDLE appears with multiple suffixes."""

    print("=" * 70)
    print("TEST 1: Do same PREFIX+MIDDLE stems appear with multiple suffixes?")
    print("=" * 70)
    print("(If suffix = location, same item should appear in multiple locations)")

    # Map: (prefix, middle) -> {suffix: count}
    stem_suffixes = defaultdict(Counter)

    for d in data:
        prefix, middle, suffix = decompose_token(d['token'])
        if prefix and suffix:
            stem_suffixes[(prefix, middle)][suffix] += 1

    # Count stems with multiple suffixes
    multi_suffix_stems = []
    single_suffix_stems = 0

    for stem, suffix_counts in stem_suffixes.items():
        if len(suffix_counts) > 1:
            total = sum(suffix_counts.values())
            multi_suffix_stems.append((stem, suffix_counts, total))
        else:
            single_suffix_stems += 1

    multi_suffix_stems.sort(key=lambda x: -x[2])

    total_stems = len(stem_suffixes)
    multi_count = len(multi_suffix_stems)

    print(f"\nTotal unique PREFIX+MIDDLE stems: {total_stems}")
    print(f"Stems with MULTIPLE suffixes: {multi_count} ({100*multi_count/total_stems:.1f}%)")
    print(f"Stems with SINGLE suffix: {single_suffix_stems} ({100*single_suffix_stems/total_stems:.1f}%)")

    print("\n--- Top 20 stems with multiple suffixes ---")
    print(f"{'Stem':<20} {'Suffixes':<40} {'Total':<8}")
    print("-" * 70)

    for (prefix, middle), suffix_counts, total in multi_suffix_stems[:20]:
        stem_str = f"{prefix}+{middle}" if middle else f"{prefix}+"
        suffix_str = ', '.join(f"{s}({c})" for s, c in suffix_counts.most_common(5))
        print(f"{stem_str:<20} {suffix_str:<40} {total:<8}")

    # Calculate if this is more than chance
    # If random, how many stems would have multiple suffixes?
    unique_suffixes = set()
    for suffix_counts in stem_suffixes.values():
        unique_suffixes.update(suffix_counts.keys())

    print(f"\nTotal unique suffixes observed: {len(unique_suffixes)}")

    return multi_count / total_stems if total_stems > 0 else 0

def test_suffix_folio_clustering(data):
    """Test if suffixes cluster by folio."""

    print("\n" + "=" * 70)
    print("TEST 2: Do suffixes cluster by folio?")
    print("=" * 70)
    print("(If suffix = location, and folios = storage units, should see clustering)")

    # Map: folio -> suffix counts
    folio_suffixes = defaultdict(Counter)
    suffix_total = Counter()

    for d in data:
        prefix, middle, suffix = decompose_token(d['token'])
        if suffix:
            folio_suffixes[d['folio']][suffix] += 1
            suffix_total[suffix] += 1

    # Calculate entropy of suffix distribution per folio
    # Low entropy = clustering (few suffixes dominate)
    # High entropy = uniform (many suffixes equally)

    folio_entropies = []

    for folio, suffix_counts in folio_suffixes.items():
        total = sum(suffix_counts.values())
        if total >= 10:  # Only folios with enough data
            entropy = 0
            for count in suffix_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            folio_entropies.append((folio, entropy, total, len(suffix_counts)))

    folio_entropies.sort(key=lambda x: x[1])

    avg_entropy = sum(e[1] for e in folio_entropies) / len(folio_entropies) if folio_entropies else 0

    # Calculate max possible entropy
    max_entropy = math.log2(len(suffix_total)) if len(suffix_total) > 0 else 0

    print(f"\nFolios with >= 10 tokens: {len(folio_entropies)}")
    print(f"Average suffix entropy per folio: {avg_entropy:.2f} bits")
    print(f"Max possible entropy: {max_entropy:.2f} bits")
    print(f"Entropy ratio: {avg_entropy/max_entropy:.2f}" if max_entropy > 0 else "N/A")

    print("\n--- Folios with LOWEST suffix entropy (most clustered) ---")
    for folio, entropy, total, n_suff in folio_entropies[:10]:
        print(f"  {folio}: entropy={entropy:.2f}, n={total}, unique_suffixes={n_suff}")

    print("\n--- Folios with HIGHEST suffix entropy (least clustered) ---")
    for folio, entropy, total, n_suff in folio_entropies[-10:]:
        print(f"  {folio}: entropy={entropy:.2f}, n={total}, unique_suffixes={n_suff}")

    # Check if certain suffixes dominate certain folios
    print("\n--- Do any suffixes concentrate in specific folios? ---")

    suffix_folio_concentration = []
    for suffix, total in suffix_total.most_common(15):
        if total >= 20:
            folio_counts = []
            for folio, counts in folio_suffixes.items():
                if suffix in counts:
                    folio_counts.append((folio, counts[suffix]))
            folio_counts.sort(key=lambda x: -x[1])
            top_folio, top_count = folio_counts[0]
            concentration = top_count / total
            suffix_folio_concentration.append((suffix, total, top_folio, top_count, concentration))

    suffix_folio_concentration.sort(key=lambda x: -x[4])

    print(f"\n{'Suffix':<10} {'Total':<8} {'Top Folio':<12} {'Count':<8} {'Concentration':<12}")
    print("-" * 55)
    for suffix, total, top_folio, top_count, conc in suffix_folio_concentration[:15]:
        print(f"{suffix:<10} {total:<8} {top_folio:<12} {top_count:<8} {conc*100:.1f}%")

    return avg_entropy / max_entropy if max_entropy > 0 else 0

def test_suffix_section_distribution(data):
    """Test if suffix distributions differ by section."""

    print("\n" + "=" * 70)
    print("TEST 3: Do suffix distributions differ by section?")
    print("=" * 70)
    print("(If suffix = bin in storage room, and section = room, should differ)")

    # Map: section -> suffix counts
    section_suffixes = defaultdict(Counter)

    for d in data:
        prefix, middle, suffix = decompose_token(d['token'])
        if suffix and d['section'] in ['H', 'P', 'T']:
            section_suffixes[d['section']][suffix] += 1

    # Print distribution
    all_suffixes = set()
    for counts in section_suffixes.values():
        all_suffixes.update(counts.keys())

    top_suffixes = []
    for suffix in all_suffixes:
        total = sum(section_suffixes[s][suffix] for s in section_suffixes)
        top_suffixes.append((suffix, total))
    top_suffixes.sort(key=lambda x: -x[1])
    top_suffixes = [s for s, _ in top_suffixes[:15]]

    print(f"\n{'Suffix':<10}", end='')
    for section in ['H', 'P', 'T']:
        print(f"{section:>10}", end='')
    print(f"{'Total':>10}")
    print("-" * 50)

    for suffix in top_suffixes:
        print(f"{suffix:<10}", end='')
        total = 0
        for section in ['H', 'P', 'T']:
            count = section_suffixes[section][suffix]
            total += count
            sect_total = sum(section_suffixes[section].values())
            pct = 100 * count / sect_total if sect_total > 0 else 0
            print(f"{pct:>9.1f}%", end='')
        print(f"{total:>10}")

    # Chi-square test for independence
    print("\n--- Chi-square test: Are suffix distributions independent of section? ---")

    # Build contingency table
    sections = ['H', 'P', 'T']
    suffixes = top_suffixes[:10]

    observed = []
    for suffix in suffixes:
        row = [section_suffixes[s][suffix] for s in sections]
        observed.append(row)

    # Calculate expected values
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(len(suffixes))) for j in range(len(sections))]
    grand_total = sum(row_totals)

    chi2 = 0
    for i, suffix in enumerate(suffixes):
        for j, section in enumerate(sections):
            expected = row_totals[i] * col_totals[j] / grand_total if grand_total > 0 else 0
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    df = (len(suffixes) - 1) * (len(sections) - 1)

    print(f"Chi-square: {chi2:.1f}")
    print(f"Degrees of freedom: {df}")
    print(f"Chi2/df ratio: {chi2/df:.2f}" if df > 0 else "N/A")

    # Chi2/df > 3 suggests significant difference
    if chi2/df > 3:
        print("=> SIGNIFICANT difference in suffix distributions across sections")
    else:
        print("=> Suffix distributions are similar across sections")

    return chi2 / df if df > 0 else 0

def test_suffix_position_pattern(data):
    """Test if suffixes have positional patterns within entries."""

    print("\n" + "=" * 70)
    print("TEST 4: Do suffixes have positional patterns?")
    print("=" * 70)
    print("(If suffix = location, might see systematic ordering)")

    # Organize by folio and line
    folio_lines = defaultdict(list)
    for d in data:
        folio_lines[(d['folio'], d['line'])].append(d)

    # For lines with 3+ tokens, check if suffix changes systematically
    suffix_sequences = []

    for (folio, line), tokens in folio_lines.items():
        if len(tokens) >= 3:
            suffixes = []
            for t in tokens:
                prefix, middle, suffix = decompose_token(t['token'])
                if suffix:
                    suffixes.append(suffix)
            if len(suffixes) >= 3:
                suffix_sequences.append(suffixes)

    print(f"\nLines with 3+ decomposable tokens: {len(suffix_sequences)}")

    # Check for repetition patterns
    all_same = 0
    all_different = 0
    mixed = 0

    for seq in suffix_sequences:
        unique = len(set(seq))
        if unique == 1:
            all_same += 1
        elif unique == len(seq):
            all_different += 1
        else:
            mixed += 1

    total = len(suffix_sequences)
    print(f"\nSuffix patterns in multi-token lines:")
    print(f"  All SAME suffix: {all_same} ({100*all_same/total:.1f}%)")
    print(f"  All DIFFERENT suffix: {all_different} ({100*all_different/total:.1f}%)")
    print(f"  MIXED: {mixed} ({100*mixed/total:.1f}%)")

    # If suffix = location, we'd expect either:
    # - All same (all items in same bin)
    # - Systematic progression (bin 1, bin 2, bin 3)

    # Check for sequential patterns
    print("\n--- Sample suffix sequences ---")
    for seq in suffix_sequences[:15]:
        print(f"  {' -> '.join(seq)}")

    return all_same / total if total > 0 else 0

def main():
    print("=" * 70)
    print("SUFFIX LOCATION HYPOTHESIS PROBE")
    print("=" * 70)
    print("\nHypothesis: SUFFIX encodes bin/shelf location, not form/state")

    data = load_currier_a_tokens()
    print(f"\nLoaded {len(data)} Currier A tokens")

    # Run tests
    multi_suffix_rate = test_multi_suffix_stems(data)
    entropy_ratio = test_suffix_folio_clustering(data)
    chi2_ratio = test_suffix_section_distribution(data)
    same_suffix_rate = test_suffix_position_pattern(data)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Suffix Location Hypothesis")
    print("=" * 70)

    print(f"""
    Test                                Result              Supports Location?
    -------------------------------------------------------------------------
    Multi-suffix stems                  {multi_suffix_rate*100:.1f}%              {"YES" if multi_suffix_rate > 0.3 else "WEAK" if multi_suffix_rate > 0.15 else "NO"}
    Suffix-folio clustering             {entropy_ratio:.2f} entropy      {"YES" if entropy_ratio < 0.6 else "WEAK" if entropy_ratio < 0.8 else "NO"}
    Section-suffix dependence           {chi2_ratio:.1f} chi2/df        {"YES" if chi2_ratio > 3 else "WEAK" if chi2_ratio > 1.5 else "NO"}
    Same-suffix lines                   {same_suffix_rate*100:.1f}%              {"YES" if same_suffix_rate > 0.4 else "WEAK" if same_suffix_rate > 0.2 else "NO"}

    INTERPRETATION:
    - If mostly YES: Suffix likely encodes location
    - If mostly NO: Suffix likely encodes form/state (original interpretation)
    - If WEAK/mixed: Inconclusive
    """)

if __name__ == '__main__':
    main()
