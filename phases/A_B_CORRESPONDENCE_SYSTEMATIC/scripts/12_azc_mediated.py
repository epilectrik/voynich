"""
12_azc_mediated.py

Test A-B matching using only AZC-mediated vocabulary.

From C498.a: 214 AZC-mediated MIDDLEs vs 198 B-native overlap.
Only AZC-mediated vocabulary truly participates in the pipeline.

Hypothesis: Restricting to AZC-mediated vocabulary should improve
A-B correspondence by removing noise from B-native overlap.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("AZC-MEDIATED VOCABULARY MATCHING")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# =============================================================
# STEP 1: Identify AZC vocabulary
# =============================================================
print("\nSTEP 1: Building AZC vocabulary...")

azc_middles = set()
azc_by_position = defaultdict(set)

for t in tx.azc():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle:
            azc_middles.add(m.middle)
            if t.placement:
                # Extract position type (P, R, S, C)
                pos = t.placement[0].upper() if t.placement else 'X'
                azc_by_position[pos].add(m.middle)
    except:
        pass

print(f"AZC MIDDLEs: {len(azc_middles)}")
for pos in sorted(azc_by_position.keys()):
    print(f"  {pos}: {len(azc_by_position[pos])}")

# =============================================================
# STEP 2: Build A and B vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 2: Building A and B vocabulary...")

a_middles = set()
for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            a_middles.add(m.middle)
    except:
        pass

b_middles = set()
for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            b_middles.add(m.middle)
    except:
        pass

print(f"A PP MIDDLEs: {len(a_middles)}")
print(f"B PP MIDDLEs: {len(b_middles)}")

# =============================================================
# STEP 3: Identify AZC-mediated vs B-native vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 3: Vocabulary classification...")

# AZC-mediated: appears in both A and AZC (passes through AZC)
azc_mediated = a_middles & azc_middles & b_middles

# B-native: in A and B but NOT in AZC
b_native = (a_middles & b_middles) - azc_middles

# A-only: in A but not in B
a_only = a_middles - b_middles

print(f"\nVocabulary breakdown:")
print(f"  AZC-mediated (A & AZC & B): {len(azc_mediated)}")
print(f"  B-native (A & B - AZC): {len(b_native)}")
print(f"  A-only (A - B): {len(a_only)}")

# =============================================================
# STEP 4: Build paragraphs
# =============================================================
print("\n" + "="*70)
print("STEP 4: Building paragraphs...")

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

def extract_pp(para, filter_set=None):
    """Extract PP MIDDLEs from paragraph, optionally filtered."""
    pp = set()
    for t in para['tokens']:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                if filter_set is None or m.middle in filter_set:
                    pp.add(m.middle)
        except:
            pass
    return pp

a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# STEP 5: Compare matching with different vocabulary filters
# =============================================================
print("\n" + "="*70)
print("STEP 5: Matching comparison")
print("="*70)

def coverage(a_pp, b_pp):
    if not b_pp:
        return 0
    return len(a_pp & b_pp) / len(b_pp)

def run_matching(vocab_filter, filter_name):
    """Run A->B matching with vocabulary filter."""
    results = []
    for i, a_para in enumerate(a_paras):
        a_pp = extract_pp(a_para, vocab_filter)
        if not a_pp:
            continue

        best_b = None
        best_cov = 0
        for j, b_para in enumerate(b_paras):
            b_pp = extract_pp(b_para, vocab_filter)
            if not b_pp:
                continue
            cov = coverage(a_pp, b_pp)
            if cov > best_cov:
                best_cov = cov
                best_b = j

        results.append({
            'a_idx': i,
            'best_b_idx': best_b,
            'coverage': best_cov
        })

    if results:
        covs = [r['coverage'] for r in results]
        return {
            'filter': filter_name,
            'n_matched': len(results),
            'mean_coverage': sum(covs) / len(covs),
            'max_coverage': max(covs),
            'pct_above_80': sum(1 for c in covs if c >= 0.8) / len(covs),
            'pct_above_60': sum(1 for c in covs if c >= 0.6) / len(covs),
        }
    return None

# Run with different filters
all_pp = a_middles | b_middles
results_all = run_matching(None, "ALL PP")
results_mediated = run_matching(azc_mediated, "AZC-mediated")
results_native = run_matching(b_native, "B-native")
results_shared = run_matching(a_middles & b_middles, "A & B (shared)")

print(f"\n{'Filter':<20} {'Mean Cov':<12} {'Max':<8} {'≥80%':<8} {'≥60%':<8}")
print("-" * 56)

for r in [results_all, results_mediated, results_native, results_shared]:
    if r:
        print(f"{r['filter']:<20} {r['mean_coverage']:.1%}        {r['max_coverage']:.1%}    {r['pct_above_80']:.1%}    {r['pct_above_60']:.1%}")

# =============================================================
# STEP 6: Statistical comparison
# =============================================================
print("\n" + "="*70)
print("STEP 6: Does AZC-mediated outperform?")
print("="*70)

if results_mediated and results_shared:
    improvement = results_mediated['mean_coverage'] - results_shared['mean_coverage']
    print(f"\nAZC-mediated vs All shared:")
    print(f"  AZC-mediated mean: {results_mediated['mean_coverage']:.1%}")
    print(f"  All shared mean: {results_shared['mean_coverage']:.1%}")
    print(f"  Difference: {improvement:+.1%}")

    if improvement > 0.05:
        print(f"\n  -> AZC-mediated vocabulary IMPROVES matching")
    elif improvement < -0.05:
        print(f"\n  -> AZC-mediated vocabulary REDUCES matching")
    else:
        print(f"\n  -> No significant difference")

# =============================================================
# SAVE RESULTS
# =============================================================
out_path = Path(__file__).parent.parent / 'results' / 'azc_mediated.json'
with open(out_path, 'w') as f:
    json.dump({
        'azc_mediated_count': len(azc_mediated),
        'b_native_count': len(b_native),
        'results_all': results_all,
        'results_mediated': results_mediated,
        'results_native': results_native,
        'results_shared': results_shared,
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")
