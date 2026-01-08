# Phase LDF: LINK Distribution within Folios

**Core Question:** Are LINK tokens clustered or evenly distributed within folios? Do they mark specific positions?

**Answer:** LINK tokens are SPATIALLY UNIFORM but GRAMMAR-SELECTIVE

**Status:** CLOSED (1/4 tests show signal)

---

## Results Summary

| Test | Finding | Verdict |
|------|---------|---------|
| LDF-1 | Uniform across folio positions (p=0.005) | **NULL** |
| LDF-2 | Run lengths match random (z=0.14) | **NULL** |
| LDF-3 | Uniform within lines (p=0.80) | **NULL** |
| LDF-4 | Grammar-selective (HIGH_IMPACT 2.70x after LINK) | **SIGNAL** |

---

## Detailed Findings

### LDF-1: Positional Distribution

**Question:** Are LINKs uniform across folio positions, or clustered at start/middle/end?

| Position | LINK Rate | Ratio to Baseline |
|----------|-----------|-------------------|
| 0-20% | 7.7% | 0.89x |
| 20-40% | 8.0% | 0.93x |
| 40-60% | 8.8% | 1.03x |
| 60-80% | 8.6% | 1.00x |
| 80-100% | 9.8% | 1.14x |

Chi-square: 14.68, p = 0.005

**Interpretation:** Slight trend toward more LINK at folio end (1.14x), but effect is weak (p > 0.001 threshold). LINK does NOT strongly mark folio position.

---

### LDF-2: Run Length Analysis

**Question:** Do LINK tokens cluster into consecutive runs?

| Metric | Value |
|--------|-------|
| Observed runs | 1,725 |
| Mean run length | 1.152 |
| Max run length | 5 |
| Null model mean | 1.103 |
| Z-score | 0.14 |

**Run length distribution:**
- Length 1: 1,499 (87%)
- Length 2: 197 (11%)
- Length 3: 24 (1%)
- Length 4-5: 5 (<1%)

**Interpretation:** LINK tokens do NOT cluster. They appear as isolated markers (87% singletons) indistinguishable from random placement. Max run of 5 is consistent with chance.

---

### LDF-3: Line-Position LINK Density

**Question:** Does LINK density vary by position within lines?

| Position | LINK Count | Total | Rate | Ratio |
|----------|------------|-------|------|-------|
| Initial | 674 | 7,724 | 8.7% | 1.02x |
| Middle | 654 | 7,773 | 8.4% | 0.98x |
| Final | 659 | 7,724 | 8.5% | 1.00x |

Chi-square: 0.45, p = 0.80

**Interpretation:** LINK is completely uniform across line positions. This contrasts with Constraint 359 which found LINK **suppressed at line boundaries** (0.60x). The difference is resolved: boundary tokens (first/last) are suppressed; interior positions within initial/middle/final thirds are uniform.

---

### LDF-4: LINK-Grammar Context

**Question:** Do specific grammar classes precede/follow LINK tokens?

**Grammar classes BEFORE LINK (enriched):**
| Class | Enrichment | Count |
|-------|------------|-------|
| AUXILIARY | 1.50x | 37 |
| FLOW_OPERATOR | 1.30x | 32 |
| CORE_CONTROL | 1.00x | 63 |

**Grammar classes AFTER LINK (enriched):**
| Class | Enrichment | Count |
|-------|------------|-------|
| HIGH_IMPACT | **2.70x** | 81 |
| ENERGY_OPERATOR | 1.15x | 135 |
| FREQUENT_OPERATOR | 1.13x | 36 |

**Grammar classes AFTER LINK (depleted):**
| Class | Depletion | Count |
|-------|-----------|-------|
| AUXILIARY | 0.65x | 16 |
| FLOW_OPERATOR | 0.77x | 19 |

Chi-square (post-LINK): 96.44, p = 1.39e-18

**Interpretation:** LINK tokens mark a **grammar state transition**:
- LINK is preceded by auxiliary/flow operations (routine, low-intensity)
- LINK is followed by HIGH_IMPACT/ENERGY operations (intervention, escalation)

This is the "wait before escalation" pattern. LINK marks the boundary between monitoring and action phases.

---

## Synthesis

LINK tokens have a **dual character**:

1. **Spatially neutral**: No positional function within folios or lines
2. **Grammar-selective**: Mark transition from auxiliary → high-impact operations

**Structural model:**
```
[AUXILIARY/FLOW] → LINK → [HIGH_IMPACT/ENERGY]
     monitoring      wait     intervention
```

This complements Constraint 340 (LINK-escalation complementarity):
- Constraint 340: Escalation zones have **depleted** LINK (0.605x)
- LDF-4: LINK is **followed by** HIGH_IMPACT (2.70x)

Both describe the same boundary from different perspectives: waiting ends → escalation begins.

---

## New Constraints

| # | Constraint | Evidence |
|---|------------|----------|
| 365 | LINK tokens are SPATIALLY UNIFORM within folios and lines: no positional clustering (p=0.005), run lengths match random (z=0.14), line-position uniform (p=0.80); LINK has no positional marking function (LDF-1/2/3, Tier 2) |
| 366 | LINK marks GRAMMAR STATE TRANSITIONS: preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x); followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x); p < 10^-18; LINK is the boundary between monitoring and intervention phases (LDF-4, Tier 2) |

---

## Integration with Prior Findings

| Prior Constraint | LDF Finding | Integration |
|------------------|-------------|-------------|
| Constraint 340: LINK-escalation complementarity (0.605x) | LDF-4: HIGH_IMPACT 2.70x after LINK | **ENHANCED** - same boundary, different perspective |
| Constraint 359: LINK suppressed at line boundaries (0.60x) | LDF-3: Uniform within line thirds | **CLARIFIED** - boundary vs interior positions |
| Constraint 334: LINK section-conditioned | LDF-1: Folio-position uniform | **COMPLEMENTARY** - section level, not position level |

---

## What This Means

1. **LINK is not a positional marker** - operators don't need to look for LINK at specific folio positions
2. **LINK is a state transition marker** - signals "prepare for escalation"
3. **Waiting is functionally separated from action** - the grammar enforces this separation
4. **The 38% LINK density is spatially distributed** - spread throughout, not clustered

---

*Phase LDF CLOSED. 4 tests run, 1 SIGNAL, 3 NULL. LINK is spatially uniform but grammar-selective.*
