"""
AZC Sister Pair Probe: Do sister pairs behave the same in AZC?

Tests:
1. ch/sh bigram rates (mutual exclusion)
2. ch/sh distribution across placement classes
3. DA behavior (infrastructure or content?)
4. Comparison with Currier B patterns

Tier 4 - Exploratory
"""

from collections import defaultdict, Counter
import math

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SISTER_PAIRS = [('ch', 'sh'), ('ok', 'ot')]

# AZC sections (Astronomical, Zodiac, Cosmological)
AZC_SECTIONS = ['A', 'Z', 'C']

def load_azc_data():
    """Load tokens from AZC sections (unclassified by Currier)."""
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
            currier = parts[6]  # Language column - empty or unlabeled for AZC
            transcriber = parts[12]
            line_num = parts[11]
            line_init = parts[13]
            line_final = parts[14] if len(parts) > 14 else '0'

            # AZC = sections A, Z, C that are NOT classified as A or B
            if section in AZC_SECTIONS and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, token)
                if key not in seen:
                    seen.add(key)
                    data.append({
                        'token': token,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'line_init': line_init == '1',
                        'line_final': line_final == '1',
                        'currier': currier
                    })

    return data

def load_currier_b_data():
    """Load Currier B for comparison."""
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

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
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

def test_bigram_suppression(data, label):
    """Test if sister pairs avoid direct sequence."""

    # Organize by folio and line
    folio_lines = defaultdict(list)
    for d in data:
        folio_lines[(d['folio'], d['line'])].append(d)

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
        if tokens:
            p = get_prefix(tokens[-1]['token'])
            if p:
                prefix_counts[p] += 1

    total_bigrams = sum(bigram_counts.values())
    total_prefix = sum(prefix_counts.values())

    print(f"\n--- {label}: Sister Pair Bigram Suppression ---")
    print(f"Total prefix bigrams: {total_bigrams}")
    print(f"Total prefix tokens: {total_prefix}")

    if total_bigrams == 0:
        print("  No bigrams found!")
        return {}

    results = {}
    for p1, p2 in [('ch', 'sh'), ('sh', 'ch'), ('ok', 'ot'), ('ot', 'ok')]:
        observed = bigram_counts[(p1, p2)]
        rate1 = prefix_counts[p1] / total_prefix if total_prefix > 0 else 0
        rate2 = prefix_counts[p2] / total_prefix if total_prefix > 0 else 0
        expected = rate1 * rate2 * total_bigrams
        ratio = observed / expected if expected > 0 else 0

        results[(p1, p2)] = {'observed': observed, 'expected': expected, 'ratio': ratio}
        print(f"  {p1}->{p2}: observed={observed}, expected={expected:.1f}, ratio={ratio:.2f}x")

    return results

def test_section_distribution(data, label):
    """Test prefix distribution across sections/placements."""

    print(f"\n--- {label}: Prefix Distribution by Section ---")

    section_prefix = defaultdict(Counter)
    prefix_total = Counter()

    for d in data:
        p = get_prefix(d['token'])
        if p:
            section_prefix[d['section']][p] += 1
            prefix_total[p] += 1

    # Print distribution
    sections = sorted(section_prefix.keys())

    print(f"\n{'Prefix':<8}", end='')
    for s in sections:
        print(f"{s:>8}", end='')
    print(f"{'Total':>10}")
    print("-" * (8 + 8*len(sections) + 10))

    for p in PREFIXES:
        if prefix_total[p] > 0:
            print(f"{p:<8}", end='')
            for s in sections:
                count = section_prefix[s][p]
                pct = 100 * count / prefix_total[p] if prefix_total[p] > 0 else 0
                print(f"{pct:>7.0f}%", end='')
            print(f"{prefix_total[p]:>10}")

    # Chi-square for ch vs sh
    print("\n--- ch vs sh Section Preference ---")
    ch_counts = [section_prefix[s]['ch'] for s in sections]
    sh_counts = [section_prefix[s]['sh'] for s in sections]
    ch_total = sum(ch_counts)
    sh_total = sum(sh_counts)

    if ch_total > 0 and sh_total > 0:
        for i, s in enumerate(sections):
            ch_pct = 100 * ch_counts[i] / ch_total
            sh_pct = 100 * sh_counts[i] / sh_total
            diff = ch_pct - sh_pct
            print(f"  Section {s}: ch={ch_pct:.1f}%, sh={sh_pct:.1f}%, diff={diff:+.1f}pp")

    return section_prefix

