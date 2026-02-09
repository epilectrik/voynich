# C901: Extended e Stability Gradient

**Tier:** 2
**Scope:** A
**Phase:** TOKEN_ANNOTATION_BATCH_11

## Constraint

Extended e-sequences (e, ee, eee, eeee) form a stability depth gradient in Currier A. Frequency is inversely proportional to extension length. Quadruple-e (eeee) is extremely rare and concentrated in late Currier A folios.

## Evidence

From systematic annotation of 114 Currier A folios (1,272+ lines):

| Pattern | Folio Count | % of Corpus | Examples |
|---------|-------------|-------------|----------|
| ee (double) | Common | ~60% | podeesho, qoeeor, shesee |
| eee (triple) | 41 folios | 36% | oreeey, qoeeey |
| eeee (quadruple) | 11 folios | 9.6% | **odeeeey** (f102v2 L6) |

### Quadruple-e Distribution

Folios containing quadruple-e patterns:
- f100v, f101r1, f102v2 (late Currier A cluster)
- f21v, f25r, f27v, f87r, f89r2, f89v2, f93v, f99r

### Morphological Analysis

The token `odeeeey` (f102v2 L6) decomposes as:
- PREFIX: None (o-initial)
- MIDDLE: odeeee (4 consecutive e)
- SUFFIX: y (hub closure)

This represents maximum e-extension observed in the corpus.

## Interpretation

Per C105 (e = STABILITY_ANCHOR, 54.7% of recovery paths), extended e-sequences encode **stability depth**:

| Level | Interpretation | Corpus Frequency |
|-------|---------------|------------------|
| e | Standard stability | Very common |
| ee | Enhanced stability | Common |
| eee | Deep stability | Moderate (41 folios) |
| eeee | Maximum stability | Rare (11 folios) |

Materials or processes requiring **maximum stability assurance** (volatile aromatics, reactive compounds) may cluster at high e-extension values.

## Relationship to Kernel

The e-extension gradient operates as a **specification mechanism** orthogonal to the PP/RI distinction. While RI/PP classification determines registry role, e-extension may encode **operational requirements** for the specified entry.

## Provenance

- **Phase:** TOKEN_ANNOTATION_BATCH_11 (folio notes analysis)
- **Method:** Systematic token-by-token annotation of all 114 Currier A folios
- **Data:** data/folio_notes.json, data/token_dictionary.json
- **Date:** 2026-02-01

## Related

- C105: e = STABILITY_ANCHOR
- C521: Kernel directional asymmetry (stabilization is absorbing)
- C902: Late Currier A register characteristics
