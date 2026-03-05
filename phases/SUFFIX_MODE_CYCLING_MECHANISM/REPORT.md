# Phase 518: Suffix Mode Cycling Mechanism

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints produced:** C1422, C1423, C1424

---

## Research Question

What drives the alternation between suffix Mode A ({d, e, ee, h, y} -- THERMAL/MONITORING) and Mode B ({a, i, ii, l, m, n, o, r, s} -- STAGING/FLOW) within paragraphs? Is the cycling fully explained by MIDDLE TERMINAL atom alternation (C1412: V=0.503), or is there an independent paragraph-level rhythm?

## Background

- **C1229**: Two suffix modes alternate within paragraphs (silhouette 0.459, "80% interleaved")
- **C1410**: Modes decompose to atom-level operational partitions
- **C1412**: MIDDLE TERMINAL -> suffix mode V=0.503, full MIDDLE V=0.678
- **C1338**: I(MIDDLE; suffix_cat) = 0.697 bits, 11.57x more than I(line_mode; suffix_cat)

## Methodology

10 tests spanning token-level (T1, T2, T4-T6, T8) and line-level (T3, T7, T9, T10) analysis. Line-level mode assignment aggregates all suffix atoms within a line (matching C1229/C1410 methodology). MIDDLE decomposition uses base chars for TERMINAL/HEAD atoms (matching Phase 516 convention). MIXED modes excluded from analysis. Permutation tests used for significance assessment.

## Key Results

### T1: TERMINAL Alternation Within Paragraphs
TERMINAL atoms alternate strongly within paragraphs: switch rate 0.7344 vs 0.2169 expected under marginals (chi2=333.34, p=6.23e-44). But this is driven by TERMINAL frequency distribution (y=37.3% of all TERMINALs), not by forced alternation -- the switch-to-expected ratio is 0.938, meaning actual switching is BELOW what marginal frequencies predict. TERMINALs self-chain mildly above chance, particularly t (2.15x), k (1.96x), and h (1.89x).

### T2: TERMINAL -> Suffix Mode Mapping (REPLICATION)
Replicates C1412: V=0.5025, MI=0.187 bits (21.6% of H(mode)), N=1,755. Per-TERMINAL polarization:
- **Mode A atoms:** h (91.2%), t (72.9%), k (67.0%)
- **Mode B atoms:** r (96.7%), l (63.4%), y (62.5%), m (66.7%)
- **Weak:** n (58.3% A -- near random)

### T3: Line Mode Prediction
Dominant-TERMINAL prediction accuracy = 0.5815 (1.11x baseline). Position alternation accuracy = 0.5049 (below baseline). Position-based alternation has ZERO predictive power -- the cycling is not positional rhythm.

### T4-T5: HEAD and PREFIX Alternation
HEAD atoms alternate at 0.7786 switch rate. MI(HEAD; suffix_mode) = 0.091 bits (9.1%), consistent with C1412's HEAD V=0.323. PREFIX alternation at 0.864 but MI(PREFIX; mode) = only 0.028 bits (2.8%). HEAD-to-TERMINAL MI = 0.935 bits -- HEAD and TERMINAL are strongly coupled within the MIDDLE.

### T6: Token-Level Prediction Model
Joint features (PREFIX + HEAD + TERMINAL) explain 21.4% of suffix mode entropy. Accuracy 0.6824 (1.33x baseline). **Critical:** Previous token mode adds only 1.64% beyond token features (CMI = 0.0164 bits). No meaningful token-level sequential dependency.

### T7: Line-Level Sequential Dependency (KEY FINDING)
CMI(prev_line_mode; curr_line_mode | dominant_TERM) = 0.0289 bits (2.89% of H). 4/8 strata significant after controlling for dominant TERMINAL: y (p<0.001, n=868), l (p=0.0003, n=291), n (p=0.0012, n=207), h (p=0.025, n=71). Overall same-mode rate = 0.6065 -- lines tend to persist in the same mode.

This is a WEAK but GENUINE line-level sequential dependency that survives TERMINAL control. It represents mild mode inertia (same-mode persistence) at the line level.

### T8: TERMINAL Transition Constraints
0 forbidden TERMINAL pairs. All 8x8 transitions observed. Some depletion: m->k (0.43x), t->n (0.57x), t->r (0.63x). Self-chaining enriched for t (2.15x), k (1.96x), h (1.89x) -- Mode A terminals self-chain more than Mode B terminals.

