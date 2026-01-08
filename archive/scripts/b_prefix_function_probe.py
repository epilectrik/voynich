"""
Probe: How do prefixes function in Currier B?

Questions:
1. Do prefixes correlate with grammar classes (49 classes)?
2. Do prefixes have positional preferences (line-initial/final)?
3. Do prefixes correlate with kernel proximity?
4. Do prefixes correlate with LINK proximity?
5. Do prefixes show section-specific patterns within B?
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR_FILE = BASE / "results" / "canonical_grammar.json"

# All known prefixes
A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
HT_PREFIXES = ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'do', 'ta', 'ke', 'al', 'po', 'ko', 'yd', 'ysh', 'ych', 'kch', 'ks']
L_COMPOUNDS = ['lch', 'lk', 'lsh', 'lkch', 'lo', 'lr', 'ls']
EXTENDED_CLUSTERS = ['ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ts', 'tsh', 'ps', 'psh', 'pch', 'tch', 'dch', 'fch', 'rch', 'sch']

# Kernel characters
KERNEL = {'k', 'h', 'e'}
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

def get_prefix(token):
    """Extract prefix from token."""
    all_prefixes = L_COMPOUNDS + EXTENDED_CLUSTERS + HT_PREFIXES + A_PREFIXES
    for p in sorted(all_prefixes, key=len, reverse=True):
        if token.startswith(p):
            return p
    # Check for single-char kernel start
    if token and token[0] in KERNEL:
        return token[0]
    return None

def load_b_data():
    """Load Currier B tokens with context."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('language') == 'B' and row.get('transcriber') == 'H':
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

def test_prefix_position(data):
    """Test 1: Do prefixes have positional preferences?"""
    print("\n" + "="*70)
    print("TEST 1: PREFIX POSITIONAL PREFERENCES")
    print("="*70)

    prefix_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'mid': 0, 'total': 0})

    for row in data:
        prefix = get_prefix(row['token'])
        if prefix:
            prefix_positions[prefix]['total'] += 1
            if row['line_initial']:
                prefix_positions[prefix]['initial'] += 1
            elif row['line_final']:
                prefix_positions[prefix]['final'] += 1
            else:
                prefix_positions[prefix]['mid'] += 1

    # Calculate overall rates for baseline
    total = sum(p['total'] for p in prefix_positions.values())
    total_initial = sum(p['initial'] for p in prefix_positions.values())
    total_final = sum(p['final'] for p in prefix_positions.values())

    base_initial_rate = total_initial / total if total > 0 else 0
    base_final_rate = total_final / total if total > 0 else 0

    print(f"\nBaseline rates: initial={base_initial_rate:.1%}, final={base_final_rate:.1%}")
    print(f"\n{'Prefix':<8} {'Total':>8} {'Init%':>8} {'Final%':>8} {'Init Enr':>10} {'Final Enr':>10}")
    print("-"*60)

    enrichments = []
    for prefix in sorted(prefix_positions.keys(), key=lambda p: prefix_positions[p]['total'], reverse=True)[:20]:
        stats = prefix_positions[prefix]
        if stats['total'] < 10:
            continue
        init_rate = stats['initial'] / stats['total']
        final_rate = stats['final'] / stats['total']
        init_enr = init_rate / base_initial_rate if base_initial_rate > 0 else 0
        final_enr = final_rate / base_final_rate if base_final_rate > 0 else 0

        enrichments.append((prefix, init_enr, final_enr))

        init_marker = "*" if init_enr > 1.5 or init_enr < 0.5 else ""
        final_marker = "*" if final_enr > 1.5 or final_enr < 0.5 else ""

        print(f"{prefix:<8} {stats['total']:>8} {init_rate:>7.1%} {final_rate:>7.1%} {init_enr:>9.2f}x{init_marker} {final_enr:>9.2f}x{final_marker}")

    # Check for significant variation
    init_enrichments = [e[1] for e in enrichments if e[1] > 0]
    final_enrichments = [e[2] for e in enrichments if e[2] > 0]

    print(f"\nEnrichment variation:")
    print(f"  Initial: min={min(init_enrichments):.2f}x, max={max(init_enrichments):.2f}x, range={max(init_enrichments)-min(init_enrichments):.2f}")
    print(f"  Final: min={min(final_enrichments):.2f}x, max={max(final_enrichments):.2f}x, range={max(final_enrichments)-min(final_enrichments):.2f}")

    return enrichments

