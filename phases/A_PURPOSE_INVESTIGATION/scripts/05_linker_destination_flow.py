"""
05_linker_destination_flow.py - Test if linkers connect RI-heavy to PP-heavy contexts

Based on expert consultation:
- C835 identifies 4 linkers: cthody, ctho, ctheody, qokoiiin
- If RI encodes "preparation-relevant distinctions" and PP encodes "execution operations",
  linkers should connect preparation contexts (RI-rich) to execution contexts (PP-rich)

Tests:
1. For each linker, compare RI/PP ratio at SOURCE folio vs DESTINATION folio
2. Check if linkers flow from high-RI to high-PP contexts
3. Validate with section data (H=herbal/prep vs P=pharma/execution)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
import pandas as pd
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json

tx = Transcript()
morph = Morphology()

# Known linkers from C835
LINKERS = ['cthody', 'ctho', 'ctheody', 'qokoiiin']

# Build B vocabulary to identify RI (A-exclusive) vs PP (A-shared)
print("Building PP/RI classification...")
b_tokens = list(tx.currier_b())
b_middles = set()
for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

print(f"  B vocabulary: {len(b_middles)} unique MIDDLEs")

# Build A folio RI/PP profiles
a_tokens = list(tx.currier_a())
folio_ri = defaultdict(int)
folio_pp = defaultdict(int)
folio_total = defaultdict(int)

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        folio_total[t.folio] += 1
        if m.middle in b_middles:
            folio_pp[t.folio] += 1
        else:
            folio_ri[t.folio] += 1

print(f"  A folios with MIDDLEs: {len(folio_total)}")

# Compute RI ratio per folio
folio_ri_ratio = {}
for f in folio_total:
    total = folio_ri[f] + folio_pp[f]
    if total >= 10:  # Need minimum tokens
        folio_ri_ratio[f] = folio_ri[f] / total

print(f"  Folios with RI ratio: {len(folio_ri_ratio)}")

# ============================================================
# Find linker occurrences and destinations
# ============================================================
print("\n" + "="*70)
print("LINKER DESTINATION ANALYSIS")
print("="*70)

# Load raw transcript for section info
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df = df[~df['placement'].str.startswith('L', na=False)]

# Build folio -> section mapping
folio_section = df.groupby('folio')['section'].first().to_dict()

# Find linker occurrences
linker_occurrences = defaultdict(list)
for t in a_tokens:
    if t.word in LINKERS:
        linker_occurrences[t.word].append({
            'folio': t.folio,
            'line': t.line,
            'section': folio_section.get(t.folio, 'Unknown')
        })

print(f"\nLinker occurrences in Currier A:")
for linker, occs in sorted(linker_occurrences.items()):
    print(f"  {linker}: {len(occs)} occurrences")

# Get linker destinations from C835 data
# C835 identifies f93v and f32r as hub destinations with 5 and 4 incoming links
LINKER_DESTINATIONS = {
    'f93v': {'count': 5, 'type': 'hub'},
    'f32r': {'count': 4, 'type': 'hub'}
}

print(f"\nKnown linker hub destinations (from C835):")
for dest, info in LINKER_DESTINATIONS.items():
    section = folio_section.get(dest, 'Unknown')
    ri_ratio = folio_ri_ratio.get(dest, None)
    ri_str = f"{100*ri_ratio:.1f}%" if ri_ratio is not None else "N/A"
    print(f"  {dest}: section {section}, RI ratio {ri_str}, {info['count']} incoming links")

# ============================================================
# TEST 1: Source vs Destination RI Ratios
# ============================================================
print("\n" + "="*70)
print("TEST 1: SOURCE vs DESTINATION RI RATIOS")
print("="*70)
print("Hypothesis: Linkers connect RI-rich sources to PP-rich destinations")
print("            (preparation context -> execution context)")
print()

# Collect source folios for each linker
all_source_folios = set()
for linker, occs in linker_occurrences.items():
    for occ in occs:
        all_source_folios.add(occ['folio'])

source_ri_ratios = [folio_ri_ratio[f] for f in all_source_folios if f in folio_ri_ratio]
dest_ri_ratios = [folio_ri_ratio[f] for f in LINKER_DESTINATIONS if f in folio_ri_ratio]

print(f"Source folios (where linkers appear): {len(all_source_folios)}")
if source_ri_ratios:
    mean_source_ri = sum(source_ri_ratios) / len(source_ri_ratios)
    print(f"  Mean RI ratio: {100*mean_source_ri:.1f}%")

print(f"\nDestination folios (linker hubs): {len(LINKER_DESTINATIONS)}")
if dest_ri_ratios:
    mean_dest_ri = sum(dest_ri_ratios) / len(dest_ri_ratios)
    print(f"  Mean RI ratio: {100*mean_dest_ri:.1f}%")

if source_ri_ratios and dest_ri_ratios:
    if mean_source_ri > mean_dest_ri:
        print(f"\n  -> Source RI > Destination RI ({100*(mean_source_ri - mean_dest_ri):.1f} pp difference)")
        print("  -> SUPPORTS preparation->execution flow hypothesis")
    elif mean_dest_ri > mean_source_ri:
        print(f"\n  -> Destination RI > Source RI ({100*(mean_dest_ri - mean_source_ri):.1f} pp difference)")
        print("  -> CONTRADICTS preparation->execution flow hypothesis")
    else:
        print("\n  -> No difference in RI ratio")

# ============================================================
# TEST 2: Section-based Analysis
# ============================================================
print("\n" + "="*70)
print("TEST 2: SECTION-BASED LINKER FLOW")
print("="*70)
print("From C888: Section H is cross-referencing heavy, Section P is safety/execution heavy")
print()

# Count linker occurrences by section
linker_by_section = defaultdict(int)
for linker, occs in linker_occurrences.items():
    for occ in occs:
        linker_by_section[occ['section']] += 1

print("Linker occurrences by section:")
for section, count in sorted(linker_by_section.items()):
    print(f"  Section {section}: {count} linker tokens")

# Check destination sections
print("\nLinker destination sections:")
for dest in LINKER_DESTINATIONS:
    section = folio_section.get(dest, 'Unknown')
    print(f"  {dest}: Section {section}")

# ============================================================
# TEST 3: Detailed Folio-Level Flow
# ============================================================
print("\n" + "="*70)
print("TEST 3: DETAILED FOLIO-LEVEL FLOW")
print("="*70)

print("\nSource folio details (where linkers appear):")
print(f"{'Folio':<10} {'Section':<10} {'RI%':<10} {'Linker':<15}")
print("-" * 50)

for linker, occs in sorted(linker_occurrences.items()):
    for occ in occs:
        ri_ratio = folio_ri_ratio.get(occ['folio'], None)
        ri_str = f"{100*ri_ratio:.1f}%" if ri_ratio is not None else "N/A"
        print(f"{occ['folio']:<10} {occ['section']:<10} {ri_str:<10} {linker:<15}")

# ============================================================
# TEST 4: PP Profile in Destinations
# ============================================================
print("\n" + "="*70)
print("TEST 4: PP PROFILE IN DESTINATIONS")
print("="*70)
print("Check if destination folios have execution-characteristic PP vocabulary")
print()

# Get PP MIDDLEs used at destinations
dest_pp_middles = Counter()
dest_pp_prefixes = Counter()

for t in a_tokens:
    if t.folio in LINKER_DESTINATIONS:
        m = morph.extract(t.word)
        if m and m.middle and m.middle in b_middles:  # PP vocabulary
            dest_pp_middles[m.middle] += 1
            if m.prefix:
                dest_pp_prefixes[m.prefix] += 1

print("Top PP MIDDLEs at destination folios:")
for middle, count in dest_pp_middles.most_common(10):
    print(f"  {middle}: {count}")

print("\nPP PREFIX distribution at destinations:")
for prefix, count in dest_pp_prefixes.most_common(10):
    total = sum(dest_pp_prefixes.values())
    print(f"  {prefix}: {count} ({100*count/total:.1f}%)")

# Compare to overall A PREFIX distribution
overall_prefixes = Counter()
for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.prefix and m.middle in b_middles:  # PP only
        overall_prefixes[m.prefix] += 1

print("\nCompare to overall A PP PREFIX distribution:")
for prefix in ['qo', 'o', 'ch', 's', 'd', 'y', 'ct']:
    dest_pct = 100 * dest_pp_prefixes.get(prefix, 0) / sum(dest_pp_prefixes.values()) if dest_pp_prefixes else 0
    overall_pct = 100 * overall_prefixes.get(prefix, 0) / sum(overall_prefixes.values()) if overall_prefixes else 0
    diff = dest_pct - overall_pct
    print(f"  {prefix}: dest={dest_pct:.1f}% vs overall={overall_pct:.1f}% ({diff:+.1f}pp)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if source_ri_ratios and dest_ri_ratios:
    print(f"""