def test_da_behavior(data, label):
    """Test if DA behaves as infrastructure in this dataset."""

    print(f"\n--- {label}: DA Infrastructure Test ---")

    # Count line positions
    prefix_positions = defaultdict(lambda: {'init': 0, 'final': 0, 'mid': 0, 'total': 0})

    for d in data:
        p = get_prefix(d['token'])
        if p:
            prefix_positions[p]['total'] += 1
            if d.get('line_init'):
                prefix_positions[p]['init'] += 1
            elif d.get('line_final'):
                prefix_positions[p]['final'] += 1
            else:
                prefix_positions[p]['mid'] += 1

    print(f"\n{'Prefix':<8} {'Init%':<10} {'Final%':<10} {'Mid%':<10} {'Total':<10}")
    print("-" * 48)

    for p in PREFIXES:
        d = prefix_positions[p]
        if d['total'] > 0:
            init_pct = 100 * d['init'] / d['total']
            final_pct = 100 * d['final'] / d['total']
            mid_pct = 100 * d['mid'] / d['total']
            print(f"{p:<8} {init_pct:<10.1f} {final_pct:<10.1f} {mid_pct:<10.1f} {d['total']:<10}")

    # DA vs others comparison
    da_init = prefix_positions['da']['init'] / prefix_positions['da']['total'] if prefix_positions['da']['total'] > 0 else 0

    other_init_sum = 0
    other_total_sum = 0
    for p in PREFIXES:
        if p != 'da' and prefix_positions[p]['total'] > 0:
            other_init_sum += prefix_positions[p]['init']
            other_total_sum += prefix_positions[p]['total']

    other_init = other_init_sum / other_total_sum if other_total_sum > 0 else 0

    print(f"\nDA line-initial rate: {100*da_init:.1f}%")
    print(f"Other prefixes line-initial rate: {100*other_init:.1f}%")
    print(f"DA enrichment: {da_init/other_init:.2f}x" if other_init > 0 else "DA enrichment: N/A")

    return prefix_positions

def test_shared_contexts(data, label):
    """Test if sister pairs share predecessor contexts."""

    print(f"\n--- {label}: Shared Predecessor Contexts ---")

    # Organize by folio and line
    folio_lines = defaultdict(list)
    for d in data:
        folio_lines[(d['folio'], d['line'])].append(d)

    # Map: predecessor -> {prefix -> count}
    pred_to_prefix = defaultdict(Counter)

    for (folio, line), tokens in folio_lines.items():
        for i in range(1, len(tokens)):
            pred = tokens[i-1]['token']
            curr = tokens[i]['token']
            prefix = get_prefix(curr)
            if prefix:
                pred_to_prefix[pred][prefix] += 1

    # Count predecessors that lead to both members of sister pairs
    shared_ch_sh = 0
    shared_ok_ot = 0

    for pred, prefix_counts in pred_to_prefix.items():
        if prefix_counts['ch'] > 0 and prefix_counts['sh'] > 0:
            shared_ch_sh += 1
        if prefix_counts['ok'] > 0 and prefix_counts['ot'] > 0:
            shared_ok_ot += 1

    total_preds = len(pred_to_prefix)

    print(f"Total unique predecessors: {total_preds}")
    print(f"Predecessors leading to both ch AND sh: {shared_ch_sh} ({100*shared_ch_sh/total_preds:.1f}%)" if total_preds > 0 else "N/A")
    print(f"Predecessors leading to both ok AND ot: {shared_ok_ot} ({100*shared_ok_ot/total_preds:.1f}%)" if total_preds > 0 else "N/A")

    return {'ch_sh': shared_ch_sh, 'ok_ot': shared_ok_ot, 'total': total_preds}

