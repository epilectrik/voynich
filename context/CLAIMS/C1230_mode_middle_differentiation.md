# C1230 - Suffix Mode MIDDLE Differentiation

**Tier:** 2 | **Scope:** B | **Phase:** EXTRACTION_CYCLING_VALIDATION (Phase 439)

## Statement

The two alternating suffix modes within paragraphs (C1229) correspond to distinct MIDDLE family compositions. Mode A (terminal-heavy/specification) has 1.62x k-family MIDDLEs (p<0.000001), 2.86x preparation-tier MIDDLEs (p=0.000034), and 1.48x qo-PREFIX (p<0.000001). Mode B (bare-heavy/continuation) has elevated e-family MIDDLEs (0.824x ratio, p=0.000256). The suffix mode distinction is functionally grounded at the MIDDLE and PREFIX level, not just morphological.

## Evidence

### MIDDLE family by mode (55 paragraphs with 8+ body lines, 285 Mode A lines, 350 Mode B lines)

| MIDDLE family | Mode A mean | Mode B mean | A/B ratio | p-value |
|--------------|-------------|-------------|-----------|---------|
| k-family (k, ke, kch, ksh, ek) | 0.212 | 0.132 | 1.615 | <0.000001 |
| e-family (e, ey, edy, eey, eok) | 0.198 | 0.241 | 0.824 | 0.000256 |
| prep-family (tch, pch, lch, dch, te, ksh) | 0.022 | 0.008 | 2.855 | 0.000034 |

### PREFIX enrichment by mode

| PREFIX domain | Mode A mean | Mode B mean | A/B ratio | p-value |
|--------------|-------------|-------------|-----------|---------|
| Energy (qo) | 0.260 | 0.176 | 1.476 | <0.000001 |
| Vessel (ok, ot, ol) | 0.161 | 0.148 | 1.091 | 0.229 |
| Process (ch, sh) | 0.235 | 0.261 | 0.902 | 0.020 |

### Key observations

1. **Mode A = energy + mechanical specification**: k-family MIDDLEs (thermal operations) and prep MIDDLEs (agitation/mechanical processing) both concentrate in the terminal-heavy specification mode
2. **Mode B = equilibration/continuation**: e-family MIDDLEs (equilibration) concentrate in the bare-heavy continuation mode
3. **PREFIX partially but not fully differentiates**: qo (ENERGY) is significantly enriched in Mode A, but vessel/process PREFIXes do NOT shift to Mode B
4. **Partially lane-expressed**: QO-fraction correlates with suffix mode at r=0.256 — modes are partially about QO/CHSH lane oscillation but not reducible to it

## Interpretation

The two alternating modes represent distinct operational phases within the extraction process:
- **Mode A**: Apply energy and mechanical processing, specify parameters for the current pass (agitate/re-spec)
- **Mode B**: Let the process equilibrate and run, passive extraction continues (run/stabilize)

The prep MIDDLE enrichment (2.86x) in Mode A supports the interpretation that mechanical operations (agitation, grinding) are part of the active specification phase, not separate from energy application. The same mechanical verbs serve different positional purposes (C933 front-loading for material preparation early; Mode A enrichment for agitation/respecification throughout).

## Related constraints

- C1229: Two alternating suffix modes (k=2, silhouette 0.459, 80% interleaved)
- C1225: E-depth suffix parametricity (multi-e restructures output)
- C1226: ke/ek ratio process conditioning (REGIME and section dependent)
- C932: Body vocabulary gradient (terminal r=-0.89, bare r=+0.90)
- C911: PREFIX-MIDDLE selectivity (qo selects k-family at 4.6x)

## Provenance

- `phases/EXTRACTION_CYCLING_VALIDATION/scripts/extraction_cycling_test.py` (T1, T2, T3)
- `phases/EXTRACTION_CYCLING_VALIDATION/results/extraction_cycling_results.json`
