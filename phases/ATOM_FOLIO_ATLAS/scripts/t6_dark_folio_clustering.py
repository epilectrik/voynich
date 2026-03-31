"""
T6: Cluster folios by shared dark pipeline MIDDLEs.

If dark MIDDLEs are identification labels for materials/substances,
folios that share dark MIDDLEs work with the same materials.
Clustering folios by dark vocabulary overlap should reveal
"workshop groups" — folios that belong to the same workflow.
"""

import sys, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

with open(ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json', encoding='utf-8') as f:
    atlas = json.load(f)

from scripts.voynich import ATOM_GLOSSES

folios = sorted(atlas.keys())

# Build dark MIDDLE sets per folio
folio_darks = {}
for f in folios:
    folio_darks[f] = set(atlas[f].get('dark_mids', []))

# Jaccard similarity matrix
def jaccard(s1, s2):
    if not s1 and not s2: return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0

# Find SELECTIVE dark MIDDLEs (on < 15 folios) — these carry the most signal
all_dark_mids = set()
for f in folios:
    all_dark_mids.update(folio_darks[f])

mid_folio_count = {}
for mid in all_dark_mids:
    mid_folio_count[mid] = sum(1 for f in folios if mid in folio_darks[f])

selective_mids = {mid for mid, ct in mid_folio_count.items() if ct <= 12}
print(f"Total dark MIDDLEs: {len(all_dark_mids)}")
print(f"Selective (<=12 folios): {len(selective_mids)}")

# Build selective-only dark sets
folio_sel_darks = {}
for f in folios:
    folio_sel_darks[f] = folio_darks[f] & selective_mids

# ═══ FIND CLUSTERS: Folios sharing 2+ selective dark MIDDLEs ═══
print("\n" + "=" * 100)
print("FOLIO CLUSTERS BY SHARED SELECTIVE DARK MIDDLEs (2+ shared)")
print("=" * 100)

# Build adjacency list
clusters = defaultdict(list)
for i, f1 in enumerate(folios):
    for j, f2 in enumerate(folios):
        if i >= j: continue
        shared = folio_sel_darks[f1] & folio_sel_darks[f2]
        if len(shared) >= 2:
            clusters[(f1, f2)] = sorted(shared)

# Sort by number of shared
pairs = sorted(clusters.items(), key=lambda x: -len(x[1]))

print(f"\nFolio pairs sharing 2+ selective dark MIDDLEs: {len(pairs)}")
print(f"\n{'F1':>8s} {'F2':>8s} {'Shared':>7s} {'S1':>4s} {'S2':>4s}  MIDDLEs (atoms)")
print("-" * 90)

for (f1, f2), shared in pairs[:30]:
    s1 = atlas[f1]['section']
    s2 = atlas[f2]['section']
    mid_strs = []
    for mid in shared[:4]:
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
        ct = mid_folio_count[mid]
        mid_strs.append(f"{mid}({atoms},{ct}f)")
    print(f"{f1:>8s} {f2:>8s} {len(shared):7d} {s1:>4s} {s2:>4s}  {', '.join(mid_strs)}")

# ═══ CONNECTED COMPONENTS: Find workshop groups ═══
print("\n\n" + "=" * 100)
print("WORKSHOP GROUPS (connected components of folios sharing 2+ selective dark MIDDLEs)")
print("=" * 100)

# Build graph
adj = defaultdict(set)
for (f1, f2), shared in clusters.items():
    adj[f1].add(f2)
    adj[f2].add(f1)

# BFS to find connected components
visited = set()
components = []

for f in folios:
    if f in visited or f not in adj:
        continue
    # BFS
    component = set()
    queue = [f]
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        component.add(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                queue.append(neighbor)
    if len(component) >= 2:
        components.append(sorted(component))

components.sort(key=lambda c: -len(c))

for ci, comp in enumerate(components):
    sections = Counter(atlas[f]['section'] for f in comp)
    doc_types = Counter(atlas[f]['doc_type'] for f in comp)

    # Find the dark MIDDLEs shared within this component
    comp_darks = set()
    for f in comp:
        comp_darks.update(folio_sel_darks[f])
    # Only keep those shared by 2+ component members
    shared_darks = set()
    for mid in comp_darks:
        ct = sum(1 for f in comp if mid in folio_sel_darks[f])
        if ct >= 2:
            shared_darks.add(mid)

    print(f"\n  GROUP {ci+1}: {len(comp)} folios")
    print(f"    Folios: {', '.join(comp)}")
    print(f"    Sections: {dict(sections)}")
    print(f"    Doc types: {dict(doc_types)}")
    print(f"    Shared selective dark MIDDLEs: {len(shared_darks)}")

    # Show the most shared dark MIDDLEs
    mid_sharing = []
    for mid in shared_darks:
        ct = sum(1 for f in comp if mid in folio_sel_darks[f])
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
        mid_sharing.append((mid, ct, atoms))
    mid_sharing.sort(key=lambda x: -x[1])

    for mid, ct, atoms in mid_sharing[:8]:
        fols = [f for f in comp if mid in folio_sel_darks[f]]
        print(f"      {mid:>8s} ({atoms:>25s}) on {ct}/{len(comp)}: {fols}")

    # Are known matched folios in this group?
    known = {'f75r': 'Ch19-aquavitae', 'f76r': 'Ch18-elementsep',
             'f77v': 'Ch27-furnace', 'f84r': 'Ch14-gold', 'f108r': 'Ch16-twophase'}
    matched_in_group = {f: known[f] for f in comp if f in known}
    if matched_in_group:
        print(f"    KNOWN MATCHES: {matched_in_group}")

# ═══ rai NETWORK ═══
print("\n\n" + "=" * 100)
print("rai NETWORK: Folios sharing rai (Mercury candidate)")
print("=" * 100)

rai_folios = [f for f in folios if 'rai' in folio_darks[f]]
print(f"\nrai folios: {rai_folios}")

# What OTHER selective dark MIDDLEs do rai folios share?
rai_shared = defaultdict(list)
for mid in selective_mids:
    if mid == 'rai': continue
    fols = [f for f in rai_folios if mid in folio_sel_darks[f]]
    if len(fols) >= 2:
        rai_shared[mid] = fols

print(f"\nSelective dark MIDDLEs shared by 2+ rai folios:")
for mid, fols in sorted(rai_shared.items(), key=lambda x: -len(x[1])):
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    ct = mid_folio_count[mid]
    print(f"  {mid:>8s} ({atoms:>25s}) {ct}f: {fols}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
