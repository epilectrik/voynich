"""
Phase 531: Modifier Stacking Order
====================================
Answers the C1393 open question: when multiple modifiers {p, c, i, f, d, s}
appear in one MIDDLE, is their internal sub-order fixed?

C1394 T4 established the ordering gradient p -> f -> i -> c -> d -> s via mean
stack positions. C1394 T10 called it "morphological convention." This phase
performs the definitive pairwise analysis:

1. For every pair of modifiers (X, Y), count how often X precedes Y vs Y precedes X
2. Compute ordering ratios and binomial significance for each pair
3. Test whether the C1393 gradient (p < f < i < c < d < s) correctly predicts
   ALL observed pairwise orderings
4. Check for absolute orderings (pairs that NEVER appear in one direction)
5. Identify any surprising violations or reversals
6. Analyze by token frequency (type-level vs token-weighted)

Output: phases/MODIFIER_STACKING_ORDER/results/modifier_stacking_order.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# ============================================================
# Constants
# ============================================================
MOD_ATOMS = {'p', 'c', 'i', 'f', 'd', 's'}

# C1393 mean position gradient (from C1393 table)
C1393_GRADIENT = ['p', 'f', 'i', 'c', 'd', 's']
C1393_MEAN_POS = {'p': 0.38, 'c': 0.40, 'i': 0.44, 'f': 0.50, 'd': 0.54, 's': 0.64}

# C1394 T4 mean stack position (more precise, from modifier_stack_test)
C1394_GRADIENT = ['p', 'f', 'i', 'c', 'd', 's']
C1394_MEAN_STACK_POS = {'p': 0.225, 'f': 0.395, 'i': 0.519, 'c': 0.532, 'd': 0.696, 's': 0.713}


def binomial_test_two_sided(k, n, p=0.5):
    """
    Two-sided binomial test: is k successes in n trials significantly
    different from p=0.5?
    Returns approximate p-value using normal approximation for large n,
    exact for small n.
    """
    if n == 0:
        return 1.0
    if n <= 25:
        # Exact binomial
        from math import comb
        # P(X >= k) + P(X <= n-k) for two-sided
        if k > n / 2:
            tail = sum(comb(n, j) * (p ** j) * ((1 - p) ** (n - j)) for j in range(k, n + 1))
        else:
            tail = sum(comb(n, j) * (p ** j) * ((1 - p) ** (n - j)) for j in range(0, k + 1))
        return min(2 * tail, 1.0)
    else:
        # Normal approximation
        mean = n * p
        std = (n * p * (1 - p)) ** 0.5
        if std == 0:
            return 1.0
        z = abs(k - mean) / std
        # Two-sided p-value from z
        # Using complementary error function approximation
        p_val = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        return p_val


# ============================================================
# Data Loading
# ============================================================
print("=" * 70)
print("PHASE 531: MODIFIER STACKING ORDER")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Collect all Currier B tokens with valid MIDDLEs
# Filter: H track, exclude labels, uncertain, empty
tokens_b = []
for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    if token.placement.startswith('L'):
        continue
    m = morph.extract(token.word)
    if m.middle and len(m.middle) >= 1:
        tokens_b.append({
            'word': token.word,
            'folio': token.folio,
            'middle': m.middle,
            'prefix': m.prefix,
        })

print(f"Loaded {len(tokens_b)} Currier B tokens with valid MIDDLEs")

# Pre-compute MIDDLE -> count
middle_counts = Counter(t['middle'] for t in tokens_b)
print(f"Unique MIDDLEs: {len(middle_counts)}")

# ============================================================
# Decompose MIDDLEs and extract modifier sequences
# ============================================================
# For each MIDDLE, get the modifier string from decompose_middle_hmt
# Then filter to only modifier chars from {p, c, i, f, d, s}

# MIDDLE -> modifier list (only chars from MOD_ATOMS set)
middle_mod_seqs = {}
for mid in middle_counts:
    head, mods, term, frame = decompose_middle_hmt(mid)
    # mods is the string between HEAD and TERM
    # Filter to only the 6 modifier atoms
    mod_chars = [ch for ch in mods if ch in MOD_ATOMS]
    if len(mod_chars) >= 2:
        middle_mod_seqs[mid] = mod_chars

# Also collect from full MIDDLE (some modifiers might appear in head/term
# positions in unusual cases - but we use the strict HMT decomposition)
print(f"\nMIDDLEs with 2+ modifier atoms in MOD slot: {len(middle_mod_seqs)} types")
total_tokens_2plus = sum(middle_counts[m] for m in middle_mod_seqs)
print(f"Token count with 2+ modifiers: {total_tokens_2plus}")

# Show distribution of modifier counts
mod_count_dist = Counter(len(v) for v in middle_mod_seqs.values())
print(f"\nModifier count distribution (types with 2+):")
for k in sorted(mod_count_dist):
    print(f"  {k} modifiers: {mod_count_dist[k]} types, "
          f"{sum(middle_counts[m] for m, v in middle_mod_seqs.items() if len(v) == k)} tokens")

# ============================================================
# ANALYSIS 1: Pairwise Ordering Counts (Type-Level)
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 1: PAIRWISE MODIFIER ORDERING (TYPE-LEVEL)")
print("=" * 70)

# For each pair (A, B), count: A-before-B vs B-before-A
# We look at all 15 pairs of the 6 modifiers
pair_before_type = defaultdict(lambda: Counter())   # pair_before_type[(a,b)] = {'ab': N, 'ba': M}
pair_before_token = defaultdict(lambda: Counter())  # same, weighted by token count

for mid, mod_seq in middle_mod_seqs.items():
    count = middle_counts[mid]
    # Get unique modifier set for this MIDDLE
    # For each pair, determine order
    seen_pairs = set()
    for i in range(len(mod_seq)):
        for j in range(i + 1, len(mod_seq)):
            a, b = mod_seq[i], mod_seq[j]
            if a == b:
                continue  # Same modifier repeated (e.g., ii - but i is the only one that repeats)
            pair_key = tuple(sorted([a, b]))
            if pair_key in seen_pairs:
                continue  # Already counted this pair for this MIDDLE
            seen_pairs.add(pair_key)

            # a appears before b in this compound
            pair_before_type[pair_key][f"{a}_before_{b}"] += 1
            pair_before_token[pair_key][f"{a}_before_{b}"] += count

# Print results
print(f"\n{'Pair':>6s} | {'A<B (types)':>12s} | {'B<A (types)':>12s} | {'Total':>6s} | "
      f"{'Ratio A<B':>10s} | {'p-value':>10s} | {'C1393 pred':>12s} | {'Match?':>8s}")
print("-" * 100)

results_pairwise = {}
c1393_predictions_correct = 0
c1393_predictions_total = 0
all_strict = True

for a, b in combinations(C1393_GRADIENT, 2):
    pair_key = (a, b)  # a is predicted to come before b by C1393 gradient

    ab_key = f"{a}_before_{b}"
    ba_key = f"{b}_before_{a}"

    n_ab_type = pair_before_type[pair_key].get(ab_key, 0)
    n_ba_type = pair_before_type[pair_key].get(ba_key, 0)
    total_type = n_ab_type + n_ba_type

    n_ab_token = pair_before_token[pair_key].get(ab_key, 0)
    n_ba_token = pair_before_token[pair_key].get(ba_key, 0)
    total_token = n_ab_token + n_ba_token

    if total_type > 0:
        ratio_type = n_ab_type / total_type
        p_val = binomial_test_two_sided(n_ab_type, total_type)
    else:
        ratio_type = float('nan')
        p_val = 1.0

    if total_token > 0:
        ratio_token = n_ab_token / total_token
    else:
        ratio_token = float('nan')

    # C1393 predicts a before b (since a has lower mean position)
    c1393_predicted = f"{a}<{b}"
    is_correct = ratio_type > 0.5 if total_type > 0 else None
    is_strict = n_ba_type == 0 and total_type > 0

    if total_type > 0:
        c1393_predictions_total += 1
        if is_correct:
            c1393_predictions_correct += 1

    if not is_strict and total_type > 0:
        all_strict = False

    match_str = "STRICT" if is_strict else ("YES" if is_correct else "NO" if is_correct is not None else "N/A")

    p_str = f"{p_val:.2e}" if p_val < 0.01 else f"{p_val:.4f}"

    print(f"  {a},{b}  | {n_ab_type:12d} | {n_ba_type:12d} | {total_type:6d} | "
          f"{ratio_type:10.3f} | {p_str:>10s} | {c1393_predicted:>12s} | {match_str:>8s}")

    results_pairwise[f"{a}_{b}"] = {
        'pair': [a, b],
        'a_before_b_types': n_ab_type,
        'b_before_a_types': n_ba_type,
        'total_types': total_type,
        'ratio_a_before_b_types': round(ratio_type, 4) if not math.isnan(ratio_type) else None,
        'a_before_b_tokens': n_ab_token,
        'b_before_a_tokens': n_ba_token,
        'total_tokens': total_token,
        'ratio_a_before_b_tokens': round(ratio_token, 4) if not math.isnan(ratio_token) else None,
        'p_value': round(p_val, 8),
        'c1393_prediction': c1393_predicted,
        'prediction_correct': is_correct,
        'is_strict': is_strict,
    }

print(f"\nC1393 gradient prediction accuracy: {c1393_predictions_correct}/{c1393_predictions_total}")
print(f"All orderings strict (100%)? {all_strict}")

# ============================================================
# ANALYSIS 2: Token-Weighted Pairwise Ordering
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 2: TOKEN-WEIGHTED PAIRWISE ORDERING")
print("=" * 70)

print(f"\n{'Pair':>6s} | {'A<B (tokens)':>12s} | {'B<A (tokens)':>12s} | {'Total':>8s} | "
      f"{'Ratio A<B':>10s} | {'p-value':>10s}")
print("-" * 80)

for a, b in combinations(C1393_GRADIENT, 2):
    pair_key = (a, b)
    ab_key = f"{a}_before_{b}"
    ba_key = f"{b}_before_{a}"

    n_ab = pair_before_token[pair_key].get(ab_key, 0)
    n_ba = pair_before_token[pair_key].get(ba_key, 0)
    total = n_ab + n_ba

    if total > 0:
        ratio = n_ab / total
        p_val = binomial_test_two_sided(n_ab, total)
    else:
        ratio = float('nan')
        p_val = 1.0

    p_str = f"{p_val:.2e}" if p_val < 0.01 else f"{p_val:.4f}"
    print(f"  {a},{b}  | {n_ab:12d} | {n_ba:12d} | {total:8d} | "
          f"{ratio:10.3f} | {p_str:>10s}")

# ============================================================
# ANALYSIS 3: Examples of Compounds with Each Pair
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 3: EXAMPLES OF COMPOUNDS WITH MULTI-MODIFIER PAIRS")
print("=" * 70)

for a, b in combinations(C1393_GRADIENT, 2):
    pair_key = (a, b)
    ab_key = f"{a}_before_{b}"
    ba_key = f"{b}_before_{a}"

    # Find example compounds for each ordering
    ab_examples = []
    ba_examples = []

    for mid, mod_seq in middle_mod_seqs.items():
        if a in mod_seq and b in mod_seq:
            # Determine order
            a_pos = mod_seq.index(a)
            b_pos = mod_seq.index(b)
            head, mods, term, frame = decompose_middle_hmt(mid)
            count = middle_counts[mid]
            example_str = f"{mid}(H={head},M={mods},T={term},n={count})"

            if a_pos < b_pos:
                ab_examples.append((count, example_str))
            else:
                ba_examples.append((count, example_str))

    ab_examples.sort(key=lambda x: -x[0])
    ba_examples.sort(key=lambda x: -x[0])

    n_ab = len(ab_examples)
    n_ba = len(ba_examples)
    total = n_ab + n_ba

    if total == 0:
        continue

    print(f"\n  {a},{b}: {n_ab} types {a}<{b}, {n_ba} types {b}<{a} ({total} total)")
    if ab_examples:
        top_ab = [e[1] for e in ab_examples[:5]]
        print(f"    {a}<{b}: {', '.join(top_ab)}")
    if ba_examples:
        top_ba = [e[1] for e in ba_examples[:5]]
        print(f"    {b}<{a}: {', '.join(top_ba)}")

# ============================================================
# ANALYSIS 4: Absolute Orderings and Violations
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 4: ABSOLUTE ORDERINGS AND VIOLATIONS")
print("=" * 70)

strict_pairs = []
near_strict_pairs = []  # >95%
moderate_pairs = []  # >75%
weak_pairs = []  # >50%
reversed_pairs = []  # <50%
empty_pairs = []

for a, b in combinations(C1393_GRADIENT, 2):
    pair_key = (a, b)
    ab_key = f"{a}_before_{b}"
    ba_key = f"{b}_before_{a}"

    n_ab = pair_before_type[pair_key].get(ab_key, 0)
    n_ba = pair_before_type[pair_key].get(ba_key, 0)
    total = n_ab + n_ba

    if total == 0:
        empty_pairs.append((a, b))
        continue

    ratio = n_ab / total

    if ratio == 1.0:
        strict_pairs.append((a, b, total, ratio))
    elif ratio >= 0.95:
        near_strict_pairs.append((a, b, total, ratio))
    elif ratio >= 0.75:
        moderate_pairs.append((a, b, total, ratio))
    elif ratio >= 0.50:
        weak_pairs.append((a, b, total, ratio))
    else:
        reversed_pairs.append((a, b, total, ratio))

print(f"\nStrict ordering (100%): {len(strict_pairs)} pairs")
for a, b, n, r in strict_pairs:
    print(f"  {a}<{b}: {n} types, 100% compliant")

print(f"\nNear-strict ordering (>=95%): {len(near_strict_pairs)} pairs")
for a, b, n, r in near_strict_pairs:
    print(f"  {a}<{b}: {n} types, {r:.1%} compliant")

print(f"\nModerate ordering (>=75%): {len(moderate_pairs)} pairs")
for a, b, n, r in moderate_pairs:
    print(f"  {a}<{b}: {n} types, {r:.1%} compliant")

print(f"\nWeak ordering (>=50%): {len(weak_pairs)} pairs")
for a, b, n, r in weak_pairs:
    print(f"  {a}<{b}: {n} types, {r:.1%} compliant")

print(f"\nReversed ordering (<50%): {len(reversed_pairs)} pairs")
for a, b, n, r in reversed_pairs:
    print(f"  {a}<{b}: {n} types, {r:.1%} compliant — VIOLATES gradient!")

print(f"\nEmpty pairs (never co-occur): {len(empty_pairs)} pairs")
for a, b in empty_pairs:
    print(f"  {a},{b}: never co-occur in modifier slot")

# ============================================================
# ANALYSIS 5: Transitivity Check
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 5: TRANSITIVITY CHECK")
print("=" * 70)

# For every triple (a, b, c), if a<b and b<c are both >50%, check a<c
transitivity_violations = []
for a, b, c in combinations(C1393_GRADIENT, 3):
    # Get pair ratios
    def get_ratio(x, y):
        pk = tuple(sorted([x, y]))
        xk = f"{x}_before_{y}"
        yk = f"{y}_before_{x}"
        nx = pair_before_type[pk].get(xk, 0)
        ny = pair_before_type[pk].get(yk, 0)
        total = nx + ny
        if total == 0:
            return None
        return nx / total

    r_ab = get_ratio(a, b)
    r_bc = get_ratio(b, c)
    r_ac = get_ratio(a, c)

    if r_ab is not None and r_bc is not None and r_ac is not None:
        if r_ab > 0.5 and r_bc > 0.5:
            if r_ac <= 0.5:
                transitivity_violations.append((a, b, c, r_ab, r_bc, r_ac))
                print(f"  VIOLATION: {a}<{b} ({r_ab:.1%}) and {b}<{c} ({r_bc:.1%}) but {a}>={c} ({r_ac:.1%})")

if not transitivity_violations:
    print("  No transitivity violations found — ordering is fully transitive.")

# ============================================================
# ANALYSIS 6: Alternative Ordering Test
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 6: BEST-FIT ORDERING")
print("=" * 70)

# Try all 720 permutations of 6 modifiers and find which maximizes
# the number of correctly-predicted pairwise orderings
from itertools import permutations

best_perm = None
best_score = -1
best_score_weighted = -1
all_perms_scores = []

for perm in permutations(C1393_GRADIENT):
    score_type = 0
    score_token = 0
    total_type = 0
    total_token = 0

    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            a, b = perm[i], perm[j]
            pk = tuple(sorted([a, b]))
            ak = f"{a}_before_{b}"
            bk = f"{b}_before_{a}"

            n_ab_t = pair_before_type[pk].get(ak, 0)
            n_ba_t = pair_before_type[pk].get(bk, 0)
            n_ab_tk = pair_before_token[pk].get(ak, 0)
            n_ba_tk = pair_before_token[pk].get(bk, 0)

            score_type += n_ab_t
            total_type += n_ab_t + n_ba_t
            score_token += n_ab_tk
            total_token += n_ab_tk + n_ba_tk

    type_ratio = score_type / total_type if total_type > 0 else 0
    token_ratio = score_token / total_token if total_token > 0 else 0

    all_perms_scores.append((perm, score_type, total_type, type_ratio, score_token, total_token, token_ratio))

    if score_type > best_score:
        best_score = score_type
        best_perm = perm

# Sort by type score
all_perms_scores.sort(key=lambda x: -x[3])

print(f"\nBest type-level ordering: {'->'.join(best_perm)}")
print(f"  Score: {best_score}/{all_perms_scores[0][2]} = {all_perms_scores[0][3]:.1%}")

# Compare C1393 gradient
c1393_score = None
for perm, st, tt, tr, stk, ttk, tkr in all_perms_scores:
    if list(perm) == C1393_GRADIENT:
        c1393_score = (st, tt, tr, stk, ttk, tkr)
        break

if c1393_score:
    print(f"\nC1393 gradient (p->f->i->c->d->s):")
    print(f"  Type-level: {c1393_score[0]}/{c1393_score[1]} = {c1393_score[2]:.1%}")
    print(f"  Token-level: {c1393_score[3]}/{c1393_score[4]} = {c1393_score[5]:.1%}")

# Show top 5 orderings
print(f"\nTop 5 orderings by type-level accuracy:")
for perm, st, tt, tr, stk, ttk, tkr in all_perms_scores[:5]:
    marker = " <-- C1393" if list(perm) == C1393_GRADIENT else ""
    marker = " <-- BEST" if perm == best_perm and not marker else marker
    print(f"  {'->'.join(perm)}: {tr:.1%} types, {tkr:.1%} tokens{marker}")

# Also find best token-weighted
all_perms_scores_token = sorted(all_perms_scores, key=lambda x: -x[6])
best_perm_token = all_perms_scores_token[0][0]
print(f"\nBest token-weighted ordering: {'->'.join(best_perm_token)}")
print(f"  Score: {all_perms_scores_token[0][4]}/{all_perms_scores_token[0][5]} = {all_perms_scores_token[0][6]:.1%}")

# How many permutations share the best score?
best_type_score = all_perms_scores[0][3]
tied_count = sum(1 for x in all_perms_scores if abs(x[3] - best_type_score) < 0.0001)
print(f"\nPermutations tied for best type-level score: {tied_count}")

# ============================================================
# ANALYSIS 7: Per-Modifier Position Statistics
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 7: PER-MODIFIER POSITION IN MODIFIER STACK")
print("=" * 70)

# For each modifier, compute its mean position within the modifier substring
# when co-occurring with other modifiers
mod_positions = defaultdict(list)  # char -> list of normalized positions
mod_positions_token = defaultdict(list)  # weighted

for mid, mod_seq in middle_mod_seqs.items():
    count = middle_counts[mid]
    n_mods = len(mod_seq)
    for idx, ch in enumerate(mod_seq):
        if n_mods > 1:
            norm_pos = idx / (n_mods - 1)  # 0.0 = first, 1.0 = last
        else:
            norm_pos = 0.5
        mod_positions[ch].append(norm_pos)
        for _ in range(count):
            mod_positions_token[ch].append(norm_pos)

print(f"\n{'Atom':>6s} | {'Mean Pos':>10s} | {'Std':>8s} | {'N types':>8s} | "
      f"{'Mean (token)':>12s} | {'N tokens':>10s} | {'C1393 pos':>10s}")
print("-" * 80)

for ch in C1393_GRADIENT:
    positions = mod_positions.get(ch, [])
    positions_t = mod_positions_token.get(ch, [])
    if positions:
        mean_p = sum(positions) / len(positions)
        std_p = (sum((x - mean_p) ** 2 for x in positions) / len(positions)) ** 0.5
    else:
        mean_p = float('nan')
        std_p = float('nan')
    if positions_t:
        mean_pt = sum(positions_t) / len(positions_t)
    else:
        mean_pt = float('nan')

    c1393_pos = C1393_MEAN_POS.get(ch, None)
    c1393_str = f"{c1393_pos:.3f}" if c1393_pos is not None else "?"
    print(f"  {ch:>4s}  | {mean_p:10.3f} | {std_p:8.3f} | {len(positions):8d} | "
          f"{mean_pt:12.3f} | {len(positions_t):10d} | {c1393_str:>10s}")

# ============================================================
# ANALYSIS 8: Three+ Modifier Sequences
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 8: THREE+ MODIFIER SEQUENCES")
print("=" * 70)

three_plus = {m: s for m, s in middle_mod_seqs.items() if len(s) >= 3}
print(f"\nMIDDLEs with 3+ modifiers: {len(three_plus)} types, "
      f"{sum(middle_counts[m] for m in three_plus)} tokens")

# Check if ALL 3+ modifier sequences follow the gradient
gradient_compliant_3plus = 0
gradient_violation_3plus = 0

for mid, mod_seq in three_plus.items():
    # Check if the modifier sequence is in the gradient order
    positions = [C1393_GRADIENT.index(ch) for ch in mod_seq if ch in C1393_GRADIENT]
    is_sorted = all(positions[i] <= positions[i + 1] for i in range(len(positions) - 1))
    if is_sorted:
        gradient_compliant_3plus += 1
    else:
        gradient_violation_3plus += 1
        count = middle_counts[mid]
        head, mods, term, frame = decompose_middle_hmt(mid)
        print(f"  Violation: {mid} (H={head}, M={mods}, T={term}, n={count})")
        print(f"    Mod sequence: {mod_seq}, gradient positions: {positions}")

print(f"\n3+ modifier gradient compliance: {gradient_compliant_3plus}/{gradient_compliant_3plus + gradient_violation_3plus} "
      f"({gradient_compliant_3plus / (gradient_compliant_3plus + gradient_violation_3plus):.1%})"
      if (gradient_compliant_3plus + gradient_violation_3plus) > 0 else "")

# ============================================================
# ANALYSIS 9: Check if i-repeats affect ordering
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 9: EXTENSIBLE MODIFIERS (i-repeats)")
print("=" * 70)

# i is the only modifier that can repeat (C1197). Check if ii vs i
# changes ordering relative to other modifiers.
i_repeat_compounds = {}
for mid, mod_seq in middle_mod_seqs.items():
    # Check if 'i' appears multiple times in mod_seq
    i_count = mod_seq.count('i')
    if i_count >= 2:
        i_repeat_compounds[mid] = mod_seq

print(f"MIDDLEs with 2+ i in modifier slot: {len(i_repeat_compounds)} types, "
      f"{sum(middle_counts[m] for m in i_repeat_compounds)} tokens")

for mid, mod_seq in sorted(i_repeat_compounds.items(), key=lambda x: -middle_counts[x[0]]):
    head, mods, term, frame = decompose_middle_hmt(mid)
    count = middle_counts[mid]
    print(f"  {mid}: H={head}, M={mods}, T={term}, n={count}, mod_seq={mod_seq}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

n_strict = len(strict_pairs)
n_near = len(near_strict_pairs)
n_moderate = len(moderate_pairs)
n_weak = len(weak_pairs)
n_reversed = len(reversed_pairs)
n_empty = len(empty_pairs)
n_testable = n_strict + n_near + n_moderate + n_weak + n_reversed

print(f"\n15 possible modifier pairs:")
print(f"  Empty (never co-occur): {n_empty}")
print(f"  Testable: {n_testable}")
print(f"    Strict (100%): {n_strict}")
print(f"    Near-strict (>=95%): {n_near}")
print(f"    Moderate (>=75%): {n_moderate}")
print(f"    Weak (>=50%): {n_weak}")
print(f"    Reversed (<50%): {n_reversed}")

print(f"\nC1393 gradient prediction: {c1393_predictions_correct}/{c1393_predictions_total} pairs correct")
print(f"Transitivity: {'FULLY TRANSITIVE' if not transitivity_violations else f'{len(transitivity_violations)} violations'}")
print(f"Best ordering: {'->'.join(best_perm)}")
print(f"Best ordering = C1393 gradient? {list(best_perm) == C1393_GRADIENT}")

# ============================================================
# Save Results
# ============================================================
output = {
    'phase': 'Phase 531: Modifier Stacking Order',
    'total_b_tokens': len(tokens_b),
    'unique_middles': len(middle_counts),
    'middles_2plus_mods': len(middle_mod_seqs),
    'tokens_2plus_mods': total_tokens_2plus,
    'modifier_count_distribution': {str(k): v for k, v in sorted(mod_count_dist.items())},
    'pairwise_ordering': results_pairwise,
    'c1393_gradient': C1393_GRADIENT,
    'c1393_prediction_accuracy': f"{c1393_predictions_correct}/{c1393_predictions_total}",
    'all_strict': all_strict,
    'best_type_ordering': list(best_perm),
    'best_type_score': f"{all_perms_scores[0][3]:.4f}",
    'best_token_ordering': list(best_perm_token),
    'best_token_score': f"{all_perms_scores_token[0][6]:.4f}",
    'c1393_is_best': list(best_perm) == C1393_GRADIENT,
    'tied_permutations': tied_count,
    'transitivity_violations': len(transitivity_violations),
    'strict_pairs': [[a, b] for a, b, _, _ in strict_pairs],
    'near_strict_pairs': [[a, b] for a, b, _, _ in near_strict_pairs],
    'moderate_pairs': [[a, b] for a, b, _, _ in moderate_pairs],
    'weak_pairs': [[a, b] for a, b, _, _ in weak_pairs],
    'reversed_pairs': [[a, b] for a, b, _, _ in reversed_pairs],
    'empty_pairs': [[a, b] for a, b in empty_pairs],
    'three_plus_mods': {
        'types': len(three_plus),
        'gradient_compliant': gradient_compliant_3plus,
        'gradient_violations': gradient_violation_3plus,
    },
    'i_repeat_compounds': {
        'count': len(i_repeat_compounds),
        'examples': [{'middle': mid, 'mod_seq': mod_seq, 'tokens': middle_counts[mid]}
                     for mid, mod_seq in i_repeat_compounds.items()],
    },
    'per_modifier_position_stats': {
        ch: {
            'mean_pos_type': round(sum(mod_positions.get(ch, [])) / len(mod_positions.get(ch, [1])), 4)
                if mod_positions.get(ch) else None,
            'n_type': len(mod_positions.get(ch, [])),
            'c1393_mean_pos': C1393_MEAN_POS.get(ch),
        }
        for ch in C1393_GRADIENT
    },
}

results_path = PROJECT_ROOT / 'phases' / 'MODIFIER_STACKING_ORDER' / 'results' / 'modifier_stacking_order.json'
with open(results_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {results_path}")
print("DONE")
