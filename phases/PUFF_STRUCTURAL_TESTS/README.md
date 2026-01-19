# PUFF_STRUCTURAL_TESTS

**Phase Type:** Exploratory
**Status:** COMPLETE
**Date:** 2026-01-19

---

## Purpose

Test whether improved AZC and Currier A understanding enables new Puff-Voynich structural linkages beyond the existing curriculum-level alignment (10/11 prior tests pass).

## Expert Consultation

Expert-advisor prioritized tests:
1. **T7 (Data Audit)** - Prerequisite
2. **T4 (Category -> PREFIX)** - Highest discriminating potential
3. **T8 (Complexity -> Cluster)** - Cognitive interface test
4. **T9 (Danger -> HT)** - Constraint substitution test

Expert also flagged:
- **T3 (Organ -> Zone):** SKIP - Too close to semantic encoding (C171, C469 risk)

## Tests Executed

| Test | Script | Result |
|------|--------|--------|
| T7 | `puff_data_audit.py` | Clean data sufficient |
| T4 | N/A (constrained) | Weak A-B linkage prevents test |
| T9 | `t9_danger_ht_correlation.py` | **FAIL** |
| T8 | `t8_complexity_breadth.py` | **FAIL** |

## Key Findings

1. **T9:** Dangerous Puff materials do NOT have elevated HT (effect reversed)
2. **T8:** Complex Puff positions do NOT have larger vocabulary (effect reversed)
3. **T4:** A-B linkage too weak (29% vs 25% baseline) for meaningful test

## Conclusion

Puff-Voynich relationship has reached **evidential ceiling**:
- Curriculum alignment: ESTABLISHED
- Structural linkage: NOT FOUND
- Further testing: Would require prohibited semantic interpretation

## Files

- `puff_data_audit.py` - T7 data quality audit
- `t9_danger_ht_correlation.py` - T9 danger-HT test
- `t8_complexity_breadth.py` - T8 complexity-breadth test
- `PUFF_STRUCTURAL_TESTS_REPORT.md` - Full report

## Results

See `results/puff_*.json` for detailed test outputs.
