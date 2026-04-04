"""
Comprehensive shuffle test v3 — 10 dimensions including fine-grained signals.

Tests whether the real 41 chapter-folio assignments beat random shuffles
on coarse structural AND fine-grained atom-level dimensions.
"""

import sys, io, random, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

N_SHUFFLES = 10000
RNG = random.Random(639)

# ============================================================
# 1. Define matches
# ============================================================

MATCHES = [
    # (chapter, folio, part, ch_number, expected_dar, expected_zero_dar, has_fermentation)
    ('Ch1M', 'f112v', 'M', 1, None, False, False),
    ('Ch2+3+6M', 'f77r', 'M', 2, None, False, False),
    ('Ch4M', 'f116r', 'M', 4, None, False, False),
    ('Ch7-10M', 'f39r', 'M', 7, None, False, False),
    ('Ch10M', 'f111v', 'M', 10, None, False, False),
    ('Ch11M', 'f112r', 'M', 11, None, False, False),
    ('Ch12M', 'f79r', 'M', 12, None, False, False),
    ('Ch14M', 'f78v', 'M', 14, None, False, True),
    ('Ch15M', 'f76v', 'M', 15, None, False, True),
    ('Ch16M', 'f103r', 'M', 16, None, False, True),
    ('Ch17M', 'f106r', 'M', 17, None, False, True),
    ('Ch18M', 'f81v', 'M', 18, None, False, False),
    ('Ch19M', 'f75r', 'M', 19, 'high', False, False),
    ('Ch20M', 'f79v', 'M', 20, None, False, False),
    ('Ch21-25M', 'f80r', 'M', 21, None, False, False),
    ('Ch22M', 'f82r', 'M', 22, None, False, False),
    ('Ch27M', 'f77v', 'M', 27, None, False, False),
    ('Ch28M', 'f82v', 'M', 28, None, False, False),
    ('Ch40M', 'f106v', 'M', 40, None, False, False),
    ('Ch44M', 'f107r', 'M', 44, None, False, False),
    ('Ch47M', 'f113r', 'M', 47, None, False, False),
    ('Ch48M', 'f113v', 'M', 48, None, False, True),
    ('Ch50M', 'f111r', 'M', 50, None, True, False),  # error correction = zero dar
    ('Ch9P', 'f83r', 'P', 109, None, False, False),
    ('Ch10+11P', 'f108v', 'P', 110, None, False, False),
    ('Ch12+20+22P', 'f85r1', 'P', 112, None, False, False),
    ('Ch14P', 'f84r', 'P', 114, None, False, False),
    ('Ch15P', 'f84v', 'P', 115, 'high', False, False),  # dar=4 for 4 introductions
    ('Ch16P', 'f108r', 'P', 116, None, False, False),
    ('Ch18P', 'f76r', 'P', 118, None, False, False),
    ('Ch19P', 'f46r', 'P', 119, None, False, False),
    ('Ch21P+28P', 'f115r', 'P', 121, None, False, False),
    ('Ch23P', 'f114r', 'P', 123, None, True, False),   # testing = zero dar effectively
    ('Ch24P', 'f66r', 'P', 124, None, False, False),
    ('Ch25P', 'f115v', 'P', 125, None, True, False),   # fixation = zero dar
    ('Ch26P', 'f66v', 'P', 126, None, False, False),
    ('Ch27P', 'f103v', 'P', 127, None, False, False),
    ('Ch29P', 'f43v', 'P', 129, None, False, False),
    ('Ch30P', 'f105v', 'P', 130, None, False, False),
    ('Ch31P', 'f114v', 'P', 131, None, False, False),
    ('Brun', 'f31r', 'B_ext', 999, None, False, False),
]

chapters = [m[0] for m in MATCHES]
folios = [m[1] for m in MATCHES]
parts = [m[2] for m in MATCHES]
ch_nums = [m[3] for m in MATCHES]
expected_dars = [m[4] for m in MATCHES]
expected_zero_dars = [m[5] for m in MATCHES]
has_fermentation = [m[6] for m in MATCHES]
N = len(MATCHES)

# ============================================================
# 2. Precompute folio properties
# ============================================================

print("Precomputing folio properties...")