Source RI ratio (linker origin):      {100*mean_source_ri:.1f}%
Destination RI ratio (linker hubs):   {100*mean_dest_ri:.1f}%
Difference:                           {100*(mean_source_ri - mean_dest_ri):+.1f} percentage points
""")

    if mean_source_ri > mean_dest_ri + 0.05:
        flow_result = "SUPPORTS"
        print("Result: SUPPORTS preparation->execution flow")
        print("  Linkers appear in RI-rich contexts and point to PP-rich destinations")
    elif mean_dest_ri > mean_source_ri + 0.05:
        flow_result = "CONTRADICTS"
        print("Result: CONTRADICTS preparation->execution flow")
        print("  Linkers appear in PP-rich contexts and point to RI-rich destinations")
    else:
        flow_result = "NEUTRAL"
        print("Result: NEUTRAL - no clear directional flow in RI/PP")
else:
    flow_result = "INSUFFICIENT_DATA"
    print("Result: Insufficient data for comparison")

# Save results
output = {
    'linker_occurrences': {k: len(v) for k, v in linker_occurrences.items()},
    'source_folio_count': len(all_source_folios),
    'source_mean_ri_ratio': float(mean_source_ri) if source_ri_ratios else None,
    'dest_mean_ri_ratio': float(mean_dest_ri) if dest_ri_ratios else None,
    'flow_result': flow_result,
    'linker_by_section': dict(linker_by_section),
    'destinations': {
        dest: {
            'section': folio_section.get(dest),
            'ri_ratio': folio_ri_ratio.get(dest)
        }
        for dest in LINKER_DESTINATIONS
    }
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/linker_destination_flow.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to linker_destination_flow.json")
