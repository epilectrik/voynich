#!/usr/bin/env python3
"""
SUFFIX TRACK DISTRIBUTION TEST

Question: Do SUFFIX distributions differ between registry-internal and
pipeline-participating vocabulary tracks in Currier A?

Hypothesis: Registry-internal tokens may avoid "execution-routing" suffixes
because they don't need decision points - they're notational, not actionable.

Following the same methodology as PREFIX track distribution test.
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Suffixes grouped by hypothesized function
EXECUTION_SUFFIXES = ['-ey', '-dy', '-edy', '-aiin', '-ain']  # Kernel-heavy, execution routing
CLOSURE_SUFFIXES = ['-y', '-ol', '-or', '-al', '-ar']  # Positional/closure
STRUCTURAL_SUFFIXES = ['-am', '-om', '-an', '-in', '-m', '-n']  # Line-final structural
MINIMAL_SUFFIXES = ['-r', '-l', '-s', '-d']  # Minimal markers

ALL_SUFFIXES = EXECUTION_SUFFIXES + CLOSURE_SUFFIXES + STRUCTURAL_SUFFIXES + MINIMAL_SUFFIXES

def get_prefix(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def get_suffix(token):
    """Extract suffix - try longer matches first."""
    for s in sorted(ALL_SUFFIXES, key=len, reverse=True):
        suffix_str = s.replace('-', '')
        if token.endswith(suffix_str) and len(token) > len(suffix_str):
            return s
    return None

def get_suffix_class(suffix):
    """Classify suffix by hypothesized function."""
    if suffix in EXECUTION_SUFFIXES:
        return 'EXECUTION'
    elif suffix in CLOSURE_SUFFIXES:
        return 'CLOSURE'
    elif suffix in STRUCTURAL_SUFFIXES:
        return 'STRUCTURAL'
    elif suffix in MINIMAL_SUFFIXES:
        return 'MINIMAL'
    else:
        return 'NONE'

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_a_tokens():
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
                'suffix': get_suffix(word),
                'suffix_class': get_suffix_class(get_suffix(word))
            })
    return tokens

# ============================================================
# ANALYSIS
# ============================================================

def analyze_suffix_distribution(tokens, registry_internal):
    """Analyze SUFFIX distribution by track."""

    # Classify tokens by track
    track_tokens = {'registry_internal': [], 'pipeline': []}

    for t in tokens:
        middle = t['middle']
        if middle in registry_internal:
            track_tokens['registry_internal'].append(t)
        else:
            track_tokens['pipeline'].append(t)

    print("=" * 70)
    print("SUFFIX TRACK DISTRIBUTION TEST")
    print("=" * 70)
    print()
    print(f"Registry-internal tokens: {len(track_tokens['registry_internal'])}")
    print(f"Pipeline-participating tokens: {len(track_tokens['pipeline'])}")
    print()

    # ============================================================
    # SUFFIX DISTRIBUTION BY TRACK
    # ============================================================

    print("=" * 70)
    print("SUFFIX DISTRIBUTION BY TRACK")
    print("=" * 70)
    print()

    suffix_by_track = {}
    for track, toks in track_tokens.items():
        suffix_counts = Counter()
        for t in toks:
            suffix_key = t['suffix'] if t['suffix'] else '[none]'
            suffix_counts[suffix_key] += 1
        suffix_by_track[track] = suffix_counts
        total = sum(suffix_counts.values())
        print(f"{track.upper()}:")
        for s, count in suffix_counts.most_common(15):
            pct = 100 * count / total
            print(f"  {s}: {count} ({pct:.1f}%)")
        print()

    # ============================================================
    # SUFFIX CLASS DISTRIBUTION
    # ============================================================

    print("=" * 70)
    print("SUFFIX CLASS DISTRIBUTION BY TRACK")
    print("=" * 70)
    print()

    class_by_track = {}
    for track, toks in track_tokens.items():
        class_counts = Counter(t['suffix_class'] for t in toks)
        class_by_track[track] = class_counts
        total = sum(class_counts.values())
        print(f"{track.upper()}:")
        for c in ['EXECUTION', 'CLOSURE', 'STRUCTURAL', 'MINIMAL', 'NONE']:
            count = class_counts.get(c, 0)
            pct = 100 * count / total
            print(f"  {c}: {count} ({pct:.1f}%)")
        print()

    # ============================================================
    # CHI-SQUARE TEST
    # ============================================================

    print("=" * 70)
    print("CHI-SQUARE TEST: SUFFIX DISTRIBUTION DIFFERENCE")
    print("=" * 70)
    print()

    all_suffixes = set(suffix_by_track['registry_internal'].keys()) | set(suffix_by_track['pipeline'].keys())

    ri_total = sum(suffix_by_track['registry_internal'].values())
    pp_total = sum(suffix_by_track['pipeline'].values())
    grand_total = ri_total + pp_total

    chi2 = 0
    for s in all_suffixes:
        ri = suffix_by_track['registry_internal'].get(s, 0)
        pp = suffix_by_track['pipeline'].get(s, 0)
        row_total = ri + pp
        expected_ri = row_total * ri_total / grand_total
        expected_pp = row_total * pp_total / grand_total

        if expected_ri > 0:
            chi2 += (ri - expected_ri)**2 / expected_ri
        if expected_pp > 0:
            chi2 += (pp - expected_pp)**2 / expected_pp

    df = len(all_suffixes) - 1
    n = grand_total
    k = 2
    r = len(all_suffixes)
    cramers_v = math.sqrt(chi2 / (n * min(k-1, r-1))) if n > 0 else 0

    print(f"Chi-square: {chi2:.2f}, df={df}")
    print(f"Cramér's V: {cramers_v:.3f}")
    print()

    # ============================================================
    # SUFFIX ENRICHMENT
    # ============================================================

    print("=" * 70)
    print("SUFFIX ENRICHMENT IN REGISTRY-INTERNAL TRACK")
    print("=" * 70)
    print()

    ri_rate_total = ri_total / grand_total

    enrichments = []
    for s in all_suffixes:
        ri = suffix_by_track['registry_internal'].get(s, 0)
        pp = suffix_by_track['pipeline'].get(s, 0)
        if pp > 0 or ri > 0:
            total_s = ri + pp
            ri_rate = ri / total_s if total_s > 0 else 0
            enrichment = ri_rate / ri_rate_total if ri_rate_total > 0 else 0
            suffix_class = get_suffix_class(s if s != '[none]' else None)
            enrichments.append((s, enrichment, ri, pp, suffix_class))

    enrichments.sort(key=lambda x: -x[1])

    print(f"Baseline registry-internal rate: {ri_rate_total:.1%}")
    print()
    print(f"{'SUFFIX':<10} {'Enrichment':>12} {'Reg-Int':>10} {'Pipeline':>10} {'Class':<12}")
    print("-" * 60)

    for s, enrich, ri, pp, sclass in enrichments:
        if enrich > 1.5:
            marker = "REGISTRY+"
        elif enrich < 0.67:
            marker = "PIPELINE+"
        else:
            marker = ""
        print(f"{s:<10} {enrich:>12.2f}x {ri:>10} {pp:>10} {sclass:<12} {marker}")

    print()

    # ============================================================
    # SUFFIX CLASS ENRICHMENT
    # ============================================================

    print("=" * 70)
    print("SUFFIX CLASS ENRICHMENT")
    print("=" * 70)
    print()

    for sclass in ['EXECUTION', 'CLOSURE', 'STRUCTURAL', 'MINIMAL', 'NONE']:
        ri = class_by_track['registry_internal'].get(sclass, 0)
        pp = class_by_track['pipeline'].get(sclass, 0)
        total = ri + pp
        if total > 0:
            ri_rate = ri / total
            enrichment = ri_rate / ri_rate_total if ri_rate_total > 0 else 0
            print(f"{sclass:<12}: {enrichment:.2f}x enrichment in registry-internal")
            print(f"             Registry: {ri} ({100*ri/ri_total:.1f}%), Pipeline: {pp} ({100*pp/pp_total:.1f}%)")
            print()

    # ============================================================
    # TYPE-LEVEL ANALYSIS
    # ============================================================

    print("=" * 70)
    print("TYPE-LEVEL ANALYSIS (MIDDLE types, not tokens)")
    print("=" * 70)
    print()

    # For each MIDDLE type, what's its dominant suffix?
    ri_middles = set(t['middle'] for t in track_tokens['registry_internal'])
    pp_middles = set(t['middle'] for t in track_tokens['pipeline'])

    def get_middle_suffix_profile(toks):
        middle_suffixes = defaultdict(Counter)
        for t in toks:
            middle_suffixes[t['middle']][t['suffix'] if t['suffix'] else '[none]'] += 1
        return middle_suffixes

    ri_profiles = get_middle_suffix_profile(track_tokens['registry_internal'])
    pp_profiles = get_middle_suffix_profile(track_tokens['pipeline'])

    # Count MIDDLEs by their dominant suffix class
    def classify_middle_by_suffix(profile):
        if not profile:
            return 'NONE'
        dominant = profile.most_common(1)[0][0]
        return get_suffix_class(dominant if dominant != '[none]' else None)

    ri_middle_classes = Counter(classify_middle_by_suffix(ri_profiles[m]) for m in ri_middles)
    pp_middle_classes = Counter(classify_middle_by_suffix(pp_profiles[m]) for m in pp_middles)

    print("MIDDLE types by dominant suffix class:")
    print()
    print(f"{'Class':<12} {'Reg-Int':>10} {'Pipeline':>10}")
    print("-" * 35)
    for c in ['EXECUTION', 'CLOSURE', 'STRUCTURAL', 'MINIMAL', 'NONE']:
        ri = ri_middle_classes.get(c, 0)
        pp = pp_middle_classes.get(c, 0)
        ri_pct = 100 * ri / len(ri_middles) if ri_middles else 0
        pp_pct = 100 * pp / len(pp_middles) if pp_middles else 0
        print(f"{c:<12} {ri:>5} ({ri_pct:>4.1f}%) {pp:>5} ({pp_pct:>4.1f}%)")
    print()

    # Suffix-less MIDDLEs specifically
    ri_suffixless = sum(1 for m in ri_middles if ri_profiles[m].get('[none]', 0) == sum(ri_profiles[m].values()))
    pp_suffixless = sum(1 for m in pp_middles if pp_profiles[m].get('[none]', 0) == sum(pp_profiles[m].values()))

    print(f"MIDDLEs that are ALWAYS suffix-less:")
    print(f"  Registry-internal: {ri_suffixless}/{len(ri_middles)} ({100*ri_suffixless/len(ri_middles):.1f}%)")
    print(f"  Pipeline: {pp_suffixless}/{len(pp_middles)} ({100*pp_suffixless/len(pp_middles):.1f}%)")
    print()

    # ============================================================
    # SYNTHESIS
    # ============================================================

    print("=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    print()

    # Key findings
    exec_ri = class_by_track['registry_internal'].get('EXECUTION', 0)
    exec_pp = class_by_track['pipeline'].get('EXECUTION', 0)
    exec_ri_pct = 100 * exec_ri / ri_total
    exec_pp_pct = 100 * exec_pp / pp_total

    closure_ri = class_by_track['registry_internal'].get('CLOSURE', 0)
    closure_pp = class_by_track['pipeline'].get('CLOSURE', 0)
    closure_ri_pct = 100 * closure_ri / ri_total
    closure_pp_pct = 100 * closure_pp / pp_total

    print(f"EXECUTION suffixes (-ey, -dy, -edy, -aiin, -ain):")
    print(f"  Registry-internal: {exec_ri_pct:.1f}%")
    print(f"  Pipeline: {exec_pp_pct:.1f}%")
    print(f"  Difference: {exec_ri_pct - exec_pp_pct:+.1f}pp")
    print()

    print(f"CLOSURE suffixes (-y, -ol, -or, -al, -ar):")
    print(f"  Registry-internal: {closure_ri_pct:.1f}%")
    print(f"  Pipeline: {closure_pp_pct:.1f}%")
    print(f"  Difference: {closure_ri_pct - closure_pp_pct:+.1f}pp")
    print()

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if exec_ri_pct < exec_pp_pct - 5:
        print("Registry-internal track AVOIDS execution-routing suffixes.")
        print("This supports the hypothesis: notational tokens don't need")
        print("decision archetypes because they're not routed to execution.")
    elif exec_ri_pct > exec_pp_pct + 5:
        print("Registry-internal track is ENRICHED in execution-routing suffixes.")
        print("This contradicts the hypothesis.")
    else:
        print("Execution-routing suffixes are similarly distributed in both tracks.")
        print("The hypothesis is not clearly supported.")
    print()

    # Save results
    results = {
        'test': 'SUFFIX_TRACK_DISTRIBUTION',
        'date': '2026-01-20',
        'token_counts': {
            'registry_internal': len(track_tokens['registry_internal']),
            'pipeline': len(track_tokens['pipeline'])
        },
        'chi_square': round(chi2, 2),
        'cramers_v': round(cramers_v, 3),
        'suffix_class_rates': {
            'registry_internal': {k: round(100*v/ri_total, 1) for k, v in class_by_track['registry_internal'].items()},
            'pipeline': {k: round(100*v/pp_total, 1) for k, v in class_by_track['pipeline'].items()}
        },
        'enrichments': {s: round(e, 3) for s, e, _, _, _ in enrichments},
        'type_level': {
            'ri_suffixless_middles': ri_suffixless,
            'ri_total_middles': len(ri_middles),
            'pp_suffixless_middles': pp_suffixless,
            'pp_total_middles': len(pp_middles)
        }
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/suffix_track_distribution.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/suffix_track_distribution.json")

def main():
    registry_internal = load_registry_internal_middles()
    tokens = load_a_tokens()
    analyze_suffix_distribution(tokens, registry_internal)

if __name__ == '__main__':
    main()
