"""
Test: Does Currier A show the same phase-encoded morphology patterns as B/AZC?

Expected: NO - A is position-free, database-like, should lack:
1. Kernel dichotomy in prefixes
2. LINK affinity patterns
3. Positional preferences

If A lacks these patterns, it confirms A is architecturally distinct.
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Same classifications as B/AZC analysis
A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol', 'al', 'sa', 'ct']
COMMON_SUFFIXES = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey', 'ol', 'eey', 'al',
                   'r', 'dy', 'l', 'or', 'in', 'ody', 'am', 's', 'd', 'chy', 'shy', 'om', 'an']

KERNEL = {'k', 'h', 'e'}
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

def get_prefix(token):
    for p in sorted(A_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def get_suffix(token):
    for s in sorted(COMMON_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            return s
    return None

def load_a_data():
    """Load Currier A tokens."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') == 'A':
                token = row.get('word', '')
                if token and '*' not in token:
                    data.append({
                        'token': token,
                        'folio': row['folio'],
                        'line': row.get('line_number', '1'),
                        'section': row.get('section', ''),
                        'line_initial': row.get('line_initial', '0') == '1',
                        'line_final': row.get('line_final', '0') == '1'
                    })
    return data

def load_b_data():
    """Load Currier B tokens for comparison."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') == 'B':
                token = row.get('word', '')
                if token and '*' not in token:
                    data.append({
                        'token': token,
                        'folio': row['folio'],
                        'line': row.get('line_number', '1'),
                        'section': row.get('section', ''),
                        'line_initial': row.get('line_initial', '0') == '1',
                        'line_final': row.get('line_final', '0') == '1'
                    })
    return data

def test_prefix_kernel(data, label):
    """Test prefix kernel contact patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 1: PREFIX KERNEL DICHOTOMY ({label})")
    print("="*70)

    prefix_kernel = defaultdict(lambda: {'kernel': 0, 'total': 0})

    for row in data:
        token = row['token']
        prefix = get_prefix(token)
        if prefix:
            prefix_kernel[prefix]['total'] += 1
            if any(c in KERNEL for c in token):
                prefix_kernel[prefix]['kernel'] += 1

    print(f"\n{'Prefix':<8} {'Total':>8} {'Kernel%':>10}")
    print("-"*30)

    results = {}
    for prefix in sorted(prefix_kernel.keys(), key=lambda p: prefix_kernel[p]['total'], reverse=True):
        stats = prefix_kernel[prefix]
        if stats['total'] < 5:
            continue
        kernel_pct = stats['kernel'] / stats['total'] * 100
        results[prefix] = kernel_pct
        print(f"{prefix:<8} {stats['total']:>8} {kernel_pct:>9.1f}%")

    # Check for dichotomy
    kernel_rates = []
    for prefix, stats in prefix_kernel.items():
        if stats['total'] >= 10:
            kernel_rates.append(stats['kernel'] / stats['total'])

    if kernel_rates:
        print(f"\nKernel rate range: {min(kernel_rates)*100:.1f}% - {max(kernel_rates)*100:.1f}%")
        spread = max(kernel_rates) - min(kernel_rates)
        if spread > 0.8:
            print("-> STRONG DICHOTOMY (like B)")
        elif spread > 0.5:
            print("-> MODERATE DICHOTOMY")
        else:
            print("-> NO DICHOTOMY (uniformly high or low)")

    return results