folio_props = {}
for folio in set(folios):
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and not t.is_label]
    n = len(tokens)
    dar = sum(1 for t in tokens if t.word == 'dar')
    dal = sum(1 for t in tokens if t.word == 'dal')
    daiin = sum(1 for t in tokens if t.word == 'daiin')

    fch = False
    cs = False
    ro = False
    eed_count = 0
    e_depth_2plus = 0

    prefixes = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        a = morph.atomize(t.word)
        if m.middle == 'fch': fch = True
        if m.middle == 'cs': cs = True
        if m.middle == 'ro': ro = True
        if m.middle == 'eed': eed_count += 1
        if a.e_depth >= 2: e_depth_2plus += 1
        if a.prefix: prefixes[a.prefix] += 1

    section = tokens[0].section if tokens else '?'

    folio_props[folio] = {
        'n': n, 'dar': dar, 'dal': dal, 'daiin': daiin,
        'fch': fch, 'cs': cs, 'ro': ro, 'eed': eed_count,
        'e2plus': e_depth_2plus / n if n > 0 else 0,
        'section': section,
        'sh_frac': prefixes.get('sh', 0) / n if n > 0 else 0,
        'ch_frac': prefixes.get('ch', 0) / n if n > 0 else 0,
        'qo_frac': prefixes.get('qo', 0) / n if n > 0 else 0,
        'lk_pfx': prefixes.get('lk', 0),
    }

def get_leaf(folio):
    base = folio.rstrip('0123456789')
    if base.endswith('r') or base.endswith('v'):
        return base[:-1]
    return base

# ============================================================
# 3. Scoring functions (10 dimensions)
# ============================================================

def score_all(assignment):
    scores = []

    # DIM 1: Merc prep (Ch1-28) in Section B
    s = sum(1 for i, ci in enumerate(assignment)
            if parts[ci] == 'M' and ch_nums[ci] <= 28
            and folio_props[folios[i]]['section'] == 'B')
    scores.append(s)

    # DIM 2: Higher Merc (Ch40+) in Section S
    s = sum(1 for i, ci in enumerate(assignment)
            if parts[ci] == 'M' and ch_nums[ci] >= 40
            and folio_props[folios[i]]['section'] == 'S')
    scores.append(s)

    # DIM 3: Recto/verso chapter adjacency (within 5)
    folio_to_chnum = {folios[i]: ch_nums[ci] for i, ci in enumerate(assignment)}
    leaf_groups = {}
    for f in folios:
        leaf = get_leaf(f)
        if leaf not in leaf_groups:
            leaf_groups[leaf] = []
        leaf_groups[leaf].append(f)
    s = 0
    for leaf, lf in leaf_groups.items():
        if len(lf) == 2:
            c1 = folio_to_chnum.get(lf[0])
            c2 = folio_to_chnum.get(lf[1])
            if c1 is not None and c2 is not None and abs(c1 - c2) <= 5:
                s += 1
    scores.append(s)

    # DIM 4: fch folios match mercury chapters
    mercury_chs = {'Ch12M','Ch14M','Ch15M','Ch16M','Ch17M','Ch18M','Ch19M',
                   'Ch20M','Ch40M','Ch44M','Ch47M','Ch48M','Ch50M',
                   'Ch9P','Ch10+11P','Ch14P','Ch15P','Ch16P','Ch18P','Ch27P'}
    s = sum(1 for i, ci in enumerate(assignment)
            if folio_props[folios[i]]['fch'] and chapters[ci] in mercury_chs)
    scores.append(s)

    # DIM 5: Zero-dar folios match non-additive recipes
    zero_dar_chs = [i for i in range(N) if expected_zero_dars[i]]
    s = sum(1 for i, ci in enumerate(assignment)
            if expected_zero_dars[ci] and folio_props[folios[i]]['dar'] <= 2)
    scores.append(s)

    # DIM 6: ro (fermentation marker) on fermentation chapters
    ferment_chs = [i for i in range(N) if has_fermentation[i]]
    s = sum(1 for i, ci in enumerate(assignment)
            if has_fermentation[ci] and folio_props[folios[i]]['ro'])
    scores.append(s)

    # DIM 7: High-eed folios match cooling-heavy chapters
    # Chapters with known heavy cooling: Ch25P (fixation), Ch23P (testing), Ch50M (correction)
    cooling_chs = {'Ch25P', 'Ch23P', 'Ch50M'}
    s = sum(1 for i, ci in enumerate(assignment)
            if chapters[ci] in cooling_chs and folio_props[folios[i]]['eed'] >= 5)
    scores.append(s)

    # DIM 8: e_depth >= 2 fraction correlates with balneum recipes
    # Chapters with known balneum: Ch14P, Ch10+11P, Ch18P, Ch19M
    balneum_chs = {'Ch14P', 'Ch10+11P', 'Ch18P', 'Ch19M'}
    balneum_e2 = [folio_props[folios[i]]['e2plus'] for i, ci in enumerate(assignment)
                  if chapters[ci] in balneum_chs]
    other_e2 = [folio_props[folios[i]]['e2plus'] for i, ci in enumerate(assignment)
                if chapters[ci] not in balneum_chs]
    if balneum_e2 and other_e2:
        s = sum(balneum_e2) / len(balneum_e2) - sum(other_e2) / len(other_e2)
    else:
        s = 0
    scores.append(s)

    # DIM 9: High daiin on iterative recipes
    iterative_chs = {'Ch23P', 'Ch48M', 'Ch19M'}
    s = sum(folio_props[folios[i]]['daiin'] for i, ci in enumerate(assignment)
            if chapters[ci] in iterative_chs)
    scores.append(s)

    # DIM 10: cs (gold marker) on gold-involving chapters
    gold_chs = {'Ch14P', 'Ch15P', 'Ch18M', 'Ch23P', 'Ch31P'}
    s = sum(1 for i, ci in enumerate(assignment)
            if chapters[ci] in gold_chs and folio_props[folios[i]]['cs'])
    scores.append(s)

    return scores