def test_minimal_pairs(data, label):
    """Count minimal pairs (same suffix, different sister prefix)."""

    print(f"\n--- {label}: Minimal Pairs ---")

    # Collect suffix counts by prefix
    suffix_by_prefix = defaultdict(Counter)

    for d in data:
        token = d['token']
        prefix = get_prefix(token)
        if prefix:
            suffix = token[len(prefix):]
            suffix_by_prefix[prefix][suffix] += 1

    # Count shared suffixes for sister pairs
    ch_suffixes = set(suffix_by_prefix['ch'].keys())
    sh_suffixes = set(suffix_by_prefix['sh'].keys())
    ok_suffixes = set(suffix_by_prefix['ok'].keys())
    ot_suffixes = set(suffix_by_prefix['ot'].keys())

    ch_sh_shared = ch_suffixes & sh_suffixes
    ok_ot_shared = ok_suffixes & ot_suffixes

    print(f"CH unique suffixes: {len(ch_suffixes)}")
    print(f"SH unique suffixes: {len(sh_suffixes)}")
    print(f"CH/SH shared suffixes (minimal pairs): {len(ch_sh_shared)}")

    print(f"\nOK unique suffixes: {len(ok_suffixes)}")
    print(f"OT unique suffixes: {len(ot_suffixes)}")
    print(f"OK/OT shared suffixes (minimal pairs): {len(ok_ot_shared)}")

    # Show top minimal pairs
    if ch_sh_shared:
        print("\nTop 10 CH/SH minimal pairs:")
        pairs = []
        for suffix in ch_sh_shared:
            ch_count = suffix_by_prefix['ch'][suffix]
            sh_count = suffix_by_prefix['sh'][suffix]
            pairs.append((suffix, ch_count, sh_count))
        pairs.sort(key=lambda x: -(x[1] + x[2]))

        for suffix, ch_c, sh_c in pairs[:10]:
            print(f"  ch{suffix}/sh{suffix}: {ch_c}/{sh_c}")

    return {'ch_sh': len(ch_sh_shared), 'ok_ot': len(ok_ot_shared)}

