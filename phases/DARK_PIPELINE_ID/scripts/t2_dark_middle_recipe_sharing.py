"""
T2: Do folios matched to similar recipes share more dark MIDDLEs?

Pointer hypothesis: dark MIDDLEs are pointers to external referents
(materials, tools, conditions). If so, folios matched to recipes with
SIMILAR materials should share more dark MIDDLEs than folios matched
to DIFFERENT materials.

Test groups:
  BALNEUM pair: f75r + f84r (both balneum mariae, honey-based recipes)
  BALNEUM+DISTILL: f75r + f76r (both distillation, but different methods)
  DIFFERENT: f75r + f77v (aqua vitae vs furnace specification)

Controls:
  - Random folio pairs from same section/REGIME (background sharing rate)
  - Random folio pairs from different sections (cross-section baseline)
  - Bridge MIDDLE sharing rate for same pairs (is dark sharing different?)

Null: permutation test — shuffle dark MIDDLE identities across folios,
recompute pairwise sharing rates, compare real to null.
"""

import sys, os, io, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
bridge_set = pp_middles - dp_set

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# ═══ BUILD PER-FOLIO DARK AND BRIDGE MIDDLE SETS ═══
folio_dark = defaultdict(set)    # folio -> set of dark MIDDLEs present
folio_bridge = defaultdict(set)  # folio -> set of bridge MIDDLEs present
folio_dark_ct = defaultdict(Counter)  # folio -> dark MIDDLE -> count
folio_section = {}

for t in all_b:
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    if mid in dp_set:
        folio_dark[t.folio].add(mid)
        folio_dark_ct[t.folio][mid] += 1
    elif mid in bridge_set:
        folio_bridge[t.folio].add(mid)
    folio_section[t.folio] = t.section

folios = sorted(folio_dark.keys())
print(f"Folios with dark MIDDLEs: {len(folios)}")
print(f"Mean dark MIDDLEs per folio: {sum(len(v) for v in folio_dark.values())/len(folios):.1f}")

# ═══ JACCARD SIMILARITY ═══
def jaccard(s1, s2):
    if not s1 and not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0

# ═══ MATCHED FOLIO PAIRS ═══
print("\n" + "=" * 100)
print("RECIPE-MATCHED FOLIO PAIRS: Dark MIDDLE sharing")
print("=" * 100)

matched_pairs = [
    ('f75r', 'f84r', 'BALNEUM pair (both balneum mariae, honey-based)'),
    ('f75r', 'f108r', 'BALNEUM pair (both balneum, Ch19 vs Ch16)'),
    ('f84r', 'f108r', 'BALNEUM pair (both balneum, Ch14 vs Ch16)'),
    ('f75r', 'f76r', 'DISTILL pair (both distillation, different methods)'),
    ('f75r', 'f77v', 'DIFFERENT (aqua vitae vs furnace)'),
    ('f76r', 'f77v', 'DIFFERENT (element separation vs furnace)'),
    ('f76r', 'f84r', 'MIXED (element sep vs balneum gold dissolution)'),
]

print(f"\n  {'Pair':>16s} {'Dark Jac':>9s} {'Bridge Jac':>11s} {'Dark shared':>12s} {'Dark union':>11s} {'Type':>40s}")
print(f"  {'-'*100}")

for f1, f2, label in matched_pairs:
    d_jac = jaccard(folio_dark.get(f1, set()), folio_dark.get(f2, set()))
    b_jac = jaccard(folio_bridge.get(f1, set()), folio_bridge.get(f2, set()))
    d_shared = len(folio_dark.get(f1, set()) & folio_dark.get(f2, set()))
    d_union = len(folio_dark.get(f1, set()) | folio_dark.get(f2, set()))
    print(f"  {f1}-{f2:>5s} {d_jac:9.3f} {b_jac:11.3f} {d_shared:12d} {d_union:11d} {label:>40s}")

# ═══ BALNEUM vs NON-BALNEUM COMPARISON ═══
print("\n" + "=" * 100)
print("BALNEUM vs NON-BALNEUM: Is dark sharing higher within balneum folios?")
print("=" * 100)

balneum = ['f75r', 'f84r', 'f108r']
# Within-balneum pairs
bal_jacs = []
for i in range(len(balneum)):
    for j in range(i+1, len(balneum)):
        bal_jacs.append(jaccard(folio_dark[balneum[i]], folio_dark[balneum[j]]))

