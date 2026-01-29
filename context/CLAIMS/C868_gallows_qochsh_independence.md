# C868: Gallows-QO/CHSH Independence

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Gallows type and EN subfamily (QO vs CHSH) are independent axes. Gallows explains only 0.3% of QO rate variance. All gallows types have similar QO/CHSH profiles.

## Evidence

### QO Rates by Gallows

```
Gallows   QO Rate   CHSH Rate   QO/CHSH
p          44.3%      55.7%       0.80
t          45.7%      54.3%       0.84
k          45.8%      54.2%       0.84
f          41.0%      59.0%       0.69
```

All gallows types have QO rates between 41-46%.

### Variance Decomposition

```
Total QO rate variance: 0.0326
Variance explained by GALLOWS: 0.0001 (0.3%)
Variance explained by ORDINAL: 0.0003 (1.0%)
```

Neither gallows nor ordinal strongly predicts QO/CHSH.

## Interpretation

Gallows and QO/CHSH represent orthogonal control dimensions:
- **Gallows**: Procedure type (what kind of paragraph)
- **QO/CHSH**: Operational mode (energy input vs stabilization)

These can be combined freely - any gallows can use any EN subfamily.

## Alignment with Existing Constraints

Consistent with:
- C574: QO/CHSH grammatically equivalent but lexically partitioned
- C577: EN interleaving is content-driven, not positional
- C608: No lane coherence at line level

## Provenance

- Script: `12_gallows_qo_ch_correlation.py`
- Data: `gallows_qo_ch_correlation.json`

## Related

- C864-C867 (gallows findings)
- C574 (EN distributional convergence)
- C863 (paragraph-ordinal EN gradient)
