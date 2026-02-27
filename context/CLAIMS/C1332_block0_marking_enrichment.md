# C1332: Block-0 Marking Enrichment

**Tier:** 2
**Scope:** B (all sections)
**Phase:** MULTIPLEXED_PROCEDURE_TEST (467)

## Constraint

MIDDLEs unique to block 0 (appearing in the first block but no later block on the same folio) have a categorically distinct profile from shared MIDDLEs and later-block-unique MIDDLEs. Block-0-unique vocabulary is MARKING-enriched (2.48x vs shared) and MONITORING-enriched (1.57x), while depleted in OPERATION (0.65x) and TRANSITION (0.64x).

STAGING and CONTAINMENT are NOT enriched in block-0-unique vocabulary (ratio 0.92x), falsifying the "setup block" prediction.

## Evidence

From multiplexed_procedure_test.py test M1:

**3-pool comparison (block0_unique / shared / later_unique):**

| Category | Block-0-unique | Shared | Later-unique | B0U/Shared |
|----------|---------------|--------|-------------|------------|
| MARKING | 25.0% | 10.1% | 23.3% | **2.48x** |
| MONITORING | 4.5% | 2.9% | 5.1% | **1.57x** |
| THERMAL | 18.2% | 18.8% | 19.4% | 0.97x |
| STAGING | 12.5% | 12.7% | 12.4% | 0.98x |
| CONTAINMENT | 5.0% | 6.3% | 4.8% | 0.80x |
| FLOW | 16.8% | 21.3% | 15.4% | 0.79x |
| OPERATION | 7.9% | 12.2% | 9.5% | **0.65x** |
| TRANSITION | 10.1% | 15.8% | 10.2% | **0.64x** |

**Statistics:**
- Chi-squared: 212.32, p < 0.001
- Cramér's V: 0.136
- Pool sizes: block-0-unique=760, shared=1,895, later-unique=3,053
- Sections passing (p<0.01, V>0.10): 3/3 major sections

## Interpretation

Block 0 is NOT a "setup" block (STAGING/CONTAINMENT flat). It is a **marking/annotation context block**: its unique vocabulary provides operational flags, annotations, and monitoring specifications that later blocks don't need to repeat. The actual process work (OPERATION, TRANSITION) is shared across all blocks — every block does the operational work, but only block 0 annotates the full operational context.

This is consistent with the first block documenting "what to watch for, what to note, what to flag" while later blocks focus on execution. Connects to C1287 (paragraph headers are MARKING-enriched) — the marking specification concentrates at the start.

## Provenance

- multiplexed_procedure_test.json: test M1, overall and section_breakdown
- Relates to: C1287 (paragraph header MARKING enrichment), C1318 (block PREFIX complementarity), C1330 (vocabulary narrowing)

## Status

CONFIRMED — block-0-unique vocabulary is MARKING/MONITORING-enriched, not STAGING/CONTAINMENT-enriched.
