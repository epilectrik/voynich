"""
10_hazard_exposure.py

Test hazard exposure matching between A and B.

From C684: 83.9% of A records fully eliminate all 17 forbidden transitions.
Different A records leave different hazard subsets active.

Hypothesis: A records with specific hazard profiles should match B execution
contexts with similar hazard exposure.

Binary signal - should be cleanest test.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("HAZARD EXPOSURE MATCHING")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Load hazard topology from BCSC
# The 17 forbidden transitions organized into 5 classes
HAZARD_CLASSES = {
    'HC1_DOUBLE_ESCAPE': [('qo', 'qo')],  # Consecutive escape attempts
    'HC2_ESCAPE_AFTER_HAZARD': [('ch', 'qo'), ('sh', 'qo')],  # Escape after phase marker
    'HC3_UNMONITORED_FLOW': [('da', 'da')],  # Double flow without monitoring
    'HC4_KERNEL_COLLISION': [('ok', 'ok'), ('ot', 'ot')],  # Consecutive kernel ops
    'HC5_ANCHOR_VIOLATION': [('ol', 'qo'), ('or', 'qo')],  # Escape from anchor state
}

# Flatten to list of forbidden transitions
FORBIDDEN_TRANSITIONS = []
for hc, transitions in HAZARD_CLASSES.items():
    for t in transitions:
        FORBIDDEN_TRANSITIONS.append((hc, t[0], t[1]))

print(f"Hazard classes: {len(HAZARD_CLASSES)}")
print(f"Forbidden transitions: {len(FORBIDDEN_TRANSITIONS)}")

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter):
    by_folio_line = defaultdict(list)
    for t in tokens_iter:
        if t.word and '*' not in t.word:
            by_folio_line[(t.folio, t.line)].append(t)

    paragraphs = []
    current_para = {'tokens': [], 'folio': None}
    current_folio = None

    for (folio, line) in sorted(by_folio_line.keys()):
        tokens = by_folio_line[(folio, line)]
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'tokens': [], 'folio': folio}
            current_folio = folio
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs

def get_prefix_set(tokens):
    """Get set of PREFIXes in token list."""
    prefixes = set()
    for t in tokens:
        try:
            m = morph.extract(t.word if hasattr(t, 'word') else t['word'])
            if m.prefix:
                prefixes.add(m.prefix)
        except:
            pass
    return prefixes

def compute_hazard_exposure(prefixes):
    """
    Given a set of available PREFIXes, compute which hazard classes are exposed.
    A hazard is exposed if BOTH prefixes in the forbidden transition are available.
    """
    exposed = set()
    for hc, p1, p2 in FORBIDDEN_TRANSITIONS:
        if p1 in prefixes and p2 in prefixes:
            exposed.add(hc)
    return exposed

# =============================================================
# BUILD A AND B PARAGRAPHS
# =============================================================
print("\nBuilding paragraphs...")

a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# COMPUTE HAZARD EXPOSURE
# =============================================================
print("\n" + "="*70)
print("COMPUTING HAZARD EXPOSURE")
print("="*70)

a_hazards = []
for i, para in enumerate(a_paras):
    prefixes = get_prefix_set(para['tokens'])
    exposed = compute_hazard_exposure(prefixes)
    a_hazards.append({
        'idx': i,
        'folio': para['folio'],
        'prefixes': prefixes,
        'exposed_hazards': exposed,
        'n_exposed': len(exposed)
    })

b_hazards = []
for i, para in enumerate(b_paras):
    prefixes = get_prefix_set(para['tokens'])
    exposed = compute_hazard_exposure(prefixes)
    b_hazards.append({
        'idx': i,
        'folio': para['folio'],
        'prefixes': prefixes,
        'exposed_hazards': exposed,
        'n_exposed': len(exposed)
    })

# Summary
a_exposure_counts = Counter(h['n_exposed'] for h in a_hazards)
b_exposure_counts = Counter(h['n_exposed'] for h in b_hazards)

print(f"\nA hazard exposure distribution:")
for n in sorted(a_exposure_counts.keys()):
    print(f"  {n} hazards exposed: {a_exposure_counts[n]} paragraphs")

print(f"\nB hazard exposure distribution:")
for n in sorted(b_exposure_counts.keys()):
    print(f"  {n} hazards exposed: {b_exposure_counts[n]} paragraphs")

# =============================================================
# HAZARD PROFILE MATCHING
# =============================================================
print("\n" + "="*70)
print("HAZARD PROFILE MATCHING")
print("="*70)

def hazard_match_score(a_exposed, b_exposed):
    """Jaccard similarity of exposed hazard sets."""
    if not a_exposed and not b_exposed:
        return 1.0  # Both have zero exposure = perfect match
    if not a_exposed or not b_exposed:
        return 0.0
    intersection = len(a_exposed & b_exposed)
    union = len(a_exposed | b_exposed)
    return intersection / union if union > 0 else 0

# For each A paragraph, find best hazard-matching B paragraph
results = []
for a in a_hazards:
    best_b = None
    best_score = -1

    for b in b_hazards:
        score = hazard_match_score(a['exposed_hazards'], b['exposed_hazards'])
        if score > best_score:
            best_score = score
            best_b = b

    results.append({
        'a_idx': a['idx'],
        'a_folio': a['folio'],
        'a_hazards': list(a['exposed_hazards']),
        'best_b_idx': best_b['idx'] if best_b else -1,
        'best_b_folio': best_b['folio'] if best_b else None,
        'b_hazards': list(best_b['exposed_hazards']) if best_b else [],
        'match_score': best_score
    })

scores = [r['match_score'] for r in results]
print(f"\nHazard match scores:")
print(f"  Mean: {sum(scores)/len(scores):.3f}")
print(f"  Perfect matches (1.0): {sum(1 for s in scores if s == 1.0)}")
print(f"  High matches (≥0.8): {sum(1 for s in scores if s >= 0.8)}")
print(f"  Zero matches (0.0): {sum(1 for s in scores if s == 0.0)}")

# =============================================================
# ANALYZE HAZARD CLASS PATTERNS
# =============================================================
print("\n" + "="*70)
print("HAZARD CLASS ANALYSIS")
print("="*70)

# Which hazard classes appear most often?
a_hc_counts = Counter()
for h in a_hazards:
    for hc in h['exposed_hazards']:
        a_hc_counts[hc] += 1

b_hc_counts = Counter()
for h in b_hazards:
    for hc in h['exposed_hazards']:
        b_hc_counts[hc] += 1

print(f"\nHazard class frequency:")
print(f"{'Class':<25} {'A paras':<10} {'B paras':<10}")
print("-" * 45)
for hc in HAZARD_CLASSES.keys():
    print(f"{hc:<25} {a_hc_counts[hc]:<10} {b_hc_counts[hc]:<10}")

# =============================================================
# TEST: Do low-hazard A match low-hazard B?
# =============================================================
print("\n" + "="*70)
print("LOW-HAZARD MATCHING TEST")
print("="*70)

# A paragraphs with 0 hazards exposed
a_zero = [h for h in a_hazards if h['n_exposed'] == 0]
# B paragraphs with 0 hazards exposed
b_zero = [h for h in b_hazards if h['n_exposed'] == 0]

print(f"A paragraphs with 0 hazards: {len(a_zero)}")
print(f"B paragraphs with 0 hazards: {len(b_zero)}")

if a_zero and b_zero:
    # Do zero-hazard A's PP vocabulary overlap with zero-hazard B's PP?
    a_zero_pp = set()
    for h in a_zero:
        para = a_paras[h['idx']]
        for t in para['tokens']:
            try:
                m = morph.extract(t.word)
                if m.middle and m.middle in pp_middles:
                    a_zero_pp.add(m.middle)
            except:
                pass

    b_zero_pp = set()
    for h in b_zero:
        para = b_paras[h['idx']]
        for t in para['tokens']:
            try:
                m = morph.extract(t.word)
                if m.middle and m.middle in pp_middles:
                    b_zero_pp.add(m.middle)
            except:
                pass

    overlap = len(a_zero_pp & b_zero_pp)
    print(f"\nZero-hazard vocabulary overlap:")
    print(f"  A PP: {len(a_zero_pp)}")
    print(f"  B PP: {len(b_zero_pp)}")
    print(f"  Shared: {overlap} ({100*overlap/len(b_zero_pp):.1f}% of B)")

# =============================================================
# SAVE RESULTS
# =============================================================
out_path = Path(__file__).parent.parent / 'results' / 'hazard_exposure.json'
with open(out_path, 'w') as f:
    json.dump({
        'n_a_paras': len(a_paras),
        'n_b_paras': len(b_paras),
        'mean_match_score': sum(scores)/len(scores),
        'perfect_matches': sum(1 for s in scores if s == 1.0),
        'a_zero_hazard': len(a_zero),
        'b_zero_hazard': len(b_zero),
        'hazard_class_counts': {
            'A': dict(a_hc_counts),
            'B': dict(b_hc_counts)
        }
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")
