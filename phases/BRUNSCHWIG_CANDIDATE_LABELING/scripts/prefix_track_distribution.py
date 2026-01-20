#!/usr/bin/env python3
"""
PREFIX TRACK DISTRIBUTION TEST

Question: Do PREFIX distributions differ between registry-internal and
pipeline-participating vocabulary tracks in Currier A?

Expert guidance:
- Frame as DISTRIBUTION comparison, not function test
- Avoid Brunschwig product types (circularity with B)
- Compare PREFIX × SUFFIX interactions between tracks
- Measure PREFIX exclusivity

If distributions are similar: C383 unified semantics supported
If distributions differ: Track-specific PREFIX function (valid finding)
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['-aiin', '-ain', '-ar', '-or', '-al', '-ol', '-am', '-om', '-an', '-in',
                  '-ey', '-dy', '-edy', '-y', '-r', '-l', '-m', '-n', '-s', '-d']

def get_prefix(token):
    """Extract prefix from token."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def get_middle(token):
    """Extract middle from token."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def get_suffix(token):
    """Extract suffix from token."""
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s.replace('-', '')):
            return s
    return None

def entropy(counts):
    """Compute Shannon entropy from counts."""
    total = sum(counts.values())
    if total == 0:
        return 0
    h = 0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    """Load registry-internal MIDDLEs from 2-track classification."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_a_tokens():
    """Load all Currier A tokens."""
    tokens = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue
            tokens.append({
                'word': word,
                'folio': folio,
                'prefix': get_prefix(word),
                'middle': get_middle(word),
                'suffix': get_suffix(word)
            })
    return tokens

# ============================================================
# ANALYSIS
# ============================================================

