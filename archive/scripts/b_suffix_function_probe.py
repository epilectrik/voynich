"""
Probe: How do suffixes function in Currier B?

Parallel to BPF prefix analysis - checking:
1. Positional preferences (line-initial/final)
2. Kernel correlation
3. LINK proximity
4. Section association
5. Prefix-suffix interaction
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Known suffixes (from CAS-MORPH and full_token_audit)
COMMON_SUFFIXES = ['aiin', 'ain', 'ar', 'or', 'al', 'ol', 'dy', 'ey', 'y', 'r', 'l', 's', 'd',
                   'chy', 'shy', 'eey', 'ody', 'edy', 'oly', 'am', 'an', 'in', 'om']

# Kernel characters
KERNEL = {'k', 'h', 'e'}
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

def get_suffix(token):
    """Extract suffix from token."""
    for s in sorted(COMMON_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            return s
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

def test_suffix_position(data):
    """Test 1: Do suffixes have positional preferences?"""
    print("\n" + "="*70)
    print("TEST 1: SUFFIX POSITIONAL PREFERENCES")
    print("="*70)

    suffix_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'mid': 0, 'total': 0})

    for row in data:
        suffix = get_suffix(row['token'])
        if suffix:
            suffix_positions[suffix]['total'] += 1
            if row['line_initial']:
                suffix_positions[suffix]['initial'] += 1
            elif row['line_final']:
                suffix_positions[suffix]['final'] += 1
            else:
                suffix_positions[suffix]['mid'] += 1

    # Baseline rates
    total = sum(p['total'] for p in suffix_positions.values())
    total_initial = sum(p['initial'] for p in suffix_positions.values())
    total_final = sum(p['final'] for p in suffix_positions.values())

    base_initial_rate = total_initial / total if total > 0 else 0
    base_final_rate = total_final / total if total > 0 else 0

    print(f"\nBaseline rates: initial={base_initial_rate:.1%}, final={base_final_rate:.1%}")
    print(f"\n{'Suffix':<8} {'Total':>8} {'Init%':>8} {'Final%':>8} {'Init Enr':>10} {'Final Enr':>10}")
    print("-"*60)

    for suffix in sorted(suffix_positions.keys(), key=lambda s: suffix_positions[s]['total'], reverse=True):
        stats = suffix_positions[suffix]
        if stats['total'] < 20:
            continue
        init_rate = stats['initial'] / stats['total']
        final_rate = stats['final'] / stats['total']
        init_enr = init_rate / base_initial_rate if base_initial_rate > 0 else 0
        final_enr = final_rate / base_final_rate if base_final_rate > 0 else 0

        init_marker = "*" if init_enr > 1.5 or init_enr < 0.5 else ""
        final_marker = "*" if final_enr > 1.5 or final_enr < 0.5 else ""

        print(f"{suffix:<8} {stats['total']:>8} {init_rate:>7.1%} {final_rate:>7.1%} {init_enr:>9.2f}x{init_marker} {final_enr:>9.2f}x{final_marker}")

def test_suffix_kernel(data):
    """Test 2: Do suffixes correlate with kernel presence?"""
    print("\n" + "="*70)
    print("TEST 2: SUFFIX-KERNEL CORRELATION")
    print("="*70)

    suffix_kernel = defaultdict(lambda: {'has_kernel': 0, 'no_kernel': 0})

    for row in data:
        token = row['token']
        suffix = get_suffix(token)
        if suffix:
            # Check kernel in non-suffix part
            base = token[:-len(suffix)]
            has_kernel = any(c in KERNEL for c in base)
            if has_kernel:
                suffix_kernel[suffix]['has_kernel'] += 1
            else:
                suffix_kernel[suffix]['no_kernel'] += 1

    # Baseline
    total_kernel = sum(p['has_kernel'] for p in suffix_kernel.values())
    total_no = sum(p['no_kernel'] for p in suffix_kernel.values())
    base_kernel_rate = total_kernel / (total_kernel + total_no) if (total_kernel + total_no) > 0 else 0

    print(f"\nBaseline kernel presence (in base): {base_kernel_rate:.1%}")
    print(f"\n{'Suffix':<8} {'Total':>8} {'Kernel%':>10} {'Enrichment':>12}")
    print("-"*45)

    for suffix in sorted(suffix_kernel.keys(), key=lambda s: suffix_kernel[s]['has_kernel'] + suffix_kernel[s]['no_kernel'], reverse=True):
        stats = suffix_kernel[suffix]
        total = stats['has_kernel'] + stats['no_kernel']
        if total < 20:
            continue
        kernel_rate = stats['has_kernel'] / total
        enrichment = kernel_rate / base_kernel_rate if base_kernel_rate > 0 else 0
        marker = "*" if enrichment > 1.3 or enrichment < 0.7 else ""
        print(f"{suffix:<8} {total:>8} {kernel_rate:>9.1%} {enrichment:>11.2f}x{marker}")

def test_suffix_link(data):
    """Test 3: Do suffixes appear near LINK tokens?"""
    print("\n" + "="*70)
    print("TEST 3: SUFFIX-LINK PROXIMITY")
    print("="*70)

    # Build sequences
    sequences = defaultdict(list)
    for row in data:
        key = (row['folio'], row['line'])
        sequences[key].append(row['token'])

    suffix_near_link = defaultdict(lambda: {'near': 0, 'far': 0})

    for key, tokens in sequences.items():
        link_positions = [i for i, t in enumerate(tokens) if t in LINK_TOKENS]

        for i, token in enumerate(tokens):
            suffix = get_suffix(token)
            if not suffix:
                continue

            near_link = any(abs(i - lp) <= 2 for lp in link_positions)
            if near_link:
                suffix_near_link[suffix]['near'] += 1
            else:
                suffix_near_link[suffix]['far'] += 1

    # Baseline
    total_near = sum(p['near'] for p in suffix_near_link.values())
    total_far = sum(p['far'] for p in suffix_near_link.values())
    base_near_rate = total_near / (total_near + total_far) if (total_near + total_far) > 0 else 0

    print(f"\nBaseline LINK-proximity rate: {base_near_rate:.1%}")
    print(f"\n{'Suffix':<8} {'Total':>8} {'Near%':>10} {'Enrichment':>12}")
    print("-"*45)

    for suffix in sorted(suffix_near_link.keys(), key=lambda s: suffix_near_link[s]['near'] + suffix_near_link[s]['far'], reverse=True):
        stats = suffix_near_link[suffix]
        total = stats['near'] + stats['far']
        if total < 20:
            continue
        near_rate = stats['near'] / total
        enrichment = near_rate / base_near_rate if base_near_rate > 0 else 0
        marker = "*" if enrichment > 1.3 or enrichment < 0.7 else ""
        print(f"{suffix:<8} {total:>8} {near_rate:>9.1%} {enrichment:>11.2f}x{marker}")

def test_suffix_section(data):
    """Test 4: Do suffixes show section-specific patterns?"""
    print("\n" + "="*70)
    print("TEST 4: SUFFIX-SECTION ASSOCIATION")
    print("="*70)

    suffix_section = defaultdict(lambda: defaultdict(int))
    section_totals = Counter()

    for row in data:
        section = row['section']
        if not section:
            continue
        suffix = get_suffix(row['token'])
        if suffix:
            suffix_section[suffix][section] += 1
            section_totals[section] += 1

    print(f"\nSections in B: {dict(section_totals)}")

    sections = sorted(section_totals.keys())
    suffixes = [s for s in suffix_section.keys() if sum(suffix_section[s].values()) >= 50]

    if len(sections) >= 2 and len(suffixes) >= 2:
        table = [[suffix_section[s][sec] for sec in sections] for s in suffixes]
        chi2, p_val, dof, expected = chi2_contingency(table)

        print(f"\nChi-square test (suffix × section):")
        print(f"  Chi2 = {chi2:.1f}, p = {p_val:.2e}, dof = {dof}")

        if p_val < 0.001:
            print("  -> SIGNIFICANT: Suffixes have section preferences")
        else:
            print("  -> NOT SIGNIFICANT: Suffixes distributed evenly")

    print(f"\n{'Suffix':<8} {'Total':>8} ", end="")
    for s in sections[:5]:
        print(f"{s:>8}", end="")
    print()
    print("-"*55)

    for suffix in sorted(suffixes, key=lambda s: sum(suffix_section[s].values()), reverse=True)[:15]:
        total = sum(suffix_section[suffix].values())
        print(f"{suffix:<8} {total:>8} ", end="")
        for s in sections[:5]:
            count = suffix_section[suffix][s]
            pct = count / total * 100 if total > 0 else 0
            print(f"{pct:>7.0f}%", end="")
        print()

def test_prefix_suffix_interaction(data):
    """Test 5: Do prefix-suffix combinations show patterns?"""
    print("\n" + "="*70)
    print("TEST 5: PREFIX-SUFFIX INTERACTION")
    print("="*70)

    # Get prefixes
    A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    def get_prefix(token):
        for p in sorted(A_PREFIXES, key=len, reverse=True):
            if token.startswith(p):
                return p
        return None

    prefix_suffix = defaultdict(lambda: defaultdict(int))

    for row in data:
        token = row['token']
        prefix = get_prefix(token)
        suffix = get_suffix(token)
        if prefix and suffix:
            prefix_suffix[prefix][suffix] += 1

    # Chi-square for independence
    prefixes = sorted(prefix_suffix.keys())
    suffixes = list(set(s for p in prefixes for s in prefix_suffix[p].keys()))
    suffixes = [s for s in suffixes if sum(prefix_suffix[p][s] for p in prefixes) >= 20]

    if len(prefixes) >= 2 and len(suffixes) >= 2:
        table = [[prefix_suffix[p][s] for s in suffixes] for p in prefixes]
        chi2, p_val, dof, expected = chi2_contingency(table)

        print(f"\nChi-square test (prefix × suffix independence):")
        print(f"  Chi2 = {chi2:.1f}, p = {p_val:.2e}, dof = {dof}")

        if p_val < 0.001:
            print("  -> DEPENDENT: Prefix constrains suffix choice")
        else:
            print("  -> INDEPENDENT: Prefix and suffix combine freely")

    # Show matrix
    print(f"\nPrefix × Suffix frequency (top combinations):")
    print(f"{'':>8}", end="")
    for s in sorted(suffixes, key=lambda x: sum(prefix_suffix[p][x] for p in prefixes), reverse=True)[:8]:
        print(f"{s:>8}", end="")
    print()

    for p in prefixes:
        total_p = sum(prefix_suffix[p].values())
        if total_p < 50:
            continue
        print(f"{p:>8}", end="")
        for s in sorted(suffixes, key=lambda x: sum(prefix_suffix[p][x] for p in prefixes), reverse=True)[:8]:
            count = prefix_suffix[p][s]
            pct = count / total_p * 100 if total_p > 0 else 0
            print(f"{pct:>7.0f}%", end="")
        print()

def main():
    print("="*70)
    print("CURRIER B SUFFIX FUNCTION PROBE")
    print("="*70)

    data = load_b_data()
    print(f"\nLoaded {len(data)} Currier B tokens")

    # Count suffix distribution
    suffix_counts = Counter(get_suffix(row['token']) for row in data)
    suffix_counts = {k: v for k, v in suffix_counts.items() if k is not None}

    print(f"Tokens with identified suffix: {sum(suffix_counts.values())} ({sum(suffix_counts.values())/len(data):.1%})")
    print(f"Unique suffixes: {len(suffix_counts)}")

    print("\nTop 15 suffixes in B:")
    for suffix, count in sorted(suffix_counts.items(), key=lambda x: -x[1])[:15]:
        pct = count / len(data) * 100
        print(f"  -{suffix}: {count} ({pct:.1f}%)")

    test_suffix_position(data)
    test_suffix_kernel(data)
    test_suffix_link(data)
    test_suffix_section(data)
    test_prefix_suffix_interaction(data)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

if __name__ == '__main__':
    main()
