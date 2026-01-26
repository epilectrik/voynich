# C565: AUXILIARY Execution Scaffold Function

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED (re-verified 2026-01-26 with 19 AX classes)

## Claim

AUXILIARY provides a positionally ordered execution scaffold that mirrors the named role structure but carries no functional semantics. AX is the "connective tissue" of the grammar.

## Evidence

### Role Comparison

| Property | Named Roles | AX Sub-Roles |
|----------|-------------|--------------|
| Initial bias | CC (daiin 27.7%) | AX_INIT (25.4%) |
| Medial concentration | EN (C556) | AX_MED (neutral) |
| Final bias | FL (up to 59.7%) | AX_FINAL (34.6%) |
| Hazard involvement | EN/FL have hazard classes | AX: **0% across all sub-groups** |
| ENERGY triggering | CC triggers EN (C557) | AX_INIT does NOT trigger EN |
| Flow semantics | FL redirects flow (C562) | AX_FINAL closes frames only |
| Self-chaining | EN 2.38x, FL 2.11x (C550) | AX 1.10x (barely above random) |

### Key Properties

1. **Zero hazard involvement**: All 19 AX classes are structurally safe. No AX class appears in any forbidden transition (C109). This is absolute across all sub-groups.

2. **Flat transition grammar**: AX -> any role enrichment is 0.95-1.19x (near-random). AX does not preferentially connect to any specific role. This is unique -- EN, FL, CC all have strong transition preferences (C550).

3. **Weak self-chaining**: AX -> AX enrichment = 1.10x (barely above random). Compare EN -> EN = 2.38x (C550). AX is not "clumpy" -- it's uniformly distributed.

4. **Structural framing without semantic commitment**: AX_INIT opens frames but doesn't trigger ENERGY chains (unlike CC/daiin which has 47.1% ENERGY followers per C557). AX_FINAL closes frames but doesn't redirect flow (unlike FL which has terminal bias per C562).

### Section/REGIME Sensitivity

| Sub-Group | REGIME_1 | BIO | Interpretation |
|-----------|----------|-----|----------------|
| AX_INIT | 34.1% (baseline) | 30.1% | Neutral scaffold |
| AX_MED | 27.7% (baseline) | 26.0% | Neutral scaffold |
| AX_FINAL | **39.4%** | **40.9%** | Thermal/BIO enriched |

AX_FINAL is enriched in REGIME_1 and BIO contexts -- the same contexts where ENERGY is highest (C553: BIO + REGIME_1 = 48.9% ENERGY). Frame closure is more important in thermal processing.

## Interpretation

AX functions as execution infrastructure:
- **Not residual**: Positional stratification is statistically robust (p = 3.6e-47)
- **Not functional**: Zero hazard, flat transitions, no semantic triggers
- **Not random**: 71.8% INIT-before-FINAL ordering

AX is the STRUCTURAL SKELETON of the line, within which CC/EN/FL/FQ perform FUNCTIONAL operations. Every line has a frame (AX), and within that frame, operations occur.

## Cross-References

- C109: 17 forbidden transitions (AX never involved)
- C411: AX internal redundancy (97.4% co-occurrence)
- C550: Role transition grammar (AX has flat transitions vs named roles)
- C553: BIO-REGIME energy independence (AX_FINAL enriched in same contexts)
- C556: ENERGY medial concentration (AX_MED parallel)
- C557: daiin opener (AX_INIT parallel but non-triggering)
- C563: AX positional stratification (structural basis)
