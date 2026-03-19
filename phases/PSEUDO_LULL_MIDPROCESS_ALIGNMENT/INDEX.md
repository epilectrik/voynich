# Phase 603: PSEUDO_LULL_MIDPROCESS_ALIGNMENT

**Status:** COMPLETE
**Verdict:** MIDPROCESS_CONTROL_ALIGNMENT_CONFIRMED (4/5 primary tests pass, N1 negative control passes)
**Constraints:** C1744-C1748
**Script:** `scripts/pseudo_lull_alignment.py` (~6s)
**Results:** `results/pseudo_lull_alignment_results.json` (4.7 KB)
**Pre-registration:** `PREDICTIONS.md` (SHA-256: `6d8b1579c00469e3...`)

## Motivation

Phase 602 characterized pseudo-Lull's Testamentum corpus on its own terms. Phase 603 tests whether that operational control architecture predicts specific, validated properties of the Voynich's structural grammar. The Brunschwig alignment (Phases 598-601) confirmed thermal-intensity safety substitution but failed to reach the midprocess control layer (C1056). Pseudo-Lull fills that gap.

**Design principle:** Each test derives a quantitative prediction from Phase 602 data and tests it against a named Voynich constraint. Tests target structural homology, not just "pseudo-Lull is richer than Brunschwig" (expert feedback on v1 draft).

## Results

### S1: Calibration Anchor (Stars Thermal-Intensity) -- PASS
- Stars R1 ey_rate: 0.1823 (n=10) vs R3: 0.1039 (n=12)
- Mann-Whitney U=112.0, p=0.0003
- Replicates C1735/C1740

### P1: Monitor->Action Chain Outcome Distribution -- PASS (C1744)
- **P1a (stabilization ratio):** (continue+stop+correct)/(proceed+adjust) = 67/28 = **2.39** (>= 2.0)
  - Matches Voynich kernel directionality: k->e 4.02x, h->e 6.09x (observation -> stabilize dominant)
- **P1b (abort fraction):** 1/96 = **1.0%** (< 5%)
  - Matches Voynich e->h blockage (0.004x)
- P1c (diagnostic): Theorica stabilize/escalate=2.00, only part with enough E8 cues in sample

### P2: Recovery Doctrine <-> Safety-Style Split -- PASS (C1745)
- Pseudo-Lull: 156 recoverable / 25 irrecoverable = **6.24:1** (preventive dominant)
- Voynich: mean ey_rate 0.1377 / mean ii_rate 0.0717 = **1.92:1** (preventive dominant)
- Both ratios > 1.0 and same direction: preventive/forgiving pathway dominates transformative
- P2b (diagnostic): Furnis has highest correction density (1.20/chapter); Bio has highest Voynich safety_balance (+0.157)

### P3: Thresholded Termination <-> Closure Authenticity -- PASS (C1746)
- Pseudo-Lull: 139 threshold / 10 count = **13.9:1**
- Brunschwig: 252 threshold / 178 count = **1.42:1**
- Gap: **9.82x** (>= 3x threshold)
- MONOSTATE diagnostic: All sections AXM > 50% (B=0.743, C=0.643, H=0.573, S=0.689, T=0.584)

### P4: Recovery Asymmetry (C458 Replication) -- PASS (C1747)
- **P4a:** Pseudo-Lull 5 failure modes / 2 correction strategies = **2.50** (> 2.0, convergent recovery)
- **P4b:** Voynich hazard CV = **0.115** (< 0.15); recovery CV = **0.824** (> 0.50)
- Replicates C458: "constrain the dangerous interactions tightly, let recovery vary freely"
- P4c (diagnostic): Per-part correction density CV = 0.31 (> 0.30, recovery free to vary)

### P5: Register Architecture -- FAIL (C1748)
- All 6 pairwise JSD > 0.05: YES (range 0.169-0.408)
- All pairs overlap >= 60%: **NO** (Theorica overlaps 36-50% with operational parts)
- Operational parts only: Practica/Mercuriorum/Furnis overlap at 64% (passes)
- **Failure cause:** Theorica is 88% theoretical chapters with only 6/14 families
- Voynich analog C1134 shows 94.1% shared vocabulary because ALL sections are operational. Pseudo-Lull's Theorica is qualitatively non-operational.

### N1: Negative Control -- PASS
- Mantel-like test: 24 part-to-section pairings tested
- Best raw p=0.123, Bonferroni-corrected p=1.000
- No cross-system structural distance prediction (matches C1739 pattern)

### D1: Diagnostic -- Formalization Boundary
- Pseudo-Lull: 61 formalized / 35 discretionary = 1.74
- Voynich: 49 encodable / 13 non-encodable = 3.77
- Voynich encodes 2.16x more of its operational space (consistent with a coded system vs natural-language text)

## Key Findings

1. **Midprocess control alignment is real.** 4/5 tests pass at pre-registered thresholds. Pseudo-Lull's monitoring->action chain architecture predicts the Voynich's kernel operator directionality (stabilization-dominant, escalation-suppressed).

2. **Recovery doctrine maps to safety-style split.** Both systems show a preventive-dominant safety architecture (PL 6.24:1, V 1.92:1), confirming that the Voynich's two-strategy safety design (e->y preventive vs ii transformative) has a historical operational parallel.

3. **Thresholded termination is the key differentiator.** Pseudo-Lull's 13.9:1 threshold/count ratio vs Brunschwig's 1.42:1 (9.8x gap) confirms that quality-dependent stopping — not fixed step counts — is what distinguishes the midprocess control layer from recipe-level specification.

4. **Cross-system rank concordance correctly fails.** The N1 negative control passes (p=1.0), matching the C1739 lesson: within-context alignment works, cross-context rank prediction does not. Pseudo-Lull is a legitimate comparator under the same constraints as Brunschwig.

5. **Register architecture is partial.** The "same inventory, different weighting" pattern (C1134) holds within pseudo-Lull's operational parts but breaks when including Theorica. The Voynich has no purely theoretical section, so the analogy is incomplete.

## What This Phase Does NOT Do

- No chapter-to-folio mapping
- No cipher letter to Voynich token mapping
- No cross-section rank predictions (tested and correctly rejected as N1)
- No content-level semantic mapping
- No apparatus-name matching
