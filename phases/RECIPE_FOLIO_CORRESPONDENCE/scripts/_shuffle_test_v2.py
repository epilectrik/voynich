"""
Comprehensive shuffle test v2 — sharper tests.

Tests whether the real 41 chapter-folio assignments beat random shuffles
on structural dimensions that actually discriminate.
"""

import sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

N_SHUFFLES = 10000
RNG = random.Random(639)

# ============================================================
# 1. Define matches with specific properties
# ============================================================

# Each entry: (chapter, folio, part, folio_section, chapter_number_in_source)
# chapter_number is sequential position within Mercuriorum or Practica
MATCHES = [
    ('Ch1M', 'f112v', 'M', 'S', 1),
    ('Ch2+3+6M', 'f77r', 'M', 'B', 2),
    ('Ch4M', 'f116r', 'M', 'S', 4),
    ('Ch7-10M', 'f39r', 'M', 'H', 7),
    ('Ch10M', 'f111v', 'M', 'S', 10),
    ('Ch11M', 'f112r', 'M', 'S', 11),
    ('Ch12M', 'f79r', 'M', 'B', 12),
    ('Ch14M', 'f78v', 'M', 'B', 14),
    ('Ch15M', 'f76v', 'M', 'B', 15),
    ('Ch16M', 'f103r', 'M', 'S', 16),
    ('Ch17M', 'f106r', 'M', 'S', 17),
    ('Ch18M', 'f81v', 'M', 'B', 18),
    ('Ch19M', 'f75r', 'M', 'B', 19),
    ('Ch20M', 'f79v', 'M', 'B', 20),
    ('Ch21-25M', 'f80r', 'M', 'B', 21),
    ('Ch22M', 'f82r', 'M', 'B', 22),
    ('Ch27M', 'f77v', 'M', 'B', 27),
    ('Ch28M', 'f82v', 'M', 'B', 28),
    ('Ch40M', 'f106v', 'M', 'S', 40),
    ('Ch44M', 'f107r', 'M', 'S', 44),
    ('Ch47M', 'f113r', 'M', 'S', 47),
    ('Ch48M', 'f113v', 'M', 'S', 48),
    ('Ch50M', 'f111r', 'M', 'S', 50),
    ('Ch9P', 'f83r', 'P', 'B', 109),
    ('Ch10+11P', 'f108v', 'P', 'S', 110),
    ('Ch12+20+22P', 'f85r1', 'P', 'C', 112),
    ('Ch14P', 'f84r', 'P', 'B', 114),
    ('Ch15P', 'f84v', 'P', 'B', 115),
    ('Ch16P', 'f108r', 'P', 'S', 116),
    ('Ch18P', 'f76r', 'P', 'B', 118),
    ('Ch19P', 'f46r', 'P', 'H', 119),
    ('Ch21P+28P', 'f115r', 'P', 'S', 121),
    ('Ch23P', 'f114r', 'P', 'S', 123),
    ('Ch24P', 'f66r', 'P', 'T', 124),
    ('Ch25P', 'f115v', 'P', 'S', 125),
    ('Ch26P', 'f66v', 'P', 'T', 126),
    ('Ch27P', 'f103v', 'P', 'S', 127),
    ('Ch29P', 'f43v', 'P', 'H', 129),
    ('Ch30P', 'f105v', 'P', 'S', 130),
    ('Ch31P', 'f114v', 'P', 'S', 131),
    ('Brun', 'f31r', 'B_ext', 'H', 999),
]

chapters = [m[0] for m in MATCHES]
folios = [m[1] for m in MATCHES]
parts = [m[2] for m in MATCHES]
sections = [m[3] for m in MATCHES]
ch_numbers = [m[4] for m in MATCHES]
N = len(MATCHES)

print(f"Testing {N} assignments against {N_SHUFFLES} shuffles\n")

# ============================================================
# 2. Precompute folio properties
# ============================================================

folio_props = {}
for folio in set(folios):
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and not t.is_label]
    n = len(tokens)
    dar = sum(1 for t in tokens if t.word == 'dar')
    fch = any(morph.extract(t.word).middle == 'fch' for t in tokens)
    section = tokens[0].section if tokens else '?'
    folio_props[folio] = {'n': n, 'dar': dar, 'fch': fch, 'section': section}

