# PHASE_716: Test C1212 Multi-Step Chaining as Mechanism for C1727 Line-Ordering Smoothness

**Status:** COMPLETE
**Date:** 2026-05-20
**Verdicts:** Three Tier 2 registrations after blocking-control scrutiny:
- C2049 (Tier 2 falsification): C1212 cross-line chaining is NOT mechanism for line-ordering smoothness
- C2050 (Tier 2 falsification): Mode A/B coherence is NOT mechanism
- C2051 (Tier 2 measurement): HEAD+TERM JOINT coherence is the localizable smoothness signal (rank 2% of random 13-feature subsets)
**Scope:** folio-segmented measurement (my z=-3.81 vs original C1727 z=-6.05 due to segmentation difference)
**Methodology note:** paragraph-mean residualization tests were mathematically invalid (constant shift identity); flagged and documented.
**Posture:** Crazy-expert's PHASE_715 follow-up proposal. C1727 established that within-paragraph line ordering is significantly smoother than shuffled (z=-6.05, p<0.001) — consecutive lines more similar than random. C2048 established C1212-type cross-token TERM→MIDDLE[0] chaining is multi-step (extends lag+2/+3). The hypothesis: **multi-step C1212 chaining ACROSS line boundaries is the mechanism producing C1727 line-ordering smoothness.**

If lines have multi-step coherence at the cross-token chaining level (terminal TERM atoms of line_i influence head MIDDLE atoms of line_{i+1}'s first several tokens), then real line ordering would smooth out at the feature level — exactly the C1727 signature.

---

## The test

**C1727 measurement** (per `phases/LINE_ORDERING_INFORMATION_CONTENT/`): build 15-dim feature vector per line (6 HEAD types + 7 TERM types + suffix mode + line length), compute sequential_structure_score = sum of squared consecutive differences within paragraph, compare to shuffled paragraph-line ordering. Real ordering is smoother (z=-6.05).

**Hypothesis:** the smoothness comes from cross-line C1212 chaining — TERM atoms at end of line_i propagate constraints to MIDDLE[0] atoms at start of line_{i+1}'s first few tokens (multi-step per C2048).

**Discriminating test:** exclude the first N tokens of each line when computing features. If C1212 cross-line chaining IS the mechanism:
- N=0 (full line): z ≈ -6.05 (baseline reproduction)
- N=1 (skip first token): z should be less negative
- N=3 (skip first 3 tokens): z should collapse significantly toward 0
- N=5 (skip first 5 tokens): z should approach 0 if multi-step chaining is the only mechanism

**Control test:** exclude the last N tokens of each line. If C1212 is the mechanism, this should ALSO collapse the smoothness (since it removes the SOURCE TERM atoms that propagate to next line).

**Anti-mechanism control:** if z stays around -6.05 even when first/last N tokens excluded, then C1212 is NOT the dominant mechanism — line-ordering smoothness has additional structural sources.

---

## Pre-registered decision rules (LOCKED)

| Outcome | Verdict |
|---|---|
| z(N=3 excluded) is within 50% of z(N=0) in magnitude | **C1212 NOT mechanism** — line-ordering smoothness has other structural drivers |
| z(N=3 excluded) collapses by 50%-80% from z(N=0) | **C1212 PARTIAL mechanism** — accounts for substantial portion but not all |
| z(N=3 excluded) collapses by >80% from z(N=0) | **C1212 DOMINANT mechanism** — multi-step chaining IS the line-ordering signature |
| z(N=3 excluded) actually MORE negative than z(N=0) | **PATHOLOGICAL** — exclusion methodology has confound |

Symmetric verdicts for last-N exclusion.

---

## Why this could be high-yield

If C1212 multi-step chaining IS the mechanism behind C1727:
- We've identified a SPECIFIC structural mechanism producing line-ordering smoothness
- The "compositional carry-over" reading from C2048 gets concrete spatial scope (extends across line boundaries)
- C1212 + C1727 + C2048 form a coherent multi-step picture: cross-token chaining produces line-ordering smoothness via cross-line propagation
- This is the kind of mechanism-identification that breaks through the procedural ceiling — a constraint becomes EXPLANATORY of another constraint, not just measured alongside

If it ISN'T the mechanism:
- Line-ordering smoothness comes from OTHER structural sources (paragraph composition, topic coherence, scribal habits)
- C1212/C2048 multi-step chaining is real but doesn't propagate across lines in a way that affects feature-level ordering
- Both findings stand as independent measurements

---

## Methodology details

**Feature construction** (per C1727 methodology):
- HEAD profile (6 dims): a, e, o, k, t, headless fractions
- TERM profile (7 dims): y, l, r, h, m, n, bare fractions
- Suffix mode (1 dim): A=1, B=0, none=0.5
- Line length (1 dim): token count

Total: 15-dim feature vector per line.

**Sequential structure score:** Σ ||f_{i+1} - f_i||² across consecutive lines within paragraph.

**Permutation null:** shuffle line order within each paragraph, recompute score. N=1000 shuffles.

**Z-score:** (observed - null_mean) / null_std. Negative z means observed is smaller than null (smoother).

**Exclusion variants:** for each N in {0, 1, 2, 3, 5}, compute features using only tokens at positions N onwards within each line (or for last-N: positions 0 to len-N).

**Within-folio shuffle null** (per `feedback_within_folio_shuffle_null_first.md`): also shuffle features across lines within folio (preserving folio composition) to check if any signal isn't just folio-composition shadow.

---

## Implementation

| Script | Purpose |
|---|---|
| `_c1212_line_ordering_test.py` | Reproduce C1727 baseline + test N-token exclusion variants |

---

## Effort estimate

~2-3 hours implementation, ~10 min runtime (1000 shuffles × 5 variants × first/last).

---

## Registration-trap audit

- Pre-registered decision rules locked BEFORE running
- 4 outcome categories (DOMINANT / PARTIAL / NOT_MECHANISM / PATHOLOGICAL)
- Symmetric first-N vs last-N exclusion controls
- Within-folio shuffle null comparison
- Per `feedback_framework_as_null.md`: result fits crazy-expert prediction → extra skepticism
- Mechanism identification result (if positive) needs to survive external scrutiny before promotion
