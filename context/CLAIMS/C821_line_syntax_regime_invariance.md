# C821: Line Syntax REGIME Invariance

## Constraint

Line-level execution syntax (SETUP->WORK->CHECK->CLOSE per C556) is **INVARIANT across all four REGIMEs**. No role shows significant positional variation by REGIME.

This CONFIRMS C124 (grammar universality) - REGIME encodes execution requirements (what to do), not syntax structure (how to organize instructions).

## Evidence

### Role Positions by REGIME (Kruskal-Wallis tests)

| Role | REGIME_1 | REGIME_2 | REGIME_3 | REGIME_4 | H | p | Verdict |
|------|----------|----------|----------|----------|---|---|---------|
| CC | 0.488 | 0.434 | 0.466 | 0.499 | 2.81 | 0.42 | INVARIANT |
| EN | 0.487 | 0.479 | 0.476 | 0.479 | 1.94 | 0.59 | INVARIANT |
| FL | 0.573 | 0.548 | 0.584 | 0.603 | 2.91 | 0.41 | INVARIANT |
| FQ | 0.551 | 0.561 | 0.573 | 0.560 | 1.98 | 0.58 | INVARIANT |
| AX | 0.486 | 0.492 | 0.507 | 0.482 | 2.03 | 0.57 | INVARIANT |

**All 5 roles show p > 0.4** - no significant REGIME effect.

### Variance Decomposition (eta-squared)

| Role | eta^2 | % Variance |
|------|-------|------------|
| CC | 0.0028 | 0.28% |
| EN | 0.0003 | 0.03% |
| FL | 0.0024 | 0.24% |
| FQ | 0.0008 | 0.08% |
| AX | 0.0005 | 0.05% |
| **Mean** | **0.0013** | **0.13%** |

Compare to C815: PHASE explains 1.5% of position variance.
REGIME explains 0.13% - **11x less than PHASE itself**.

## Interpretation

REGIME determines WHAT operations to perform (class enrichment per C545):
- REGIME_1: ENERGY-heavy, qo-concentrated
- REGIME_2: FREQUENT/FLOW-heavy
- REGIME_3: CORE_CONTROL-heavy (1.83x)
- REGIME_4: Balanced, precision mode

But REGIME does NOT determine WHERE in the line operations appear.
The SETUP->WORK->CHECK->CLOSE template is universal.

This separation confirms REGIME is an **execution requirements axis**, not a procedural variation axis.

## Provenance

- Phase: REGIME_LINE_SYNTAX_INTERACTION
- Scripts: t1-t6 (comprehensive testing)
- Related: C124 (grammar universality), C556 (line syntax), C545 (REGIME class profiles)

## Tier

2 (Validated Finding - NULL result confirming universality)