# Leaf mapping: which folios share a physical leaf
def get_leaf(folio):
    """Extract leaf identifier (e.g., f84 from f84r or f84v)."""
    base = folio.rstrip('0123456789')
    if base.endswith('r') or base.endswith('v'):
        return base[:-1]
    return base

# ============================================================
# 3. Define SHARP scoring functions
# ============================================================

def score_merc_in_section_b(assignment):
    """SPECIFIC: Mercuriorum PREPARATION chapters (Ch1-Ch28) in Section B only."""
    score = 0
    for i, ch_idx in enumerate(assignment):
        part = parts[ch_idx]
        ch_num = ch_numbers[ch_idx]
        folio_section = folio_props[folios[i]]['section']
        # Mercuriorum chapters 1-28 = preparation → should be Section B
        if part == 'M' and ch_num <= 28 and folio_section == 'B':
            score += 1
    return score

def score_higher_merc_in_section_s(assignment):
    """SPECIFIC: Higher Mercuriorum chapters (Ch40+) in Section S only."""
    score = 0
    for i, ch_idx in enumerate(assignment):
        part = parts[ch_idx]
        ch_num = ch_numbers[ch_idx]
        folio_section = folio_props[folios[i]]['section']
        if part == 'M' and ch_num >= 40 and folio_section == 'S':
            score += 1
    return score

def score_practica_in_section_s(assignment):
    """SPECIFIC: Practica transmutation chapters in Section S only."""
    score = 0
    for i, ch_idx in enumerate(assignment):
        part = parts[ch_idx]
        ch_num = ch_numbers[ch_idx]
        folio_section = folio_props[folios[i]]['section']
        if part == 'P' and folio_section == 'S':
            score += 1
    return score

def score_recto_verso_adjacency(assignment):
    """For folios on the same leaf, are the assigned chapters ADJACENT in source?"""
    # Build folio→chapter_number mapping
    folio_to_chnum = {}
    for i, ch_idx in enumerate(assignment):
        folio_to_chnum[folios[i]] = ch_numbers[ch_idx]

    # Check each pair of folios on the same leaf
    leaf_groups = {}
    for f in folios:
        leaf = get_leaf(f)
        if leaf not in leaf_groups:
            leaf_groups[leaf] = []
        leaf_groups[leaf].append(f)

    score = 0
    for leaf, leaf_folios in leaf_groups.items():
        if len(leaf_folios) == 2:
            ch1 = folio_to_chnum.get(leaf_folios[0])
            ch2 = folio_to_chnum.get(leaf_folios[1])
            if ch1 is not None and ch2 is not None:
                diff = abs(ch1 - ch2)
                # Adjacent = within 5 chapter numbers of each other
                # (allows for multi-chapter folios and small gaps)
                if diff <= 5:
                    score += 1
    return score

def score_fch_on_mercury_recipe(assignment):
    """SPECIFIC: Among folios WITH fch, how many are assigned to mercury-processing chapters?"""
    mercury_chapters = {'Ch12M', 'Ch14M', 'Ch15M', 'Ch16M', 'Ch17M', 'Ch18M', 'Ch19M',
                       'Ch20M', 'Ch40M', 'Ch44M', 'Ch47M', 'Ch48M', 'Ch50M',
                       'Ch9P', 'Ch10+11P', 'Ch14P', 'Ch15P', 'Ch16P', 'Ch18P', 'Ch27P'}
    score = 0
    total_fch = 0
    for i, ch_idx in enumerate(assignment):
        folio = folios[i]
        if folio_props[folio]['fch']:
            total_fch += 1
            if chapters[ch_idx] in mercury_chapters:
                score += 1
    return score, total_fch

# ============================================================
# 4. Score real assignment
# ============================================================

real = list(range(N))
r_merc_b = score_merc_in_section_b(real)
r_higher_s = score_higher_merc_in_section_s(real)
r_prac_s = score_practica_in_section_s(real)
r_rv = score_recto_verso_adjacency(real)
r_fch, fch_total = score_fch_on_mercury_recipe(real)

