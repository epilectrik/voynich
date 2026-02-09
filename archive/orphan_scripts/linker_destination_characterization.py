#!/usr/bin/env python3
"""
Linker Destination Characterization

Research question: What structural properties distinguish linker destination
folios (f93v, f32r) from other A folios?

From C835, the 4 linker tokens create this network:
- cthody: 5 sources -> f93v
- ctho: 4 sources -> f32r
- ctheody: 2 sources -> f87r
- qokoiiin: 1 source -> f37v

We want to understand WHY these folios receive convergent links.
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
print("LINKER DESTINATION CHARACTERIZATION")
print("="*70)

# Define the linker network from C835
LINKER_NETWORK = {
    'cthody': {
        'sources': ['f21r', 'f53v', 'f54r', 'f87r', 'f89v1'],
        'destination': 'f93v'
    },
    'ctho': {
        'sources': ['f27r', 'f30v', 'f42r', 'f93r'],
        'destination': 'f32r'
    },
    'ctheody': {
        'sources': ['f53v', 'f87r'],
        'destination': 'f87r'  # Self-loop
    },
    'qokoiiin': {
        'sources': ['f89v1'],
        'destination': 'f37v'
    }
}

# Primary destinations (hubs with multiple inputs)
HUB_DESTINATIONS = ['f93v', 'f32r']
ALL_DESTINATIONS = ['f93v', 'f32r', 'f87r', 'f37v']
SOURCE_FOLIOS = list(set(
    f for info in LINKER_NETWORK.values() for f in info['sources']
))

print(f"\nHub destinations (4+ inputs): {HUB_DESTINATIONS}")
print(f"All destinations: {ALL_DESTINATIONS}")
print(f"Source folios: {sorted(SOURCE_FOLIOS)}")

# Build folio-level data for all Currier A
folio_data = defaultdict(lambda: {
    'tokens': [],
    'paragraphs': [],
    'ri_tokens': [],
    'pp_tokens': [],
    'lines': set()
})

# Build paragraph data
paragraphs = []
current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    folio_data[token.folio]['tokens'].append(token.word)
    folio_data[token.folio]['lines'].add(token.line)

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'tokens': [t.word for t in current_para]
            })
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'tokens': [t.word for t in current_para]
            })
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'tokens': [t.word for t in current_para]
    })

# Assign paragraphs to folios and extract RI
for para in paragraphs:
    folio = para['folio']
    tokens = para['tokens']
    folio_data[folio]['paragraphs'].append(para)

    # RI = first 3 tokens of paragraph
    if len(tokens) >= 3:
        folio_data[folio]['ri_tokens'].extend(tokens[:3])

    # PP = tokens after RI (positions 3+)
    if len(tokens) > 3:
        folio_data[folio]['pp_tokens'].extend(tokens[3:])

all_a_folios = sorted(folio_data.keys())
print(f"\nTotal A folios: {len(all_a_folios)}")

# Check which destinations are actually in Currier A
destinations_in_a = [f for f in ALL_DESTINATIONS if f in all_a_folios]
print(f"Destinations in Currier A: {destinations_in_a}")

# Analysis 1: Basic metrics
print("\n" + "="*70)
print("ANALYSIS 1: BASIC FOLIO METRICS")
print("="*70)

def compute_folio_metrics(folio):
    data = folio_data[folio]
    tokens = data['tokens']
    paras = data['paragraphs']
    ri = data['ri_tokens']
    pp = data['pp_tokens']

    return {
        'folio': folio,
        'n_tokens': len(tokens),
        'n_paragraphs': len(paras),
        'n_lines': len(data['lines']),
        'n_ri': len(ri),
        'n_pp': len(pp),
        'unique_ri': len(set(ri)),
        'unique_pp': len(set(pp)),
        'ri_density': len(ri) / len(tokens) if tokens else 0,
        'tokens_per_para': len(tokens) / len(paras) if paras else 0
    }

# Compute for all folios
all_metrics = [compute_folio_metrics(f) for f in all_a_folios]
metrics_df = {m['folio']: m for m in all_metrics}

# Compare destinations vs population
print(f"\n{'Folio':<10} {'Tokens':<8} {'Paras':<7} {'RI':<6} {'PP':<6} {'UniqueRI':<9} {'RI%':<8}")
print("-"*65)

# Show destinations first
for folio in ALL_DESTINATIONS:
    if folio in metrics_df:
        m = metrics_df[folio]
        marker = "*** HUB" if folio in HUB_DESTINATIONS else "*"
        print(f"{m['folio']:<10} {m['n_tokens']:<8} {m['n_paragraphs']:<7} {m['n_ri']:<6} {m['n_pp']:<6} {m['unique_ri']:<9} {100*m['ri_density']:<8.1f} {marker}")

print("-"*65)

# Population statistics
pop_tokens = [m['n_tokens'] for m in all_metrics]
pop_paras = [m['n_paragraphs'] for m in all_metrics]
pop_ri_density = [m['ri_density'] for m in all_metrics]

print(f"{'POPULATION':<10} {np.mean(pop_tokens):<8.1f} {np.mean(pop_paras):<7.1f} {'-':<6} {'-':<6} {'-':<9} {100*np.mean(pop_ri_density):<8.1f} mean")
print(f"{'std':<10} {np.std(pop_tokens):<8.1f} {np.std(pop_paras):<7.1f} {'-':<6} {'-':<6} {'-':<9} {100*np.std(pop_ri_density):<8.1f}")

# Analysis 2: Section assignment
print("\n" + "="*70)
print("ANALYSIS 2: SECTION ASSIGNMENT")
print("="*70)

# Get section info from transcript
section_map = {}
for token in tx.currier_a():
    if token.folio not in section_map:
        section_map[token.folio] = token.section

print(f"\n{'Folio':<10} {'Section':<10} {'Role':<15}")
print("-"*40)

for folio in ALL_DESTINATIONS:
    section = section_map.get(folio, 'unknown')
    role = "HUB DESTINATION" if folio in HUB_DESTINATIONS else "destination"
    print(f"{folio:<10} {section:<10} {role:<15}")

print("-"*40)
for folio in sorted(SOURCE_FOLIOS)[:8]:
    section = section_map.get(folio, 'unknown')
    print(f"{folio:<10} {section:<10} source")

# Section distribution
dest_sections = [section_map.get(f, 'unknown') for f in ALL_DESTINATIONS if f in section_map]
source_sections = [section_map.get(f, 'unknown') for f in SOURCE_FOLIOS if f in section_map]
all_sections = [section_map.get(f, 'unknown') for f in all_a_folios]

print(f"\nSection distribution:")
print(f"  Destinations: {Counter(dest_sections)}")
print(f"  Sources: {Counter(source_sections)}")
print(f"  All A folios: {Counter(all_sections)}")

# Analysis 3: PREFIX distribution in destinations vs population
print("\n" + "="*70)
print("ANALYSIS 3: PREFIX DISTRIBUTION")
print("="*70)

def get_prefix_distribution(tokens):
    prefixes = []
    for token in tokens:
        try:
            m = morph.extract(token)
            if m.prefix:
                prefixes.append(m.prefix)
        except:
            pass
    return Counter(prefixes)

# Get prefix distribution for destinations
print("\nDestination folio PREFIX profiles:")
for folio in ALL_DESTINATIONS:
    if folio in folio_data:
        tokens = folio_data[folio]['tokens']
        prefix_dist = get_prefix_distribution(tokens)
        top_prefixes = prefix_dist.most_common(5)
        prefix_str = ', '.join(f"{p}:{c}" for p, c in top_prefixes)
        marker = "*** HUB" if folio in HUB_DESTINATIONS else ""
        print(f"  {folio}: {prefix_str} {marker}")

# Population prefix distribution
all_tokens = []
for folio in all_a_folios:
    all_tokens.extend(folio_data[folio]['tokens'])
pop_prefix_dist = get_prefix_distribution(all_tokens)

print(f"\nPopulation top prefixes: {pop_prefix_dist.most_common(8)}")

# Check for distinctive prefixes in destinations
print("\nComparing hub destinations to population:")
for folio in HUB_DESTINATIONS:
    if folio in folio_data:
        tokens = folio_data[folio]['tokens']
        prefix_dist = get_prefix_distribution(tokens)
        total = sum(prefix_dist.values())

        print(f"\n{folio}:")
        for prefix, count in prefix_dist.most_common(5):
            folio_rate = count / total if total > 0 else 0
            pop_rate = pop_prefix_dist.get(prefix, 0) / sum(pop_prefix_dist.values())
            ratio = folio_rate / pop_rate if pop_rate > 0 else float('inf')
            enrichment = "ENRICHED" if ratio > 1.5 else "depleted" if ratio < 0.67 else "-"
            print(f"  {prefix}: {100*folio_rate:.1f}% (pop: {100*pop_rate:.1f}%) ratio={ratio:.2f} {enrichment}")

# Analysis 4: The linker tokens themselves
print("\n" + "="*70)
print("ANALYSIS 4: LINKER TOKEN MORPHOLOGY")
print("="*70)

print("\nLinker token analysis:")
for linker, info in LINKER_NETWORK.items():
    try:
        m = morph.extract(linker)
        print(f"\n{linker}:")
        print(f"  Prefix: {m.prefix or '-'}")
        print(f"  Middle: {m.middle or '-'}")
        print(f"  Suffix: {m.suffix or '-'}")
        print(f"  Sources: {info['sources']}")
        print(f"  Destination: {info['destination']}")
    except Exception as e:
        print(f"  [parse error: {e}]")

# Analysis 5: What tokens appear in INITIAL position in destinations?
print("\n" + "="*70)
print("ANALYSIS 5: INITIAL RI IN DESTINATION FOLIOS")
print("="*70)

print("\nWhat RI tokens START records in hub destinations?")
for folio in HUB_DESTINATIONS:
    if folio in folio_data:
        paras = folio_data[folio]['paragraphs']
        initial_tokens = []
        for para in paras:
            if para['tokens']:
                initial_tokens.append(para['tokens'][0])

        initial_dist = Counter(initial_tokens)
        print(f"\n{folio} initial tokens ({len(paras)} paragraphs):")
        for token, count in initial_dist.most_common(10):
            print(f"  {token}: {count}")

# Check if linker tokens appear as INITIAL in their destinations
print("\nLinker tokens as INITIAL in their destinations:")
for linker, info in LINKER_NETWORK.items():
    dest = info['destination']
    if dest in folio_data:
        paras = folio_data[dest]['paragraphs']
        found = False
        for para in paras:
            if para['tokens'] and linker in para['tokens'][:3]:
                found = True
                break
        print(f"  {linker} -> {dest}: {'FOUND in initial RI' if found else 'NOT in initial RI'}")

# Analysis 6: Unique vocabulary in destinations
print("\n" + "="*70)
print("ANALYSIS 6: UNIQUE VOCABULARY IN DESTINATIONS")
print("="*70)

# Find tokens that appear in destinations but rarely elsewhere
dest_tokens = set()
for folio in HUB_DESTINATIONS:
    if folio in folio_data:
        dest_tokens.update(folio_data[folio]['tokens'])

other_tokens = set()
for folio in all_a_folios:
    if folio not in HUB_DESTINATIONS:
        other_tokens.update(folio_data[folio]['tokens'])

dest_only = dest_tokens - other_tokens
shared = dest_tokens & other_tokens

print(f"\nTokens in hub destinations: {len(dest_tokens)}")
print(f"Tokens unique to hub destinations: {len(dest_only)}")
print(f"Shared with other folios: {len(shared)}")

if dest_only:
    print(f"\nTokens UNIQUE to hub destinations:")
    for token in sorted(dest_only)[:20]:
        print(f"  {token}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Compute z-scores for hub destinations
hub_metrics = [metrics_df[f] for f in HUB_DESTINATIONS if f in metrics_df]

if hub_metrics:
    print("\nHub destination characteristics vs population:")

    for metric_name in ['n_tokens', 'n_paragraphs', 'ri_density']:
        pop_values = [m[metric_name] for m in all_metrics]
        pop_mean = np.mean(pop_values)
        pop_std = np.std(pop_values)

        for m in hub_metrics:
            z = (m[metric_name] - pop_mean) / pop_std if pop_std > 0 else 0
            direction = "above" if z > 0 else "below"
            sig = "**" if abs(z) > 2 else "*" if abs(z) > 1 else ""
            print(f"  {m['folio']} {metric_name}: z={z:+.2f} ({direction} mean) {sig}")

print("""
INTERPRETATION:
- Hub destinations (f93v, f32r) receive convergent links from multiple sources
- If they show distinctive structural properties, this suggests functional significance
- If they appear structurally typical, linkers may be organizational rather than semantic
""")

# Save results
output = {
    'hub_destinations': HUB_DESTINATIONS,
    'all_destinations': ALL_DESTINATIONS,
    'source_folios': SOURCE_FOLIOS,
    'linker_network': LINKER_NETWORK,
    'destination_metrics': {f: metrics_df[f] for f in ALL_DESTINATIONS if f in metrics_df},
    'population_means': {
        'n_tokens': float(np.mean(pop_tokens)),
        'n_paragraphs': float(np.mean(pop_paras)),
        'ri_density': float(np.mean(pop_ri_density))
    }
}

output_path = Path(__file__).parent.parent / 'results' / 'linker_destination_characterization.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
