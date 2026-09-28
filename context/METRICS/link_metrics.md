# LINK Metrics

**Status:** CLOSED | **Tier:** 2

> **Status note (v7.25; see SYSTEM/STATUS_BRIEF.md §3):** LINK is 13.2% of Currier B and a morphological artifact of "ol" (C609, C1174). The "waiting" / "monitoring vs intervention" readings in this file are withdrawn (C171 demoted to Tier 3; F-B-001 superseded). The density and enrichment numbers remain measurements.

---

## Overall LINK Density

| System | LINK Density |
|--------|--------------|
| Currier B | 13.2% (3,047/23,096) |
| Currier A | 3.0% |
| AZC | 7.6% (highest) |

> **C609 Correction:** Previous values of "6.6%" and "38% (weighted by folio)" were legacy figures with undocumented methodology. Reconciliation audit (Phase LINK_DENSITY_RECONCILIATION) established true B density at 13.2% token-level, 12.5% folio mean. No aggregation reproduces 38%.

---

## LINK by Section (C334)

| Section | LINK Density | Relative |
|---------|--------------|----------|
| B | 19.6% | 1.45x baseline |
| H | 9.1% | Baseline |
| C | 10.1% | ~Baseline |
| S | 9.8% | ~Baseline |

Section B requires 45% more waiting. [Historical reading, withdrawn (C1174): the measurement is 1.45x LINK (ol) density in Section B.]

---

## LINK Distribution Properties (C365 — refuted by C805; dead)

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** C365 ("LINK tokens are spatially uniform") is refuted by C805: LINK has a positional bias (mean position 0.476 vs 0.504; first 17.2%, last 15.3%, middle 12.4%).

| Property | Value | p-value |
|----------|-------|---------|
| Spatial uniformity | YES | 0.005 |
| Run length | Random | z=0.14 |
| Line-position | Uniform | 0.80 |
| Positional clustering | NO | - |

LINK has **no positional marking function**. [Refuted by C805.]

---

## LINK Context (C366 — revised by C804: predecessor claims not confirmed, successor enrichment weak) [v7.26 status: C366 demoted to Tier 3 (not confirmed (C804); LINK is morphological (C1174))]

### Preceding LINK
| Role | Enrichment |
|------|------------|
| AUXILIARY | 1.50x |
| FLOW_OPERATOR | 1.30x |

### Following LINK
| Role | Enrichment |
|------|------------|
| HIGH_IMPACT | 2.70x |
| ENERGY_OPERATOR | 1.15x |

LINK marks **boundary between monitoring and intervention**. [Withdrawn: superseded by C1174 (morphological artifact); see also C804.]

---

## LINK-CEI Relationship (C190)

| Metric | Value |
|--------|-------|
| Correlation | r = -0.7057 |
| Direction | Strong negative |
| Meaning | More LINK → Less engagement [statistic valid; interpretation superseded by C1174] |

---

## LINK at Boundaries (C359) [v7.26 status: C359 demoted to Tier 3 (conflicts with C805 (weaker method))]

| Position | LINK Presence |
|----------|---------------|
| Line boundaries | 0.60x (suppressed) |
| Mid-line | 1.0x (baseline) |

Lines are NOT pause points.

---

## LINK-Escalation Complementarity (C340)

| Context | LINK Density |
|---------|--------------|
| Near escalation (k/h) | 0.605x |
| Baseline | 1.0x |

Waiting and intervention are functionally segregated. [Historical reading, withdrawn (C1174; kernel framing of k/h superseded, C089 → C2082): the measurement is lower ol density near k/h-containing tokens.]

---

## Navigation

← [hazard_metrics.md](hazard_metrics.md) | [coverage_metrics.md](coverage_metrics.md) →
