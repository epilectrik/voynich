# C1279: Mode A/B Lines Differ by Category

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

Mode A and Mode B lines (C1231 suffix classification) have statistically distinct category compositions. Chi2=536.7, V=0.153, p<0.001. Mode A lines are THERMAL-enriched (28.9% vs 19.9%, ratio 1.45) and MONITORING-enriched (2.3% vs 1.1%, ratio 2.19). Mode B lines are TRANSITION-enriched (17.4% vs 11.3%, ratio 0.65) and STAGING-enriched (14.3% vs 10.8%, ratio 0.76). 1,035 Mode A lines, 1,371 Mode B lines.

## Architecture

- **Mode A = escape-capable vocabulary.** Combined with C1277 (THERMAL→qo→escape), Mode A lines inject THERMAL vocabulary that gets routed through escape-permissive PREFIX. C1256's "specification injection" is categorically: injecting thermal/escape-capable MIDDLEs.
- **Mode B = transition-dominated continuity.** C1256's "continuity" track is TRANSITION-enriched, which C1277/C5 show is escape-restrictive through a PREFIX-independent mechanism. Mode B maintains the operational baseline.
- **Extends C1230.** C1230 established Mode A = k-family 1.62x enriched. Now we know this maps to THERMAL category (k=heat). C1279 extends beyond the kernel axis: MONITORING, STAGING, FLOW also differentiate modes.

## Key Findings

| Category | Mode A | Mode B | Ratio |
|----------|--------|--------|-------|
| THERMAL | 0.289 | 0.199 | 1.45 |
| MONITORING | 0.023 | 0.011 | 2.19 |
| MARKING | 0.091 | 0.069 | 1.33 |
| OPERATION | 0.160 | 0.144 | 1.11 |
| TRANSITION | 0.113 | 0.174 | 0.65 |
| STAGING | 0.108 | 0.143 | 0.76 |
| FLOW | 0.170 | 0.211 | 0.81 |

## Provenance

- Extends C1230 (suffix mode MIDDLE differentiation) with category dimension
- Extends C1256 (opener mode selection) with category mechanism
- Connects C1277 (THERMAL escape mediation) to mode architecture