def test_link_affinity(data, label):
    """Test LINK proximity patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 2: LINK AFFINITY ({label})")
    print("="*70)

    # Count LINK tokens
    link_count = sum(1 for row in data if row['token'] in LINK_TOKENS)
    link_pct = link_count / len(data) * 100 if data else 0
    print(f"\nLINK density: {link_count}/{len(data)} = {link_pct:.1f}%")

    if link_pct < 1:
        print("-> LINK too sparse for meaningful affinity analysis")
        return {}

    # Build sequences
    sequences = defaultdict(list)
    for row in data:
        key = (row['folio'], row['line'])
        sequences[key].append(row['token'])

    prefix_link = defaultdict(lambda: {'near': 0, 'far': 0})

    for key, tokens in sequences.items():
        link_positions = [i for i, t in enumerate(tokens) if t in LINK_TOKENS]

        for i, token in enumerate(tokens):
            near_link = any(abs(i - lp) <= 2 for lp in link_positions)
            prefix = get_prefix(token)

            if prefix:
                if near_link:
                    prefix_link[prefix]['near'] += 1
                else:
                    prefix_link[prefix]['far'] += 1

    # Calculate baseline
    total_near = sum(p['near'] for p in prefix_link.values())
    total_far = sum(p['far'] for p in prefix_link.values())
    base_rate = total_near / (total_near + total_far) if (total_near + total_far) > 0 else 0

    print(f"\nBaseline LINK-proximity: {base_rate:.1%}")

    print(f"\n{'Prefix':<8} {'Near%':>10} {'Enrichment':>12}")
    print("-"*35)

    results = {}
    for prefix in sorted(prefix_link.keys(), key=lambda p: prefix_link[p]['near'] + prefix_link[p]['far'], reverse=True)[:10]:
        stats = prefix_link[prefix]
        total = stats['near'] + stats['far']
        if total < 10:
            continue
        near_rate = stats['near'] / total
        enr = near_rate / base_rate if base_rate > 0 else 0
        results[prefix] = enr
        marker = "*" if enr > 1.3 or enr < 0.7 else ""
        print(f"{prefix:<8} {near_rate*100:>9.1f}% {enr:>11.2f}x{marker}")

    # Check for pattern
    enrichments = [v for v in results.values()]
    if enrichments:
        spread = max(enrichments) - min(enrichments)
        print(f"\nEnrichment range: {min(enrichments):.2f}x - {max(enrichments):.2f}x")
        if spread > 1.0:
            print("-> STRONG LINK AFFINITY PATTERNS (like B)")
        elif spread > 0.5:
            print("-> MODERATE LINK AFFINITY")
        else:
            print("-> NO LINK AFFINITY (uniform distribution)")

    return results

def test_positional(data, label):
    """Test line position patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 3: POSITIONAL PATTERNS ({label})")
    print("="*70)

    prefix_pos = defaultdict(lambda: {'init': 0, 'final': 0, 'total': 0})

    for row in data:
        prefix = get_prefix(row['token'])
        if prefix:
            prefix_pos[prefix]['total'] += 1
            if row['line_initial']:
                prefix_pos[prefix]['init'] += 1
            if row['line_final']:
                prefix_pos[prefix]['final'] += 1

    # Baselines
    total = sum(p['total'] for p in prefix_pos.values())
    total_init = sum(p['init'] for p in prefix_pos.values())
    total_final = sum(p['final'] for p in prefix_pos.values())
    base_init = total_init / total if total > 0 else 0
    base_final = total_final / total if total > 0 else 0

    print(f"\nBaseline: initial={base_init:.1%}, final={base_final:.1%}")

    print(f"\n{'Prefix':<8} {'Init Enr':>10} {'Final Enr':>12}")
    print("-"*35)

    results = {}
    for prefix in sorted(prefix_pos.keys(), key=lambda p: prefix_pos[p]['total'], reverse=True)[:10]:
        stats = prefix_pos[prefix]
        if stats['total'] < 20:
            continue
        init_rate = stats['init'] / stats['total']
        final_rate = stats['final'] / stats['total']
        init_enr = init_rate / base_init if base_init > 0 else 0
        final_enr = final_rate / base_final if base_final > 0 else 0
        results[prefix] = {'init': init_enr, 'final': final_enr}
        init_m = "*" if init_enr > 1.5 or init_enr < 0.5 else ""
        final_m = "*" if final_enr > 1.5 or final_enr < 0.5 else ""
        print(f"{prefix:<8} {init_enr:>9.2f}x{init_m} {final_enr:>11.2f}x{final_m}")

    # Check for pattern
    if results:
        init_spread = max(r['init'] for r in results.values()) - min(r['init'] for r in results.values())
        final_spread = max(r['final'] for r in results.values()) - min(r['final'] for r in results.values())
        print(f"\nEnrichment spreads: initial={init_spread:.2f}, final={final_spread:.2f}")
        if init_spread > 2.0 or final_spread > 2.0:
            print("-> STRONG POSITIONAL GRAMMAR (like B)")
        elif init_spread > 1.0 or final_spread > 1.0:
            print("-> MODERATE POSITIONAL PATTERNS")
        else:
            print("-> NO POSITIONAL GRAMMAR (position-free)")

    return results

def compare_systems():
    """Compare A vs B patterns."""
    print("="*70)
    print("CURRIER A vs B PHASE PATTERN COMPARISON")
    print("="*70)

    a_data = load_a_data()
    b_data = load_b_data()

    print(f"\nLoaded: {len(a_data)} Currier A tokens, {len(b_data)} Currier B tokens")

    # Test A
    print("\n" + "#"*70)
    print("# CURRIER A")
    print("#"*70)
    a_kernel = test_prefix_kernel(a_data, "Currier A")
    a_link = test_link_affinity(a_data, "Currier A")
    a_pos = test_positional(a_data, "Currier A")

    # Test B for comparison
    print("\n" + "#"*70)
    print("# CURRIER B (reference)")
    print("#"*70)
    b_kernel = test_prefix_kernel(b_data, "Currier B")
    b_link = test_link_affinity(b_data, "Currier B")
    b_pos = test_positional(b_data, "Currier B")

    # Summary comparison
    print("\n" + "="*70)
    print("SUMMARY COMPARISON")
    print("="*70)

    print("""
    Pattern              Currier A              Currier B
    ----------------------------------------------------------------""")

    # Kernel dichotomy
    if a_kernel and b_kernel:
        a_range = max(a_kernel.values()) - min(a_kernel.values()) if a_kernel else 0
        b_range = max(b_kernel.values()) - min(b_kernel.values()) if b_kernel else 0
        print(f"    Kernel spread        {a_range:>6.1f}%               {b_range:>6.1f}%")

    # LINK affinity
    if a_link and b_link:
        a_link_spread = max(a_link.values()) - min(a_link.values()) if a_link else 0
        b_link_spread = max(b_link.values()) - min(b_link.values()) if b_link else 0
        print(f"    LINK enr. spread     {a_link_spread:>6.2f}x              {b_link_spread:>6.2f}x")

    print("""
    ----------------------------------------------------------------

    Interpretation:
    - If A shows FLAT patterns (low spreads), it confirms A is position-free
    - If A shows B-like patterns (high spreads), A has hidden structure
    """)

if __name__ == '__main__':
    compare_systems()
