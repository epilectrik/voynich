# HT Line-Type Annotation System - Analysis Report

**Phase:** Exploratory
**Corpus:** Currier B (75,401 tokens, 8,124 lines)
**Date:** 2026-01-09

---

## Executive Summary

Line-initial Human Track (HT) tokens function as a **LINE TYPE ANNOTATION SYSTEM** in the Voynich Manuscript's Currier B text. Different HT prefixes predict different grammatical patterns within lines with extremely high statistical significance.

### Key Statistics

| Metric | Value |
|--------|-------|
| Total B lines | 8,124 |
| HT-initial lines | 2,720 (33.5%) |
| Chi-square (HT vs grammar) | 933.9 (p < 10^-145) |
| Chi-square (HT vs 2nd token) | 508.5 (p < 10^-63) |
| Chi-square (HT vs suffix) | 299.0 (p < 10^-46) |
| Within-type similarity | 0.274 vs 0.250 between-type (p=0.004) |

---

## HT Prefix Inventory

### Major HT Prefixes (n >= 30)

| Prefix | Count | Avg Length | Primary Second Token |
|--------|-------|------------|---------------------|
| SA | 509 | 9.1 | SH (24%), CH (19%) |
| SO | 411 | 9.0 | SH (30%), CH (16%) |
| PCH | 339 | 10.1 | SH (20%), CH (11%) |
| YCHE | 282 | 8.9 | CH (18%), L_OP (13%) |
| YK | 223 | 9.1 | CH (24%), ESCAPE (13%) |
| DCH | 218 | 9.1 | CH (18%), ESCAPE (17%) |
| YT | 198 | 9.3 | CH (15%), ESCAPE (13%) |
| YSH | 195 | 9.3 | QO (18%), ESCAPE (12%) |
| PSH | 77 | 9.8 | SH (19%), O_OTHER (18%) |
| Y (bare) | 72 | 9.2 | SH (38%), CH (32%) |

---

## Line-Type Dictionary

### CORE CONTROL Lines

**Y (bare)** -> CORE_CONTROL_BOUNDARY
- Second token: 70% SH/CH combined (2x baseline)
- Function: Marks major control flow boundaries
- Very high density of core control operators

**YCHE** -> CH_CONTROL + L_COMPOUND_ENTRY
- CH enriched 1.28x
- L_OP in second position: 13.2% (3.6x baseline)
- Function: Core CH-family control blocks with L-compound invocation

**YK** -> CH_DOMINANT_GENERAL
- CH enriched, QO/SH depleted
- Moderate escape rate
- Function: General CH-phase control

### SH-PHASE Lines

**SA** -> SH_PHASE + LINK_HEAVY
- LINK enriched 2.2x, SH high
- ar/or nucleus enriched 1.6x
- Function: SH-phase blocks with waiting periods

**SO** -> SH_PHASE + RECOVERY
- SH enriched 1.45x
- ESCAPE enriched 1.25x, LINK enriched 1.41x
- Function: SH-phase blocks with recovery potential

### INTERVENTION Lines

**DCH** -> INTERVENTION + RECOVERY
- Kernel-heavy suffixes enriched 1.18x
- ESCAPE in second position: 17.1% (1.9x baseline)
- Function: Active intervention with recovery procedures

**PSH** -> HIGH_INTERVENTION
- Kernel-heavy suffixes: 45% (1.27x baseline)
- LINK nearly zero (0.1x baseline)
- o_OTHER in second position: 5.8x enriched
- Function: Maximum-intensity intervention blocks

### EXTENDED EXECUTION Lines

**PCH** -> EXTENDED_EXECUTION
- Longest avg length: 10.1 tokens
- QO enriched 1.47x
- LINK depleted 0.69x
- Function: Substantial procedure blocks

### STEADY-STATE Lines

**YT** -> STEADY_STATE
- ESCAPE depleted 0.66x (lowest escape rate: 7%)
- DA/OT enriched ~1.4x
- L_OP depleted 0.35x
- Function: Stable-phase execution