def main():
    print("=" * 70)
    print("AZC SISTER PAIR PROBE")
    print("=" * 70)
    print("\nQuestion: Do sister pairs behave the same in AZC as in Currier B?")

    # Load data
    azc_data = load_azc_data()
    b_data = load_currier_b_data()

    print(f"\nLoaded {len(azc_data)} AZC tokens")
    print(f"Loaded {len(b_data)} Currier B tokens")

    # Count by section
    azc_sections = Counter(d['section'] for d in azc_data)
    print(f"\nAZC by section: {dict(azc_sections)}")

    # Test 1: Bigram suppression
    print("\n" + "=" * 70)
    print("TEST 1: BIGRAM SUPPRESSION (Mutual Exclusion)")
    print("=" * 70)

    azc_bigrams = test_bigram_suppression(azc_data, "AZC")
    b_bigrams = test_bigram_suppression(b_data, "Currier B")

    # Compare
    print("\n--- Comparison ---")
    print(f"{'Bigram':<12} {'AZC ratio':<12} {'B ratio':<12} {'Match?':<10}")
    print("-" * 46)
    for pair in [('ch', 'sh'), ('sh', 'ch'), ('ok', 'ot'), ('ot', 'ok')]:
        azc_r = azc_bigrams.get(pair, {}).get('ratio', 0)
        b_r = b_bigrams.get(pair, {}).get('ratio', 0)
        # Match if both suppressed (<1.0) or both enriched (>1.0)
        match = "YES" if (azc_r < 1 and b_r < 1) or (azc_r > 1 and b_r > 1) else "NO"
        print(f"{pair[0]}->{pair[1]:<8} {azc_r:<12.2f} {b_r:<12.2f} {match:<10}")

    # Test 2: Section/placement distribution
    print("\n" + "=" * 70)
    print("TEST 2: SECTION DISTRIBUTION")
    print("=" * 70)

    test_section_distribution(azc_data, "AZC")

    # Test 3: DA behavior
    print("\n" + "=" * 70)
    print("TEST 3: DA INFRASTRUCTURE BEHAVIOR")
    print("=" * 70)

    azc_da = test_da_behavior(azc_data, "AZC")
    b_da = test_da_behavior(b_data, "Currier B")

    # Test 4: Shared contexts
    print("\n" + "=" * 70)
    print("TEST 4: SHARED PREDECESSOR CONTEXTS")
    print("=" * 70)

    azc_shared = test_shared_contexts(azc_data, "AZC")
    b_shared = test_shared_contexts(b_data, "Currier B")

    # Test 5: Minimal pairs
    print("\n" + "=" * 70)
    print("TEST 5: MINIMAL PAIRS")
    print("=" * 70)

    azc_minimal = test_minimal_pairs(azc_data, "AZC")
    b_minimal = test_minimal_pairs(b_data, "Currier B")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: AZC vs Currier B Sister Pair Behavior")
    print("=" * 70)

    print("""
    Test                        AZC             Currier B       Match?
    ----------------------------------------------------------------""")

    # Bigram suppression
    azc_ch_sh_supp = (azc_bigrams.get(('ch', 'sh'), {}).get('ratio', 1) +
                      azc_bigrams.get(('sh', 'ch'), {}).get('ratio', 1)) / 2
    b_ch_sh_supp = (b_bigrams.get(('ch', 'sh'), {}).get('ratio', 1) +
                    b_bigrams.get(('sh', 'ch'), {}).get('ratio', 1)) / 2
    match1 = "YES" if azc_ch_sh_supp < 1 and b_ch_sh_supp < 1 else "PARTIAL" if azc_ch_sh_supp < 1 or b_ch_sh_supp < 1 else "NO"
    print(f"    ch-sh bigram suppression    {azc_ch_sh_supp:.2f}x           {b_ch_sh_supp:.2f}x           {match1}")

    # Shared contexts (as % of predecessors)
    azc_shared_pct = 100 * azc_shared['ch_sh'] / azc_shared['total'] if azc_shared['total'] > 0 else 0
    b_shared_pct = 100 * b_shared['ch_sh'] / b_shared['total'] if b_shared['total'] > 0 else 0
    match2 = "YES" if azc_shared_pct > 5 and b_shared_pct > 5 else "NO"
    print(f"    ch-sh shared contexts       {azc_shared_pct:.1f}%           {b_shared_pct:.1f}%           {match2}")

    # Minimal pairs
    match3 = "YES" if azc_minimal['ch_sh'] > 10 and b_minimal['ch_sh'] > 10 else "PARTIAL"
    print(f"    ch-sh minimal pairs         {azc_minimal['ch_sh']}              {b_minimal['ch_sh']}             {match3}")

    # DA line-initial
    azc_da_init = 100 * azc_da['da']['init'] / azc_da['da']['total'] if azc_da['da']['total'] > 0 else 0
    b_da_init = 100 * b_da['da']['init'] / b_da['da']['total'] if b_da['da']['total'] > 0 else 0
    match4 = "YES" if azc_da_init > 10 and b_da_init > 10 else "NO"
    print(f"    DA line-initial rate        {azc_da_init:.1f}%           {b_da_init:.1f}%           {match4}")

    print("""
    ----------------------------------------------------------------

    INTERPRETATION:
    - If all YES: Sister pair behavior is UNIFORM across AZC and B
    - If mixed: AZC has PARTIAL alignment (hybrid behavior)
    - If all NO: AZC sister pairs behave DIFFERENTLY
    """)

if __name__ == '__main__':
    main()
