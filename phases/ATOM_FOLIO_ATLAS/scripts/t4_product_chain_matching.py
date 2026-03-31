"""
Product chain matching: PL chapters that USE philosophical Mercury,
quintessence, and ferments as inputs -> Voynich folios.

Known chain:
  Ch18 (f76r) -> produces philosophical Mercury
  Ch19 (f75r) -> produces quintessence (9x distilled aqua vitae)
  Ch27 (f77v) -> furnace specification

Chapters that USE those products:
  Ch13-16: fermentation chapters (use Mercury + balneum mariae)
  Ch16: explicitly "bath of Maria" -> should match chekar folio
  Ch17: dissolution using Mercury + bath + ash separation
  Ch42-43: fixation of lead/tin using prepared elements
  Ch47: separation using ALL cipher-letter products (H,B,I,V,C,E)
  Ch51: uses "ninth wine" (= quintessence from Ch19/f75r)

Matching approach: derive expected operational profile from recipe text,
find closest folio in atlas feature space.
"""

import sys, io, json, math
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

with open(ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json', encoding='utf-8') as f:
    atlas = json.load(f)

# Already-matched folios (exclude from candidate pool)
already_matched = {'f75r', 'f76r', 'f77v', 'f84r', 'f108r', 'f81v', 'f83r', 'f84v', 'f112r'}

# Feature vector for matching
FEATURES = ['qo_pct', 'ch_pct', 'sh_pct', 'ok_pct', 'ot_pct', 'k_pct', 'e_pct', 'gentle_ratio']

def folio_vec(folio):
    e = atlas[folio]
    return [e[k] if k != 'gentle_ratio' else e[k] * 100 for k in FEATURES]

def euclidean(v1, v2):
    return sum((a-b)**2 for a,b in zip(v1, v2)) ** 0.5

# Candidate folios (unmatched)
candidates = [f for f in atlas if f not in already_matched]

# ═══ RECIPE-DERIVED EXPECTED PROFILES ═══
# Each recipe's operational expectations derived from the PL text

expected_profiles = {
    'Ch13_fermentation_tincture': {
        'description': 'Ferment of tincture — 7 cipher-letter substances, composite preparation',
        'recipe_text': 'Seven ferments composed of tincture: B(gold), C(sulfur), D(dissolved gold), E(water of composition), F, G',
        'expected': {
            'qo_pct': 15,    # moderate heat (fermentation, not distillation)
            'ch_pct': 20,    # testing products for quality
            'sh_pct': 15,    # monitoring fermentation
            'ok_pct': 5,     # some vessel work
            'ot_pct': 5,     # ops checking
            'k_pct': 12,     # moderate thermal
            'e_pct': 30,     # stability-dominant (fermentation)
            'gentle_ratio': 25, # balneum-compatible
        },
        'must_have': [],  # no specific markers required
        'prefer': {'doc_type': 'PROCEDURE'},
    },
    'Ch16_fermentation_balneum': {
        'description': 'Ferment multiplication via balneum mariae — EXPLICIT water bath',
        'recipe_text': 'evaporate them in the bath of Maria, and afterward place [them] upon...',
        'expected': {
            'qo_pct': 18,    # moderate heat
            'ch_pct': 15,    # some testing
            'sh_pct': 12,    # monitoring
            'ok_pct': 4,     # vessel work
            'ot_pct': 4,     # ops
            'k_pct': 15,     # thermal presence
            'e_pct': 28,     # stability
            'gentle_ratio': 25, # balneum = gentle
        },
        'must_have': ['chekar'],  # MUST have chekar (balneum marker)
        'prefer': {'doc_type': 'PROCEDURE'},
    },
    'Ch17_dissolution_mercury': {
        'description': 'Dissolve silver in Mercury water, separate via bath + ashes',
        'recipe_text': 'dissolve silver against one water of Mercury... Separate the water through the bath, and sift through ashes',
        'expected': {
            'qo_pct': 20,    # heating for dissolution
            'ch_pct': 15,    # testing dissolution progress
            'sh_pct': 15,    # monitoring
            'ok_pct': 6,     # vessel separation
            'ot_pct': 5,     # ops verification
            'k_pct': 18,     # active thermal
            'e_pct': 28,     # cooling phases
            'gentle_ratio': 20, # mixed heat (bath + ashes)
        },
        'must_have': [],
        'prefer': {'doc_type': 'PROCEDURE', 'dar_min': 2},
    },
    'Ch42_fixation_lead': {
        'description': 'Fix lead — separate, purify, decoction by gradual fire degrees',
        'recipe_text': 'divide and separate that lead from its said substances... purified by drawing out fat sliminess in the elementation',
        'expected': {
            'qo_pct': 22,    # heating for fixation
            'ch_pct': 15,    # testing
            'sh_pct': 10,    # less monitoring
            'ok_pct': 5,     # vessel work
            'ot_pct': 5,     # ops
            'k_pct': 20,     # thermal-heavy (fixation = strong heat)
            'e_pct': 25,     # some cooling
            'gentle_ratio': 15, # not gentle — fixation uses strong fire
        },
        'must_have': [],
        'prefer': {'doc_type': 'PROCEDURE'},
    },
    'Ch47_separation_cipher': {
        'description': 'Element separation using ALL cipher products (H,B,I,V,C,E,X,Z,Q)',
        'recipe_text': 'make H, project from B, separate H and B through I, mix in furnace, separate H Q C through Z...',
        'expected': {
            'qo_pct': 18,    # moderate heat
            'ch_pct': 20,    # heavy testing (multiple separations)
            'sh_pct': 18,    # heavy monitoring
            'ok_pct': 8,     # lots of vessel transfers
            'ot_pct': 6,     # ops verification
            'k_pct': 15,     # moderate thermal
            'e_pct': 30,     # stability-dominant
            'gentle_ratio': 20, # mixed
        },
        'must_have': [],
        'prefer': {'doc_type': 'PROCEDURE', 'dark_min': 15},  # many substances = many dark IDs
    },
    'Ch51_ninth_wine': {
        'description': 'Dissolve with "ninth wine" (= quintessence from Ch19/f75r)',
        'recipe_text': 'Take the ninth wine, well dried, dissolve D... if in place of wine you put juice of lunaria, one part worth ten',
        'expected': {
            'qo_pct': 20,    # moderate heating
            'ch_pct': 15,    # testing
            'sh_pct': 12,    # monitoring
            'ok_pct': 5,     # vessel
            'ot_pct': 4,     # ops
            'k_pct': 16,     # moderate
            'e_pct': 28,     # stability
            'gentle_ratio': 20, # moderate
        },
        'must_have': [],
        'prefer': {'doc_type': 'PROCEDURE'},
    },
}

print("PRODUCT CHAIN MATCHING: PL chapters -> Voynich folios")
print("=" * 110)
print(f"Candidate folios: {len(candidates)} (excluding {len(already_matched)} already matched)")

for ch_name, spec in expected_profiles.items():
    print(f"\n\n{'=' * 110}")
    print(f"  {ch_name}: {spec['description']}")
    print(f"  Recipe: {spec['recipe_text'][:100]}...")
    print(f"{'=' * 110}")

    expected_vec = [spec['expected'][k] for k in FEATURES]

    # Filter candidates by must_have
    pool = candidates[:]
    if 'chekar' in spec['must_have']:
        pool = [f for f in pool if atlas[f].get('chekar', 0) > 0]
        print(f"  Filtered to chekar folios: {len(pool)}")

    # Filter by preferences
    prefs = spec.get('prefer', {})
    if 'doc_type' in prefs:
        preferred = [f for f in pool if atlas[f]['doc_type'] == prefs['doc_type']]
        if preferred:
            pool = preferred
            print(f"  Filtered to {prefs['doc_type']}: {len(pool)}")
    if 'dar_min' in prefs:
        preferred = [f for f in pool if atlas[f]['dar'] >= prefs['dar_min']]
        if preferred:
            pool = preferred
    if 'dark_min' in prefs:
        preferred = [f for f in pool if atlas[f]['dark_unique'] >= prefs['dark_min']]
        if preferred:
            pool = preferred
            print(f"  Filtered to dark>={prefs['dark_min']}: {len(pool)}")

    # Rank by distance to expected profile
    ranked = []
    for f in pool:
        fvec = folio_vec(f)
        d = euclidean(fvec, expected_vec)
        ranked.append((f, d))
    ranked.sort(key=lambda x: x[1])

    print(f"\n  Expected: qo={spec['expected']['qo_pct']} ch={spec['expected']['ch_pct']} "
          f"sh={spec['expected']['sh_pct']} k={spec['expected']['k_pct']} "
          f"e={spec['expected']['e_pct']} gentle={spec['expected']['gentle_ratio']}%")

    print(f"\n  Top 5 matches:")
    print(f"  {'Folio':>8s} {'Dist':>6s} {'Sec':>4s} {'Type':>12s} {'qo':>5s} {'ch':>5s} {'sh':>5s} "
          f"{'k':>4s} {'e':>4s} {'g%':>4s} {'dar':>4s} {'dal':>4s} {'chk':>4s} {'dkU':>4s}")
    for f, d in ranked[:5]:
        e = atlas[f]
        print(f"  {f:>8s} {d:6.1f} {e['section']:>4s} {e['doc_type']:>12s} "
              f"{e['qo_pct']:5.1f} {e['ch_pct']:5.1f} {e['sh_pct']:5.1f} "
              f"{e['k_pct']:4.1f} {e['e_pct']:4.1f} {100*e['gentle_ratio']:4.0f} "
              f"{e['dar']:4d} {e['dal']:4d} {e['chekar']:4d} {e['dark_unique']:4d}")

    # Check if top match is adjacent to known matched folios
    top_folio = ranked[0][0] if ranked else None
    if top_folio:
        # Is it near f75r-f77v cluster?
        folio_list = sorted(atlas.keys())
        top_idx = folio_list.index(top_folio)
        neighbors = folio_list[max(0,top_idx-2):top_idx+3]
        matched_neighbors = [n for n in neighbors if n in already_matched]
        if matched_neighbors:
            print(f"  ** TOP MATCH {top_folio} is near: {matched_neighbors} **")


# ═══ SPECIAL: Ch16 BALNEUM -> CHEKAR FOLIOS ═══
print(f"\n\n{'=' * 110}")
print("SPECIAL TEST: Ch16 (balneum mariae fermentation) -> chekar folios")
print("Ch16 explicitly says 'bath of Maria'. It MUST match a chekar folio.")
print("=" * 110)

chekar_unmatched = [f for f in candidates if atlas[f].get('chekar', 0) > 0]
print(f"\nUnmatched chekar folios: {chekar_unmatched}")

ch16_vec = [expected_profiles['Ch16_fermentation_balneum']['expected'][k] for k in FEATURES]
for f in chekar_unmatched:
    fvec = folio_vec(f)
    d = euclidean(fvec, ch16_vec)
    e = atlas[f]
    print(f"  {f:>8s}: dist={d:.1f}  sec={e['section']}  qo={e['qo_pct']:.1f} ch={e['ch_pct']:.1f} "
          f"sh={e['sh_pct']:.1f} dar={e['dar']} gentle={100*e['gentle_ratio']:.0f}%")


print(f"\n{'=' * 110}")
print("DONE")
print(f"{'=' * 110}")