# Same-section random pairs (section B, REGIME 1 for fair comparison)
section_b_folios = [f for f in folios if folio_section.get(f) == 'B' and f not in balneum]
random.seed(42)
random_same_sec = []
for _ in range(200):
    if len(section_b_folios) >= 2:
        f1, f2 = random.sample(section_b_folios, 2)
        random_same_sec.append(jaccard(folio_dark[f1], folio_dark[f2]))

# All random pairs (any two folios)
random_all = []
for _ in range(500):
    f1, f2 = random.sample(folios, 2)
    random_all.append(jaccard(folio_dark[f1], folio_dark[f2]))

print(f"\n  Within-balneum (3 pairs): mean Jaccard = {sum(bal_jacs)/len(bal_jacs):.3f}")
print(f"    Pairs: {bal_jacs}")
print(f"  Same-section random (200 pairs): mean Jaccard = {sum(random_same_sec)/len(random_same_sec):.3f}")
print(f"  All random (500 pairs): mean Jaccard = {sum(random_all)/len(random_all):.3f}")

# Where does balneum sit in the random distribution?
bal_mean = sum(bal_jacs) / len(bal_jacs)
pct_above = 100 * sum(1 for x in random_same_sec if x >= bal_mean) / len(random_same_sec)
print(f"\n  Balneum mean ({bal_mean:.3f}) percentile in same-section: {100-pct_above:.0f}th")

# ═══ SHARED DARK MIDDLEs BETWEEN BALNEUM FOLIOS ═══
print("\n" + "=" * 100)
print("SPECIFIC DARK MIDDLEs SHARED ACROSS BALNEUM FOLIOS")
print("=" * 100)

bal_shared_all3 = folio_dark['f75r'] & folio_dark['f84r'] & folio_dark['f108r']
bal_shared_75_84 = folio_dark['f75r'] & folio_dark['f84r']
bal_shared_75_108 = folio_dark['f75r'] & folio_dark['f108r']
bal_shared_84_108 = folio_dark['f84r'] & folio_dark['f108r']

print(f"\n  All 3 balneum folios share: {len(bal_shared_all3)} dark MIDDLEs")
print(f"  f75r + f84r share: {len(bal_shared_75_84)}")
print(f"  f75r + f108r share: {len(bal_shared_75_108)}")
print(f"  f84r + f108r share: {len(bal_shared_84_108)}")

if bal_shared_all3:
    print(f"\n  Dark MIDDLEs on ALL 3 balneum folios:")
    from scripts.voynich import ATOM_GLOSSES
    for mid in sorted(bal_shared_all3):
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
        # How many folios total?
        n_folios = sum(1 for f in folios if mid in folio_dark[f])
        # If on most folios, it's generic. If on few, it's selective.
        print(f"    {mid:>8s} ({atoms:>25s})  on {n_folios}/{len(folios)} folios  {'<-- SELECTIVE' if n_folios < 20 else ''}")

# ═══ CHEKAR FOLIOS: Do they share more? ═══
print("\n" + "=" * 100)
print("CHEKAR FOLIOS (predicted balneum): Do they share more dark MIDDLEs?")
print("=" * 100)

chekar_folios = ['f75r', 'f84r', 'f108r', 'f33r', 'f34r', 'f94r', 'f95r1']
chekar_present = [f for f in chekar_folios if f in folio_dark]

# Pairwise Jaccard within chekar folios
chekar_jacs = []
for i in range(len(chekar_present)):
    for j in range(i+1, len(chekar_present)):
        chekar_jacs.append(jaccard(folio_dark[chekar_present[i]], folio_dark[chekar_present[j]]))

if chekar_jacs:
    chekar_mean = sum(chekar_jacs) / len(chekar_jacs)
    pct_ck = 100 * sum(1 for x in random_all if x >= chekar_mean) / len(random_all)
    print(f"\n  Chekar folios present: {chekar_present}")
    print(f"  Within-chekar (pairwise): mean Jaccard = {chekar_mean:.3f} ({len(chekar_jacs)} pairs)")
    print(f"  Random baseline: mean Jaccard = {sum(random_all)/len(random_all):.3f}")
    print(f"  Chekar percentile: {100-pct_ck:.0f}th")

# ═══ PERMUTATION TEST ═══
print("\n" + "=" * 100)
print("PERMUTATION TEST: Is balneum dark sharing above chance?")
print("=" * 100)

