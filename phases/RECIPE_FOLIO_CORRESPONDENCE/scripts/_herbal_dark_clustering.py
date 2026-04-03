"""Cluster Section H herbal folios by dark pipeline MIDDLE profile.
Do they form meaningful groups that could correspond to Brunschwig procedure classes?"""
import sys, io, json, math
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

with open('C:/git/voynich/data/dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# Get all Section H folios
h_folios = sorted(set(t.folio for t in all_b if t.section == 'H'))
print(f"Section H folios: {len(h_folios)}")

# Build dark MIDDLE profile for each H folio
folio_darks = {}
folio_tokens = {}
for f in h_folios:
    toks = [t for t in all_b if t.folio == f]
    folio_tokens[f] = len(toks)
    darks = Counter()
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            darks[m.middle] += 1
    folio_darks[f] = darks

# Get all dark MIDDLEs that appear on H folios
all_h_darks = set()
for darks in folio_darks.values():
    all_h_darks.update(darks.keys())
print(f"Unique dark MIDDLEs on H folios: {len(all_h_darks)}")

# Key material/process identifiers from our dictionary
KEY_DARKS = {
    'fch': 'MERCURY',
    'cs': 'GOLD',
    'eckh': 'VOLATILE_LIQ',
    'rai': 'METALLIC',
    'lch': 'APPARATUS',
    'lk': 'FIRE',
    'eed': 'COOLING',
    'cth': 'STATE_TRANS',
    'eke': 'PRECISION_TEST',
    'ksh': 'THERMAL_SEQ',
    'tsh': 'COHOBATION',
    'eet': 'COOL_TRANSFER',
    'lsh': 'PHASE_BOUNDARY',
    'ro': 'FERMENTATION',
    'ep': 'COOL_PAUSE',
}

# Profile each H folio by key dark MIDDLEs
print("\n" + "=" * 120)
print("SECTION H FOLIO DARK PIPELINE PROFILES")
print("=" * 120)

header = f"{'Folio':>8s} {'Tok':>4s} {'Dark':>4s} {'%':>5s}"
for k, label in list(KEY_DARKS.items())[:12]:
    header += f" {label[:6]:>6s}"
print(header)
print("-" * 120)

profiles = {}
for f in h_folios:
    n = folio_tokens[f]
    darks = folio_darks[f]
    n_dark = sum(darks.values())
    dark_pct = 100 * n_dark / n if n > 0 else 0

    row = f"{f:>8s} {n:4d} {n_dark:4d} {dark_pct:5.1f}"
    profile = {}
    for k, label in list(KEY_DARKS.items())[:12]:
        count = darks.get(k, 0)
        profile[k] = count
        row += f" {count:6d}"
    profiles[f] = profile
    print(row)

# Group by material identifiers present
print("\n\n" + "=" * 120)
print("GROUPING BY MATERIAL IDENTIFIERS")
print("=" * 120)

groups = defaultdict(list)
for f in h_folios:
    darks = folio_darks[f]
    has_mercury = darks.get('fch', 0) > 0
    has_gold = darks.get('cs', 0) > 0
    has_volatile = darks.get('eckh', 0) > 0
    has_metallic = darks.get('rai', 0) > 0
    has_cohobation = darks.get('tsh', 0) > 0
    has_fermentation = darks.get('ro', 0) > 0

    tags = []
    if has_mercury: tags.append('MERCURY')
    if has_gold: tags.append('GOLD')
    if has_volatile: tags.append('VOLATILE')
    if has_metallic: tags.append('METALLIC')
    if has_cohobation: tags.append('COHOBATION')
    if has_fermentation: tags.append('FERMENTATION')

    key = '+'.join(tags) if tags else 'NONE'
    groups[key].append(f)

for key in sorted(groups.keys(), key=lambda k: -len(groups[k])):
    folios = groups[key]
    print(f"\n  {key} ({len(folios)} folios):")
    for f in folios:
        n = folio_tokens[f]
        darks = folio_darks[f]
        n_dark = sum(darks.values())
        top_darks = darks.most_common(5)
        top_str = ', '.join(f'{m}={c}' for m, c in top_darks)
        print(f"    {f} ({n} tok, {n_dark} dark): {top_str}")

# Pairwise Jaccard similarity between H folios based on dark MIDDLE overlap
print("\n\n" + "=" * 120)
print("DARK MIDDLE JACCARD SIMILARITY CLUSTERS")
print("=" * 120)

# Only folios with 3+ dark tokens
active_h = [f for f in h_folios if sum(folio_darks[f].values()) >= 3]
print(f"\nFolios with 3+ dark tokens: {len(active_h)}")

# Compute Jaccard
dark_sets = {f: set(folio_darks[f].keys()) for f in active_h}

# Find most similar pairs
pairs = []
for i, f1 in enumerate(active_h):
    for f2 in active_h[i+1:]:
        s1, s2 = dark_sets[f1], dark_sets[f2]
        if len(s1 | s2) > 0:
            jaccard = len(s1 & s2) / len(s1 | s2)
            shared = s1 & s2
            pairs.append((jaccard, f1, f2, shared))

pairs.sort(reverse=True)
print(f"\nTop 20 most similar H folio pairs (by dark MIDDLE Jaccard):")
for j, f1, f2, shared in pairs[:20]:
    shared_str = ','.join(sorted(shared)[:6])
    print(f"  {f1} <-> {f2}: J={j:.3f} shared={shared_str}")

# Find natural clusters
print(f"\nFolios with NO shared dark MIDDLEs with any other H folio:")
for f in active_h:
    has_any_shared = False
    for f2 in active_h:
        if f2 != f and dark_sets[f] & dark_sets[f2]:
            has_any_shared = True
            break
    if not has_any_shared:
        print(f"  {f} ({folio_tokens[f]} tok): darks = {dict(folio_darks[f])}")

# Brunschwig procedure class predictions
print("\n\n" + "=" * 120)
print("BRUNSCHWIG PROCEDURE CLASS PREDICTIONS")
print("=" * 120)

print("""
Brunschwig's fire degrees (from Small Book, confirmed in Large Book):
  Degree 1: Balneum mariae (water bath) — gentlest
  Degree 2: Ash bath / sand bath — moderate
  Degree 3: Direct fire / flame — strongest

If dark pipeline profiles encode process class, H folios should cluster by:
  - fch presence → mercury-water used as solvent (compound preparation)
  - eckh presence → volatile plant liquid (careful distillation)
  - eet presence → cooling transfer (balneum with condenser)
  - ksh presence → sequential thermal observation (graduated fire)
  - tsh presence → cohobation (return distillation)
  - None of above → simple degree-2 ash distillation (default herbal)
""")

for key in sorted(groups.keys(), key=lambda k: -len(groups[k])):
    folios = groups[key]
    if key == 'NONE':
        prediction = "Simple distillation (degree 2 ash) — no special material/process markers"
    elif 'MERCURY' in key:
        prediction = "Compound preparation using mercury-water as solvent"
    elif 'VOLATILE' in key:
        prediction = "Careful distillation of volatile plant liquid (degree 1 balneum)"
    elif 'METALLIC' in key:
        prediction = "Metal-containing compound (gold leaf, antimony, etc.)"
    elif 'COHOBATION' in key:
        prediction = "Return distillation / cohobation recipe"
    elif 'FERMENTATION' in key:
        prediction = "Fermentation-based preparation"
    elif 'GOLD' in key:
        prediction = "Gold-containing compound water"
    else:
        prediction = "Unknown process class"

    print(f"\n  {key} ({len(folios)} folios): {prediction}")
    for f in folios:
        print(f"    {f} ({folio_tokens[f]} tok)")
