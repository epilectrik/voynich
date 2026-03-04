#!/usr/bin/env python3
"""
SM-8 (DECISIVE): Is s's base-dependent behavior ITSELF consistent and predictable?

Split Currier B corpus into two halves (odd-index vs even-index folios by sort
order). For each half, compute category profile of s-compounds and sh, then
measure cosine similarity between the two halves.

If s is a genuine structural modifier, its effect on each base should be
STABLE across independent corpus halves.

Tested bases: {k, e, o, c, l} as compounds ks/es/os/cs/ls, plus sh.

Pass: mean across-half cosine >= 0.80 for all bases with N >= 5 in both halves.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def cosine_similarity(vec_a, vec_b, keys):
    """Compute cosine similarity between two vectors indexed by keys.

    vec_a, vec_b: dict-like {key: value}.
    Returns cosine similarity or 0.0 if either vector is zero.
    """
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for k in keys:
        a = vec_a.get(k, 0)
        b = vec_b.get(k, 0)
        dot += a * b
        norm_a += a * a
        norm_b += b * b
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("SM-8 (DECISIVE): s-modifier cross-half consistency")
    print("=" * 75)

    # --- Step 1: Identify all B folios and split into odd/even by sort index ---
    folio_set = set()
    for token in tx.currier_b():
        folio_set.add(token.folio)

    sorted_folios = sorted(folio_set)
    odd_folios = set(sorted_folios[i] for i in range(0, len(sorted_folios), 2))  # indices 0, 2, 4, ...
    even_folios = set(sorted_folios[i] for i in range(1, len(sorted_folios), 2))  # indices 1, 3, 5, ...

    print()
    print("Total B folios: %d" % len(sorted_folios))
    print("Odd-index folios (half 1): %d" % len(odd_folios))
    print("Even-index folios (half 2): %d" % len(even_folios))

    # --- Step 2: Collect category profiles per compound per half ---
    # Compounds to track:
    #   ks: MIDDLE starts with 'ks'
    #   es: MIDDLE starts with 'es'
    #   os: MIDDLE starts with 'os'
    #   cs: MIDDLE starts with 'cs'
    #   ls: MIDDLE starts with 'ls'
    #   sh: MIDDLE starts with 'sh'

    compound_defs = {
        'ks': lambda mid: mid.startswith('ks'),
        'es': lambda mid: mid.startswith('es'),
        'os': lambda mid: mid.startswith('os'),
        'cs': lambda mid: mid.startswith('cs'),
        'ls': lambda mid: mid.startswith('ls'),
        'sh': lambda mid: mid.startswith('sh'),
    }

    # half -> compound -> category -> count
    half_profiles = {
        'half1': {comp: Counter() for comp in compound_defs},
        'half2': {comp: Counter() for comp in compound_defs},
    }
    half_totals = {
        'half1': {comp: 0 for comp in compound_defs},
        'half2': {comp: 0 for comp in compound_defs},
    }

    total_classified = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue

        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        total_classified += 1

        # Determine half
        if token.folio in odd_folios:
            half = 'half1'
        elif token.folio in even_folios:
            half = 'half2'
        else:
            continue

        # Check each compound
        for comp_name, matcher in compound_defs.items():
            if matcher(mid):
                half_profiles[half][comp_name][cat] += 1
                half_totals[half][comp_name] += 1

    print("Total classified B tokens: %d" % total_classified)

    # --- Step 3: Compute cosine similarities ---
    print()
    print("-" * 75)
    print("Per-compound cross-half category profile cosine similarity")
    print("-" * 75)
    print()

    min_n = 5
    cosines = []
    inconclusive = []

    print("%-10s %8s %8s %10s %s" % ("Compound", "N-half1", "N-half2", "Cosine", "Verdict"))
    print("-" * 55)

    for comp_name in ['ks', 'es', 'os', 'cs', 'ls', 'sh']:
        n1 = half_totals['half1'][comp_name]
        n2 = half_totals['half2'][comp_name]

        if n1 < min_n or n2 < min_n:
            print("%-10s %8d %8d %10s %s" % (comp_name, n1, n2, "---", "INCONCLUSIVE (N < %d)" % min_n))
            inconclusive.append(comp_name)
            continue

        # Build fractional profiles
        prof1 = {}
        prof2 = {}
        for cat in CATEGORIES:
            prof1[cat] = half_profiles['half1'][comp_name].get(cat, 0) / n1
            prof2[cat] = half_profiles['half2'][comp_name].get(cat, 0) / n2

        cos = cosine_similarity(prof1, prof2, CATEGORIES)
        cosines.append((comp_name, cos, n1, n2))

        status = "STABLE" if cos >= 0.80 else "UNSTABLE"
        print("%-10s %8d %8d %10.4f %s" % (comp_name, n1, n2, cos, status))

    # --- Per-compound detail ---
    print()
    print("-" * 75)
    print("Category profiles per half (for testable compounds)")
    print("-" * 75)

    for comp_name, cos, n1, n2 in cosines:
        print()
        print("  %s (cosine = %.4f)" % (comp_name, cos))
        print("  %-14s %8s %8s" % ("Category", "Half1 %", "Half2 %"))
        print("  " + "-" * 35)
        for cat in CATEGORIES:
            p1 = 100 * half_profiles['half1'][comp_name].get(cat, 0) / n1
            p2 = 100 * half_profiles['half2'][comp_name].get(cat, 0) / n2
            print("  %-14s %7.1f%% %7.1f%%" % (cat, p1, p2))

    # --- VERDICT ---
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    if len(cosines) == 0:
        print("SM-8 OVERALL: INCONCLUSIVE (no testable compounds)")
        return

    mean_cos = sum(c for _, c, _, _ in cosines) / len(cosines)
    min_cos = min(c for _, c, _, _ in cosines)
    max_cos = max(c for _, c, _, _ in cosines)

    stable_count = sum(1 for _, c, _, _ in cosines if c >= 0.80)
    total_tested = len(cosines)

    print("Testable compounds:  %d / %d" % (total_tested, total_tested + len(inconclusive)))
    print("Inconclusive:        %d (%s)" % (len(inconclusive), ", ".join(inconclusive) if inconclusive else "none"))
    print()
    print("Cosine similarities:")
    for comp_name, cos, n1, n2 in cosines:
        print("  %-10s  %.4f  (N=%d + %d)" % (comp_name, cos, n1, n2))
    print()
    print("Mean cosine:   %.4f" % mean_cos)
    print("Min cosine:    %.4f" % min_cos)
    print("Max cosine:    %.4f" % max_cos)
    print("Stable (>= 0.80): %d / %d" % (stable_count, total_tested))
    print()

    overall = mean_cos >= 0.80
    print("Threshold: mean cosine >= 0.80")
    print()
    print("SM-8 OVERALL: %s" % ("PASS" if overall else "FAIL"))
    if overall:
        print("  s-modifier behavior is STABLE across independent corpus halves.")
        print("  s's base-dependent category effects are reproducible and predictable.")
    else:
        print("  s-modifier behavior is NOT consistently stable across corpus halves.")
        print("  s's effects may be context-dependent rather than structurally determined.")


if __name__ == '__main__':
    main()
