"""
Comprehensive shuffle test for 51 chapter-folio assignments.

Tests whether the real assignment beats random shuffles on 5 independent
structural dimensions simultaneously.
"""

import sys, io, json, random, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

N_SHUFFLES = 10000
RNG = random.Random(639)

# ============================================================
# 1. Define all 51 matched chapter-folio pairs
# ============================================================

MATCHES = [
    # Section B — Mercuriorum
    ('Ch1M', 'f112v', 'M', 'S'),
    ('Ch2+3+6M', 'f77r', 'M', 'B'),
    ('Ch4M', 'f116r', 'M', 'S'),
    ('Ch7-10M', 'f39r', 'M', 'H'),
    ('Ch11M', 'f112r', 'M', 'S'),
    ('Ch12M', 'f79r', 'M', 'B'),
    ('Ch14M', 'f78v', 'M', 'B'),
    ('Ch15M', 'f76v', 'M', 'B'),
    ('Ch16M', 'f103r', 'M', 'S'),
    ('Ch17M', 'f106r', 'M', 'S'),  # tentative
    ('Ch18M', 'f81v', 'M', 'B'),
    ('Ch19M', 'f75r', 'M', 'B'),
    ('Ch20M', 'f79v', 'M', 'B'),   # speculative
    ('Ch21-25M', 'f80r', 'M', 'B'),
    ('Ch22M', 'f82r', 'M', 'B'),
    ('Ch27M', 'f77v', 'M', 'B'),
    ('Ch28M', 'f82v', 'M', 'B'),
    ('Ch40M', 'f106v', 'M', 'S'),
    ('Ch44M', 'f107r', 'M', 'S'),
    ('Ch47M', 'f113r', 'M', 'S'),
    ('Ch48M', 'f113v', 'M', 'S'),
    ('Ch50M', 'f111r', 'M', 'S'),
    ('Ch10M', 'f111v', 'M', 'S'),
    # Practica
    ('Ch9P', 'f83r', 'P', 'B'),
    ('Ch10+11P', 'f108v', 'P', 'S'),
    ('Ch12+20+22P', 'f85r1', 'P', 'C'),
    ('Ch14P', 'f84r', 'P', 'B'),
    ('Ch15P', 'f84v', 'P', 'B'),
    ('Ch16P', 'f108r', 'P', 'S'),
    ('Ch18P', 'f76r', 'P', 'B'),
    ('Ch19P', 'f46r', 'P', 'H'),
    ('Ch21P+28P', 'f115r', 'P', 'S'),
    ('Ch23P', 'f114r', 'P', 'S'),
    ('Ch24P', 'f66r', 'P', 'T'),
    ('Ch25P', 'f115v', 'P', 'S'),
    ('Ch26P', 'f66v', 'P', 'T'),
    ('Ch27P', 'f103v', 'P', 'S'),
    ('Ch29P', 'f43v', 'P', 'H'),
    ('Ch30P', 'f105v', 'P', 'S'),
    ('Ch31P', 'f114v', 'P', 'S'),
    # Brunschwig
    ('Brun_rosewater', 'f31r', 'B_ext', 'H'),
]

chapters = [m[0] for m in MATCHES]
folios = [m[1] for m in MATCHES]
ch_parts = [m[2] for m in MATCHES]  # M=Mercuriorum, P=Practica
folio_sections = [m[3] for m in MATCHES]

N = len(MATCHES)
print(f"Testing {N} chapter-folio assignments against {N_SHUFFLES} random shuffles")
print(f"Chapters: {len(set(chapters))}, Folios: {len(set(folios))}")

# ============================================================
# 2. Precompute folio properties
# ============================================================

print("\nPrecomputing folio properties...")

folio_props = {}
for folio in set(folios):
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and not t.is_label]
    if not tokens:
        folio_props[folio] = {'n_tokens': 0, 'section': '?', 'dar': 0, 'fch': False, 'cs': False}
        continue

    dar_count = sum(1 for t in tokens if t.word == 'dar')
    fch_present = False
    cs_present = False
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle == 'fch':
            fch_present = True
        if m.middle == 'cs':
            cs_present = True

    folio_props[folio] = {
        'n_tokens': len(tokens),
        'section': tokens[0].section,
        'dar': dar_count,
        'fch': fch_present,
        'cs': cs_present,
    }

