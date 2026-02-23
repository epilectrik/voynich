# C1220: PREFIX Modifier Consistency Varies by Character

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PREFIX_ATOM_ROLES (Phase 434)
**Extends:** C1218 (PREFIX positional grammar), C1219 (base determines MIDDLE content)
**Relates to:** C1193 (PREFIX composition low additivity), C1001 (PREFIX dual encoding)

---

## Statement

PREFIX modifier characters (POS-0 in the base-modifier grammar) vary substantially in their cross-base consistency. Some modifiers contribute a similar behavioral shift regardless of base character (o: cosine 0.836, l: 0.794, a: 0.756), while others have base-dependent effects (d: 0.345, s: 0.368, c: 0.380). PREFIX compositionality is therefore partial: base character is always predictive (C1219), but modifier contributions range from consistent to context-dependent.

### Cross-Base Modifier Consistency

| Modifier | PREFIXes | Mean Cosine | Consistency |
|----------|----------|-------------|-------------|
| o | ol, ok, ot, or | 0.836 | HIGH |
| l | lch, lsh, lk | 0.794 | HIGH |
| a | al, ar | 0.756 | HIGH |
| t | te, tch, to, ta | 0.464 | MODERATE |
| p | pch, po | 0.450 | MODERATE |
| k | ko, kch, ka, ke | 0.413 | LOW |
| c | ch, ct | 0.380 | LOW |
| s | sa, so, sh | 0.368 | LOW |
| d | do, da, dch | 0.345 | LOW |

### Within-Base Modifier Differentiation

Within h-base (the largest group, 10 PREFIXes):
- ch: 26% CLOSURE vs kch: 52% CLOSURE vs rch: 42% CLOSURE
- ch: 10% MONITORING vs sh: 7% MONITORING vs dch: 2% MONITORING
- Modifiers create measurable differentiation within the base-defined domain

Within a-base (4 PREFIXes):
- da: 78% ITER, ka: 81% ITER, sa: 85% ITER, ta: 83% ITER
- Very uniform -- modifiers create minimal differentiation in a-base

Within o-base (6 PREFIXes):
- qo: 4% ITER, 12% STRUCTURAL vs so: 30% ITER, 1% STRUCTURAL
- qo is the most distinctive o-base PREFIX (least iteration, most structural)

---

## Interpretation

The three consistency tiers suggest different modifier mechanisms:

1. **Consistent modifiers (o, l, a):** These characters contribute similar effects regardless of base. The 'o' modifier consistently shifts toward iteration/vessel operations. The 'l' modifier consistently adds a completion/late-phase quality (aligns with C931 lch line-final tendency). These are genuine compositional elements.

2. **Moderate modifiers (t, p):** These contribute partially consistent effects, modulated by the base. Their behavior changes somewhat across bases but retains recognizable characteristics.

3. **Base-dependent modifiers (c, d, s, k):** These characters behave very differently depending on the base character. The 'c' modifier in ch (STABILITY-heavy) vs ct (72% MONITORING) shows extreme context-dependence. These may function more as allomorphs than compositional units.

This resolves the tension between C1193 (low additivity) and the clear compositionality visible in PREFIX structure: compositionality is real but modifier-specific, not universal.

---

## Method

- 23,096 Currier B tokens with non-empty MIDDLEs
- For each modifier character appearing in 2+ PREFIXes across different bases:
  - Computed MIDDLE atom profiles for each PREFIX containing that modifier
  - Calculated mean pairwise cosine similarity across bases
- Within-base analysis: compared modifier-specific profiles within each base group
- 9 modifiers tested across 2-4 bases each

**Script:** `phases/PREFIX_ATOM_ROLES/scripts/prefix_atom_test.py` (T3)
**Results:** `phases/PREFIX_ATOM_ROLES/results/prefix_atom_results.json`