def analyze_prefix_distribution(tokens, registry_internal):
    """Analyze PREFIX distribution by track."""

    # Classify tokens by track
    track_tokens = {'registry_internal': [], 'pipeline': []}

    for t in tokens:
        middle = t['middle']
        if middle in registry_internal:
            track_tokens['registry_internal'].append(t)
        else:
            track_tokens['pipeline'].append(t)

    print("=" * 70)
    print("PREFIX TRACK DISTRIBUTION TEST")
    print("=" * 70)
    print()
    print(f"Registry-internal tokens: {len(track_tokens['registry_internal'])}")
    print(f"Pipeline-participating tokens: {len(track_tokens['pipeline'])}")
    print()

    # PREFIX distribution by track
    print("=" * 70)
    print("PREFIX DISTRIBUTION BY TRACK")
    print("=" * 70)
    print()

    prefix_by_track = {}
    for track, toks in track_tokens.items():
        prefix_counts = Counter(t['prefix'] for t in toks if t['prefix'])
        prefix_by_track[track] = prefix_counts
        total = sum(prefix_counts.values())
        print(f"{track.upper()}:")
        for p, count in prefix_counts.most_common():
            pct = 100 * count / total
            print(f"  {p}: {count} ({pct:.1f}%)")
        print(f"  [no prefix]: {len([t for t in toks if not t['prefix']])}")
        print()

    # Chi-square test for distribution difference
    print("=" * 70)
    print("CHI-SQUARE TEST: PREFIX DISTRIBUTION DIFFERENCE")
    print("=" * 70)
    print()

    all_prefixes = set(prefix_by_track['registry_internal'].keys()) | set(prefix_by_track['pipeline'].keys())

    # Build contingency table
    observed = []
    for p in sorted(all_prefixes):
        ri = prefix_by_track['registry_internal'].get(p, 0)
        pp = prefix_by_track['pipeline'].get(p, 0)
        observed.append((p, ri, pp))

    # Calculate chi-square
    ri_total = sum(prefix_by_track['registry_internal'].values())
    pp_total = sum(prefix_by_track['pipeline'].values())
    grand_total = ri_total + pp_total

    chi2 = 0
    print(f"{'PREFIX':<8} {'Reg-Int':>10} {'Pipeline':>10} {'Expected-RI':>12} {'Contrib':>10}")
    print("-" * 55)

    for p, ri, pp in observed:
        row_total = ri + pp
        expected_ri = row_total * ri_total / grand_total
        expected_pp = row_total * pp_total / grand_total

        if expected_ri > 0:
            contrib_ri = (ri - expected_ri)**2 / expected_ri
        else:
            contrib_ri = 0
        if expected_pp > 0:
            contrib_pp = (pp - expected_pp)**2 / expected_pp
        else:
            contrib_pp = 0

        chi2 += contrib_ri + contrib_pp
        print(f"{p:<8} {ri:>10} {pp:>10} {expected_ri:>12.1f} {contrib_ri:>10.2f}")

    df = len(all_prefixes) - 1
    # Cramér's V
    n = grand_total
    k = 2  # number of tracks
    r = len(all_prefixes)
    cramers_v = math.sqrt(chi2 / (n * min(k-1, r-1))) if n > 0 else 0

    print("-" * 55)
    print(f"Chi-square: {chi2:.2f}, df={df}")
    print(f"Cramér's V: {cramers_v:.3f}")
    print()

    # Enrichment ratios
    print("=" * 70)
    print("PREFIX ENRICHMENT IN REGISTRY-INTERNAL TRACK")
    print("=" * 70)
    print()

    ri_rate_total = ri_total / (ri_total + pp_total)

    enrichments = []
    for p, ri, pp in observed:
        if pp > 0:
            total_p = ri + pp
            ri_rate = ri / total_p
            enrichment = ri_rate / ri_rate_total
            enrichments.append((p, enrichment, ri, pp))

    enrichments.sort(key=lambda x: -x[1])

    print(f"Baseline registry-internal rate: {ri_rate_total:.1%}")
    print()
    print(f"{'PREFIX':<8} {'Enrichment':>12} {'Reg-Int':>10} {'Pipeline':>10} {'Interpretation':<20}")
    print("-" * 70)

    for p, enrich, ri, pp in enrichments:
        if enrich > 1.5:
            interp = "REGISTRY-ENRICHED"
        elif enrich < 0.67:
            interp = "PIPELINE-ENRICHED"
        else:
            interp = "balanced"
        print(f"{p:<8} {enrich:>12.2f}x {ri:>10} {pp:>10} {interp:<20}")

    print()

    # SUFFIX analysis by track
    print("=" * 70)
    print("SUFFIX DISTRIBUTION BY TRACK")
    print("=" * 70)
    print()

    suffix_by_track = {}
    for track, toks in track_tokens.items():
        suffix_counts = Counter()
        no_suffix = 0
        for t in toks:
            if t['suffix']:
                suffix_counts[t['suffix']] += 1
            else:
                no_suffix += 1
        suffix_by_track[track] = {'with_suffix': suffix_counts, 'no_suffix': no_suffix}

        total = sum(suffix_counts.values()) + no_suffix
        print(f"{track.upper()}:")
        print(f"  [no suffix]: {no_suffix} ({100*no_suffix/total:.1f}%)")
        for s, count in suffix_counts.most_common(10):
            pct = 100 * count / total
            print(f"  {s}: {count} ({pct:.1f}%)")
        print()

    # Suffix-less rate comparison
    ri_suffixless = suffix_by_track['registry_internal']['no_suffix']
    ri_total_suf = ri_suffixless + sum(suffix_by_track['registry_internal']['with_suffix'].values())
    pp_suffixless = suffix_by_track['pipeline']['no_suffix']
    pp_total_suf = pp_suffixless + sum(suffix_by_track['pipeline']['with_suffix'].values())

    ri_suffixless_rate = ri_suffixless / ri_total_suf
    pp_suffixless_rate = pp_suffixless / pp_total_suf

    print(f"Suffix-less rate:")
    print(f"  Registry-internal: {ri_suffixless_rate:.1%}")
    print(f"  Pipeline: {pp_suffixless_rate:.1%}")
    print(f"  Ratio: {ri_suffixless_rate/pp_suffixless_rate:.2f}x")
    print()

    # PREFIX × SUFFIX interaction
    print("=" * 70)
    print("PREFIX × SUFFIX INTERACTION BY TRACK")
    print("=" * 70)
    print()

    for track in ['registry_internal', 'pipeline']:
        print(f"{track.upper()}:")
        prefix_suffix = defaultdict(Counter)
        for t in track_tokens[track]:
            if t['prefix']:
                suffix_key = t['suffix'] if t['suffix'] else '[none]'
                prefix_suffix[t['prefix']][suffix_key] += 1

        # Show top 5 prefix × suffix combinations
        combos = []
        for prefix, suffix_counts in prefix_suffix.items():
            for suffix, count in suffix_counts.items():
                combos.append((prefix, suffix, count))
        combos.sort(key=lambda x: -x[2])

        print(f"  Top PREFIX × SUFFIX combinations:")
        for prefix, suffix, count in combos[:10]:
            print(f"    {prefix} + {suffix}: {count}")
        print()

    # PREFIX exclusivity
    print("=" * 70)
    print("PREFIX EXCLUSIVITY")
    print("=" * 70)
    print()

    ri_only = set(prefix_by_track['registry_internal'].keys()) - set(prefix_by_track['pipeline'].keys())
    pp_only = set(prefix_by_track['pipeline'].keys()) - set(prefix_by_track['registry_internal'].keys())
    shared = set(prefix_by_track['registry_internal'].keys()) & set(prefix_by_track['pipeline'].keys())

    print(f"Registry-internal only: {ri_only if ri_only else 'none'}")
    print(f"Pipeline only: {pp_only if pp_only else 'none'}")
    print(f"Shared: {shared}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    if cramers_v > 0.3:
        strength = "STRONG"
    elif cramers_v > 0.15:
        strength = "MODERATE"
    elif cramers_v > 0.05:
        strength = "WEAK"
    else:
        strength = "NEGLIGIBLE"

    print(f"Distribution difference: {strength} (V = {cramers_v:.3f})")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if cramers_v < 0.1:
        print("PREFIX distributions are SIMILAR across both tracks.")
        print("This supports C383 (global morphological type system).")
        print("PREFIX likely carries consistent functional typing even for")
        print("registry-internal vocabulary that never reaches B execution.")
    elif cramers_v < 0.2:
        print("PREFIX distributions show MODERATE difference between tracks.")
        print("Both tracks use the same PREFIX inventory but with different")
        print("frequencies. This suggests track-specific usage patterns")
        print("within a unified morphological system.")
    else:
        print("PREFIX distributions show STRONG difference between tracks.")
        print("This suggests PREFIX may have track-specific function:")
        print("- Pipeline track: Control-flow participation (C466)")
        print("- Registry-internal track: Possibly classification markers")

    # Save results
    results = {
        'test': 'PREFIX_TRACK_DISTRIBUTION',
        'date': '2026-01-20',
        'token_counts': {
            'registry_internal': len(track_tokens['registry_internal']),
            'pipeline': len(track_tokens['pipeline'])
        },
        'prefix_distributions': {
            'registry_internal': dict(prefix_by_track['registry_internal']),
            'pipeline': dict(prefix_by_track['pipeline'])
        },
        'chi_square': round(chi2, 2),
        'df': df,
        'cramers_v': round(cramers_v, 3),
        'distribution_difference': strength,
        'enrichments': {p: round(e, 3) for p, e, _, _ in enrichments},
        'suffix_less_rates': {
            'registry_internal': round(ri_suffixless_rate, 3),
            'pipeline': round(pp_suffixless_rate, 3),
            'ratio': round(ri_suffixless_rate/pp_suffixless_rate, 2)
        }
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/prefix_track_distribution.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/prefix_track_distribution.json")

    return results

# ============================================================
# MAIN
# ============================================================

def main():
    registry_internal = load_registry_internal_middles()
    tokens = load_a_tokens()
    analyze_prefix_distribution(tokens, registry_internal)

if __name__ == '__main__':
    main()
