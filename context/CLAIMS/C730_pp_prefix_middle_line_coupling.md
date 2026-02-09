# C730: PP PREFIX-MIDDLE Within-Line Coupling

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

Within Currier A lines, the PREFIX of one PP token is correlated with the MIDDLE of another PP token on the same line. This cross-token PREFIX-MIDDLE coupling exceeds shuffled baselines.

> **Aggregation Note (2026-01-30):** This constraint analyzes within-line structure.
> Line-level patterns describe A-internal morphological structure. For A-B vocabulary
> correspondence, the operational unit is the A FOLIO (114 units, 81% coverage per C885).

| Metric | Value |
|--------|-------|
| Within-line MI(PREFIX; MIDDLE) | 0.1330 |
| Null MI (shuffled) | 0.1207 +/- 0.0019 |
| Between-line MI (different lines, same folio) | 0.0477 |
| MI ratio (within/between) | 2.79x |
| p (within > null) | < 0.001 |
| Cross-token pairs analyzed | 53,724 |

The observed within-line MI (0.133) exceeds all 1,000 shuffled values (max ~0.125). The between-line baseline (0.048) is much lower because it compares across different lines where the PREFIX-MIDDLE mapping varies more.

## Implication

PP tokens sharing a line have coordinated PREFIX-MIDDLE combinations — specific PREFIXes tend to co-occur with specific MIDDLEs of neighboring tokens. The effect is small in absolute terms (0.133 vs 0.121, delta ~0.012 bits) but highly significant.

**Caveat:** This coupling may be partially mediated by MIDDLE incompatibility (C475/C728). If incompatible MIDDLEs carry systematically different PREFIXes, then incompatibility-driven line composition would produce apparent PREFIX-MIDDLE coupling as a secondary effect. The shuffle breaks incompatibility structure, which alone could explain the MI excess.

This finding is consistent with PREFIX being a structural property that participates in the compatibility system (C697: PREFIX clusters non-randomly within lines).

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_dimension_tests.py` (T4)
- Consistent with: C697 (PREFIX clustering within lines), C475 (MIDDLE incompatibility)
- Extends: C267 (morphological decomposition), C660-C663 (PREFIX-MIDDLE selectivity)
