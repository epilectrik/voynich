#!/usr/bin/env python3
"""
Linker Destination Follow-up Analysis

Key findings from initial characterization:
1. Hub destinations are structurally TYPICAL (not outliers)
2. ALL in section H (herbal)
3. 3/4 linkers have ct-prefix + ho MIDDLE (ct-ho pattern)
4. Linkers mostly DON'T appear as INITIAL in destinations

This follow-up investigates:
1. The ct-ho pattern: What's special about ct-ho tokens?
2. Where DO the linkers appear in destination folios?
3. Source-destination relationships: What do sources have in common?
4. AND vs OR: Can we distinguish aggregation from alternatives?
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("LINKER DESTINATION FOLLOW-UP ANALYSIS")
print("="*70)

# Linker network from C835
LINKER_NETWORK = {
    'cthody': {'sources': ['f21r', 'f53v', 'f54r', 'f87r', 'f89v1'], 'destination': 'f93v'},
    'ctho': {'sources': ['f27r', 'f30v', 'f42r', 'f93r'], 'destination': 'f32r'},
    'ctheody': {'sources': ['f53v', 'f87r'], 'destination': 'f87r'},
    'qokoiiin': {'sources': ['f89v1'], 'destination': 'f37v'}
}

# Build folio data
folio_data = defaultdict(lambda: {'tokens': [], 'paragraphs': []})
paragraphs = []
current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue
    folio_data[token.folio]['tokens'].append(token.word)

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({'folio': current_folio, 'tokens': [t.word for t in current_para]})
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            paragraphs.append({'folio': current_folio, 'tokens': [t.word for t in current_para]})
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({'folio': current_folio, 'tokens': [t.word for t in current_para]})

for para in paragraphs:
    folio_data[para['folio']]['paragraphs'].append(para)

# Analysis 1: CT-HO Token Population
print("\n" + "="*70)
print("ANALYSIS 1: CT-HO TOKEN POPULATION")
print("="*70)

# Find all tokens with ct- prefix and ho/heo MIDDLE
ct_ho_tokens = []
all_tokens = []

for folio, data in folio_data.items():
    for token in data['tokens']:
        all_tokens.append(token)
        try:
            m = morph.extract(token)
            if m.prefix == 'ct' and m.middle and ('ho' in m.middle or 'heo' in m.middle):
                ct_ho_tokens.append({'token': token, 'folio': folio, 'morph': m})
        except:
            pass

ct_ho_unique = set(t['token'] for t in ct_ho_tokens)
print(f"\nTotal ct-ho tokens: {len(ct_ho_tokens)}")
print(f"Unique ct-ho types: {len(ct_ho_unique)}")
print(f"ct-ho types: {sorted(ct_ho_unique)}")

# Which are the linkers?
linker_tokens = set(LINKER_NETWORK.keys())
ct_ho_linkers = ct_ho_unique & linker_tokens
ct_ho_non_linkers = ct_ho_unique - linker_tokens

print(f"\nct-ho tokens that ARE linkers: {ct_ho_linkers}")
print(f"ct-ho tokens that are NOT linkers: {ct_ho_non_linkers}")

# Analysis 2: Where do linkers appear in destination folios?
print("\n" + "="*70)
print("ANALYSIS 2: LINKER POSITIONS IN DESTINATIONS")
print("="*70)

for linker, info in LINKER_NETWORK.items():
    dest = info['destination']
    if dest in folio_data:
        print(f"\n{linker} -> {dest}:")

        for para_idx, para in enumerate(folio_data[dest]['paragraphs']):
            tokens = para['tokens']
            if linker in tokens:
                pos = tokens.index(linker)
                rel_pos = pos / len(tokens) if tokens else 0
                zone = "INITIAL" if pos < 3 else "FINAL" if pos >= len(tokens) - 3 else "MIDDLE"
                print(f"  Para {para_idx}: position {pos}/{len(tokens)} ({zone}, rel={rel_pos:.2f})")

        # If not found in any paragraph
        all_dest_tokens = folio_data[dest]['tokens']
        if linker not in all_dest_tokens:
            print(f"  NOT FOUND in destination tokens!")

# Analysis 3: Source folio commonalities
print("\n" + "="*70)
print("ANALYSIS 3: SOURCE FOLIO COMMONALITIES")
print("="*70)

for linker, info in LINKER_NETWORK.items():
    sources = info['sources']
    if len(sources) < 2:
        continue

    print(f"\n{linker} sources ({len(sources)} folios):")

    # Find tokens common to ALL sources
    source_token_sets = []
    for src in sources:
        if src in folio_data:
            source_token_sets.append(set(folio_data[src]['tokens']))

    if source_token_sets:
        common_tokens = source_token_sets[0]
        for ts in source_token_sets[1:]:
            common_tokens = common_tokens & ts

        print(f"  Tokens common to ALL {len(sources)} sources: {len(common_tokens)}")
        if common_tokens and len(common_tokens) <= 20:
            print(f"  Common tokens: {sorted(common_tokens)}")

        # Check if the linker itself is in ALL sources
        linker_in_all = all(linker in folio_data[s]['tokens'] for s in sources if s in folio_data)
        print(f"  Linker '{linker}' in all sources: {linker_in_all}")

        # Where does linker appear in sources?
        for src in sources:
            if src in folio_data:
                for para_idx, para in enumerate(folio_data[src]['paragraphs']):
                    tokens = para['tokens']
                    if linker in tokens:
                        pos = tokens.index(linker)
                        zone = "INITIAL" if pos < 3 else "FINAL" if pos >= len(tokens) - 3 else "MIDDLE"
                        print(f"    {src} para {para_idx}: {zone} (pos {pos})")

# Analysis 4: AND vs OR - Prefix overlap test
print("\n" + "="*70)
print("ANALYSIS 4: AND vs OR - PREFIX OVERLAP TEST")
print("="*70)

print("""
If AND (aggregation): Sources should have DIFFERENT prefixes (each contributes distinct ingredient)
If OR (alternatives): Sources should have SIMILAR prefixes (interchangeable sources)
""")

for linker, info in LINKER_NETWORK.items():
    sources = info['sources']
    if len(sources) < 2:
        continue

    print(f"\n{linker} ({len(sources)} sources):")

    # Get prefix distribution for each source
    source_prefix_dists = {}
    for src in sources:
        if src in folio_data:
            tokens = folio_data[src]['tokens']
            prefixes = []
            for token in tokens:
                try:
                    m = morph.extract(token)
                    if m.prefix:
                        prefixes.append(m.prefix)
                except:
                    pass
            source_prefix_dists[src] = Counter(prefixes)

    # Check overlap vs distinctiveness
    all_prefixes = set()
    for dist in source_prefix_dists.values():
        all_prefixes.update(dist.keys())

    # For each prefix, count how many sources have it
    prefix_coverage = {}
    for prefix in all_prefixes:
        n_sources = sum(1 for dist in source_prefix_dists.values() if prefix in dist)
        prefix_coverage[prefix] = n_sources

    # Universal prefixes (in all sources) vs specialized
    universal = [p for p, n in prefix_coverage.items() if n == len(sources)]
    specialized = [p for p, n in prefix_coverage.items() if n == 1]

    print(f"  Prefixes in ALL sources: {universal[:5]}")
    print(f"  Prefixes in ONLY ONE source: {len(specialized)} types")

    # Jaccard similarity between source prefix sets
    if len(sources) >= 2:
        src_list = list(source_prefix_dists.keys())
        for i in range(len(src_list)):
            for j in range(i+1, len(src_list)):
                s1, s2 = src_list[i], src_list[j]
                set1 = set(source_prefix_dists[s1].keys())
                set2 = set(source_prefix_dists[s2].keys())
                jaccard = len(set1 & set2) / len(set1 | set2) if set1 | set2 else 0
                print(f"  Jaccard({s1}, {s2}): {jaccard:.2f}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("""
