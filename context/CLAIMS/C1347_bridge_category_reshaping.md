# C1347: B Reshapes Bridge Category Usage

**Tier:** 2
**Scope:** cross-system
**Phase:** A_B_CATEGORY_FLOW (471)

## Constraint

Bridge MIDDLEs (85) carry the same category assignment in both systems (CategoryClassifier is system-agnostic), but B reshapes their USAGE frequency profile. A delivers a STAGING-heavy profile (25.0%); B consumes a THERMAL-heavy profile (23.7%). Four categories shift significantly: B amplifies THERMAL (1.72x), OPERATION (1.58x) and suppresses MONITORING (0.27x), STAGING (0.54x). Despite the reshaping, the profiles remain recognizably correlated (rho=0.64, JSD=0.026). Bridge consumption closely matches B's total category landscape (JSD=0.004), not A's delivery profile (JSD=0.026).

## Evidence

From a_b_category_flow.py tests T1 and T2 (85 bridge MIDDLEs, 82 with category assignments):

**Category profiles (bridge MIDDLEs only):**

| Category | A delivery | B consumption | Amplification |
|----------|-----------|---------------|---------------|
| THERMAL | 13.8% | 23.7% | **1.72x** |
| OPERATION | 9.7% | 15.3% | **1.58x** |
| FLOW | 17.3% | 20.1% | 1.16x |
| TRANSITION | 19.6% | 17.0% | 0.87x |
| CONTAINMENT | 5.3% | 5.4% | 1.01x |
| MARKING | 4.1% | 3.7% | 0.91x |
| STAGING | **25.0%** | 13.4% | **0.54x** |
| MONITORING | 5.3% | 1.4% | **0.27x** |

| Metric | Value |
|--------|-------|
| JSD(delivery, consumption) | 0.026 |
| JSD(delivery, B_total) | 0.028 |
| JSD(consumption, B_total) | 0.004 |
| Spearman rho(delivery, consumption) | 0.643 |

**Mode correlation (T2):** B folios with high bridge THERMAL fraction have significantly higher Mode A line proportion (0.503 vs 0.321, Mann-Whitney Z=3.45, p=0.0004).

## Interpretation

B does not passively consume what the bridge delivers. It amplifies the categories it needs for execution (THERMAL for escape/energy, OPERATION for procedural action) and suppresses categories that serve A's organizational purpose (STAGING for parameterization context, MONITORING for oversight). The near-zero JSD between consumption and B's total profile (0.004) means bridge consumption is perfectly integrated into B's category landscape — not a foreign import but a native component.

The mode correlation finding (Z=3.45) connects this to the suffix mode architecture: folios where the bridge delivers more THERMAL vocabulary run more Mode A lines, consistent with C1274 (THERMAL→escape) and C1279 (Mode A = THERMAL-enriched).

## Provenance

- a_b_category_flow.json: tests T1, T2
- Extends: C918 (A parameterizes B — now quantified: A delivers STAGING-heavy, B reshapes to THERMAL-heavy)
- Extends: C1264 (bridge category profile — now shown to shift between A and B usage)
- Extends: C1274 (THERMAL→escape — mode correlation confirms at folio level)
- Extends: C1279 (Mode A = THERMAL-enriched — bridge THERMAL delivery predicts mode composition)

## Status

CONFIRMED — B actively reshapes bridge category usage, amplifying THERMAL/OPERATION and suppressing STAGING/MONITORING (4 categories shift >1.5x or <0.67x).
