#!/usr/bin/env python3
"""Extract and analyze the A-like labels from f85v2 rosette regions."""
import sys
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer,
                              BFolioDecoder)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# ============================================================
# 1. SEPARATE LABEL vs DESCRIPTION REGIONS on f85v2
# ============================================================
print("=" * 65)
print("f85v2 REGION CLASSIFICATION: LABEL vs DESCRIPTION")
print("=" * 65)

label_regions = []  # Single-token dominated (A-like)
desc_regions = []   # Continuous text (B-like)

for region in ra.get_regions('f85v2'):
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue
    lines = defaultdict(list)
    for t in toks:
        lines[t.line].append(t)
    line_lens = [len(v) for v in lines.values()]
    single_rate = sum(1 for l in line_lens if l == 1) / len(line_lens)

    if single_rate > 0.5:
        label_regions.append(region)
        rtype = "LABEL"
    else:
        desc_regions.append(region)
        rtype = "DESCRIPTION"

    print(f"  {region:>3}: {len(toks):>3} tok, {len(lines)} lines, "
          f"single-tok={single_rate:.0%} => {rtype}")

print(f"\nLabel regions: {label_regions}")
print(f"Description regions: {desc_regions}")

# ============================================================
# 2. EXTRACT ALL LABELS (single tokens from label regions)
# ============================================================
print("\n" + "=" * 65)
print("LABEL TOKENS (single-token entries from label regions)")
print("=" * 65)

all_labels = []
labels_by_region = {}

for region in label_regions:
    toks = ra.get_tokens('f85v2', region)
    region_labels = []
    for t in toks:
        m = morph.extract(t.word)
        analysis = decoder.analyze_token(t.word)
        region_labels.append({
            'word': t.word,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'macro_state': analysis.macro_state,
            'hub_role': analysis.hub_sub_role,
            'prefix_role': analysis.prefix_role,
            'middle_kernel': analysis.middle_kernel,
        })
        all_labels.append(t.word)

    labels_by_region[region] = region_labels
    print(f"\n  Region {region} ({len(region_labels)} labels):")
    for lb in region_labels:
        hub = f" hub={lb['hub_role']}" if lb['hub_role'] else ""
        ms = f" state={lb['macro_state']}" if lb['macro_state'] else ""
        mk = f" kern={lb['middle_kernel']}" if lb['middle_kernel'] else ""
        print(f"    {lb['word']:18s} pre={str(lb['prefix']):>5s} "
              f"mid={str(lb['middle']):>10s} suf={str(lb['suffix']):>5s}"
              f"{hub}{ms}{mk}")

# ============================================================
# 3. WHERE DO THESE LABELS APPEAR IN THE REST OF THE MANUSCRIPT?
# ============================================================
print("\n" + "=" * 65)
print("LABEL CROSS-REFERENCES (where do these words appear elsewhere?)")
print("=" * 65)

label_set = set(all_labels)

# Search in A corpus
a_locations = defaultdict(list)
for tok in tx.currier_a():
    if tok.word in label_set:
        a_locations[tok.word].append((tok.folio, tok.section, tok.placement))

# Search in B corpus
b_locations = defaultdict(list)
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS and tok.word in label_set:
        b_locations[tok.word].append((tok.folio, tok.section, tok.placement))

# Search in AZC
azc_locations = defaultdict(list)
for tok in tx.azc():
    if tok.word in label_set:
        azc_locations[tok.word].append((tok.folio, tok.section, tok.placement))

print(f"\n{'Label':<18s} {'in_A':>4} {'in_B':>4} {'in_AZC':>5} A_folios")
print("-" * 70)
for word in sorted(label_set):
    a_ct = len(a_locations.get(word, []))
    b_ct = len(b_locations.get(word, []))
    azc_ct = len(azc_locations.get(word, []))
    a_folios = sorted(set(f for f, s, p in a_locations.get(word, [])))[:5]
    print(f"  {word:<18s} {a_ct:>4} {b_ct:>4} {azc_ct:>5} {a_folios}")

# ============================================================
# 4. LABEL MIDDLEs — do they appear in body text contexts?
# ============================================================
print("\n" + "=" * 65)
print("LABEL MIDDLE ANALYSIS")
print("=" * 65)