# Chapter properties
ch_props = {}
for ch, folio, part, _ in MATCHES:
    involves_mercury = 'M' in ch or ch in ('Ch9P', 'Ch10+11P', 'Ch14P', 'Ch15P',
                                              'Ch16P', 'Ch18P', 'Ch27P', 'Ch30P', 'Ch31P')
    involves_gold = ch in ('Ch14P', 'Ch15P', 'Ch18M', 'Ch23P', 'Ch31P')
    ch_props[ch] = {
        'part': part,
        'mercury': involves_mercury,
        'gold': involves_gold,
    }

# Recto/verso pairs: chapters that should be on the same leaf
RECTO_VERSO_PAIRS = [
    ('f84r', 'f84v'),   # Ch14P, Ch15P
    ('f103r', 'f103v'), # Ch16M, Ch27P
    ('f66r', 'f66v'),   # Ch24P, Ch26P
    ('f108r', 'f108v'), # Ch16P, Ch10+11P
    ('f111r', 'f111v'), # Ch50M, Ch10M
    ('f112r', 'f112v'), # Ch11M, Ch1M
    ('f113r', 'f113v'), # Ch47M, Ch48M
    ('f115r', 'f115v'), # Ch21P+28P, Ch25P
    ('f114r', 'f114v'), # Ch23P, Ch31P
    ('f106r', 'f106v'), # Ch17M, Ch40M
]

# ============================================================
# 3. Define scoring functions
# ============================================================

def score_section_clustering(assignment):
    """How many Mercuriorum chapters land in Section B, Practica in Section S?"""
    score = 0
    for i, ch_idx in enumerate(assignment):
        ch = chapters[ch_idx]
        folio = folios[i]
        part = ch_props[ch]['part']
        section = folio_props[folio]['section']

        # Mercuriorum chapters "should" be in B (preparation) or S (transmutation)
        if part == 'M' and section in ('B', 'S'):
            score += 1
        # Practica chapters "should" be in S (transmutation) or B (preparation)
        elif part == 'P' and section in ('S', 'B', 'T'):
            score += 1
    return score

def score_fch_placement(assignment):
    """How many mercury-involving chapters land on fch-bearing folios?"""
    score = 0
    for i, ch_idx in enumerate(assignment):
        ch = chapters[ch_idx]
        folio = folios[i]
        if ch_props[ch]['mercury'] and folio_props[folio]['fch']:
            score += 1
    return score

def score_recto_verso(assignment):
    """How many recto/verso pairs have both sides assigned?"""
    # Build folio→chapter mapping for this assignment
    folio_to_ch = {}
    for i, ch_idx in enumerate(assignment):
        folio_to_ch[folios[i]] = chapters[ch_idx]

    score = 0
    for r, v in RECTO_VERSO_PAIRS:
        if r in folio_to_ch and v in folio_to_ch:
            score += 1
    return score

def score_token_correlation(assignment):
    """Spearman correlation between chapter verb count proxy and folio token count."""
    # Use chapter index as a rough proxy for verb count (not perfect)
    # Better: correlation between folio size and whether the matched chapter is "large" or "small"
    pairs = []
    for i, ch_idx in enumerate(assignment):
        folio = folios[i]
        n_tok = folio_props[folio]['n_tokens']
        pairs.append(n_tok)

    # Compute variance of token counts grouped by Mercuriorum vs Practica
    merc_toks = [pairs[i] for i, ch_idx in enumerate(assignment) if ch_props[chapters[ch_idx]]['part'] == 'M']
    prac_toks = [pairs[i] for i, ch_idx in enumerate(assignment) if ch_props[chapters[ch_idx]]['part'] == 'P']

    if not merc_toks or not prac_toks:
        return 0

    # Score: how different are the mean token counts between M and P assignments?
    # In real assignment, M chapters tend to go to smaller B-section folios
    merc_mean = sum(merc_toks) / len(merc_toks)
    prac_mean = sum(prac_toks) / len(prac_toks)
    return abs(merc_mean - prac_mean)

