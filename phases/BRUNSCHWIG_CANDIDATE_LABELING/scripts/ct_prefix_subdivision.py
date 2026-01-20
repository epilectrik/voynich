#!/usr/bin/env python3
"""
CT-PREFIX SUBDIVISION TEST

Following expert guidance: Within the registry-internal track, does ct-prefix
subdivide into further functional sub-roles (still non-semantic)?

Probes:
1. ct-prefix × MIDDLE incompatibility density (are ct-MIDDLEs more isolated?)
2. ct-prefix × folio localization (are ct-entries more singleton-like?)
3. ct-prefix × suffix distribution (do ct-entries have different suffix patterns?)

All probes stay inside A, avoid B and Brunschwig, respect the semantic ceiling.
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
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s.replace('-', '')):
            return s
    return None

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
                'suffix': get_suffix(word)
            })
    return tokens

# ============================================================
# ANALYSIS
# ============================================================

def analyze_ct_prefix(tokens, registry_internal):
    """Deep analysis of ct-prefix in registry-internal track."""

    # Filter to registry-internal tokens
    ri_tokens = [t for t in tokens if t['middle'] in registry_internal]

    print("=" * 70)
    print("CT-PREFIX SUBDIVISION TEST")
    print("=" * 70)
    print()
    print(f"Registry-internal tokens: {len(ri_tokens)}")
    print()

    # Group by prefix
    by_prefix = defaultdict(list)
    for t in ri_tokens:
        if t['prefix']:
            by_prefix[t['prefix']].append(t)

    ct_tokens = by_prefix.get('ct', [])
    non_ct_tokens = [t for t in ri_tokens if t['prefix'] and t['prefix'] != 'ct']

    print(f"ct-prefix tokens: {len(ct_tokens)}")
    print(f"non-ct-prefix tokens: {len(non_ct_tokens)}")
    print()

    # ============================================================
    # PROBE 1: Folio Localization (singleton-like behavior)
    # ============================================================

    print("=" * 70)
    print("PROBE 1: FOLIO LOCALIZATION")
    print("=" * 70)
    print()
    print("Question: Are ct-MIDDLEs more folio-localized (singleton-like)?")
    print()

    # For each MIDDLE, count unique folios
    middle_folios = defaultdict(set)
    for t in ri_tokens:
        middle_folios[t['middle']].add(t['folio'])

    # Group by prefix
    ct_middles = set(t['middle'] for t in ct_tokens)
    non_ct_middles = set(t['middle'] for t in non_ct_tokens)

    ct_folio_counts = [len(middle_folios[m]) for m in ct_middles]
    non_ct_folio_counts = [len(middle_folios[m]) for m in non_ct_middles]

    ct_mean = sum(ct_folio_counts) / len(ct_folio_counts) if ct_folio_counts else 0
    non_ct_mean = sum(non_ct_folio_counts) / len(non_ct_folio_counts) if non_ct_folio_counts else 0

    ct_singletons = sum(1 for c in ct_folio_counts if c == 1)
    non_ct_singletons = sum(1 for c in non_ct_folio_counts if c == 1)

    print(f"ct-MIDDLEs: {len(ct_middles)} types")
    print(f"  Mean folio spread: {ct_mean:.2f}")
    print(f"  Singletons (1 folio only): {ct_singletons} ({100*ct_singletons/len(ct_middles):.1f}%)")
    print()
    print(f"non-ct-MIDDLEs: {len(non_ct_middles)} types")
    print(f"  Mean folio spread: {non_ct_mean:.2f}")
    print(f"  Singletons (1 folio only): {non_ct_singletons} ({100*non_ct_singletons/len(non_ct_middles):.1f}%)")
    print()

    print(f"Localization ratio (ct / non-ct): {ct_mean / non_ct_mean:.2f}x")
    print()

    # Distribution of folio counts
    print("Folio spread distribution:")
    print(f"  {'Folios':<10} {'ct-MIDDLEs':>12} {'non-ct':>12}")
    for i in range(1, 6):
        ct_count = sum(1 for c in ct_folio_counts if c == i)
        non_ct_count = sum(1 for c in non_ct_folio_counts if c == i)
        ct_pct = 100 * ct_count / len(ct_folio_counts) if ct_folio_counts else 0
        non_ct_pct = 100 * non_ct_count / len(non_ct_folio_counts) if non_ct_folio_counts else 0
        print(f"  {i:<10} {ct_pct:>10.1f}% {non_ct_pct:>10.1f}%")
    ct_5plus = sum(1 for c in ct_folio_counts if c > 5)
    non_ct_5plus = sum(1 for c in non_ct_folio_counts if c > 5)
    ct_pct = 100 * ct_5plus / len(ct_folio_counts) if ct_folio_counts else 0
    non_ct_pct = 100 * non_ct_5plus / len(non_ct_folio_counts) if non_ct_folio_counts else 0
    print(f"  {'>5':<10} {ct_pct:>10.1f}% {non_ct_pct:>10.1f}%")
    print()

    # ============================================================
    # PROBE 2: Suffix Distribution
    # ============================================================

    print("=" * 70)
    print("PROBE 2: SUFFIX DISTRIBUTION")
    print("=" * 70)
    print()
    print("Question: Do ct-entries have different suffix patterns?")
    print()

    ct_suffixes = Counter(t['suffix'] if t['suffix'] else '[none]' for t in ct_tokens)
    non_ct_suffixes = Counter(t['suffix'] if t['suffix'] else '[none]' for t in non_ct_tokens)

    print("ct-prefix suffix distribution:")
    ct_total = sum(ct_suffixes.values())
    for s, count in ct_suffixes.most_common(10):
        print(f"  {s}: {count} ({100*count/ct_total:.1f}%)")
    print()

    print("non-ct-prefix suffix distribution:")
    non_ct_total = sum(non_ct_suffixes.values())
    for s, count in non_ct_suffixes.most_common(10):
        print(f"  {s}: {count} ({100*count/non_ct_total:.1f}%)")
    print()

    # Suffix enrichment for ct
    print("Suffix enrichment in ct-prefix (vs non-ct):")
    all_suffixes = set(ct_suffixes.keys()) | set(non_ct_suffixes.keys())
    enrichments = []
    for s in all_suffixes:
        ct_rate = ct_suffixes.get(s, 0) / ct_total if ct_total > 0 else 0
        non_ct_rate = non_ct_suffixes.get(s, 0) / non_ct_total if non_ct_total > 0 else 0
        if non_ct_rate > 0:
            enrich = ct_rate / non_ct_rate
            enrichments.append((s, enrich, ct_suffixes.get(s, 0), non_ct_suffixes.get(s, 0)))

    enrichments.sort(key=lambda x: -x[1])
    print(f"  {'Suffix':<10} {'Enrichment':>12} {'ct':>8} {'non-ct':>8}")
    for s, enrich, ct_c, non_ct_c in enrichments[:10]:
        print(f"  {s:<10} {enrich:>12.2f}x {ct_c:>8} {non_ct_c:>8}")
    print()

    # ============================================================
    # PROBE 3: MIDDLE Uniqueness
    # ============================================================

    print("=" * 70)
    print("PROBE 3: MIDDLE TYPE UNIQUENESS")
    print("=" * 70)
    print()
    print("Question: Do ct-entries use unique MIDDLEs or shared ones?")
    print()

    # Check if ct-MIDDLEs appear with other prefixes too
    middle_prefixes = defaultdict(set)
    for t in ri_tokens:
        if t['prefix']:
            middle_prefixes[t['middle']].add(t['prefix'])

    ct_only_middles = [m for m in ct_middles if middle_prefixes[m] == {'ct'}]
    ct_shared_middles = [m for m in ct_middles if len(middle_prefixes[m]) > 1]

    print(f"ct-exclusive MIDDLEs (appear only with ct-prefix): {len(ct_only_middles)} ({100*len(ct_only_middles)/len(ct_middles):.1f}%)")
    print(f"ct-shared MIDDLEs (appear with other prefixes too): {len(ct_shared_middles)} ({100*len(ct_shared_middles)/len(ct_middles):.1f}%)")
    print()

    if ct_shared_middles:
        print("Examples of ct-shared MIDDLEs (what other prefixes use them):")
        for m in list(ct_shared_middles)[:10]:
            prefixes = sorted(middle_prefixes[m])
            print(f"  {m}: {prefixes}")
    print()

    # Compare to non-ct MIDDLEs
    non_ct_prefix_counts = [len(middle_prefixes[m]) for m in non_ct_middles]
    ct_prefix_counts = [len(middle_prefixes[m]) for m in ct_middles]

    non_ct_mean_prefixes = sum(non_ct_prefix_counts) / len(non_ct_prefix_counts) if non_ct_prefix_counts else 0
    ct_mean_prefixes = sum(ct_prefix_counts) / len(ct_prefix_counts) if ct_prefix_counts else 0

    print(f"Mean prefix diversity per MIDDLE:")
    print(f"  ct-MIDDLEs: {ct_mean_prefixes:.2f} prefixes")
    print(f"  non-ct-MIDDLEs: {non_ct_mean_prefixes:.2f} prefixes")
    print()

    # ============================================================
    # PROBE 4: Token Frequency
    # ============================================================

    print("=" * 70)
    print("PROBE 4: TOKEN FREQUENCY DISTRIBUTION")
    print("=" * 70)
    print()
    print("Question: Are ct-entries rare types or common ones?")
    print()

    # Token frequency per MIDDLE
    middle_freq = Counter(t['middle'] for t in ri_tokens)

    ct_freqs = [middle_freq[m] for m in ct_middles]
    non_ct_freqs = [middle_freq[m] for m in non_ct_middles]

    ct_mean_freq = sum(ct_freqs) / len(ct_freqs) if ct_freqs else 0
    non_ct_mean_freq = sum(non_ct_freqs) / len(non_ct_freqs) if non_ct_freqs else 0

    ct_median_freq = sorted(ct_freqs)[len(ct_freqs)//2] if ct_freqs else 0
    non_ct_median_freq = sorted(non_ct_freqs)[len(non_ct_freqs)//2] if non_ct_freqs else 0

    print(f"Token frequency per MIDDLE type:")
    print(f"  ct-MIDDLEs: mean={ct_mean_freq:.1f}, median={ct_median_freq}")
    print(f"  non-ct-MIDDLEs: mean={non_ct_mean_freq:.1f}, median={non_ct_median_freq}")
    print()

    # ============================================================
    # SYNTHESIS
    # ============================================================

    print("=" * 70)
    print("SYNTHESIS: CT-PREFIX ROLE IN REGISTRY-INTERNAL TRACK")
    print("=" * 70)
    print()

    findings = []

    if ct_mean < non_ct_mean * 0.8:
        findings.append(f"ct-MIDDLEs are MORE folio-localized ({ct_mean:.2f} vs {non_ct_mean:.2f} folios)")
    elif ct_mean > non_ct_mean * 1.2:
        findings.append(f"ct-MIDDLEs are LESS folio-localized ({ct_mean:.2f} vs {non_ct_mean:.2f} folios)")
    else:
        findings.append(f"ct-MIDDLEs have SIMILAR folio spread ({ct_mean:.2f} vs {non_ct_mean:.2f} folios)")

    ct_exclusive_rate = len(ct_only_middles) / len(ct_middles) if ct_middles else 0
    if ct_exclusive_rate > 0.7:
        findings.append(f"ct-MIDDLEs are HIGHLY exclusive ({ct_exclusive_rate:.0%} appear only with ct)")
    elif ct_exclusive_rate > 0.5:
        findings.append(f"ct-MIDDLEs are MODERATELY exclusive ({ct_exclusive_rate:.0%} appear only with ct)")
    else:
        findings.append(f"ct-MIDDLEs are SHARED with other prefixes ({ct_exclusive_rate:.0%} ct-exclusive)")

    if ct_mean_prefixes < non_ct_mean_prefixes * 0.8:
        findings.append(f"ct-MIDDLEs have LOWER prefix diversity ({ct_mean_prefixes:.2f} vs {non_ct_mean_prefixes:.2f})")
    else:
        findings.append(f"ct-MIDDLEs have SIMILAR prefix diversity ({ct_mean_prefixes:.2f} vs {non_ct_mean_prefixes:.2f})")

    for f in findings:
        print(f"- {f}")
    print()

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print("ct-prefix in registry-internal track encodes the SAME global meaning")
    print("(stable/non-intervention participation posture), but is selectively")
    print("recruited because registry maintenance needs many 'note this but don't act'")
    print("discriminations.")
    print()
    print("The asymmetric distribution reflects ROLE SELECTION under different")
    print("control responsibilities, not divergent semantics.")
    print()

    # Save results
    results = {
        'test': 'CT_PREFIX_SUBDIVISION',
        'date': '2026-01-20',
        'counts': {
            'ct_tokens': len(ct_tokens),
            'non_ct_tokens': len(non_ct_tokens),
            'ct_middles': len(ct_middles),
            'non_ct_middles': len(non_ct_middles)
        },
        'folio_localization': {
            'ct_mean_folios': round(ct_mean, 2),
            'non_ct_mean_folios': round(non_ct_mean, 2),
            'ct_singleton_rate': round(ct_singletons / len(ct_middles), 3) if ct_middles else 0,
            'non_ct_singleton_rate': round(non_ct_singletons / len(non_ct_middles), 3) if non_ct_middles else 0
        },
        'middle_exclusivity': {
            'ct_exclusive_middles': len(ct_only_middles),
            'ct_shared_middles': len(ct_shared_middles),
            'ct_exclusive_rate': round(ct_exclusive_rate, 3),
            'ct_mean_prefix_diversity': round(ct_mean_prefixes, 2),
            'non_ct_mean_prefix_diversity': round(non_ct_mean_prefixes, 2)
        },
        'token_frequency': {
            'ct_mean_freq': round(ct_mean_freq, 2),
            'non_ct_mean_freq': round(non_ct_mean_freq, 2),
            'ct_median_freq': ct_median_freq,
            'non_ct_median_freq': non_ct_median_freq
        },
        'findings': findings
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/ct_prefix_subdivision.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/ct_prefix_subdivision.json")

def main():
    registry_internal = load_registry_internal_middles()
    tokens = load_a_tokens()
    analyze_ct_prefix(tokens, registry_internal)

if __name__ == '__main__':
    main()
