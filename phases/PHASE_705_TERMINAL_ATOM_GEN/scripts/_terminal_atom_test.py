"""
PHASE_705: C2041 terminal-atom generalization test.

C2041 registered Tier 3 finding: ar -> al directional asymmetry within
LATE-class bigrams (39 vs 14, +0.47, p_BH=0.005). C2030 framing predicted
closure protocols may have internal grammar parallel to C886's MIDDLE
asymmetry. This phase tests whether C2041 generalizes to a broader
TERMINAL-ATOM class-level pattern:

  HYPOTHESIS: r-terminal LATE MIDDLEs systematically precede l-terminal
  LATE MIDDLEs in within-line adjacency.

Partition of locked LATE inventory by terminal atom:
  r-class: ar, dar, or       (ends in -r)
  l-class: al, dal, ol       (ends in -l)
  y-class: ary, aly, dary, daly, ory, oly  (ends in -y)

The C2041 finding ar->al is a single (r-class, l-class) pair. Three
near-miss pairs from PHASE_703 (ar->ol, al->ol, or->ol, all at +0.23
asymmetry) all involve ol as later position. Two of these (ar->ol,
or->ol) are r-class -> l-class consistent with the hypothesis. The
third (al->ol) is l-class -> l-class internal.

Pre-registered decision rules (LOCKED before computing aggregates):

Test A: r-class -> l-class vs l-class -> r-class
  Aggregate: sum all r-class to l-class bigrams; sum all l-class to
  r-class bigrams. Binomial test (null p=0.5 under within-line shuffle).
  PASS if FDR-corrected p_BH < 0.05 AND |aggregate asymmetry| >= 0.20.

Test B: position of y-class
  Aggregate r-class -> y-class vs y-class -> r-class; l-class -> y-class
  vs y-class -> l-class. Binomial tests with same threshold. Documents
  y-class positional preference if any.

Test C: pair-by-pair within r-class -> l-class
  Examine the 9 cross-class pairs (ar/al, ar/dal, ar/ol, dar/al, dar/dal,
  dar/ol, or/al, or/dal, or/ol) -- how many show A->B > B->A direction
  consistent with hypothesis? Binomial test on 9 pairs with at least one
  observation: probability >= 6/9 directional consistency under random null.

Combined criteria:
  Tier 2 if Test A passes AND >= 6/9 pairs in Test C show r->l direction
    (broad category claim that generalizes C2041)
  Tier 3 if Test A passes only (statistical aggregate but per-pair
    direction is mixed -- aggregate-only claim)
  No new constraint if Test A fails (C2041 remains specific, not
    generalizable to category)
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_705_TERMINAL_ATOM_GEN' / 'results' / 'terminal_atom_test.json'

# LATE inventory (same as PHASE_703)
LATE_INVENTORY = ['ar', 'ary', 'aly', 'al', 'dar', 'dal', 'dary', 'daly',
                   'or', 'ory', 'oly', 'ol']

# Partition by terminal atom (locked pre-test)
R_CLASS = ['ar', 'dar', 'or']        # ends in -r
L_CLASS = ['al', 'dal', 'ol']        # ends in -l
Y_CLASS = ['ary', 'aly', 'dary', 'daly', 'ory', 'oly']  # ends in -y

TERMINAL_OF = {m: 'r' for m in R_CLASS}
TERMINAL_OF.update({m: 'l' for m in L_CLASS})
TERMINAL_OF.update({m: 'y' for m in Y_CLASS})

# Pre-registered thresholds (LOCKED)
ASYMMETRY_EFFECT_FLOOR = 0.20  # aggregate asymmetry threshold (looser than per-pair 0.30)
FDR_THRESHOLD = 0.05
N_FLOOR_AGGREGATE = 30  # need at least 30 directional pairs for aggregate test
PER_PAIR_CONSISTENCY_THRESHOLD = 6  # of 9 cross-class pairs, need at least 6 in same direction


def binomial_two_sided_p(k, n, p=0.5):
    from math import comb
    if n == 0:
        return 1.0
    expected = n * p
    obs_dev = abs(k - expected)
    p_val = 0.0
    for i in range(n + 1):
        if abs(i - expected) >= obs_dev:
            p_val += comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return min(1.0, p_val)


def benjamini_hochberg(p_values_with_keys, alpha=0.05):
    if not p_values_with_keys:
        return []
    sorted_items = sorted(p_values_with_keys, key=lambda x: x[1])
    n = len(sorted_items)
    bh_adjusted = []
    for i, (key, p) in enumerate(sorted_items):
        rank = i + 1
        adj = min(1.0, p * n / rank)
        bh_adjusted.append((key, p, adj))
    for i in range(len(bh_adjusted) - 2, -1, -1):
        key, p, adj = bh_adjusted[i]
        _, _, next_adj = bh_adjusted[i + 1]
        if adj > next_adj:
            bh_adjusted[i] = (key, p, next_adj)
    return [(k, p, a, a < alpha) for k, p, a in bh_adjusted]


def collect_bigrams():
    tx = Transcript()
    morph = Morphology()
    late_set = set(LATE_INVENTORY)

    line_buffer = defaultdict(list)
    for t in tx.currier_b(h_only=True, exclude_labels=True, exclude_uncertain=True):
        if not (t.placement and t.placement.startswith('P')):
            continue
        if not t.word.strip():
            continue
        word = t.word.lower()
        try:
            m = morph.extract(word)
            middle = m.middle
        except Exception:
            middle = None
        key = (t.folio, t.line)
        if key[1] is None or key[1] == '':
            continue
        line_buffer[key].append(middle)

    bigrams = Counter()
    n_lines = 0
    for (folio, line), middles in line_buffer.items():
        n_lines += 1
        for i in range(len(middles) - 1):
            a, b = middles[i], middles[i + 1]
            if a in late_set and b in late_set:
                bigrams[(a, b)] += 1
    return bigrams, n_lines


def aggregate_class_to_class(bigrams, class_a, class_b):
    """Sum all bigrams from class_a -> class_b."""
    total = 0
    contributing = []
    for a in class_a:
        for b in class_b:
            count = bigrams.get((a, b), 0)
            if count > 0:
                contributing.append((a, b, count))
                total += count
    return total, contributing


def per_pair_direction(bigrams, class_a, class_b):
    """For each (a in class_a, b in class_b) pair, report A->B vs B->A.
    Returns list of dicts with pair info and direction indicator."""
    results = []
    for a in class_a:
        for b in class_b:
            n_ab = bigrams.get((a, b), 0)
            n_ba = bigrams.get((b, a), 0)
            total = n_ab + n_ba
            if total == 0:
                continue
            asym = (n_ab - n_ba) / total
            results.append({
                'a': a, 'b': b,
                'n_a_to_b': n_ab, 'n_b_to_a': n_ba,
                'total': total,
                'asymmetry': asym,
                'direction': '+' if n_ab > n_ba else ('-' if n_ab < n_ba else '0'),
            })
    return results


def main():
    print("=" * 90)
    print("PHASE_705 TERMINAL-ATOM GENERALIZATION TEST")
    print("=" * 90)

    print("\nStep 1: Collect within-line LATE-LATE bigrams (Currier B, P-placement)")
    bigrams, n_lines = collect_bigrams()
    total_bigrams = sum(bigrams.values())
    print(f"  Lines: {n_lines}, total LATE-LATE bigrams: {total_bigrams}")

    print(f"\n  Class membership:")
    print(f"    r-class ({len(R_CLASS)}): {R_CLASS}")
    print(f"    l-class ({len(L_CLASS)}): {L_CLASS}")
    print(f"    y-class ({len(Y_CLASS)}): {Y_CLASS}")

    # ============================================================
    # Test A: r-class <-> l-class aggregate
    # ============================================================
    print("\n" + "=" * 90)
    print("TEST A: r-class -> l-class vs l-class -> r-class (aggregate)")
    print("=" * 90)

    n_r_to_l, contrib_r_to_l = aggregate_class_to_class(bigrams, R_CLASS, L_CLASS)
    n_l_to_r, contrib_l_to_r = aggregate_class_to_class(bigrams, L_CLASS, R_CLASS)
    total_rl = n_r_to_l + n_l_to_r
    asym_rl = (n_r_to_l - n_l_to_r) / total_rl if total_rl > 0 else 0
    k_rl = max(n_r_to_l, n_l_to_r)
    p_rl = binomial_two_sided_p(k_rl, total_rl, 0.5) if total_rl > 0 else 1.0

    print(f"\n  r-class -> l-class: {n_r_to_l}")
    print(f"  l-class -> r-class: {n_l_to_r}")
    print(f"  Total directional: {total_rl}")
    print(f"  Aggregate asymmetry: {asym_rl:+.4f}")
    print(f"  Two-sided binomial p (null=0.5): {p_rl:.6f}")

    print(f"\n  Contributing r->l bigrams:")
    for a, b, c in sorted(contrib_r_to_l, key=lambda x: -x[2]):
        print(f"    {a:>4} -> {b:<4}  {c:>5}")
    print(f"\n  Contributing l->r bigrams:")
    for a, b, c in sorted(contrib_l_to_r, key=lambda x: -x[2]):
        print(f"    {a:>4} -> {b:<4}  {c:>5}")

    # ============================================================
    # Test B: r/l <-> y class
    # ============================================================
    print("\n" + "=" * 90)
    print("TEST B: y-class positional preference (relative to r and l)")
    print("=" * 90)

    n_r_to_y, _ = aggregate_class_to_class(bigrams, R_CLASS, Y_CLASS)
    n_y_to_r, _ = aggregate_class_to_class(bigrams, Y_CLASS, R_CLASS)
    n_l_to_y, _ = aggregate_class_to_class(bigrams, L_CLASS, Y_CLASS)
    n_y_to_l, _ = aggregate_class_to_class(bigrams, Y_CLASS, L_CLASS)

    print(f"\n  r-class -> y-class: {n_r_to_y}")
    print(f"  y-class -> r-class: {n_y_to_r}")
    total_ry = n_r_to_y + n_y_to_r
    asym_ry = (n_r_to_y - n_y_to_r) / total_ry if total_ry > 0 else 0
    p_ry = binomial_two_sided_p(max(n_r_to_y, n_y_to_r), total_ry, 0.5) if total_ry > 0 else 1.0
    print(f"  r/y asymmetry: {asym_ry:+.4f}, total={total_ry}, p={p_ry:.4f}")

    print(f"\n  l-class -> y-class: {n_l_to_y}")
    print(f"  y-class -> l-class: {n_y_to_l}")
    total_ly = n_l_to_y + n_y_to_l
    asym_ly = (n_l_to_y - n_y_to_l) / total_ly if total_ly > 0 else 0
    p_ly = binomial_two_sided_p(max(n_l_to_y, n_y_to_l), total_ly, 0.5) if total_ly > 0 else 1.0
    print(f"  l/y asymmetry: {asym_ly:+.4f}, total={total_ly}, p={p_ly:.4f}")

    # ============================================================
    # Test C: per-pair direction consistency within r-class x l-class
    # ============================================================
    print("\n" + "=" * 90)
    print("TEST C: per-pair direction consistency (r-class -> l-class)")
    print("=" * 90)

    pair_results = per_pair_direction(bigrams, R_CLASS, L_CLASS)
    # Combine (a,b) and (b,a) since we already aggregated; just dedupe by sorted pair
    seen_pairs = set()
    unique_pairs = []
    for r_mid in R_CLASS:
        for l_mid in L_CLASS:
            key = tuple(sorted([r_mid, l_mid]))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            n_rl = bigrams.get((r_mid, l_mid), 0)
            n_lr = bigrams.get((l_mid, r_mid), 0)
            total = n_rl + n_lr
            if total == 0:
                unique_pairs.append({'pair': (r_mid, l_mid), 'n_rl': 0, 'n_lr': 0,
                                      'total': 0, 'direction': 'none', 'asym': 0})
            else:
                asym = (n_rl - n_lr) / total
                direction = 'r->l' if n_rl > n_lr else ('l->r' if n_lr > n_rl else 'tie')
                unique_pairs.append({'pair': (r_mid, l_mid), 'n_rl': n_rl, 'n_lr': n_lr,
                                      'total': total, 'direction': direction, 'asym': asym})

    print(f"\n  {'r-class':<6} {'l-class':<6} {'r->l':>6} {'l->r':>6} {'total':>7} {'asym':>8} {'dir':>8}")
    print("  " + "-" * 60)
    for p in unique_pairs:
        a, b = p['pair']
        dir_label = p['direction']
        print(f"  {a:<6} {b:<6} {p['n_rl']:>6} {p['n_lr']:>6} {p['total']:>7} "
              f"{p['asym']:>+8.3f} {dir_label:>8}")

    n_rl_direction = sum(1 for p in unique_pairs if p['direction'] == 'r->l')
    n_lr_direction = sum(1 for p in unique_pairs if p['direction'] == 'l->r')
    n_none = sum(1 for p in unique_pairs if p['direction'] in ('none', 'tie'))
    n_total_pairs = len(unique_pairs)

    print(f"\n  Direction summary: {n_rl_direction}/{n_total_pairs} pairs go r->l, "
          f"{n_lr_direction}/{n_total_pairs} go l->r, {n_none} ties/empty")

    # Binomial test on 9 pairs: under null (random direction), probability of
    # observing at least n_rl_direction in r->l direction (binomial p=0.5)
    n_decided = n_rl_direction + n_lr_direction
    p_consistency = binomial_two_sided_p(max(n_rl_direction, n_lr_direction), n_decided, 0.5) if n_decided else 1.0
    print(f"  Direction-consistency binomial p: {p_consistency:.4f}")

    # FDR across the three tests
    test_pvals = [('TestA_r_to_l', p_rl), ('TestB_r_to_y', p_ry), ('TestB_l_to_y', p_ly),
                  ('TestC_pair_consistency', p_consistency)]
    bh_results = benjamini_hochberg(test_pvals, alpha=FDR_THRESHOLD)
    print(f"\n  FDR-corrected p-values:")
    for key, p, p_adj, reject in bh_results:
        print(f"    {key:<28} raw={p:.6f}  p_BH={p_adj:.6f}  reject_null={reject}")

    # ============================================================
    # Verdict
    # ============================================================
    print("\n" + "=" * 90)
    print("PRE-REGISTERED VERDICT")
    print("=" * 90)

    # Re-extract BH results for test A and test C
    bh_dict = {k: (p, p_adj, reject) for k, p, p_adj, reject in bh_results}

    test_a_pass = (total_rl >= N_FLOOR_AGGREGATE
                   and abs(asym_rl) >= ASYMMETRY_EFFECT_FLOOR
                   and bh_dict['TestA_r_to_l'][2])
    test_c_pass = n_rl_direction >= PER_PAIR_CONSISTENCY_THRESHOLD

    print(f"\n  Test A (aggregate r/l asymmetry): "
          f"asym={asym_rl:+.3f}, N={total_rl}, p_BH={bh_dict['TestA_r_to_l'][1]:.4f} "
          f"-> {'PASS' if test_a_pass else 'FAIL'}")
    print(f"  Test C (per-pair direction >= 6/9): "
          f"r->l={n_rl_direction}/{n_total_pairs}, l->r={n_lr_direction}/{n_total_pairs} "
          f"-> {'PASS' if test_c_pass else 'FAIL'}")

    if test_a_pass and test_c_pass:
        verdict = (f"TIER 2 REGISTERABLE: terminal-atom generalization confirmed. "
                   f"r-class -> l-class aggregate asymmetry +{asym_rl:.3f} (p_BH={bh_dict['TestA_r_to_l'][1]:.4f}, "
                   f"N={total_rl}) AND {n_rl_direction}/{n_total_pairs} pairs show consistent direction. "
                   f"C2041 ar->al is one instance of a broader -r terminal -> -l terminal "
                   f"closure-grammar pattern.")
    elif test_a_pass:
        verdict = (f"TIER 3: aggregate r->l asymmetry passes ({asym_rl:+.3f}, p_BH={bh_dict['TestA_r_to_l'][1]:.4f}) "
                   f"but per-pair direction is mixed ({n_rl_direction}/{n_total_pairs} r->l). "
                   "Aggregate effect driven by specific pairs (likely ar->al dominant), not class-level grammar.")
    elif test_c_pass:
        verdict = (f"TIER 3: per-pair direction consistent ({n_rl_direction}/{n_total_pairs}) "
                   "but aggregate asymmetry fails effect-size or significance threshold. "
                   "Directional bias exists but is weak in magnitude.")
    else:
        verdict = ("NO TERMINAL-ATOM GENERALIZATION: neither aggregate asymmetry nor "
                   "per-pair consistency reaches threshold. C2041 ar->al is specific, "
                   "not a class-level pattern.")

    print(f"\n  {verdict}")

    out = {
        "method": "PHASE_705 terminal-atom generalization of C2041",
        "hypothesis": "r-terminal LATE MIDDLEs systematically precede l-terminal LATE MIDDLEs",
        "late_inventory": LATE_INVENTORY,
        "class_partition": {"r-class": R_CLASS, "l-class": L_CLASS, "y-class": Y_CLASS},
        "pre_registered_thresholds": {
            "ASYMMETRY_EFFECT_FLOOR": ASYMMETRY_EFFECT_FLOOR,
            "FDR_THRESHOLD": FDR_THRESHOLD,
            "N_FLOOR_AGGREGATE": N_FLOOR_AGGREGATE,
            "PER_PAIR_CONSISTENCY_THRESHOLD": PER_PAIR_CONSISTENCY_THRESHOLD,
        },
        "n_lines": n_lines,
        "total_bigrams": total_bigrams,
        "test_A": {
            "n_r_to_l": n_r_to_l,
            "n_l_to_r": n_l_to_r,
            "total": total_rl,
            "aggregate_asymmetry": asym_rl,
            "p_raw": p_rl,
            "p_BH": bh_dict['TestA_r_to_l'][1],
            "pass": test_a_pass,
            "contributing_r_to_l": [(a, b, c) for a, b, c in contrib_r_to_l],
            "contributing_l_to_r": [(a, b, c) for a, b, c in contrib_l_to_r],
        },
        "test_B": {
            "r_y": {"n_r_to_y": n_r_to_y, "n_y_to_r": n_y_to_r,
                    "asymmetry": asym_ry, "p_raw": p_ry, "p_BH": bh_dict['TestB_r_to_y'][1]},
            "l_y": {"n_l_to_y": n_l_to_y, "n_y_to_l": n_y_to_l,
                    "asymmetry": asym_ly, "p_raw": p_ly, "p_BH": bh_dict['TestB_l_to_y'][1]},
        },
        "test_C": {
            "per_pair_results": unique_pairs,
            "n_r_to_l_direction": n_rl_direction,
            "n_l_to_r_direction": n_lr_direction,
            "n_total_pairs": n_total_pairs,
            "binomial_p_consistency": p_consistency,
            "p_BH": bh_dict['TestC_pair_consistency'][1],
            "pass": test_c_pass,
        },
        "verdict": verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