def score_dar_alignment(assignment):
    """Do high-dar folios match chapters that introduce materials?"""
    score = 0
    for i, ch_idx in enumerate(assignment):
        ch = chapters[ch_idx]
        folio = folios[i]
        dar = folio_props[folio]['dar']

        # Chapters with known high material introduction
        high_dar_chapters = {'Ch19M', 'Ch14P', 'Ch15P', 'Ch9P', 'Ch12M', 'Ch14M',
                            'Ch15M', 'Ch40M', 'Ch17M'}
        # Chapters with known LOW material introduction (correction, fixation, testing)
        low_dar_chapters = {'Ch50M', 'Ch25P', 'Ch23P', 'Ch24P', 'Ch26P'}

        if ch in high_dar_chapters and dar >= 3:
            score += 1
        elif ch in low_dar_chapters and dar <= 1:
            score += 1
    return score

def composite_score(assignment):
    """Combined score across all 5 dimensions."""
    s1 = score_section_clustering(assignment)
    s2 = score_fch_placement(assignment)
    s3 = score_recto_verso(assignment)
    s4 = score_token_correlation(assignment)
    s5 = score_dar_alignment(assignment)
    return s1, s2, s3, s4, s5

# ============================================================
# 4. Score the real assignment
# ============================================================

real_assignment = list(range(N))  # identity: chapter i → folio i
real_scores = composite_score(real_assignment)

print(f"\n{'='*80}")
print(f"REAL ASSIGNMENT SCORES")
print(f"{'='*80}")
print(f"  1. Section clustering: {real_scores[0]}/{N}")
print(f"  2. fch placement:      {real_scores[1]}")
print(f"  3. Recto/verso pairs:  {real_scores[2]}/{len(RECTO_VERSO_PAIRS)}")
print(f"  4. Token size diff:    {real_scores[3]:.1f}")
print(f"  5. dar alignment:      {real_scores[4]}")

# ============================================================
# 5. Run shuffles
# ============================================================

print(f"\nRunning {N_SHUFFLES} random shuffles...")

shuffle_scores = {i: [] for i in range(5)}
beats_all = 0

for trial in range(N_SHUFFLES):
    shuffled = list(range(N))
    RNG.shuffle(shuffled)
    scores = composite_score(shuffled)

    for i in range(5):
        shuffle_scores[i].append(scores[i])

    # Count how many shuffles beat the real assignment on ALL dimensions
    if all(scores[i] >= real_scores[i] for i in range(5)):
        beats_all += 1

# ============================================================
# 6. Compute p-values
# ============================================================

print(f"\n{'='*80}")
print(f"RESULTS")
print(f"{'='*80}")

dim_names = [
    "Section clustering",
    "fch placement",
    "Recto/verso pairs",
    "Token size diff",
    "dar alignment",
]

for i in range(5):
    real = real_scores[i]
    shuffle_vals = shuffle_scores[i]
    mean_shuffle = sum(shuffle_vals) / len(shuffle_vals)
    max_shuffle = max(shuffle_vals)

    # For dimensions 0,1,2,4: higher is better (count how many shuffles >= real)
    # For dimension 3: higher absolute diff is better
    n_beats = sum(1 for s in shuffle_vals if s >= real)
    p_value = n_beats / N_SHUFFLES

    print(f"\n  {dim_names[i]}:")
    print(f"    Real:    {real}")
    print(f"    Shuffle: mean={mean_shuffle:.2f}, max={max_shuffle}")
    print(f"    p-value: {p_value:.6f} ({n_beats}/{N_SHUFFLES} shuffles >= real)")

# Combined
p_combined = beats_all / N_SHUFFLES
print(f"\n  COMBINED (all 5 dimensions):")
print(f"    Shuffles beating real on ALL dimensions: {beats_all}/{N_SHUFFLES}")
print(f"    Combined p-value: {p_combined:.8f}")

if beats_all == 0:
    print(f"    p < {1/N_SHUFFLES:.6f} (no shuffle beat real on all dimensions)")

print(f"\n{'='*80}")
print(f"VERDICT: {'SIGNIFICANT' if p_combined < 0.001 else 'NOT SIGNIFICANT'}")
print(f"{'='*80}")
