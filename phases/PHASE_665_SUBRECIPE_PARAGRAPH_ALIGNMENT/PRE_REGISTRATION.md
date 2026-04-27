# Phase 665 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test (sub-folio quantitative alignment)
**Motivation:** H1 from expert packet consultation (2026-04-26). Both expert-advisor and crazy-expert independently ranked this hypothesis #1 highest-payoff. Expert convergence is itself signal.

---

## Context

C1959 established that paragraph layout-order on confirmed-match folios corresponds to recipe-phase order at **rank-correlation level** (mean Spearman ρ=+0.81 across 5-7 confirmed matches). C1959 used rank-vs-rank: paragraph rank by layout vs subrecipe rank by phase ordinal.

Phase 665 tests at **quantitative level** rather than rank: do paragraph attributes (token count, verb-category densities) correlate with corresponding subrecipe attributes (char count, verb-category densities) when ordinal-mapped?

This is **distinct from C1959**:
- C1959 tested ordering only (whether paragraphs are in the right rank order)
- Phase 665 tests magnitude (whether paragraph SIZE/composition tracks subrecipe SIZE/composition)

The test target is III.19 ↔ f75r, the only CONFIRMED match with multiple subrecipes (9 subrecipes in III.19, 9 paragraphs in f75r).

---

## Hypothesis

**H1 (primary):** Under ordinal mapping P_i ↔ III.19.{i-1}, Spearman ρ between paragraph token-count and subrecipe char-count is ≥ +0.6.

**H2 (secondary):** Under same mapping, paragraph verb-category density correlates with subrecipe verb-category density for ≥ 2 of 4 pre-specified high-frequency categories.

**H₀:** No quantitative correlation; paragraph sizes/compositions are independent of subrecipe sizes/compositions.

---

## Locked decisions

### 1. Mapping (locked)

Strict ordinal mapping:
- f75r P1 (L1-L5, 46T) ↔ III.19.0
- f75r P2 (L6, 9T) ↔ III.19.1
- f75r P3 (L7-L12, 58T) ↔ III.19.2
- f75r P4 (L13-L16, 39T) ↔ III.19.3
- f75r P5 (L17-L22, 52T) ↔ III.19.4
- f75r P6 (L23-L26, 31T) ↔ III.19.5
- f75r P7 (L27, 11T) ↔ III.19.6
- f75r P8 (L28-L31, 46T) ↔ III.19.7
- f75r P9 (L32-L46, 120T) ↔ III.19.8

This mapping is **frozen before any correlation runs**. No post-hoc shuffling permitted.

### 2. Primary endpoint (locked, single)

**Spearman ρ between (paragraph token-count) and (subrecipe char-count)** under the locked mapping. n=9 pairs.

Permutation null: 10,000 shuffles of the subrecipe assignment (paragraphs hold fixed; subrecipes shuffle through 9 positions). Compute ρ on each shuffle. p-value = fraction with ρ ≥ observed.

### 3. Secondary endpoint (locked, multi-test with Bonferroni)

For each of 4 pre-specified verb categories from Phase 660 corpus:
- DISTILLATION
- MATERIAL_TAKE
- MATERIAL_PLACE
- OBSERVATION

Compute per-paragraph verb-category density (count / token-count) on f75r. Compute per-subrecipe density (count / char-count) on III.19. Spearman ρ under same mapping.

Bonferroni-corrected α: 0.05 / 4 = 0.0125.

### 4. Tertiary descriptive (NOT load-bearing)

Pearson correlation on the same data. Reported alongside Spearman for sanity-check. Does not contribute to verdict.

### 5. Verdicts (locked)

| Verdict | Criterion |
|---|---|
| SUPPORTED | H1 ρ ≥ 0.6, p ≤ 0.05; AND H2 ≥ 2/4 categories meet ρ ≥ 0.4, p ≤ 0.0125 |
| DIRECTIONAL | H1 ρ ≥ 0.4, p ≤ 0.10; OR H2 ≥ 2/4 categories meet ρ ≥ 0.4, p ≤ 0.10 |
| INCONCLUSIVE | H1 ρ ≥ 0.2 but doesn't reach DIRECTIONAL |
| FALSIFIED | H1 ρ < 0.2 OR REVERSED direction |

### 6. Verb assignment for f75r paragraphs

f75r paragraph-level verb-category density requires VMS-side categorization, which is not in Phase 660 (Phase 660 categorized Catalan). For VMS-side verb-category density, **use Phase 660 categories applied to ATOM glosses** via the existing atom-gloss system. Specifically:

- DISTILLATION proxy: presence of `qok-` prefixed tokens (per C1969 distillation-cycle context) — paragraph density = (qok-class tokens)/(paragraph tokens)
- MATERIAL_TAKE proxy: `pen-`/`pol-`/`pch-` opener tokens — paragraph rate = (such tokens)/(paragraph tokens)
- MATERIAL_PLACE proxy: `dar`/`dal`/`daly` tokens (per C1925) — paragraph density
- OBSERVATION proxy: `aiin`/`ain` substring (per C1234 bounded-loop control) — paragraph density

These proxies are **locked before run**. They are imperfect — VMS-side verb categorization isn't a solved problem — but they are the closest existing constraint-grounded analogs.

### 7. What this phase does NOT do

- No mapping shuffles after running.
- No exploration of alternative paragraph definitions.
- No expansion to f76r/f84r (single-subrecipe matches; no internal alignment to test).
- No constraint registration without LOO sensitivity check (drop one (paragraph, subrecipe) pair; verify result holds).

---

## Honest expectation

f75r paragraph token counts: 46, 9, 58, 39, 52, 31, 11, 46, 120 (P1-P9)
III.19 subrecipe char counts: 546, 337, 207, 369, 143, 195, 163, 1002, 2265 (.0-.8)

Naive eyeballing:
- P9 (120T) ↔ III.19.8 (2265 chars) — both are massive tails. Strong contribution to +ρ.
- P8 (46T) ↔ III.19.7 (1002 chars) — both medium-large. Contributes.
- P7 (11T) ↔ III.19.6 (163 chars) — both small. Contributes.
- P2 (9T) ↔ III.19.1 (337 chars) — P2 is smallest, .1 is moderate. Hurts.
- P3 (58T) ↔ III.19.2 (207 chars) — P3 is large, .2 is small. Hurts.

The tail (P7, P8, P9 vs .6, .7, .8) is well-aligned. The middle (P2-P5 vs .1-.4) is mismatched. Honest expected ρ: probably +0.4 to +0.6 — DIRECTIONAL likely, SUPPORTED uncertain.

If H1 SUPPORTED at +0.6: paragraph sizes really do track subrecipe sizes; would refine C1959 with quantitative claim.

If FALSIFIED (ρ < 0.2): C1959's rank-correlation finding doesn't extend to magnitude — paragraphs are in approximately the right order but don't size-match.