def test_prefix_kernel_proximity(data):
    """Test 2: Do prefixes correlate with kernel character presence?"""
    print("\n" + "="*70)
    print("TEST 2: PREFIX-KERNEL CORRELATION")
    print("="*70)

    prefix_kernel = defaultdict(lambda: {'has_kernel': 0, 'no_kernel': 0})

    for row in data:
        token = row['token']
        prefix = get_prefix(token)
        if prefix:
            has_kernel = any(c in KERNEL for c in token)
            if has_kernel:
                prefix_kernel[prefix]['has_kernel'] += 1
            else:
                prefix_kernel[prefix]['no_kernel'] += 1

    # Baseline kernel rate
    total_kernel = sum(p['has_kernel'] for p in prefix_kernel.values())
    total_no = sum(p['no_kernel'] for p in prefix_kernel.values())
    base_kernel_rate = total_kernel / (total_kernel + total_no) if (total_kernel + total_no) > 0 else 0

    print(f"\nBaseline kernel presence rate: {base_kernel_rate:.1%}")
    print(f"\n{'Prefix':<8} {'Total':>8} {'Kernel%':>10} {'Enrichment':>12}")
    print("-"*45)

    for prefix in sorted(prefix_kernel.keys(), key=lambda p: prefix_kernel[p]['has_kernel'] + prefix_kernel[p]['no_kernel'], reverse=True)[:15]:
        stats = prefix_kernel[prefix]
        total = stats['has_kernel'] + stats['no_kernel']
        if total < 10:
            continue
        kernel_rate = stats['has_kernel'] / total
        enrichment = kernel_rate / base_kernel_rate if base_kernel_rate > 0 else 0
        marker = "*" if enrichment > 1.3 or enrichment < 0.7 else ""
        print(f"{prefix:<8} {total:>8} {kernel_rate:>9.1%} {enrichment:>11.2f}x{marker}")

def test_prefix_link_proximity(data):
    """Test 3: Do prefixes appear near LINK tokens?"""
    print("\n" + "="*70)
    print("TEST 3: PREFIX-LINK PROXIMITY")
    print("="*70)

    # Build token sequences by folio/line
    sequences = defaultdict(list)
    for row in data:
        key = (row['folio'], row['line'])
        sequences[key].append(row['token'])

    # Count prefix appearances within 2 tokens of LINK
    prefix_near_link = defaultdict(lambda: {'near': 0, 'far': 0})

    for key, tokens in sequences.items():
        link_positions = [i for i, t in enumerate(tokens) if t in LINK_TOKENS]

        for i, token in enumerate(tokens):
            prefix = get_prefix(token)
            if not prefix:
                continue

            # Check if within 2 positions of any LINK
            near_link = any(abs(i - lp) <= 2 for lp in link_positions)

            if near_link:
                prefix_near_link[prefix]['near'] += 1
            else:
                prefix_near_link[prefix]['far'] += 1

    # Baseline
    total_near = sum(p['near'] for p in prefix_near_link.values())
    total_far = sum(p['far'] for p in prefix_near_link.values())
    base_near_rate = total_near / (total_near + total_far) if (total_near + total_far) > 0 else 0

    print(f"\nBaseline LINK-proximity rate: {base_near_rate:.1%}")
    print(f"\n{'Prefix':<8} {'Total':>8} {'Near%':>10} {'Enrichment':>12}")
    print("-"*45)

    for prefix in sorted(prefix_near_link.keys(), key=lambda p: prefix_near_link[p]['near'] + prefix_near_link[p]['far'], reverse=True)[:15]:
        stats = prefix_near_link[prefix]
        total = stats['near'] + stats['far']
        if total < 10:
            continue
        near_rate = stats['near'] / total
        enrichment = near_rate / base_near_rate if base_near_rate > 0 else 0
        marker = "*" if enrichment > 1.3 or enrichment < 0.7 else ""
        print(f"{prefix:<8} {total:>8} {near_rate:>9.1%} {enrichment:>11.2f}x{marker}")

def test_prefix_section(data):
    """Test 4: Do prefixes show section-specific patterns within B?"""
    print("\n" + "="*70)
    print("TEST 4: PREFIX-SECTION ASSOCIATION (within B)")
    print("="*70)

    prefix_section = defaultdict(lambda: defaultdict(int))
    section_totals = Counter()

    for row in data:
        section = row['section']
        if not section:
            continue
        prefix = get_prefix(row['token'])
        if prefix:
            prefix_section[prefix][section] += 1
            section_totals[section] += 1

    print(f"\nSections in B: {dict(section_totals)}")

    # Build contingency table for chi-square
    sections = sorted(section_totals.keys())
    prefixes = [p for p in prefix_section.keys() if sum(prefix_section[p].values()) >= 20]

    if len(sections) >= 2 and len(prefixes) >= 2:
        table = [[prefix_section[p][s] for s in sections] for p in prefixes]
        chi2, p_val, dof, expected = chi2_contingency(table)

        print(f"\nChi-square test (prefix × section):")
        print(f"  Chi2 = {chi2:.1f}, p = {p_val:.2e}, dof = {dof}")

        if p_val < 0.001:
            print("  -> SIGNIFICANT: Prefixes have section preferences")
        else:
            print("  -> NOT SIGNIFICANT: Prefixes distributed evenly across sections")

    # Show top section-specific prefixes
    print(f"\n{'Prefix':<8} {'Total':>8} ", end="")
    for s in sections[:5]:
        print(f"{s:>8}", end="")
    print()
    print("-"*50)

    for prefix in sorted(prefixes, key=lambda p: sum(prefix_section[p].values()), reverse=True)[:12]:
        total = sum(prefix_section[prefix].values())
        print(f"{prefix:<8} {total:>8} ", end="")
        for s in sections[:5]:
            count = prefix_section[prefix][s]
            pct = count / total * 100 if total > 0 else 0
            print(f"{pct:>7.0f}%", end="")
        print()

