# C1312: No Cross-Line Sequential Category Coupling

**Tier:** 2
**Scope:** B
**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Date:** 2026-02-25

## Finding

Cross-mode coupling between Mode A and Mode B lines is positional (C1310) and paragraph-scoped (C1308), NOT sequential. Five tests of sequential coupling all failed:

1. **No zig-zag grammar** (T5): Zig-zag coupling (AB+BA mean r=0.350) is WEAKER than mode-shuffled null (null mean=0.378, Z=-3.39, perm p=0.999). This is predicted by C1309's mode specialization: interleaving category-complementary modes naturally produces more entropy than same-mode sequences.

2. **No A->B category prediction** (T2): A's dominant category does not predict the next B line's category (V=0.170, p=0.146, perm p=0.154).

3. **No cross-line transition grammar** (T4): Category transitions at line boundaries show no structure for any mode pair type (AA p=0.51, AB p=0.085, BA p=0.49, BB p=0.006 WEAK only).

4. **No cross-line forbidden transitions** (T6): 0 of 1,384 cross-line transitions violate the 17 forbidden pairs. Hazard topology is strictly line-internal (consistent with C360).

5. **No token interleaving signal** (P3): All interleaving ratios tested (1:1, 1:2, 2:1, 1:3, 3:1, 2:3, 3:2) produce higher entropy than individual lines. 1:1 interleaving is indistinguishable from random pairing (Z=-0.01, perm p=0.51). The Z=-0.01 result means the mode interleaving pattern carries provably zero information about category sequencing — coupling is not just undetected but absent at this resolution.

## Same-Mode > Cross-Mode (T1)

Same-mode consecutive pairs show stronger category coupling than cross-mode pairs:
- AA: mean r=0.463
- BB: mean r=0.383
- AB: mean r=0.372
- BA: mean r=0.328
- Kruskal-Wallis H=22.05, p=6.4e-5

## BA Handoff Pattern (P4)

Despite no sequential grammar, the BA boundary shows a characteristic handoff: TRANSITION->THERMAL dominates at 12.0% of BA transitions — the single most common BA category transition. B lines exit through TRANSITION, A lines re-enter through THERMAL specification. AB handoffs are more diffuse (top transition FLOW->STAGING at 6.0%). The directional asymmetry (AB vs BA cosine similarity = 0.833 but structurally different) is consistent with C1311's finding that B->A feedback is real while A->B is null.

## Interpretation

The parallel mode tracks are coordinated by shared paragraph context (C1308) and positional synchronization (C1310), not by sequential token-to-token or line-to-line dependency. Each line is operationally self-contained (C360), and the grammar truly resets at line boundaries. The tracks read from the same "key signature" (paragraph category profile) but play their parts independently.

## Extends

- C360 (line-invariant grammar) — category-level evidence confirms line independence
- C972 (cross-line MI below random Markov) — category grammar mirrors the token-level reset
- C670 (adjacent line vocabulary coupling = NULL) — now confirmed at category level
- C1233 (mode sequence near-random) — no sequential structure at category level either

## Falsifiability

Would be falsified if zig-zag coupling exceeds permutation null (T5 perm p < 0.05) or if any interleaving ratio produces lower entropy than individual lines (P3 delta < 0).

## Evidence Files

- `phases/CROSS_MODE_CATEGORY_COUPLING/results/cross_mode_category_coupling.json` (T1-T7)
- `phases/CROSS_MODE_CATEGORY_COUPLING/results/parallel_track_probe.json` (P3, P4)