label_middles = set()
for region_labels in labels_by_region.values():
    for lb in region_labels:
        if lb['middle']:
            label_middles.add(lb['middle'])

print(f"Unique MIDDLEs in labels: {len(label_middles)}")
print(f"Labels: {sorted(label_middles)}")

# Which body text sections use these MIDDLEs?
mid_section_usage = defaultdict(lambda: Counter())
for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    m = morph.extract(tok.word)
    if m.middle in label_middles:
        mid_section_usage[m.middle][tok.section] += 1

print(f"\nLabel MIDDLE usage in body text sections:")
for mid in sorted(label_middles):
    usage = mid_section_usage.get(mid, Counter())
    if usage:
        total = sum(usage.values())
        top = usage.most_common(3)
        print(f"  {mid:<12s}: {total:>4} occurrences -> {top}")
    else:
        print(f"  {mid:<12s}: NOT IN B BODY TEXT")

# ============================================================
# 5. DESCRIPTION REGIONS — structural profile
# ============================================================
print("\n" + "=" * 65)
print("DESCRIPTION REGIONS (B-like continuous text)")
print("=" * 65)

for region in desc_regions:
    toks = ra.get_tokens('f85v2', region)
    if len(toks) < 10:
        continue

    # Hub role distribution
    hub_dist = Counter()
    macro_dist = Counter()
    kernel_dist = Counter()

    for t in toks:
        analysis = decoder.analyze_token(t.word)
        if analysis.hub_sub_role:
            hub_dist[analysis.hub_sub_role] += 1
        if analysis.macro_state:
            macro_dist[analysis.macro_state] += 1
        if analysis.middle_kernel:
            kernel_dist[analysis.middle_kernel] += 1

    print(f"\n  Region {region} ({len(toks)} tokens):")
    print(f"    Hub roles: {dict(hub_dist.most_common())}")
    print(f"    Macro states: {dict(macro_dist.most_common())}")
    print(f"    Kernel profile: {dict(kernel_dist.most_common())}")

    # Show first few tokens with glosses
    print(f"    First 10 tokens:")
    for t in toks[:10]:
        analysis = decoder.analyze_token(t.word)
        gloss = analysis.structural()
        print(f"      {t.word:<18s} {gloss}")

# ============================================================
# 6. LABEL-DESCRIPTION PAIRING (spatial proximity)
# ============================================================
print("\n" + "=" * 65)
print("LABEL-DESCRIPTION PAIRING")
print("=" * 65)
print("Hypothesis: label regions NAME nearby description regions")

# Group by probable rosette association
# B regions (B1/B2/B3) are probably one rosette area
# M regions (M1/M2/M3) are another
# N regions (N1/N2) together
# V regions (V1/V2) together
# U regions (U1/U2/U3) together
# C2 and D1 and W1 are individual

rosette_groups = {
    'BOTTOM': {'label': ['B1', 'B2', 'B3'], 'desc': []},
    'MIDDLE': {'label': ['M1', 'M2', 'M3'], 'desc': []},
    'NORTH': {'label': [], 'desc': ['N1', 'N2']},
    'VERT': {'label': [], 'desc': ['V1', 'V2']},
    'UPPER': {'label': ['U1', 'U2', 'U3'], 'desc': []},
    'CENTER': {'label': [], 'desc': ['C2']},
    'D_W': {'label': ['W1'], 'desc': ['D1']},
}

for group_name, regions in rosette_groups.items():
    all_label_words = []
    all_desc_hubs = Counter()
    all_desc_kernels = Counter()

    for r in regions.get('label', []):
        for lb in labels_by_region.get(r, []):
            all_label_words.append(lb['word'])

    for r in regions.get('desc', []):
        for t in ra.get_tokens('f85v2', r):
            a = decoder.analyze_token(t.word)
            if a.hub_sub_role:
                all_desc_hubs[a.hub_sub_role] += 1
            if a.middle_kernel:
                all_desc_kernels[a.middle_kernel] += 1

    if all_label_words or all_desc_hubs:
        print(f"\n  {group_name}:")
        if all_label_words:
            print(f"    Labels: {all_label_words[:10]}")
        if all_desc_hubs:
            print(f"    Description hubs: {dict(all_desc_hubs.most_common())}")
        if all_desc_kernels:
            print(f"    Description kernels: {dict(all_desc_kernels.most_common())}")