### T9: Line Boundary Effect
Token-level cross-line switch rate (43.7%) slightly below within-line (46.4%), p=0.037. Line boundaries mildly suppress mode switching. LINE-level mode switch rate = 0.3935 -- lines tend to PERSIST in mode, not alternate.

### T10: C1229 Decomposition (CRITICAL)

**Observed line-level interleave rate = 0.3935.**

This is BELOW the random expectation of 0.499 (permutation mean = 0.417, p=0.999). Lines show **mode PERSISTENCE**, not mode interleaving. The C1229 "80% interleaving" refers to the fraction of paragraphs containing interleaved patterns (k-means classification), not to the raw mode switch rate between consecutive lines.

Decomposition:
- Mode switch when same dominant term: 39.1%
- Mode switch when different dominant term: 39.4%
- **TERMINAL switching does NOT drive mode switching** -- mode switch rate is identical regardless of whether the dominant TERMINAL changed.
- The below-random interleaving is fully captured by TERMINAL vocabulary effects (100.6% of the deficit from random)

## Synthesis

### What Drives Suffix Mode Selection?

The suffix mode of a token is ~80% determined by its MIDDLE identity (C1338, C1412), particularly the TERMINAL atom:
- **h, k, t terminals** -> Mode A (specification/thermal)
- **r, l, y terminals** -> Mode B (continuation/flow)

The remaining ~20% is contextual modulation (C1346): PREFIX contributes 50%, environment 29%, position 12%, opener 8%.

### What Drives Line-Level Mode Patterns?

Lines show **mild mode persistence** (60.6% same-mode between consecutive lines), not the "80% interleaving" that C1229 appeared to claim. The persistence arises from:

1. **MIDDLE vocabulary continuity** -- consecutive lines tend to use similar MIDDLE vocabularies (C670, C675), so their dominant TERMINALs tend to agree, producing same-mode runs
2. **Weak genuine inertia** -- 2.89% of line-mode entropy is sequentially determined beyond TERMINAL, representing mild operational state persistence

### C1229 Reconciliation

C1229's "80% interleaved" should be understood as: "80% of paragraphs with 8+ body lines contain both Mode A and Mode B lines in a non-trivial mixture" (paragraph-level classification), NOT as "80% of consecutive line pairs switch modes." The actual consecutive-line switch rate is 39.4%, which is 10.5 pp BELOW random (49.9%) -- lines mildly persist in mode.

## Constraints Produced

### C1422: Suffix Mode is MIDDLE-Determined Without Sequential Dependency (Tier 2)
Token-level suffix mode is 80% MIDDLE-determined (C1338), 20% contextual. Previous token mode adds only 1.64% beyond token features. No token-level sequential cycling mechanism exists.

### C1423: Line-Level Mode Persistence With Weak Inertia (Tier 2)
Consecutive lines show 60.6% same-mode rate (vs 50% random). 2.89% of line-mode entropy is sequentially determined beyond TERMINAL control. 4/8 TERMINAL strata show significant persistence. Lines mildly persist in mode, not alternate.

### C1424: Mode Switching Is TERMINAL-Independent at Line Level (Tier 2)
Mode switch rate is 39.1% when consecutive lines share dominant TERMINAL vs 39.4% when they differ. Whether the dominant TERMINAL changes between lines has NO effect on whether the mode changes. TERMINAL vocabulary determines each line's mode independently; the cycling pattern is not driven by TERMINAL alternation.

## Verdict

**TERMINAL_GATES_TOKEN_MODE + NO_TOKEN_SEQUENTIAL_DEPENDENCY + WEAK_LINE_SEQUENTIAL_DEPENDENCY + LINE_CYCLING_EXPLAINED_BY_TERMINAL**

The "cycling" in C1229 is better understood as: paragraphs contain a mixture of Mode A and Mode B lines because they contain a mixture of Mode A and Mode B MIDDLEs. Each line's mode is determined primarily by its MIDDLE vocabulary, with mild inertia causing short same-mode runs. There is no independent paragraph-level rhythm, no positional alternation, and no sequential dependency at the token level.

## Files

- **Script:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/scripts/suffix_mode_mechanism.py`
- **Results:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json`
