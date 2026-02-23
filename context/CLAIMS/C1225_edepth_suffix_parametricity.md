# C1225 - E-depth Suffix Parametricity

**Tier:** 2 | **Scope:** B | **Phase:** KE_THERMAL_CYCLING_VALIDATION (Phase 437)

## Statement

Within ke-family MIDDLEs (ke, ek, kee, eek, eke, keee+), e-count fundamentally restructures suffix grammar. Single-e tokens (ke, ek; n=590) use -edy 64% and -y 14%; multi-e tokens (kee, eek, eke, keee+; n=102) use -edy 12% and -y 37% (chi-squared p<0.0001). E-depth is a parametric axis that modulates output specification, not noise.

## Evidence

### Suffix distribution by e-depth (chi-squared p < 0.0001)

| Suffix | Single-e (n=590) | Multi-e (n=102) |
|--------|-------------------|-----------------|
| -edy   | 368 (62.4%)       | 12 (11.8%)      |
| -y     | 80 (13.6%)        | 36 (35.3%)      |
| -s     | 0                 | 13 (12.7%)      |
| -or    | 14 (2.4%)         | 9 (8.8%)        |
| -ar    | 15 (2.5%)         | 8 (7.8%)        |
| -ain   | 17 (2.9%)         | 6 (5.9%)        |
| -eey   | 39 (6.6%)         | 4 (3.9%)        |

### Key observations

1. **-edy dominance collapses**: 62.4% → 11.8% — the default closure for single-e ke-family is overwhelmingly -edy, but multi-e tokens diversify dramatically
2. **-y rises**: 13.6% → 35.3% — bare -y closure becomes the primary multi-e suffix
3. **-s appears**: Absent in single-e, 12.7% in multi-e — a suffix exclusive to deeper e-stacks
4. **Suffix entropy increases**: Multi-e tokens distribute across more suffix categories

### E-depth does NOT vary by REGIME or section

- E-depth × REGIME: chi-squared p=0.620 (NS)
- E-depth × section: chi-squared p=0.067 (NS, marginal)
- E-depth encodes a MIDDLE-internal parameter, not a context-dependent one

## Interpretation

E-depth within ke-family tokens functions as a graded parameter that changes what the token specifies as output. The suffix restructuring demonstrates that single-e and multi-e ke-family tokens are not variants of the same instruction — they are different instruction types within the same family.

What the graded parameter ENCODES (e.g., duration, intensity, repetition count) cannot be determined from structural evidence alone. The parametric nature is structural; the semantic domain is interpretive.

## Related constraints

- C1197: e extensible atom forming ratio families (ke/kee/keee)
- C901: Extended e stability gradient
- C521: k→e 4.32× elevated (one-way valve toward stability)
- F-BRU-014: Vowel primitive suffix saturation

## Provenance

- `phases/KE_THERMAL_CYCLING_VALIDATION/scripts/ke_thermal_test.py` (T7)
- `phases/KE_THERMAL_CYCLING_VALIDATION/results/ke_thermal_results.json`
