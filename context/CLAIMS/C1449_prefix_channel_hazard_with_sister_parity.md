# C1449: PREFIX Channel Hazard with Sister Pair Parity

**Tier:** 2
**Scope:** B, PREFIX, hazard, sister pair, ch, sh, ok, ot, channel, C109, C929, C1298, C1299
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

PREFIX channels show wide hazard variation (3.33% ct to 73.02% do) but sister pairs show remarkably similar hazard rates: ok/ot ratio 1.04x (32.11% vs 30.73%), ch/sh ratio 1.29x (12.77% vs 9.88%). Sister choice is NOT a hazard-modulation mechanism. Actual forbidden pair violations concentrate in 6 PREFIXes: ch (5/11 = 45%), sh (2), kch (1), lch (1), ol (1), te (1). qo confirmed as safe channel at 17.77% (below 25.5% corpus average).

## Evidence

### PREFIX hazard rates (top 5 and bottom 3)

| PREFIX | N tokens | Hazard rate |
|--------|----------|------------|
| do | 337 | 73.02% |
| so | 63 | 52.38% |
| ko | 48 | 52.08% |
| to | 316 | 49.57% |
| BARE | 2,680 | 43.97% |
| sh | 3,150 | 9.88% |
| lsh | 58 | 6.90% |
| ct | 60 | 3.33% |

### Sister pair analysis

| Pair | Rate 1 | Rate 2 | Ratio | Gap |
|------|--------|--------|-------|-----|
| ch vs sh | 12.77% | 9.88% | 1.29x | 2.89pp |
| ok vs ot | 32.11% | 30.73% | 1.04x | 1.38pp |

### Forbidden violation distribution by PREFIX

| PREFIX | Violations | % of total |
|--------|-----------|------------|
| ch | 5 | 45.5% |
| sh | 2 | 18.2% |
| kch | 1 | 9.1% |
| lch | 1 | 9.1% |
| ol | 1 | 9.1% |
| te | 1 | 9.1% |

### Hazard channel structure

- o-modifier PREFIXes (do, so, ko, to) have the highest hazard rates (49-73%)
- BARE tokens (no PREFIX) are high-hazard (44.0%)
- ch/sh family is low-hazard (9.9-12.8%)
- qo is moderate-low (17.8%), confirming C601 (QO lane zero hazard participation)

## Interpretation

Sister pairs modulate precision/tolerance (C929) orthogonally to hazard. ch carries slightly more risk than sh (1.29x), consistent with ch's active-test role having marginal additional risk, but the gap is small (2.89pp). ok/ot are essentially identical in hazard (1.04x). Hazard is determined by the MIDDLE content (via HEAD/TERMINAL atoms), not by the PREFIX channel. The PREFIX creates the operational context; the MIDDLE carries the hazard or safety.

## Falsification Criteria

1. If ok/ot hazard ratio exceeds 1.5x or drops below 0.67x
2. If ch/sh hazard ratio exceeds 2.0x

## Method

- 23,096 clean Currier B tokens grouped by PREFIX
- Hazard = FLOW + CONTAINMENT categories (C1280)
- Sister pair rates compared directly
- Forbidden violations (11 total) attributed to PREFIX of source token

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions)
- C601 (QO lane zero hazard participation)
- C929 (ch/sh sensory modality discrimination)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1298 (ok-ot category divergence)
- C1299 (ch-sh B-specific category divergence)
