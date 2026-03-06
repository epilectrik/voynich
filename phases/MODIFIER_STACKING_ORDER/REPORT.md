# Phase 531: Modifier Stacking Order

**Date:** 2026-03-05
**Status:** COMPLETE
**New Constraints:** C1472

## Research Question

C1393 asked: "When multiple modifiers appear in one compound, is their internal sub-order fixed?" C1394 T4 asserted a "fixed stacking order p->f->i->c->d->s" with co-occurrence avoidance ratios. C1394 T10 characterized this as "morphological convention with weak semantic coupling" but the question of whether multi-modifier compounds obey a strict ordering remained open.

## Method

Extracted all compound MIDDLEs from Currier B with 2+ modifier atoms in the MOD slot (using `decompose_middle_hmt()` from `scripts/voynich.py`). Modifier atoms are {p, f, i, c, d, s} as defined by C1393. Analyzed:
1. All 15 pairwise orderings (type-level and token-weighted)
2. Binomial significance for each pair
3. Exhaustive search over 720 permutations for best-fit ordering
4. Transitivity of pairwise preferences
5. 3+ modifier compliance with gradient orderings
6. Per-modifier position statistics in multi-modifier contexts
7. i-repeat compound inventory

## Key Results

### Co-occurrence Avoidance is the Dominant Constraint

8 of 15 modifier pairs NEVER co-occur in the modifier slot:

```
p: avoids f, i, c, d (all non-s modifiers)
f: avoids c, d
i: avoids c, d
```

Only 7 pairs are testable. This means modifier "ordering" is largely moot -- most modifier pairs never appear together to be ordered. The primary structural constraint is which modifiers CAN combine, not in what order they appear.

### No Strict or Near-Strict Orderings

| Category | Count | Pairs |
|----------|-------|-------|
| Strict (100%) | 0 | -- |
| Near-strict (>=95%) | 0 | -- |
| Moderate (75-90%) | 3 | p<s (89.7%), f<s (81.8%), c<s (78.8%) |
| Weak (50-75%) | 3 | f<i (57.1%), i<s (58.8%), c<d (71.7%) |
| Reversed vs C1393 | 1 | d,s (s precedes d 60.9%) |

All three moderate orderings involve `s` as the later element. The ordering signal is primarily "s goes late" and "p goes early," not a full linear sequence.

### d,s Reversal

C1393's positional gradient predicts d<s (d at 0.54, s at 0.64). In multi-modifier compounds, this is reversed: s precedes d 60.9% of types and 64.5% of tokens. This is the only reversal among the 7 testable pairs but it invalidates the "p->f->i->c->d->s" as a complete ordering.

### Best-Fit Ordering

```
Best:  p -> f -> c -> s -> d -> i  (68.8% type, 75.9% token)
C1393: p -> f -> i -> c -> d -> s  (65.9% type, 69.4% token)
```

Key differences from C1393:
- s moves before d (correcting the reversal)
- i moves to the end (reflecting its weak ordering with interior modifiers)
- c moves before s (reflecting its reliable s-precedence)

### 3+ Modifier Compliance

Only 42.6% of 115 types with 3+ modifiers comply with the C1393 gradient. This means long compounds frequently violate any single linear ordering. The ordering is a weak statistical preference, not a compositional rule.

### Transitivity Violation

One violation in the testable triplet {c, d, s}: c<d (71.7%) and c<s (78.8%) but d>s (reversed). The partial order is not transitive.

### i-Repeat Compounds

63 types with repeated i atoms (1,556 tokens). Dominated by aiin (834 tokens) and iin (560 tokens). These are the C1197 extensibility phenomenon -- i is one of only two atoms (with e) that can repeat consecutively. The i-repeat compounds are overwhelmingly TRANSITION category, consistent with C1455 (double-ii categorical safety).

## Interpretation

The modifier slot grammar has two layers:

1. **Co-occurrence avoidance (hard constraint):** 53% of modifier pairs (8/15) categorically exclude each other. This is the primary structural force shaping modifier composition.

2. **Ordering preference (soft constraint):** Among pairs that DO co-occur, s reliably goes late and p reliably goes early. Interior modifiers {c, d, f, i} have weak mutual preferences that can reverse.

This aligns with C1394 T10's characterization of "morphological convention with weak semantic coupling" but provides the quantitative basis that T10 lacked. The "fixed stacking order" language in C1394 T4 should be read as "preferred ordering tendency" rather than a grammatical rule.

The massive co-occurrence avoidance (53% empty pairs) means the modifier slot is NOT a freely combinable parameter stack. Instead, modifier selection is heavily constrained by compatibility -- modifiers that encode similar or conflicting parametric dimensions cannot co-occur. This extends C1394 T4's avoidance ratios from "reduced" to "categorically absent."

## Constraint Produced

| # | Name | Tier | Scope |
|---|------|------|-------|
| C1472 | Modifier co-occurrence avoidance dominates ordering | 2 | B, grammar, composition |

## Relationship to Existing Constraints

| Constraint | Status |
|------------|--------|
| C1393 open question on modifier stacking | **RESOLVED**: not fixed, statistical preference |
| C1394 T4 "fixed stacking order" | **REFINED**: preference not rule; d,s reversed; best order is p->f->c->s->d->i |
| C1394 T10 "morphological convention" | **CONFIRMED**: convention with 68.8% compliance, not grammar |
| C1394 T4 co-occurrence avoidance ratios | **STRENGTHENED**: 8/15 categorically absent, not just reduced |

## Files

- `scripts/modifier_stacking_order.py` -- analysis script
- `results/modifier_stacking_order.json` -- full results
