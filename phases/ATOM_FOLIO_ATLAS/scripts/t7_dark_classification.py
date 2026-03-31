"""
T7: Classify dark MIDDLEs into functional types, then cluster folios
by each type separately.

Hypothesis: dark MIDDLEs fall into at least 3 types:
  EQUIPMENT — apparatus/vessel identifiers (appear on many folios,
    section-uniform, headless or specification-PREFIX concentrated)
  SUBSTANCE — material identifiers (appear on fewer folios,
    section-concentrated, e-initial or monitored/tested)
  CONDITION — state/parameter identifiers (ubiquitous, short)

Classification approach:
  1. HEAD atom: k-initial=thermal, e-initial=stability, headless=infrastructure
  2. PREFIX concentration: qo-dominant=thermal-handled, ch/sh-dominant=tested/monitored,
     da/sa/po-dominant=specification/infrastructure
  3. Folio spread: high spread=equipment/condition, low spread=substance
  4. Section concentration (C1148): uniform=equipment, concentrated=substance
"""

import sys, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES, HEAD_ATOMS

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

with open(ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json', encoding='utf-8') as f:
    atlas = json.load(f)

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
folios = sorted(atlas.keys())

# ═══ BUILD PER-DARK-MIDDLE PROFILES ═══
mid_prefix = defaultdict(Counter)
mid_folios = defaultdict(set)
mid_sections = defaultdict(Counter)
mid_total = Counter()

for t in all_b:
    m = morph.extract(t.word)
    mid = m.middle
    if mid and mid in dp_set:
        pre = m.prefix or 'BARE'
        mid_prefix[mid][pre] += 1
        mid_folios[mid].add(t.folio)
        mid_sections[mid][t.section] += 1
        mid_total[mid] += 1

# ═══ CLASSIFY EACH DARK MIDDLE ═══
classifications = {}

for mid in dp_set:
    if mid_total[mid] < 2:
        classifications[mid] = 'RARE'
        continue

    n_folios = len(mid_folios[mid])
    n_tokens = mid_total[mid]
    n_sections = len(mid_sections[mid])

    # HEAD atom
    first_char = mid[0] if mid else '?'
    is_headed = first_char in HEAD_ATOMS
    head_type = first_char if is_headed else 'headless'

    # PREFIX profile
    total_pre = sum(mid_prefix[mid].values())
    thermal_pre = sum(mid_prefix[mid].get(p, 0) for p in ['qo', 'ko', 'ke', 'lk'])
    monitor_pre = sum(mid_prefix[mid].get(p, 0) for p in ['ch', 'sh', 'pch', 'tch', 'dch', 'lch', 'lsh', 'fch', 'rch'])
    spec_pre = sum(mid_prefix[mid].get(p, 0) for p in ['da', 'sa', 'po', 'so', 'to', 'do'])
    bare_pre = mid_prefix[mid].get('BARE', 0)

    thermal_pct = thermal_pre / total_pre if total_pre > 0 else 0
    monitor_pct = monitor_pre / total_pre if total_pre > 0 else 0
    spec_pct = spec_pre / total_pre if total_pre > 0 else 0
    bare_pct = bare_pre / total_pre if total_pre > 0 else 0

    # Section concentration (JSD from uniform)
    sec_total = sum(mid_sections[mid].values())
    sec_counts = [mid_sections[mid].get(s, 0) for s in ['B', 'C', 'H', 'S', 'T']]
    sec_max_pct = max(sec_counts) / sec_total if sec_total > 0 else 0

    # Classification rules
    if head_type == 'k' and thermal_pct > 0.5:
        cls = 'THERMAL_SUBSTANCE'
    elif head_type == 'e' and monitor_pct > 0.4:
        cls = 'TESTED_SUBSTANCE'
    elif head_type == 'e' and thermal_pct > 0.3:
        cls = 'THERMAL_SUBSTANCE'
    elif head_type == 'headless' and spec_pct > 0.3:
        cls = 'EQUIPMENT'
    elif head_type == 'headless' and bare_pct > 0.5:
        cls = 'EQUIPMENT'
    elif n_folios > 25:
        cls = 'COMMON_EQUIPMENT'
    elif monitor_pct > 0.5:
        cls = 'TESTED_SUBSTANCE'
    elif thermal_pct > 0.5:
        cls = 'THERMAL_SUBSTANCE'
    elif spec_pct > 0.4:
        cls = 'EQUIPMENT'
    elif n_folios <= 8 and sec_max_pct > 0.7:
        cls = 'SECTION_SUBSTANCE'
    else:
        cls = 'UNCLASSIFIED'

    classifications[mid] = cls

# ═══ SUMMARY ═══
print("DARK MIDDLE CLASSIFICATION")
print("=" * 100)

cls_counts = Counter(classifications.values())
for cls, ct in cls_counts.most_common():
    print(f"  {cls:>20s}: {ct:3d}")

# ═══ SHOW EXAMPLES OF EACH CLASS ═══
for cls in ['TESTED_SUBSTANCE', 'THERMAL_SUBSTANCE', 'SECTION_SUBSTANCE',
            'EQUIPMENT', 'COMMON_EQUIPMENT', 'UNCLASSIFIED']:
    mids = [mid for mid, c in classifications.items() if c == cls and mid_total[mid] >= 3]
    mids.sort(key=lambda m: -mid_total[m])
    if not mids:
        continue
    print(f"\n  {cls} (top examples):")
    for mid in mids[:8]:
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
        n_fol = len(mid_folios[mid])
        top_pre = mid_prefix[mid].most_common(2)
        pre_str = '+'.join(f'{p}:{c}' for p, c in top_pre)
        print(f"    {mid:>8s} ({atoms:>25s})  {n_fol:2d}f  {mid_total[mid]:3d}tok  {pre_str}")

# ═══ CLUSTER BY SUBSTANCE-ONLY DARK MIDDLEs ═══
print("\n\n" + "=" * 100)
print("CLUSTERING BY SUBSTANCE-ONLY DARK MIDDLEs")
print("(Excluding equipment/common/rare)")
print("=" * 100)

substance_classes = {'TESTED_SUBSTANCE', 'THERMAL_SUBSTANCE', 'SECTION_SUBSTANCE'}
substance_mids = {mid for mid, cls in classifications.items() if cls in substance_classes}
selective_substance = {mid for mid in substance_mids if len(mid_folios[mid]) <= 12}

print(f"\nSubstance dark MIDDLEs: {len(substance_mids)}")
print(f"Selective substance MIDDLEs (<=12 folios): {len(selective_substance)}")

# Build substance-only folio dark sets
folio_substance = {}
for f in folios:
    dark_mids_f = set(atlas[f].get('dark_mids', []))
    folio_substance[f] = dark_mids_f & selective_substance

# Find pairs sharing 2+ selective substance MIDDLEs
def jaccard(s1, s2):
    if not s1 and not s2: return 0.0
    return len(s1 & s2) / len(s1 | s2)

substance_pairs = []
for i, f1 in enumerate(folios):
    for j, f2 in enumerate(folios):
        if i >= j: continue
        shared = folio_substance[f1] & folio_substance[f2]
        if len(shared) >= 2:
            substance_pairs.append((f1, f2, shared))

substance_pairs.sort(key=lambda x: -len(x[2]))

print(f"\nFolio pairs sharing 2+ selective substance MIDDLEs: {len(substance_pairs)}")

# Build adjacency and find components
adj = defaultdict(set)
for f1, f2, shared in substance_pairs:
    adj[f1].add(f2)
    adj[f2].add(f1)

visited = set()
components = []
for f in folios:
    if f in visited or f not in adj:
        continue
    comp = set()
    queue = [f]
    while queue:
        node = queue.pop(0)
        if node in visited: continue
        visited.add(node)
        comp.add(node)
        for nb in adj[node]:
            if nb not in visited:
                queue.append(nb)
    if len(comp) >= 2:
        components.append(sorted(comp))

components.sort(key=lambda c: -len(c))

print(f"Connected components: {len(components)}")
for ci, comp in enumerate(components):
    sections = Counter(atlas[f]['section'] for f in comp)

    # Find shared substance MIDDLEs
    comp_subs = set()
    for f in comp:
        comp_subs.update(folio_substance[f])
    shared_subs = set()
    for mid in comp_subs:
        ct = sum(1 for f in comp if mid in folio_substance[f])
        if ct >= 2:
            shared_subs.add((mid, ct))

    known = {'f75r': 'Ch19', 'f76r': 'Ch18', 'f77v': 'Ch27',
             'f84r': 'Ch14', 'f108r': 'Ch16'}
    matched = {f: known[f] for f in comp if f in known}

    print(f"\n  GROUP {ci+1}: {len(comp)} folios  Sections: {dict(sections)}")
    print(f"    Folios: {', '.join(comp)}")
    if matched:
        print(f"    KNOWN: {matched}")

    # Top shared substance MIDDLEs
    top_shared = sorted(shared_subs, key=lambda x: -x[1])[:6]
    for mid, ct in top_shared:
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
        n_fol = len(mid_folios[mid])
        cls = classifications[mid]
        print(f"      {mid:>8s} ({atoms:>20s}) {ct}/{len(comp)} comp, {n_fol}f total  [{cls}]")

# ═══ ISOLATED FOLIOS ═══
isolated = [f for f in folios if f not in visited and folio_substance[f]]
if isolated:
    print(f"\n  ISOLATED (have substance MIDDLEs but no 2+ sharing): {len(isolated)}")
    print(f"    {', '.join(isolated[:20])}")

no_substance = [f for f in folios if not folio_substance[f]]
print(f"  NO SUBSTANCE MIDDLEs: {len(no_substance)} folios")

print(f"\n{'=' * 100}")
print("DONE")
print(f"{'=' * 100}")