# Shuffle dark MIDDLEs across folios while preserving per-folio count
random.seed(42)
all_dark_mids = list(dp_set)
N_PERM = 1000
null_means = []

for _ in range(N_PERM):
    # For each folio, randomly draw the same NUMBER of dark MIDDLEs from the full pool
    shuffled = {}
    for f in balneum:
        n = len(folio_dark[f])
        shuffled[f] = set(random.sample(all_dark_mids, min(n, len(all_dark_mids))))

    # Compute within-balneum Jaccard
    perm_jacs = []
    for i in range(len(balneum)):
        for j in range(i+1, len(balneum)):
            perm_jacs.append(jaccard(shuffled[balneum[i]], shuffled[balneum[j]]))
    null_means.append(sum(perm_jacs) / len(perm_jacs))

real_mean = sum(bal_jacs) / len(bal_jacs)
p_value = sum(1 for x in null_means if x >= real_mean) / N_PERM
null_avg = sum(null_means) / len(null_means)

print(f"\n  Real balneum mean Jaccard: {real_mean:.3f}")
print(f"  Null mean (shuffled): {null_avg:.3f}")
print(f"  p-value: {p_value:.3f} (fraction of nulls >= real)")
if p_value < 0.01:
    print(f"  *** p < 0.01 SIGNIFICANT — balneum folios share MORE dark MIDDLEs than chance ***")
elif p_value < 0.05:
    print(f"  * p < 0.05 SIGNIFICANT *")
else:
    print(f"  NOT SIGNIFICANT (p={p_value:.3f})")

# ═══ BRIDGE COMPARISON ═══
print("\n" + "=" * 100)
print("BRIDGE COMPARISON: Is dark sharing pattern different from bridge?")
print("=" * 100)

bal_bridge_jacs = []
for i in range(len(balneum)):
    for j in range(i+1, len(balneum)):
        bal_bridge_jacs.append(jaccard(folio_bridge[balneum[i]], folio_bridge[balneum[j]]))

random_bridge = []
for _ in range(500):
    f1, f2 = random.sample(folios, 2)
    random_bridge.append(jaccard(folio_bridge[f1], folio_bridge[f2]))

print(f"\n  Within-balneum bridge Jaccard: {sum(bal_bridge_jacs)/len(bal_bridge_jacs):.3f}")
print(f"  Random bridge Jaccard: {sum(random_bridge)/len(random_bridge):.3f}")
print(f"  Within-balneum dark Jaccard: {real_mean:.3f}")
print(f"  Random dark Jaccard: {sum(random_all)/len(random_all):.3f}")

dark_lift = real_mean / (sum(random_all)/len(random_all)) if sum(random_all) > 0 else 0
bridge_lift = (sum(bal_bridge_jacs)/len(bal_bridge_jacs)) / (sum(random_bridge)/len(random_bridge)) if sum(random_bridge) > 0 else 0
print(f"\n  Dark sharing lift (balneum/random): {dark_lift:.2f}x")
print(f"  Bridge sharing lift (balneum/random): {bridge_lift:.2f}x")
print(f"  {'Dark lifts MORE' if dark_lift > bridge_lift else 'Bridge lifts MORE or equal'}")

# ═══ VERDICT ═══
print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)

if p_value < 0.05 and dark_lift > bridge_lift:
    print(f"""
  PASS: Balneum folios share significantly more dark MIDDLEs than chance
  (p={p_value:.3f}), and the dark sharing lift ({dark_lift:.2f}x) exceeds
  bridge sharing lift ({bridge_lift:.2f}x). Dark MIDDLEs carry recipe-specific
  vocabulary that clusters by procedure type.
""")
elif p_value < 0.05:
    print(f"""
  PARTIAL: Balneum folios share more dark MIDDLEs than chance (p={p_value:.3f}),
  but bridge sharing lift ({bridge_lift:.2f}x) is equal or higher. The dark
  sharing may be driven by general section/REGIME similarity, not recipe-specific
  content.
""")
else:
    print(f"""
  FAIL: Balneum folios do NOT share significantly more dark MIDDLEs than
  chance (p={p_value:.3f}). The pointer hypothesis is not supported by
  cross-folio dark MIDDLE sharing patterns.
""")

print("=" * 100)
print("DONE")
print("=" * 100)
