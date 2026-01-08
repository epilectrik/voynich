# Control Engagement Intensity (CEI)

**Status:** CLOSED | **Tier:** 2

---

## Definition

CEI measures active intervention density in a program. Higher CEI = more frequent operator action.

---

## The 4 Regimes

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

LINK tokens represent deliberate waiting. Programs with more LINK have less active engagement.

---

## CEI and Manuscript Organization

| Finding | Value | Meaning |
|---------|-------|---------|
| CEI smoothing | d=1.89 | Adjacent folios have similar CEI |
| Restart position | d=2.24 | Restarts at low-CEI points |
| CEI bidirectional | 1.44x | Easier to decrease than increase |

---

## Intervention Cycles

Grammar separates two phases:

| Phase | Tokens | LINK Proximity |
|-------|--------|----------------|
| MONITORING | da, -in/-l/-r | Adjacent (attracted) |
| INTERVENTION | ch/sh, -edy/-ey | Distant (avoiding) |

Line structure: ENTRY → MONITORING → LINK → INTERVENTION → EXIT

---

## LINK Distribution (C365-C366)

| Property | Finding |
|----------|---------|
| Spatial uniformity | YES (no positional clustering) |
| Run length | Random (z=0.14) |
| Line-position | Uniform (p=0.80) |
| Function | Grammar state transition marker |

LINK marks boundary between monitoring and intervention phases.

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
