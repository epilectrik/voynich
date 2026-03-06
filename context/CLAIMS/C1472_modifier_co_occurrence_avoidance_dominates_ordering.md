# C1472: Modifier Co-occurrence Avoidance Dominates Ordering

**Tier:** 2 (ESTABLISHED)
**Scope:** B, grammar, composition
**Phase:** MODIFIER_STACKING_ORDER (Phase 531)
**Depends on:** C1393 (composition grammar), C1394 (instruction encoding architecture), C1065 (atom ordering grammar)

## Statement

Modifier atoms {p, f, i, c, d, s} within compound MIDDLEs are governed primarily by **co-occurrence avoidance** (8/15 pairs never appear together) and only secondarily by ordering preferences. The C1394 T4 "fixed stacking order p->f->i->c->d->s" is refined to a **statistical preference with co-occurrence avoidance as the dominant constraint**. No pair achieves strict (100%) or near-strict (>=95%) ordering. The empirically best ordering is p->f->c->s->d->i (68.8% type accuracy), which differs from the C1393 positional gradient (65.9%) in the d/s and i/c/d interior positions. The ordering is driven by s being reliably late and p being reliably early; interior modifiers {c, d, f, i} show much weaker mutual ordering. 3+ modifier sequences comply with any single ordering only 42.6% of the time. This resolves C1393's open question on modifier stacking: the ordering is real but soft, and avoidance is more structurally important than sequencing.

## Key Findings

### Corpus Statistics

- 464 MIDDLE types with 2+ modifier atoms in MOD slot (2,466 tokens)
- Distribution: 2-mod=349 types, 3-mod=98 types, 4-mod=16 types, 5-mod=1 type

### Co-occurrence Avoidance (Primary Finding)

8 of 15 modifier pairs NEVER co-occur in the modifier slot:

| Empty Pair | C1394 Avoidance Note |
|------------|---------------------|
| p,f | Yes (0.50x in C1394 T4) |
| p,i | Not noted |
| p,c | Not noted |
| p,d | Not noted |
| f,c | Not noted |
| f,d | Yes (0.50x in C1394 T4) |
| i,c | Yes (0.40x in C1394 T4) |
| i,d | Not noted |

The 8 empty pairs include all 4 pairs involving p with non-s modifiers, confirming p operates in near-complete isolation from {f, i, c, d}. Similarly, f avoids {c, d} entirely. This is stronger than C1394 T4's "co-occurrence avoidance" characterization (which reported ratios like 0.40-0.52x) -- many of these pairs are categorically absent from the modifier slot, even when they co-occur elsewhere in the compound.

### Pairwise Ordering (7 Testable Pairs)

| Pair | A<B types | B<A types | Ratio | p-value | C1393 pred | Correct? |
|------|-----------|-----------|-------|---------|------------|----------|
| p,s | 26 | 3 | 89.7% | 1.95e-5 | p<s | Yes |
| f,s | 9 | 2 | 81.8% | 0.065 | f<s | Yes |
| c,s | 26 | 7 | 78.8% | 0.00094 | c<s | Yes |
| c,d | 71 | 28 | 71.7% | 1.55e-5 | c<d | Yes |
| f,i | 8 | 6 | 57.1% | 0.79 | f<i | Yes (weak) |
| i,s | 10 | 7 | 58.8% | 0.63 | i<s | Yes (weak) |
| **d,s** | **18** | **28** | **39.1%** | **0.14** | **d<s** | **REVERSED** |

Summary:
- 0 strict (100%) pairs
- 0 near-strict (>=95%) pairs
- 3 moderate (75-90%): p<s, f<s, c<s -- all involve s
- 3 weak (50-75%): f<i, i<s, c<d -- not statistically significant
- 1 REVERSED: d,s -- s precedes d 60.9% of the time

### s-Atom Late Position Dominance

All 3 moderate orderings involve s (sequence) as the later element. s has mean modifier position 0.631, the latest of all 6 modifiers. The ordering signal is primarily driven by s reliably appearing late; the other modifiers have less fixed relative positions.

