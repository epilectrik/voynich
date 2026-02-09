"""
02_unit_para_para_large.py

A paragraph -> B paragraph matching, but only substantial B paragraphs (>=15 PP MIDDLEs).
Tests if coverage holds when we exclude trivially small B programs.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("A PARAGRAPH -> LARGE B PARAGRAPH (>=15 PP)")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

GALLOWS = {'k', 't', 'p', 'f'}
MIN_B_PP = 15  # Minimum PP MIDDLEs for B paragraph

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter, system_name):
    """Build paragraphs from token iterator."""
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

    # Extract PP
    result = []
    for i, para in enumerate(paragraphs):
        pp_set = set()
        for t in para['tokens']:
            try:
                m = morph.extract(t.word)
                if m.middle and m.middle in pp_middles:
                    pp_set.add(m.middle)
            except:
                pass
        result.append({
            'idx': i,
            'folio': para['folio'],
            'n_tokens': len(para['tokens']),
            'pp_middles': pp_set
        })

    print(f"{system_name}: {len(result)} paragraphs")
    return result

# Build paragraphs
a_paras = build_paragraphs(tx.currier_a(), "A")
b_paras_all = build_paragraphs(tx.currier_b(), "B")

# Filter B to large paragraphs only
b_paras = [p for p in b_paras_all if len(p['pp_middles']) >= MIN_B_PP]
print(f"B paragraphs with >={MIN_B_PP} PP: {len(b_paras)}")

if not b_paras:
    print("ERROR: No B paragraphs meet minimum size requirement")
    sys.exit(1)

# B paragraph size stats
pp_counts = [len(p['pp_middles']) for p in b_paras]
print(f"Large B paragraph sizes: mean={sum(pp_counts)/len(pp_counts):.1f}, min={min(pp_counts)}, max={max(pp_counts)}")

# =============================================================
# MATCHING
# =============================================================
print("\n" + "="*70)
print("A -> B PARAGRAPH MATCHING")
print("="*70)

def coverage(a_pp, b_pp):
    if not b_pp:
        return 0
    return len(a_pp & b_pp) / len(b_pp)

# For each A paragraph, find best matching large B paragraph
results = []
for a in a_paras:
    if not a['pp_middles']:
        continue

    best_b = None
    best_cov = 0
    for b in b_paras:
        cov = coverage(a['pp_middles'], b['pp_middles'])
        if cov > best_cov:
            best_cov = cov
            best_b = b

    results.append({
        'a_idx': a['idx'],
        'a_folio': a['folio'],
        'a_pp': len(a['pp_middles']),
        'best_b_idx': best_b['idx'] if best_b else -1,
        'best_b_folio': best_b['folio'] if best_b else None,
        'best_b_pp': len(best_b['pp_middles']) if best_b else 0,
        'coverage': best_cov
    })

coverages = [r['coverage'] for r in results]

print(f"\nCoverage of large B paragraphs:")
print(f"  Mean: {sum(coverages)/len(coverages):.1%}")
print(f"  Max: {max(coverages):.1%}")
print(f"  Min: {min(coverages):.1%}")

# Distribution
print(f"\nDistribution:")
bins = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
for low, high in bins:
    count = sum(1 for c in coverages if low <= c < high)
    print(f"  {low:.0%}-{high:.0%}: {count} ({100*count/len(coverages):.1f}%)")

# High coverage matches
high_cov = [r for r in results if r['coverage'] >= 0.6]
print(f"\n>=60% coverage: {len(high_cov)} A paragraphs ({100*len(high_cov)/len(results):.1f}%)")

print(f"\nTop matches:")
for r in sorted(results, key=lambda x: -x['coverage'])[:15]:
    print(f"  A_{r['a_idx']} ({r['a_folio']}, {r['a_pp']} PP) -> B_{r['best_b_idx']} ({r['best_b_folio']}, {r['best_b_pp']} PP): {r['coverage']:.1%}")

# =============================================================
# NULL MODEL
# =============================================================
print("\n" + "="*70)
print("NULL MODEL")
print("="*70)

import random
null_coverages = []
for a in a_paras[:100]:
    if not a['pp_middles']:
        continue
    for _ in range(50):
        rand_b = random.choice(b_paras)
        null_coverages.append(coverage(a['pp_middles'], rand_b['pp_middles']))

mean_null = sum(null_coverages) / len(null_coverages)
mean_actual = sum(coverages) / len(coverages)

print(f"Actual best-match: {mean_actual:.1%}")
print(f"Random match: {mean_null:.1%}")
print(f"Lift: {mean_actual/mean_null:.2f}x")

# =============================================================
# SAVE RESULTS
# =============================================================
out_path = Path(__file__).parent.parent / 'results' / 'unit_para_para_large.json'
with open(out_path, 'w') as f:
    json.dump({
        'min_b_pp': MIN_B_PP,
        'n_a_paras': len(a_paras),
        'n_b_paras_large': len(b_paras),
        'mean_coverage': mean_actual,
        'max_coverage': max(coverages),
        'lift_vs_random': mean_actual / mean_null,
        'pct_above_60': len(high_cov) / len(results),
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")