**YSH** -> SH_PHASE_STEADY
- QO enriched 3.0x in second position
- Kernel-light suffixes enriched (monitoring)
- Function: Steady SH-phase operations

---

## Second-Token Prediction Rules

The HT prefix predicts the grammar category of the immediately following token:

### High SH-following
- **Y (bare)**: 38% SH
- **SO**: 30% SH
- **SA**: 24% SH

### High CH-following
- **Y_OTHER**: 34% CH
- **YK**: 24% CH
- **YCHE**: 18% CH

### High ESCAPE-following
- **Y_OTHER**: 29% ESCAPE
- **DCH**: 17% ESCAPE
- **YK**: 13% ESCAPE

### High L_OP-following
- **YCHE**: 13% L_OP (l-compound operators lk, lch, lsh)

### High QO-following
- **YSH**: 18% QO

---

## Functional Interpretation

The HT line-type system encodes:

1. **Grammar family bias**: Whether the line is SH-dominant, CH-dominant, or QO-dominant
2. **Intervention level**: Kernel-heavy (intervention) vs kernel-light (monitoring) suffix ratio
3. **Recovery expectation**: Presence of qok- escape tokens
4. **Waiting phases**: LINK token density
5. **Execution scope**: Line length (short boundary markers vs long procedure blocks)

### Proposed Function

HT prefixes serve as a **PARALLEL NAVIGATION SYSTEM** for human operators:

- Mark line types to facilitate manual tracking of program state
- Indicate what kind of control block is coming
- Signal whether intervention, monitoring, or recovery is expected
- Synchronized to procedural phase (consistent with C348)

This is NOT random scribal activity. The statistical relationships are too strong (p < 10^-145) and too consistent across the corpus.

---

## Grammar Baseline (HT-initial lines)

| Category | Percentage |
|----------|-----------|
| ch_CONTROL | 16.8% |
| qok_ESCAPE | 11.2% |
| sh_CONTROL | 9.5% |
| ok_ENERGY | 7.1% |
| qo_ENERGY | 6.6% |
| ot_ENERGY | 6.4% |
| LINK | 4.5% |
| da_INFRA | 4.2% |
| l_COMPOUND | 3.7% |
| y_INLINE | 2.9% |
| ar_or_NUCLEUS | 3.7% |
| OTHER | 30.0% |

---

## Suffix Baseline

| Type | Percentage | Interpretation |
|------|-----------|----------------|
| NEUTRAL | 44.9% | General execution |
| HEAVY | 35.5% | Intervention phase |
| LIGHT | 17.3% | Monitoring phase |
| TERMINAL | 2.3% | Line-final markers |

---

## Constraints Supported

This analysis supports:

- **C348**: HT phase synchrony (V=0.136, p<0.0001)
- **C347**: Disjoint HT prefix vocabulary
- **C413**: HT prefix phase-class predicted by grammar (V=0.319)

And suggests new constraint:

- **C414 (proposed)**: HT line-initial prefix predicts line grammar content (Chi2=934, p<10^-145)

---

## Relationship to Existing HT Findings

The line-type annotation system is **consistent with** but **extends** prior findings:

| Prior Finding | This Analysis |
|---------------|---------------|
| HT is non-operational (C404-406) | Line-type markers don't affect execution |
| HT phase synchrony (C348) | Line types encode procedural phase |
| Disjoint prefix vocabulary (C347) | Line-type prefixes are HT-specific |
| Calligraphy practice (Tier 4) | Line-type marking could be training |

---

## Next Steps

1. Validate line-type predictions against folio-level program taxonomy
2. Test whether line-type sequences follow patterns (e.g., RECOVERY after INTERVENTION)
3. Map line-type distribution across waiting profile categories

---

*Report generated from `phases/exploration/ht_line_type_*.py` scripts*
