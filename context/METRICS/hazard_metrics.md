# Hazard Metrics

**Status:** CLOSED | **Tier:** 0-2

> **[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** The hazard layer this file describes is withdrawn. The class-level "17 forbidden transitions" is demoted (C783: powered class pairs at O/E≈1.13, 13 class-level violations in the real corpus, C2063); the 5-class failure taxonomy was imposed by keyword matching (C2060; C216 demoted to Tier 3); and the token-level zeros (C957, superseded) reduce to line composition, positional zones and boundary glyph coupling (C2081) — no prohibition layer remains. C109 is kept only as a scoped row. Rows below that remain Tier 2 in the generated table (e.g. C110–C112, C166, C169, C217, C400, C601, C645) are measurements taken on the 17-pair set; read them as properties of that pair set, not of a prohibition or safety layer. None of this file is Tier 0. Text kept for traceability.

---

## Scope Note (KERNEL_STATE_SEMANTICS, 2026-01)

The 17 "forbidden transitions" operate at **CLASS level** (instruction classes 9, 10, 11, 12, 17, 23, 31, 32), not at k/h/e CHARACTER level. The term "hazard" refers to disfavored class-to-class transitions, not to k/h/e characters representing dangerous states.

- k, h, e operate at CONSTRUCTION level (within-token morphology, C521)
- Forbidden transitions operate at EXECUTION level (between-token class sequencing, C109)
- These layers are INDEPENDENT (C522)
- k/h/e content does NOT predict forbidden transition participation

See KERNEL_STATE_SEMANTICS phase for full evidence.

*[Superseded note: the CLASS-level reading of the 17 was later demoted (C783), and the "kernel" framing of k/h/e is withdrawn (C089 superseded by C2082). C521's "e→h = 0.00" is an EVA spelling identity, while its glyph-level e/bench asymmetry is real (PHASE_754 glyph-unit gate).]*

---

## Forbidden Transitions

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Total forbidden | 17 | 2 (scoped; was 0) | C109 — class level demoted (C783), zeros reduce (C2081) |
| Failure classes | 5 | struck (was 0) | C109 — taxonomy imposed, C2060 |
| Asymmetric | 65% | 2 | C111 |
| Distant from kernel | 59% | 2 | C112 |

---

## 5 Failure Classes

| Class | Count | % | Constraint |
|-------|-------|---|------------|
| PHASE_ORDERING | 7 | 41% | C110 |
| COMPOSITION_JUMP | 4 | 24% | C109 |
| CONTAINMENT_TIMING | 4 | 24% | C109 |
| RATE_MISMATCH | 1 | 6% | C109 |
| ENERGY_OVERSHOOT | 1 | 6% | C109 |

Note: CONTAINMENT_TIMING has 0 corpus impact (theoretical-only).

---

## Hybrid Hazard Model (C216 — demoted to Tier 3; computed over the imposed 5-class taxonomy, C2060)

| Type | % | LINK Nearby | Severity |
|------|---|-------------|----------|
| Batch-focused | 71% | 1.229 | 0.733 |
| Apparatus-focused | 29% | 0 | 0.800 |

Apparatus hazards require faster response (no waiting allowed).

---

## Hazard Avoidance

| Metric | Value | Constraint |
|--------|-------|------------|
| HT hazard proximity | 4.84 (vs 2.5 expected) | C169 |
| HT at forbidden seams | 0/35 | C166 |
| True HT near hazards | 0 (vs 4,510 at random) | C217 |
| Hazards at line-initial | 0.20x (5x depleted) | C400 |
| Hazards at folio-initial | 0/82 | C400 |

---

## Post-Hazard Handling (REVISED 2026-01-31)

> **Note:** Original "escape routes" terminology was incorrect. C397/C398 measured
> lane transitions, not escape. Actual hazard recovery is CHSH-dominant (C645).

| Metric | Value | Constraint |
|--------|-------|------------|
| CHSH post-hazard rate | 75.2% (PHASE_729: Markov-trivial under the 5-gram null, residual +2.3pp) | C645 |
| QO post-hazard rate | 24.8% (depleted 0.55x) | C645 |
| QO hazard participation | 0/19 events | C601 |

## Lane Transition After Hazard Sources (C397/C398 Corrected)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| qo-prefix after sources | 25-47% | CHSH→QO lane transition (not escape) |
| ENERGY_OP after sources | 40-67% | Baseline role frequency after CHSH |
| CORE_CONTROL after sources | 22-32% | Baseline role frequency after CHSH |
| Safe precedence (ENERGY_OP) | 33-67% | C399 |

---

## Suppressed Transitions

*[Historical: "beyond forbidden" and "KERNEL-HEAVY" refer to the withdrawn prohibition and kernel layers (C2081; C089 superseded by C2082).]*

| Metric | Value | Constraint |
|--------|-------|------------|
| Beyond forbidden | 8 suppressed (<0.5x) | C386 |
| All in KERNEL-HEAVY cluster | YES | C386 |
| h→k observed | 0 | C332 |
| Self-transition enrichment | 3.76x average | C388 |

---

## Navigation

← [grammar_metrics.md](grammar_metrics.md) | [link_metrics.md](link_metrics.md) →