print("=" * 80)
print("REAL ASSIGNMENT SCORES")
print("=" * 80)
print(f"  1. Merc prep (Ch1-28) in Section B:    {r_merc_b}")
print(f"  2. Higher Merc (Ch40+) in Section S:   {r_higher_s}")
print(f"  3. Practica in Section S:              {r_prac_s}")
print(f"  4. Recto/verso chapter adjacency:      {r_rv}")
print(f"  5. fch folios → mercury chapters:      {r_fch}/{fch_total}")

# ============================================================
# 5. Run shuffles
# ============================================================

print(f"\nRunning {N_SHUFFLES} shuffles...")

counts = {'merc_b': 0, 'higher_s': 0, 'prac_s': 0, 'rv': 0, 'fch': 0, 'all': 0}
shuffle_vals = {'merc_b': [], 'higher_s': [], 'prac_s': [], 'rv': [], 'fch': []}

for _ in range(N_SHUFFLES):
    shuf = list(range(N))
    RNG.shuffle(shuf)

    s_mb = score_merc_in_section_b(shuf)
    s_hs = score_higher_merc_in_section_s(shuf)
    s_ps = score_practica_in_section_s(shuf)
    s_rv = score_recto_verso_adjacency(shuf)
    s_fch, _ = score_fch_on_mercury_recipe(shuf)

    shuffle_vals['merc_b'].append(s_mb)
    shuffle_vals['higher_s'].append(s_hs)
    shuffle_vals['prac_s'].append(s_ps)
    shuffle_vals['rv'].append(s_rv)
    shuffle_vals['fch'].append(s_fch)

    if s_mb >= r_merc_b:
        counts['merc_b'] += 1
    if s_hs >= r_higher_s:
        counts['higher_s'] += 1
    if s_ps >= r_prac_s:
        counts['prac_s'] += 1
    if s_rv >= r_rv:
        counts['rv'] += 1
    if s_fch >= r_fch:
        counts['fch'] += 1
    if (s_mb >= r_merc_b and s_hs >= r_higher_s and s_ps >= r_prac_s
            and s_rv >= r_rv and s_fch >= r_fch):
        counts['all'] += 1

# ============================================================
# 6. Results
# ============================================================

print(f"\n{'='*80}")
print("RESULTS")
print("=" * 80)

tests = [
    ('Merc prep (Ch1-28) → Section B', 'merc_b', r_merc_b),
    ('Higher Merc (Ch40+) → Section S', 'higher_s', r_higher_s),
    ('Practica → Section S', 'prac_s', r_prac_s),
    ('Recto/verso adjacency (within 5 chapters)', 'rv', r_rv),
    ('fch folios → mercury chapters', 'fch', r_fch),
]

for name, key, real_val in tests:
    vals = shuffle_vals[key]
    mean_s = sum(vals) / len(vals)
    max_s = max(vals)
    p = counts[key] / N_SHUFFLES
    print(f"\n  {name}:")
    print(f"    Real: {real_val}  |  Shuffle: mean={mean_s:.2f}, max={max_s}")
    print(f"    p = {p:.6f} ({counts[key]}/{N_SHUFFLES})")

print(f"\n  COMBINED (all 5 dimensions simultaneously):")
print(f"    Shuffles >= real on ALL: {counts['all']}/{N_SHUFFLES}")
p_all = counts['all'] / N_SHUFFLES
print(f"    p = {p_all:.8f}")
if counts['all'] == 0:
    print(f"    p < {1/N_SHUFFLES:.6f}")

print(f"\n{'='*80}")
if p_all < 0.001:
    print("VERDICT: HIGHLY SIGNIFICANT (p < 0.001)")
elif p_all < 0.01:
    print("VERDICT: SIGNIFICANT (p < 0.01)")
elif p_all < 0.05:
    print("VERDICT: MARGINALLY SIGNIFICANT (p < 0.05)")
else:
    print("VERDICT: NOT SIGNIFICANT")
print("=" * 80)
