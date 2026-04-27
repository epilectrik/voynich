# Phase 664: CONFIRMED-Tier Paragraph Stratification

**Phase:** 664
**Status:** COMPLETE — VERDICT SUPPORTED with LOO safeguard passed
**Started:** 2026-04-26
**Pre-reg commit:** b9b16da

## Result

### T1: CONFIRMED vs supported-tier (predicted: CONFIRMED > supported)

| | n paragraphs | mean ke/ek |
|---|:---:|---:|
| CONFIRMED matches (f75r, f76r, f84r) | 12 | **9.74** |
| Supported-tier matches | 83 | 5.03 |

- Cohen's d = **+1.04** (large)
- p (predicted) = **0.0023**
- **Verdict: SUPPORTED**

### T2: corpus-wide sanity check (CONFIRMED vs all unmatched corpus paragraphs)

- CONFIRMED mean: 9.74 vs corpus mean: 4.68
- Cohen's d = +0.97
- p = 0.0057

CONFIRMED is elevated above BOTH supported tier AND corpus baseline — disambiguates the "supported-tier-below-average" interpretation.

### LOO safeguard (per expert-advisor, before registration)

Drop each CONFIRMED folio in turn, re-test:

| Drop | n | mean ke/ek | Cohen's d | p |
|---|:---:|---:|---:|---:|
| (full) | 12 | 9.74 | +1.04 | 0.0025 |
| Drop f75r | 9 | 8.80 | +0.92 | 0.0109 |
| Drop f76r | 8 | 10.55 | +1.21 | 0.0061 |
| Drop f84r | 7 | 10.04 | +1.09 | 0.0119 |

**All three LOO splits maintain d ≥ 0.8** (expert-advisor's threshold). Min d across LOO = +0.92. Effect is not carried by any single folio.

## Operational interpretation

`ke` within a token = k(HEAD heat) + e(MOD intensity-dampener) = **gentle/stabilized heat** (per atom system; see C1225 e-depth, C1394 HEAD+MOD model).

The 3 CONFIRMED matches all explicitly use balneum mariae operations in their Catalan recipes:
- f75r/III.19: aqua vitae distillation `en bany`
- f84r/II.14: gold dissolution `met al bany`
- f76r/II.18: element separation in controlled bath

Token-internal `ke` density on a folio appears to track **indirect/dampened thermal regime** — broader than balneum specifically, narrower than "any thermal."

## Methodological status

- **Pre-registered:** test methodology locked before run (commit b9b16da)
- **HARKing-mitigated:** T2 corpus-wide control isolates from selection-on-supported-tier
- **Selection-bias-bounded:** LOO safeguard confirms no single folio drives effect; CONFIRMED criteria did not directly include ke/ek
- **Small-N caveat:** 12 paragraphs across 3 folios; statistical significance achieved but inference is fundamentally about the 3 CONFIRMED matches
- **Both experts converged on Tier 3 registration** with tightly-scoped phrasing

## Constraint registered

C1970 (Tier 3): Token-internal ke pattern density tracks dampened/indirect thermal regime on CONFIRMED-tier matched folios. See `context/CLAIMS/C1970_ke_density_balneum_signature.md`.

## What this changes

- Cross-validates C1226 (ke/ek = process-context conditioning) with external Catalan recipe content
- Adds match-tier-stratification methodological lesson: future verb-corpus partition tests should restrict to CONFIRMED matches, since supported-tier dilutes signal
- Identifies token-internal `ke` as a folio-resolution signature for indirect-heat operations

## What this does NOT change

- C171 semantic ceiling holds (no specific token translated)
- C1969 (qok-density specificity for f75r ×9) unaffected
- Matched-pair table unchanged (no folio re-classified)
- Operational dictionary still cannot translate, only structurally cross-validate