# ============================================================
# 4. Run
# ============================================================

real = list(range(N))
real_scores = score_all(real)

DIM_NAMES = [
    "Merc prep (Ch1-28) → Section B",
    "Higher Merc (Ch40+) → Section S",
    "Recto/verso adjacency (≤5 chapters)",
    "fch folios → mercury chapters",
    "Zero-dar folios → non-additive recipes",
    "ro marker → fermentation chapters",
    "High eed (≥5) → cooling-heavy chapters",
    "Balneum e_depth enrichment",
    "Cumulative daiin on iterative recipes",
    "cs marker → gold chapters",
]

print(f"\n{'='*80}")
print(f"REAL ASSIGNMENT SCORES (10 dimensions)")
print(f"{'='*80}")
for i, name in enumerate(DIM_NAMES):
    val = real_scores[i]
    if isinstance(val, float):
        print(f"  {i+1:2d}. {name:45s} {val:.4f}")
    else:
        print(f"  {i+1:2d}. {name:45s} {val}")

print(f"\nRunning {N_SHUFFLES} shuffles...")

counts_ge = [0] * 10
counts_all = 0
shuffle_means = [0.0] * 10
shuffle_maxes = [float('-inf')] * 10

for trial in range(N_SHUFFLES):
    shuf = list(range(N))
    RNG.shuffle(shuf)
    scores = score_all(shuf)

    all_ge = True
    for i in range(10):
        shuffle_means[i] += scores[i]
        if scores[i] > shuffle_maxes[i]:
            shuffle_maxes[i] = scores[i]
        if scores[i] >= real_scores[i]:
            counts_ge[i] += 1
        else:
            all_ge = False
    if all_ge:
        counts_all += 1

for i in range(10):
    shuffle_means[i] /= N_SHUFFLES

# ============================================================
# 5. Results
# ============================================================

print(f"\n{'='*80}")
print("RESULTS (10 DIMENSIONS)")
print("=" * 80)

for i, name in enumerate(DIM_NAMES):
    real_val = real_scores[i]
    mean_s = shuffle_means[i]
    max_s = shuffle_maxes[i]
    p = counts_ge[i] / N_SHUFFLES

    if isinstance(real_val, float):
        print(f"\n  {i+1}. {name}:")
        print(f"     Real: {real_val:.4f}  |  Shuffle: mean={mean_s:.4f}, max={max_s:.4f}")
    else:
        print(f"\n  {i+1}. {name}:")
        print(f"     Real: {real_val}  |  Shuffle: mean={mean_s:.2f}, max={max_s}")

    if p == 0:
        print(f"     p < {1/N_SHUFFLES:.6f} (0/{N_SHUFFLES})")
    else:
        print(f"     p = {p:.6f} ({counts_ge[i]}/{N_SHUFFLES})")

    if p < 0.01:
        print(f"     *** SIGNIFICANT ***")
    elif p < 0.05:
        print(f"     * marginally significant *")

p_all = counts_all / N_SHUFFLES
print(f"\n{'='*80}")
print(f"COMBINED (all 10 dimensions):")
print(f"  Shuffles >= real on ALL 10: {counts_all}/{N_SHUFFLES}")
if counts_all == 0:
    print(f"  p < {1/N_SHUFFLES:.6f}")
else:
    print(f"  p = {p_all:.8f}")

# Count significant individual dimensions
n_sig = sum(1 for i in range(10) if counts_ge[i] / N_SHUFFLES < 0.05)
print(f"\n  Individual dimensions significant at p<0.05: {n_sig}/10")
print(f"  Individual dimensions significant at p<0.01: {sum(1 for i in range(10) if counts_ge[i]/N_SHUFFLES < 0.01)}/10")

print(f"\n{'='*80}")
if counts_all == 0:
    print(f"VERDICT: HIGHLY SIGNIFICANT — p < {1/N_SHUFFLES:.6f}")
    print(f"Zero shuffles out of {N_SHUFFLES} replicated the real assignment")
    print(f"across all 10 structural dimensions simultaneously.")
else:
    print(f"VERDICT: Combined p = {p_all:.6f}")
print("=" * 80)
