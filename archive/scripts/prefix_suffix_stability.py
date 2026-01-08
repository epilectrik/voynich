"""
Probe: Are prefix/suffix functional patterns stable across folios/regimes?

Or do different programs use different morphological vocabularies?
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, chi2_contingency

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
SIGNATURES = BASE / "results" / "control_signatures.json"

# Prefixes and suffixes
A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol']
COMMON_SUFFIXES = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey', 'ol', 'eey', 'al', 'r', 'dy', 'l', 'or', 'in', 'ody', 'am']

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

def load_data():
    """Load B data grouped by folio."""
    folio_data = defaultdict(list)
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('language') == 'B' and row.get('transcriber') == 'H':
                token = row.get('word', '')
                if token and '*' not in token:
                    folio_data[row['folio']].append(token)
    return folio_data

def load_regimes():
    """Load regime assignments if available."""
    try:
        with open(SIGNATURES, 'r') as f:
            data = json.load(f)
        # Extract regime from control signatures
        regimes = {}
        for folio, sig in data.get('signatures', {}).items():
            if 'regime' in sig:
                regimes[folio] = sig['regime']
        return regimes
    except:
        return {}

def test_prefix_distribution_by_folio(folio_data):
    """Test 1: Do folios use different prefix distributions?"""
    print("\n" + "="*70)
    print("TEST 1: PREFIX DISTRIBUTION BY FOLIO")
    print("="*70)

    folio_prefix_dist = {}

    for folio, tokens in folio_data.items():
        if len(tokens) < 50:
            continue
        prefix_counts = Counter(get_prefix(t) for t in tokens)
        prefix_counts = {k: v for k, v in prefix_counts.items() if k is not None}
        total = sum(prefix_counts.values())
        if total > 0:
            folio_prefix_dist[folio] = {p: prefix_counts.get(p, 0) / total for p in A_PREFIXES}

    # Calculate variance across folios for each prefix
    print(f"\nAnalyzing {len(folio_prefix_dist)} folios with 50+ tokens")

    print(f"\n{'Prefix':<8} {'Mean%':>8} {'Std%':>8} {'CV':>8} {'Min%':>8} {'Max%':>8}")
    print("-"*50)

    for prefix in A_PREFIXES:
        values = [folio_prefix_dist[f].get(prefix, 0) * 100 for f in folio_prefix_dist]
        mean_v = np.mean(values)
        std_v = np.std(values)
        cv = std_v / mean_v if mean_v > 0 else 0
        print(f"{prefix:<8} {mean_v:>7.1f}% {std_v:>7.1f}% {cv:>7.2f} {min(values):>7.1f}% {max(values):>7.1f}%")

    # Overall CV
    all_cvs = []
    for prefix in A_PREFIXES:
        values = [folio_prefix_dist[f].get(prefix, 0) for f in folio_prefix_dist]
        mean_v = np.mean(values)
        std_v = np.std(values)
        if mean_v > 0:
            all_cvs.append(std_v / mean_v)

    avg_cv = np.mean(all_cvs)
    print(f"\nAverage CV across prefixes: {avg_cv:.2f}")

    if avg_cv < 0.3:
        print("-> LOW variation: Prefix distribution is STABLE across folios")
    elif avg_cv < 0.6:
        print("-> MODERATE variation: Some folio-specific prefix preferences")
    else:
        print("-> HIGH variation: Prefixes are FOLIO-SPECIFIC")

    return folio_prefix_dist, avg_cv

def test_suffix_distribution_by_folio(folio_data):
    """Test 2: Do folios use different suffix distributions?"""
    print("\n" + "="*70)
    print("TEST 2: SUFFIX DISTRIBUTION BY FOLIO")
    print("="*70)

    folio_suffix_dist = {}

    for folio, tokens in folio_data.items():
        if len(tokens) < 50:
            continue
        suffix_counts = Counter(get_suffix(t) for t in tokens)
        suffix_counts = {k: v for k, v in suffix_counts.items() if k is not None}
        total = sum(suffix_counts.values())
        if total > 0:
            folio_suffix_dist[folio] = {s: suffix_counts.get(s, 0) / total for s in COMMON_SUFFIXES}

    print(f"\nAnalyzing {len(folio_suffix_dist)} folios")

    print(f"\n{'Suffix':<8} {'Mean%':>8} {'Std%':>8} {'CV':>8} {'Min%':>8} {'Max%':>8}")
    print("-"*50)

    top_suffixes = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey', 'dy', 'al']
    for suffix in top_suffixes:
        values = [folio_suffix_dist[f].get(suffix, 0) * 100 for f in folio_suffix_dist]
        mean_v = np.mean(values)
        std_v = np.std(values)
        cv = std_v / mean_v if mean_v > 0 else 0
        print(f"-{suffix:<7} {mean_v:>7.1f}% {std_v:>7.1f}% {cv:>7.2f} {min(values):>7.1f}% {max(values):>7.1f}%")

    # Overall CV
    all_cvs = []
    for suffix in COMMON_SUFFIXES:
        values = [folio_suffix_dist[f].get(suffix, 0) for f in folio_suffix_dist]
        mean_v = np.mean(values)
        std_v = np.std(values)
        if mean_v > 0.01:  # Only count suffixes with meaningful presence
            all_cvs.append(std_v / mean_v)

    avg_cv = np.mean(all_cvs)
    print(f"\nAverage CV across suffixes: {avg_cv:.2f}")

    if avg_cv < 0.3:
        print("-> LOW variation: Suffix distribution is STABLE across folios")
    elif avg_cv < 0.6:
        print("-> MODERATE variation: Some folio-specific suffix preferences")
    else:
        print("-> HIGH variation: Suffixes are FOLIO-SPECIFIC")

    return folio_suffix_dist, avg_cv

def test_regime_morphology(folio_data, regimes):
    """Test 3: Do regimes have different prefix/suffix profiles?"""
    print("\n" + "="*70)
    print("TEST 3: MORPHOLOGY BY CONTROL REGIME")
    print("="*70)

    if not regimes:
        print("\nNo regime data available - skipping")
        return

    regime_prefixes = defaultdict(Counter)
    regime_suffixes = defaultdict(Counter)

    for folio, tokens in folio_data.items():
        regime = regimes.get(folio)
        if not regime:
            continue
        for token in tokens:
            prefix = get_prefix(token)
            suffix = get_suffix(token)
            if prefix:
                regime_prefixes[regime][prefix] += 1
            if suffix:
                regime_suffixes[regime][suffix] += 1

    print(f"\nRegimes found: {sorted(regime_prefixes.keys())}")

    # Prefix distribution by regime
    print("\nPrefix distribution by regime:")
    print(f"{'Regime':<12}", end="")
    for p in A_PREFIXES[:6]:
        print(f"{p:>8}", end="")
    print()

    for regime in sorted(regime_prefixes.keys()):
        total = sum(regime_prefixes[regime].values())
        print(f"{regime:<12}", end="")
        for p in A_PREFIXES[:6]:
            pct = regime_prefixes[regime][p] / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end="")
        print()

    # Chi-square test
    regimes_list = sorted(regime_prefixes.keys())
    if len(regimes_list) >= 2:
        table = [[regime_prefixes[r][p] for p in A_PREFIXES] for r in regimes_list]
        chi2, p_val, dof, _ = chi2_contingency(table)
        print(f"\nChi-square (regime × prefix): chi2={chi2:.1f}, p={p_val:.2e}")
        if p_val < 0.001:
            print("-> SIGNIFICANT: Regimes have different prefix profiles")
        else:
            print("-> NOT SIGNIFICANT: Prefix distribution is regime-independent")

    # Same for suffixes
    print("\nSuffix distribution by regime:")
    top_suff = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey']
    print(f"{'Regime':<12}", end="")
    for s in top_suff:
        print(f"{s:>8}", end="")
    print()

    for regime in sorted(regime_suffixes.keys()):
        total = sum(regime_suffixes[regime].values())
        print(f"{regime:<12}", end="")
        for s in top_suff:
            pct = regime_suffixes[regime][s] / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end="")
        print()

    if len(regimes_list) >= 2:
        table = [[regime_suffixes[r][s] for s in COMMON_SUFFIXES] for r in regimes_list]
        # Filter out zero columns
        table = [[row[i] for i in range(len(row)) if sum(t[i] for t in table) > 0] for row in table]
        chi2, p_val, dof, _ = chi2_contingency(table)
        print(f"\nChi-square (regime × suffix): chi2={chi2:.1f}, p={p_val:.2e}")
        if p_val < 0.001:
            print("-> SIGNIFICANT: Regimes have different suffix profiles")
        else:
            print("-> NOT SIGNIFICANT: Suffix distribution is regime-independent")

def test_section_morphology(folio_data):
    """Test 4: Do sections within B have different morphology?"""
    print("\n" + "="*70)
    print("TEST 4: MORPHOLOGY BY SECTION (within B)")
    print("="*70)

    # Need to reload with section info
    section_prefixes = defaultdict(Counter)
    section_suffixes = defaultdict(Counter)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('language') == 'B' and row.get('transcriber') == 'H':
                token = row.get('word', '')
                section = row.get('section', '')
                if token and '*' not in token and section:
                    prefix = get_prefix(token)
                    suffix = get_suffix(token)
                    if prefix:
                        section_prefixes[section][prefix] += 1
                    if suffix:
                        section_suffixes[section][suffix] += 1

    print(f"\nSections: {sorted(section_prefixes.keys())}")

    # Prefix by section
    print("\nPrefix distribution by section:")
    print(f"{'Section':<10}", end="")
    for p in A_PREFIXES[:6]:
        print(f"{p:>8}", end="")
    print()

    for section in sorted(section_prefixes.keys()):
        total = sum(section_prefixes[section].values())
        print(f"{section:<10}", end="")
        for p in A_PREFIXES[:6]:
            pct = section_prefixes[section][p] / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end="")
        print()

    sections_list = sorted(section_prefixes.keys())
    if len(sections_list) >= 2:
        table = [[section_prefixes[s][p] for p in A_PREFIXES] for s in sections_list]
        chi2, p_val, dof, _ = chi2_contingency(table)
        print(f"\nChi-square (section × prefix): chi2={chi2:.1f}, p={p_val:.2e}")
        if p_val < 0.001:
            print("-> SIGNIFICANT: Sections have different prefix profiles")
        else:
            print("-> NOT SIGNIFICANT")

def test_functional_stability(folio_data):
    """Test 5: Are FUNCTIONAL patterns (kernel, LINK) stable even if vocabulary varies?"""
    print("\n" + "="*70)
    print("TEST 5: FUNCTIONAL PATTERN STABILITY")
    print("="*70)
    print("\nEven if vocabulary varies, do the FUNCTIONAL roles stay consistent?")

    KERNEL = {'k', 'h', 'e'}

    # For each folio, calculate:
    # 1. Correlation between prefix kernel-contact rate and global pattern
    # 2. Whether kernel-light prefixes (da, sa) stay kernel-light

    folio_prefix_kernel = {}

    for folio, tokens in folio_data.items():
        if len(tokens) < 100:
            continue

        prefix_kernel = defaultdict(lambda: {'kernel': 0, 'total': 0})
        for token in tokens:
            prefix = get_prefix(token)
            if prefix:
                prefix_kernel[prefix]['total'] += 1
                if any(c in KERNEL for c in token):
                    prefix_kernel[prefix]['kernel'] += 1

        folio_prefix_kernel[folio] = {
            p: prefix_kernel[p]['kernel'] / prefix_kernel[p]['total']
            if prefix_kernel[p]['total'] > 10 else None
            for p in A_PREFIXES
        }

    # Check if da/sa stay kernel-light across folios
    print("\nKernel contact rate for da/sa across folios:")
    da_rates = [folio_prefix_kernel[f]['da'] for f in folio_prefix_kernel if folio_prefix_kernel[f]['da'] is not None]

    if da_rates:
        print(f"  da: mean={np.mean(da_rates)*100:.1f}%, std={np.std(da_rates)*100:.1f}%, range=[{min(da_rates)*100:.1f}%, {max(da_rates)*100:.1f}%]")
        if max(da_rates) < 0.2:
            print("  -> da is CONSISTENTLY kernel-light across all folios")
        else:
            print("  -> da kernel contact VARIES by folio")

    # Check if ch/sh stay kernel-heavy
    print("\nKernel contact rate for ch/sh across folios:")
    ch_rates = [folio_prefix_kernel[f]['ch'] for f in folio_prefix_kernel if folio_prefix_kernel[f]['ch'] is not None]
    sh_rates = [folio_prefix_kernel[f]['sh'] for f in folio_prefix_kernel if folio_prefix_kernel[f]['sh'] is not None]

    if ch_rates:
        print(f"  ch: mean={np.mean(ch_rates)*100:.1f}%, min={min(ch_rates)*100:.1f}%")
        if min(ch_rates) > 0.9:
            print("  -> ch is CONSISTENTLY kernel-heavy (100%) across all folios")
    if sh_rates:
        print(f"  sh: mean={np.mean(sh_rates)*100:.1f}%, min={min(sh_rates)*100:.1f}%")
        if min(sh_rates) > 0.9:
            print("  -> sh is CONSISTENTLY kernel-heavy (100%) across all folios")

def main():
    print("="*70)
    print("PREFIX/SUFFIX STABILITY ACROSS FOLIOS/REGIMES")
    print("="*70)

    folio_data = load_data()
    regimes = load_regimes()

    print(f"\nLoaded {len(folio_data)} folios, {sum(len(v) for v in folio_data.values())} tokens")
    if regimes:
        print(f"Regime assignments: {len(regimes)} folios")

    prefix_dist, prefix_cv = test_prefix_distribution_by_folio(folio_data)
    suffix_dist, suffix_cv = test_suffix_distribution_by_folio(folio_data)
    test_regime_morphology(folio_data, regimes)
    test_section_morphology(folio_data)
    test_functional_stability(folio_data)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"""
Prefix CV across folios: {prefix_cv:.2f}
Suffix CV across folios: {suffix_cv:.2f}

Interpretation:
- CV < 0.3: Stable (same distribution everywhere)
- CV 0.3-0.6: Moderate variation (preferences exist)
- CV > 0.6: High variation (folio-specific vocabulary)
""")

if __name__ == '__main__':
    main()
