# Control Engagement Intensity (CEI)

**Status:** CLOSED | **Tier:** 2

> **Status note (v7.25; see SYSTEM/STATUS_BRIEF.md §3):** CEI and its bands (C187–C192) remain Tier 2 in the generated table as folio metrics. Their reading as "operator intervention" belongs to the closed-loop control interpretation, now demoted (C171, Tier 3). LINK is a 13.2% morphological artifact of "ol" (C609, C1174), not a waiting/monitoring operator, and REGIME is a soft gradient rather than 4 crisp classes (C1712, C2070).

---

## Definition

CEI measures active intervention density in a program. Higher CEI = more frequent operator action. [Historical interpretation; the measured quantity is the folio-level CEI metric (C187).]

---

## The 4 Regimes

*[REGIME as 4 crisp classes is retired (C1712, C2070): a soft gradient whose dominant split is Bio vs non-Bio section.]*

| Regime | CEI Level | Characteristics |
|--------|-----------|-----------------|
| REGIME_2 | Lowest | Most waiting, least intervention |
| REGIME_1 | Low | Baseline operation |
| REGIME_4 | High | Elevated engagement |
| REGIME_3 | Highest | Maximum throughput (transient) |

**Ordering:** R2 < R1 < R4 < R3

---

## CEI-LINK Relationship

| Metric | Value |
|--------|-------|
| Correlation | r = -0.7057 |
| Direction | Strong negative |
| Meaning | More LINK → Less CEI |

LINK tokens (ol-morphology, C1174: morphological artifact) anticorrelate with CEI. Programs with higher ol-density have lower active engagement.

---

## CEI and Manuscript Organization

| Finding | Value | Meaning |
|---------|-------|---------|
| CEI smoothing | d=1.89 | Adjacent folios have similar CEI |
| Restart position | d=2.24 | Restarts at low-CEI points |
| CEI bidirectional | 1.44x | Easier to decrease than increase |

---

## Intervention Cycles

*[Historical framing: "intervention cycle" and "ol-BOUNDARY" rest on the LINK monitoring reading, withdrawn (C1174). The adjacency enrichments themselves are distributional observations.]*

Grammar separates two phases:

| Phase | Tokens | LINK Proximity |
|-------|--------|----------------|
| EARLY-CYCLE | da, -in/-l/-r | Adjacent to ol-tokens (attracted) |
| LATE-CYCLE | ch/sh, -edy/-ey | Distant from ol-tokens (avoiding) |

Line structure: ENTRY → EARLY-CYCLE → ol-BOUNDARY → LATE-CYCLE → EXIT

---

## LINK Distribution (C365-C366) — C365 refuted by C805 (dead); C366 revised by C804

| Property | Finding |
|----------|---------|
| Spatial uniformity | ~~YES (no positional clustering)~~ refuted: LINK has a positional bias (C805) |
| Run length | Random (z=0.14) |
| Line-position | ~~Uniform (p=0.80)~~ refuted by C805 (first 17.2%, last 15.3%, middle 12.4%) |
| Function | ~~Grammar state transition marker~~ C366 revised by C804 (predecessor claims not confirmed) |

ol-tokens mark a positional boundary within lines (C805, C813). The functional interpretation as "monitoring/intervention" boundary is superseded by C1174 (morphological artifact).

---

## What LINK Precedes/Follows

| Before LINK | Enrichment |
|-------------|------------|
| AUXILIARY | 1.50x |
| FLOW_OPERATOR | 1.30x |

| After LINK | Enrichment |
|------------|------------|
| HIGH_IMPACT | 2.70x |
| ENERGY_OPERATOR | 1.15x |

---

## Navigation

← [program_taxonomy.md](program_taxonomy.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
