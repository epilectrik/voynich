# Phase 683: Balneum Signature Retest with Corrected Methodology

**Status:** COMPLETE — pre-registered T1 FAILED on all 4 criteria
**Started:** 2026-05-04
**Goal:** Test whether C1970's underlying claim (CONFIRMED-tier matched folios have elevated indirect/dampened-thermal signature) is statistically supported with corrected methodology and expanded sample.

## Context

C1970 (Phase 664) was PERMANENTLY RETRACTED v6.37 per Phase 667. Original ke/ek RATIO showed d=+1.04, p=0.0023 — but the ratio metric was artifactual (unstable when denominator small). Corrected metric ke/(ke+ek) PROPORTION on the original 3-folio CONFIRMED set gave d=+0.256, p=0.24 (underpowered).

New visual evidence (rosettes_annotated.json: CENTER = multi-alembic balneum mariae, "strikingly similar to Brunschwig's woodcuts") motivated retesting whether the underlying claim is supported with:
1. Corrected metric ke/(ke+ek) proportion
2. Expanded sample (11 matched folios, not just 3 CONFIRMED)
3. Pre-registered design

Both experts validated the methodological principle: retractions are metric-specific, not claim-permanent. Pattern of C1966/C1967 re-registration applies if signal preserved at lower magnitude with corrected methodology.

## Pre-Registration (locked in PRE_REGISTRATION.md)

**T1 PRIMARY:** ke/(ke+ek) proportion per paragraph, Mann-Whitney one-tailed (matched > corpus). 

**Pass criteria (all four required):**
- Cohen's d ≥ 0.35
- p < 0.05
- LOO minimum d ≥ 0.20
- Permutation null p < 0.05

**Stopping rule:** if T1 fails, do NOT run T2/T3.

## Result: T1 FAILED on all 4 criteria

| Criterion | Threshold | Actual | Result |
|-----------|-----------|--------|--------|
| Cohen's d | ≥ 0.35 | +0.207 | **FAIL** |
| p (one-tailed) | < 0.05 | 0.257 | **FAIL** |
| LOO min d | ≥ 0.20 | +0.163 | **FAIL** |
| Permutation p | < 0.05 | 0.0547 | **FAIL** (borderline) |

**Numbers:**
- Matched mean ke/(ke+ek): 0.871 (n=84 paragraphs)
- Corpus mean: 0.817 (n=284)
- Cluster mean: 0.676 (n=62)

Crazy-expert's bet was "d=+0.30 to +0.40, marginally significant." Actual is even weaker.

## Verdict

Per pre-registration decision tree: **"T1 FAIL: workshop interpretation stays Tier 4 ceiling; underlying balneum signature claim NOT supported with corrected methodology."**

C1970 retraction is final. The underlying claim is not statistically distinguishable from chance even with the corrected metric and expanded 11-folio sample.

## Side Observation (NOT pre-registered, NOT registered)

Cluster vs corpus d = -0.45 (cluster significantly LOWER than corpus on ke proportion). Matched vs cluster d = +0.70 (matched dramatically higher than cluster). These were NOT the pre-registered comparisons; treating as evidence post-hoc would be exactly the C1970 mistake.

## Constraint Registered

### C1991 (Tier 1 falsification): C1970 underlying claim NOT supported with corrected methodology

Pre-registered Phase 683 retest of C1970's underlying claim ("CONFIRMED-tier matched folios have elevated indirect/dampened-thermal signature") with corrected metric ke/(ke+ek) proportion and expanded sample (11 matched folios, n=84 paragraphs vs corpus n=284). Failed all 4 pre-registered criteria: d=+0.207 (req ≥0.35), p=0.257 (req <0.05), LOO min d=+0.163 (req ≥0.20), perm p=0.0547 (req <0.05). C1970 retraction final; underlying balneum text-signature claim is not statistically distinguishable from chance even with corrected methodology. Workshop-diagram interpretation cannot lean on body-text balneum signature as anchor evidence.

**Tier:** 1 (Currier B paragraph-level, falsification of underlying claim)

## Methodological Note

Both experts confirmed that retractions are metric-specific, not claim-permanent. This phase tested whether the corrected methodology preserves the underlying signal (as in C1966/C1967 pattern). It does not. Direction is preserved (matched > corpus on ke proportion) but magnitude is too small for registration.

The user's instinct to challenge a retracted constraint when new evidence emerges was methodologically sound. The test was valid; the result simply confirmed the retraction was correct on substantive grounds, not just methodological grounds.

## Scripts

- `s1_balneum_retest.py` — pre-registered Mann-Whitney + LOO + permutation null

## Relationship to Existing Constraints

- **C1970 (RETRACTED v6.37):** Phase 683 retest with corrected methodology fails. Retraction final.
- **C1972** (Phase 668: e-depth tracks Brunschwig fire-degree across 15 matched folios): UNAFFECTED. Different metric, different methodology. C1972 stands.
- **C1225** (e-depth = thermal dampening): NOT tested in this phase (would be T2 secondary, not run per stopping rule)
- **C897** (FL TERMINAL state markers): UNAFFECTED. C897's state-encoding via terminals is on different morphology.