KEY FINDINGS:

1. CT-HO PATTERN:
   - 3/4 linkers have ct- prefix + ho/heo MIDDLE
   - This confirms C836 (ct-prefix linker signature) and C889 (ct-ho reserved)
   - The ct-ho combination appears to be a LINKING marker

2. LINKER POSITIONS:
   - Linkers appear as FINAL in SOURCE folios (this is how they're defined)
   - But they DON'T necessarily appear as INITIAL in DESTINATION folios
   - This suggests they're not "input tokens" but "reference tokens"

3. AND vs OR:
   - High Jaccard similarity between sources suggests OR (alternatives)
   - Low Jaccard similarity would suggest AND (distinct ingredients)

4. INTERPRETATION:
   - Linkers may be CROSS-REFERENCES rather than procedural inputs
   - "See also folio X" rather than "requires output from folio X"
   - This would explain why they appear as FINAL in sources
     (end-of-entry cross-reference) but not INITIAL in destinations
""")

# Save results
output = {
    'ct_ho_tokens': len(ct_ho_tokens),
    'ct_ho_unique': list(ct_ho_unique),
    'ct_ho_linkers': list(ct_ho_linkers),
    'ct_ho_non_linkers': list(ct_ho_non_linkers)
}

output_path = Path(__file__).parent.parent / 'results' / 'linker_destination_followup.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