### d,s Reversal

The d<s prediction from C1393's positional gradient (d=0.54, s=0.64) is reversed in multi-modifier compounds: s precedes d 60.9% of the time (28/46 types). While not statistically significant at p=0.14, the reversal is consistent at both type and token level (token ratio: 64.5% s<d). This means C1394 T4's ordering "p->f->i->c->d->s" is incorrect for the d,s pair.

### Best-Fit Ordering

Exhaustive search over 720 permutations:
- **Best type-level:** p->f->c->s->d->i (68.8% accuracy, unique winner)
- **Best token-level:** p->f->c->s->d->i (75.9% accuracy)
- **C1393 gradient:** p->f->i->c->d->s (65.9% type, 69.4% token)
- **C1394 T4 order:** p->f->i->c->d->s (same as C1393 gradient)

The key differences: s moves before d (correcting the reversal), and i moves later (reflecting its weak ordering with interior modifiers).

### Transitivity

1 transitivity violation: i<c (N=0, untestable) and c<d (71.7%) but i<d is untestable (N=0). Of the testable triplet {c,d,s}: c<d (71.7%) and c<s (78.8%) but d>s (reversed), violating transitivity.

### 3+ Modifier Compliance

- 115 types with 3+ modifier atoms
- Only 49 (42.6%) comply with the C1393 gradient ordering
- Only 42.6% comply with ANY single linear ordering
- Long compounds frequently violate ordering preferences

### Per-Modifier Position Statistics

| Modifier | Mean pos (this study) | C1393 mean pos | N types |
|----------|-----------------------|----------------|---------|
| p | 0.261 | 0.38 | 155 |
| f | 0.408 | 0.50 | 74 |
| c | 0.508 | 0.40 | 279 |
| i | 0.532 | 0.44 | 217 |
| d | 0.589 | 0.54 | 218 |
| s | 0.631 | 0.64 | 118 |

Notable: c and i positions are reversed relative to C1393 (c=0.508 > i=0.532 here, but c=0.40 < i=0.44 in C1393). This reflects C1393's measurement being over ALL compounds (including single-modifier), while this study isolates multi-modifier compounds where relative ordering matters.

## Relationship to C1394

C1394 T4 established "fixed stacking order p->f->i->c->d->s" with co-occurrence avoidance ratios. C1472 refines this:

| C1394 T4 claim | C1472 finding |
|----------------|---------------|
| "Fixed stacking order" | Statistical preference, not fixed (best accuracy 68.8%) |
| p->f->i->c->d->s | Better fit: p->f->c->s->d->i (d,s reversed) |
| Co-occurrence avoidance (ratios) | 8/15 pairs are CATEGORICALLY absent, not just reduced |
| "Modifier ordering is morphological convention" (T10) | CONFIRMED and strengthened: convention, not rule |

**No conflict.** C1394 T10's characterization of ordering as "morphological convention with weak semantic coupling" is validated. C1472 provides the precise quantification that T4's "fixed" language lacked.

## C1393 Open Question Resolution

C1393 asked: "Modifier stacking order: When multiple modifiers appear in one compound, is their internal sub-order fixed?"

**Answer: No.** The ordering is a statistical preference (best fit 68.8%), not a fixed rule. Co-occurrence avoidance (8/15 empty pairs) is the dominant structural constraint. Among modifiers that DO co-occur, s is reliably late and p is reliably early, but interior modifiers {c, d, f, i} show weak and sometimes reversed mutual ordering.

## Falsification

Would be falsified if:
1. A larger corpus reveals strict (100%) orderings for any pair
2. The 8 empty pairs are shown to be sampling artifacts (appear in a different Currier B corpus)
3. The d,s reversal is shown to be driven by a small number of high-frequency types rather than a genuine gradient

## Provenance

- `phases/MODIFIER_STACKING_ORDER/scripts/modifier_stacking_order.py` -- full analysis
- `phases/MODIFIER_STACKING_ORDER/results/modifier_stacking_order.json` -- consolidated results
