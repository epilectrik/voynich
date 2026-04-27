# Phase 663 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test (paragraph-level partition)
**Prior:** Phase 661 (DISTILLATION folio-binary, INCONCLUSIVE-reversed); Phase 662 (thermal-iteration superclass folio-binary, INCONCLUSIVE due to N=2 negatives).

---

## Context

Phase 661+662 established:
- Folio-aggregate ke/ek shows DIRECTIONALLY-CORRECT signal at operational-mode granularity (Cohen's d=+0.46, predicted direction)
- BUT folio-binary partition with N=14 matched pairs is structurally exhausted (negatives collapse to N=2 at superclass aggregation)
- The signal exists; folio-aggregate sampling can't extract it cleanly

This phase moves to **paragraph resolution**. With ~5-7 paragraphs per folio across 14 matched folios, expected N is ~70-100 paragraphs — substantially larger than 14.

The same partition logic (thermal-iteration superclass per Phase 662) applied at paragraph level.

---

## Hypothesis

**T1 (primary):** Paragraphs from thermal-iteration superclass-positive matched folios show higher ke/ek ratio than paragraphs from superclass-negative matched folios.

**H₀:** No difference at paragraph distribution level.

---

## Locked decisions

### 1. Paragraph extraction (locked)

For each of the 14 matched folios, extract paragraphs using existing project infrastructure. A paragraph = sequence of tokens with same paragraph identifier from the canonical paragraph-segmentation (per `Token.par_initial` / `par_final` markers in transcript).

Paragraphs with fewer than 8 tokens are excluded (per Phase 1961 block-pure paragraph definition; insufficient signal). This is locked: no tweaking the threshold to expand or shrink the sample.

### 2. Per-paragraph ke/ek ratio (locked, identical metric to 661/662)

ke/ek = (count of paragraph tokens containing 'ke' substring) / (max(1, count containing 'ek' substring))

Computed per paragraph independently.

### 3. Partition (locked, inherited from Phase 662)

| Group | Folios |
|---|---|
| Superclass-positive | f75r, f112r, f82v, f76r, f84r, f79r, f82r, f103r, f81v, f112v, f116r, f107r |
| Superclass-negative | f76v, f77v |

Paragraphs from superclass-positive folios → positive group.
Paragraphs from superclass-negative folios → negative group.

### 4. Statistical test (locked)

Mann-Whitney U one-sided permutation (10,000 perms). Predicted direction: positive paragraph distribution > negative paragraph distribution.

Cohen's d on the paragraph-level distributions.

### 5. Verdicts

| Verdict | Criterion |
|---|---|
| SUPPORTED | predicted direction + p ≤ 0.05 + Cohen's d ≥ 0.3 |
| DIRECTIONAL | predicted direction + p ≤ 0.20 + d ≥ 0.2 |
| INCONCLUSIVE | predicted direction but p > 0.20 OR d < 0.2 |
| REVERSED-NULL | OPPOSITE direction p ≤ 0.10 |
| FALSIFIED | OPPOSITE direction p ≤ 0.05 |

Effect-size threshold lowered from 0.5 (Phase 662) to 0.3 because:
- Per-paragraph variance is higher than per-folio aggregate
- Larger N supports detecting smaller effects
- The scientific question is whether ANY signal survives at paragraph resolution, not whether it's strong

### 6. Sensitivity check (locked, reported)

After primary test, report secondary stratification:
- Within-superclass-positive folios only: do paragraphs from CONFIRMED matches (f75r, f76r, f84r) show different ke/ek than paragraphs from supported matches?
- This is descriptive, not load-bearing on the primary verdict.

### 7. What this phase does NOT do

- No verb-position-matching analysis (paragraphs near vs not-near specific verb positions). That's Phase 664+ if 663 supports.
- No re-categorization of folios.
- No re-running with different paragraph thresholds.

---

## Honest expectation

The signal direction confirmed in Phase 662 should hold at paragraph level with bigger N driving statistical significance. Cohen's d=+0.46 at folio level often corresponds to similar or larger effects at paragraph level when within-folio variance is non-trivial. p<0.20 (DIRECTIONAL) is plausible; p<0.05 (SUPPORTED) is possible if within-folio variance is moderate.

If still null at paragraph resolution, the verb-corpus folio-binary methodology IS exhausted and the next move would need to be position-matching (paragraph-near-verb vs paragraph-not-near-verb).
