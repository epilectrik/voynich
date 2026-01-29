# LINE_LEVEL_LANE_VALIDATION

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C606-C608

## Purpose

Test whether the two-lane model (CHSH lane vs QO lane) operates at the line level, not just as an emergent folio-level pattern. Folio-level evidence was strong (C603: rho=0.345-0.355; C605: rho=-0.506). This phase asks: is it grammar or emergence?

## Scripts

| Script | Purpose |
|--------|---------|
| `line_lane_validation.py` | All 6 sections: routing, composition, coherence, escape, directionality, summary |

## Key Findings

### 1. CC->EN Line-Level Routing Confirmed (C606)

CC type predicts the immediately following EN subfamily within the same line:
- CC_OL_D -> QO at 1.67x enrichment (chi2=40.28, p<10^-6, V=0.246)
- Same-lane pairs sit closer: 1.81-1.83 tokens vs cross-lane 2.48-2.78 tokens
- 665 CC->next-EN pairs analyzed

### 2. Line-Level Escape Prediction 2.3x Stronger (C607)

EN_CHSH proportion predicts escape density much more strongly at line level:
- Line-level: rho=-0.707 (n=2240, p<10^-6)
- Folio-level: rho=-0.304 (C412)
- Escape density is fundamentally a LINE-level phenomenon; folio aggregation dilutes it

Lane balance also predicts at line level: rho=-0.363 (n=409, p<10^-6)

### 3. No Lane Coherence / Local Routing Mechanism (C608)

Lines do NOT specialize toward one subfamily:
- Coherence test: p=0.963 (observed 0.662 < null 0.672)
- Directionality: forward-reverse = -0.008, CI includes zero

The two-lane model operates via **local token routing** (CC triggers specific next EN), not through line-level lane identity. Lines mix freely.

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C606 | CC->EN Line-Level Routing | chi2=40.28, V=0.246, same-lane distance 1.81 vs cross-lane 2.78 |
| C607 | Line-Level Escape Prediction | rho=-0.707 (2.3x folio-level), escape is line-level phenomenon |
| C608 | No Lane Coherence / Local Routing | coherence p=0.963, directionality CI includes zero |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| voynich.py | scripts/ |

## Verification

- Total B lines: 2,420 (exact match)
- EN total: 7,211 (exact match to C573)
- Lines with both CC and EN: 743 (exact match)
- Mean tokens/line: 9.54
