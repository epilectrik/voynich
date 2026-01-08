"""
Test: Does AZC show the same phase-encoded morphology patterns as Currier B?

Testing:
1. Kernel dichotomy in prefixes
2. Kernel dichotomy in suffixes
3. LINK affinity patterns
4. Positional preferences
5. Prefix-suffix constraints
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Same classifications as B analysis
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

def load_azc_data():
    """Load AZC tokens (language = NA or empty, sections A/Z/C)."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            # AZC = not classified as A or B
            lang = row.get('language', '')
            section = row.get('section', '')
            if lang not in ['A', 'B'] or section in ['A', 'Z', 'C']:
                token = row.get('word', '')
                if token and '*' not in token:
                    data.append({
                        'token': token,
                        'folio': row['folio'],
                        'line': row.get('line_number', '1'),
                        'section': section,
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

    for prefix in sorted(prefix_kernel.keys(), key=lambda p: prefix_kernel[p]['total'], reverse=True):
        stats = prefix_kernel[prefix]
        if stats['total'] < 5:
            continue
        kernel_pct = stats['kernel'] / stats['total'] * 100
        print(f"{prefix:<8} {stats['total']:>8} {kernel_pct:>9.1f}%")

    # Check for dichotomy
    kernel_rates = []
    for prefix, stats in prefix_kernel.items():
        if stats['total'] >= 10:
            kernel_rates.append(stats['kernel'] / stats['total'])

    if kernel_rates:
        print(f"\nKernel rate range: {min(kernel_rates)*100:.1f}% - {max(kernel_rates)*100:.1f}%")
        if max(kernel_rates) > 0.9 and min(kernel_rates) < 0.2:
            print("-> DICHOTOMY PRESENT (like B)")
        else:
            print("-> NO clear dichotomy")

def test_suffix_kernel(data, label):
    """Test suffix kernel contact patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 2: SUFFIX KERNEL DICHOTOMY ({label})")
    print("="*70)

    suffix_kernel = defaultdict(lambda: {'kernel': 0, 'total': 0})

    for row in data:
        token = row['token']
        suffix = get_suffix(token)
        if suffix:
            base = token[:-len(suffix)]
            suffix_kernel[suffix]['total'] += 1
            if any(c in KERNEL for c in base):
                suffix_kernel[suffix]['kernel'] += 1

    print(f"\n{'Suffix':<8} {'Total':>8} {'Kernel%':>10}")
    print("-"*30)

    for suffix in sorted(suffix_kernel.keys(), key=lambda s: suffix_kernel[s]['total'], reverse=True)[:12]:
        stats = suffix_kernel[suffix]
        if stats['total'] < 5:
            continue
        kernel_pct = stats['kernel'] / stats['total'] * 100
        print(f"-{suffix:<7} {stats['total']:>8} {kernel_pct:>9.1f}%")

def test_link_affinity(data, label):
    """Test LINK proximity patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 3: LINK AFFINITY ({label})")
    print("="*70)

    # Build sequences
    sequences = defaultdict(list)
    for row in data:
        key = (row['folio'], row['line'])
        sequences[key].append(row['token'])

    prefix_link = defaultdict(lambda: {'near': 0, 'far': 0})
    suffix_link = defaultdict(lambda: {'near': 0, 'far': 0})

    for key, tokens in sequences.items():
        link_positions = [i for i, t in enumerate(tokens) if t in LINK_TOKENS]

        for i, token in enumerate(tokens):
            near_link = any(abs(i - lp) <= 2 for lp in link_positions)

            prefix = get_prefix(token)
            suffix = get_suffix(token)

            if prefix:
                if near_link:
                    prefix_link[prefix]['near'] += 1
                else:
                    prefix_link[prefix]['far'] += 1

            if suffix:
                if near_link:
                    suffix_link[suffix]['near'] += 1
                else:
                    suffix_link[suffix]['far'] += 1

    # Calculate baseline
    total_near = sum(p['near'] for p in prefix_link.values())
    total_far = sum(p['far'] for p in prefix_link.values())
    base_rate = total_near / (total_near + total_far) if (total_near + total_far) > 0 else 0

    print(f"\nBaseline LINK-proximity: {base_rate:.1%}")

    print(f"\n{'Prefix':<8} {'Near%':>10} {'Enrichment':>12}")
    print("-"*35)

    for prefix in sorted(prefix_link.keys(), key=lambda p: prefix_link[p]['near'] + prefix_link[p]['far'], reverse=True)[:8]:
        stats = prefix_link[prefix]
        total = stats['near'] + stats['far']
        if total < 10:
            continue
        near_rate = stats['near'] / total
        enr = near_rate / base_rate if base_rate > 0 else 0
        marker = "*" if enr > 1.3 or enr < 0.7 else ""
        print(f"{prefix:<8} {near_rate*100:>9.1f}% {enr:>11.2f}x{marker}")

    print(f"\n{'Suffix':<8} {'Near%':>10} {'Enrichment':>12}")
    print("-"*35)

    # Baseline for suffixes
    total_near_s = sum(p['near'] for p in suffix_link.values())
    total_far_s = sum(p['far'] for p in suffix_link.values())
    base_rate_s = total_near_s / (total_near_s + total_far_s) if (total_near_s + total_far_s) > 0 else 0

    for suffix in sorted(suffix_link.keys(), key=lambda s: suffix_link[s]['near'] + suffix_link[s]['far'], reverse=True)[:8]:
        stats = suffix_link[suffix]
        total = stats['near'] + stats['far']
        if total < 10:
            continue
        near_rate = stats['near'] / total
        enr = near_rate / base_rate_s if base_rate_s > 0 else 0
        marker = "*" if enr > 1.3 or enr < 0.7 else ""
        print(f"-{suffix:<7} {near_rate*100:>9.1f}% {enr:>11.2f}x{marker}")

def test_positional(data, label):
    """Test line position patterns."""
    print(f"\n{'='*70}")
    print(f"TEST 4: POSITIONAL PATTERNS ({label})")
    print("="*70)

    prefix_pos = defaultdict(lambda: {'init': 0, 'final': 0, 'total': 0})
    suffix_pos = defaultdict(lambda: {'init': 0, 'final': 0, 'total': 0})

    for row in data:
        prefix = get_prefix(row['token'])
        suffix = get_suffix(row['token'])

        if prefix:
            prefix_pos[prefix]['total'] += 1
            if row['line_initial']:
                prefix_pos[prefix]['init'] += 1
            if row['line_final']:
                prefix_pos[prefix]['final'] += 1

        if suffix:
            suffix_pos[suffix]['total'] += 1
            if row['line_initial']:
                suffix_pos[suffix]['init'] += 1
            if row['line_final']:
                suffix_pos[suffix]['final'] += 1

    # Baselines
    total = sum(p['total'] for p in prefix_pos.values())
    total_init = sum(p['init'] for p in prefix_pos.values())
    total_final = sum(p['final'] for p in prefix_pos.values())
    base_init = total_init / total if total > 0 else 0
    base_final = total_final / total if total > 0 else 0

    print(f"\nBaseline: initial={base_init:.1%}, final={base_final:.1%}")

    print(f"\n{'Prefix':<8} {'Init Enr':>10} {'Final Enr':>12}")
    print("-"*35)

    for prefix in sorted(prefix_pos.keys(), key=lambda p: prefix_pos[p]['total'], reverse=True)[:8]:
        stats = prefix_pos[prefix]
        if stats['total'] < 10:
            continue
        init_rate = stats['init'] / stats['total']
        final_rate = stats['final'] / stats['total']
        init_enr = init_rate / base_init if base_init > 0 else 0
        final_enr = final_rate / base_final if base_final > 0 else 0
        init_m = "*" if init_enr > 1.5 or init_enr < 0.5 else ""
        final_m = "*" if final_enr > 1.5 or final_enr < 0.5 else ""
        print(f"{prefix:<8} {init_enr:>9.2f}x{init_m} {final_enr:>11.2f}x{final_m}")

def compare_to_b():
    """Compare AZC patterns to known B patterns."""
    print("\n" + "="*70)
    print("COMPARISON TO CURRIER B PATTERNS")
    print("="*70)

    print("""
    B Pattern                     AZC Expected if Similar
    ─────────────────────────────────────────────────────
    ch/sh = 100% kernel           ch/sh should be ~100%
    da = 5% kernel                da should be <10%
    -edy = 91% kernel             -edy should be >80%
    -in/-l/-r = 6-17% kernel      Should be <20%
    da LINK-attracted (1.66x)     da should be >1.3x
    ch LINK-avoiding (1.06x)      ch should be ~1.0x
    -l LINK-attracted (2.78x)     -l should be >2x
    """)

def main():
    print("="*70)
    print("AZC PHASE PATTERN ANALYSIS")
    print("="*70)

    data = load_azc_data()
    print(f"\nLoaded {len(data)} AZC tokens")

    if len(data) < 100:
        print("WARNING: Small sample size")

    # Show section breakdown
    sections = Counter(row['section'] for row in data)
    print(f"Sections: {dict(sections)}")

    test_prefix_kernel(data, "AZC")
    test_suffix_kernel(data, "AZC")
    test_link_affinity(data, "AZC")
    test_positional(data, "AZC")
    compare_to_b()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

if __name__ == '__main__':
    main()