def test_prefix_class_mapping(data):
    """Test 5: Do prefixes map to specific functional behaviors?"""
    print("\n" + "="*70)
    print("TEST 5: PREFIX FUNCTIONAL CLASSIFICATION")
    print("="*70)

    # Group prefixes by type
    prefix_types = {
        'A_PREFIX': A_PREFIXES,
        'HT_PREFIX': HT_PREFIXES,
        'L_COMPOUND': L_COMPOUNDS,
        'EXT_CLUSTER': EXTENDED_CLUSTERS,
        'KERNEL': ['k', 'h', 'e']
    }

    type_stats = defaultdict(lambda: {
        'count': 0, 'kernel_contact': 0, 'link_adjacent': 0,
        'line_initial': 0, 'line_final': 0
    })

    # Build sequences for adjacency
    sequences = defaultdict(list)
    for row in data:
        key = (row['folio'], row['line'])
        sequences[key].append(row)

    for key, rows in sequences.items():
        for i, row in enumerate(rows):
            token = row['token']
            prefix = get_prefix(token)
            if not prefix:
                continue

            # Classify prefix type
            ptype = None
            for t, prefixes in prefix_types.items():
                if prefix in prefixes:
                    ptype = t
                    break
            if not ptype:
                ptype = 'OTHER'

            type_stats[ptype]['count'] += 1

            # Kernel contact
            if any(c in KERNEL for c in token):
                type_stats[ptype]['kernel_contact'] += 1

            # LINK adjacent
            if i > 0 and rows[i-1]['token'] in LINK_TOKENS:
                type_stats[ptype]['link_adjacent'] += 1
            if i < len(rows)-1 and rows[i+1]['token'] in LINK_TOKENS:
                type_stats[ptype]['link_adjacent'] += 1

            # Position
            if row['line_initial']:
                type_stats[ptype]['line_initial'] += 1
            if row['line_final']:
                type_stats[ptype]['line_final'] += 1

    print(f"\n{'Type':<12} {'Count':>8} {'Kernel%':>10} {'LINK-adj%':>12} {'Init%':>8} {'Final%':>8}")
    print("-"*65)

    for ptype in ['A_PREFIX', 'HT_PREFIX', 'L_COMPOUND', 'EXT_CLUSTER', 'KERNEL', 'OTHER']:
        stats = type_stats[ptype]
        if stats['count'] == 0:
            continue
        n = stats['count']
        kernel_pct = stats['kernel_contact'] / n * 100
        link_pct = stats['link_adjacent'] / n * 100
        init_pct = stats['line_initial'] / n * 100
        final_pct = stats['line_final'] / n * 100
        print(f"{ptype:<12} {n:>8} {kernel_pct:>9.1f}% {link_pct:>11.1f}% {init_pct:>7.1f}% {final_pct:>7.1f}%")

def main():
    print("="*70)
    print("CURRIER B PREFIX FUNCTION PROBE")
    print("="*70)

    data = load_b_data()
    print(f"\nLoaded {len(data)} Currier B tokens")

    # Count prefix distribution
    prefix_counts = Counter(get_prefix(row['token']) for row in data)
    prefix_counts = {k: v for k, v in prefix_counts.items() if k is not None}

    print(f"Tokens with identified prefix: {sum(prefix_counts.values())} ({sum(prefix_counts.values())/len(data):.1%})")
    print(f"Unique prefixes: {len(prefix_counts)}")

    print("\nTop 15 prefixes in B:")
    for prefix, count in sorted(prefix_counts.items(), key=lambda x: -x[1])[:15]:
        pct = count / len(data) * 100
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    test_prefix_position(data)
    test_prefix_kernel_proximity(data)
    test_prefix_link_proximity(data)
    test_prefix_section(data)
    test_prefix_class_mapping(data)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

if __name__ == '__main__':
    main()
