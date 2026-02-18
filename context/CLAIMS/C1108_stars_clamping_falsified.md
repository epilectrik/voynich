# C1108: Stars Vocabulary Clamping Hypothesis Falsified

**Tier:** 2 (STRUCTURAL INFERENCE — NEGATIVE)
**Scope:** B
**Phase:** STARS_RECIPE_CHARACTERIZATION (Phase 392)
**Qualifies:** C1104 (bridge density enables freedom)
**Leaves open:** Stars Paradox (most REGIME diversity, lowest AXM variance)

---

## Statement

The hypothesis that Stars' low AXM variance (0.0059, lowest of B/H/S) is caused by vocabulary clamping — low bridge density restricting behavioral options and e-stability concentration forcing convergence — is NOT supported by the evidence. Four clamping tests (S7-S10) produced 0 PASS and 3 FAIL:

1. **No consistent intra-REGIME clamping** (S7): Stars variance ratio is 0.66 in REGIME_1 (lower, as predicted) but 1.34 in REGIME_3 (higher, opposite). Levene's NS for both.
2. **No e-stability mediation** (S8): Within Stars, e-kernel fraction has zero relationship with AXM deviation (rho=-0.023, p=0.918). Mediation is negative (-19%).
3. **No bridge mediation** (S9): Bridge density mediation is -2% (amplifies rather than explains the Stars effect).
4. **Stars vocabulary is NOT more homogeneous across REGIMEs** (S10): Cross-REGIME Jaccard is LOWER for Stars (0.283) than non-Stars (0.309).

The Stars Paradox remains unexplained.

---

## Evidence

### S7: Intra-REGIME AXM Convergence
| REGIME | Stars var | NS var | Ratio | Levene p |
|--------|-----------|--------|-------|----------|
| REGIME_1 | 0.00437 | 0.00661 | 0.661 | 0.356 |
| REGIME_3 | 0.00635 | 0.00473 | 1.343 | 0.753 |

R1 ratio < 1 but R3 ratio > 1. No consistent direction.

### S8: e-Stability Mediation
- Within Stars: rho(e_frac, |AXM_dev|) = -0.023, p=0.918
- Mediation coefficient reduction: -19.1% (opposite direction)

### S9: Bridge Bottleneck
- Within Stars: rho(bridge_density, |c1017_residual|) = +0.187, p=0.394
- Bridge mediation: -2.0% (amplifying, not mediating)

### S10: Cross-REGIME Vocabulary Homogeneity
- Stars R1-R3 cross-REGIME Jaccard: 0.283
- Non-Stars R1-R3 cross-REGIME Jaccard: 0.309
- Permutation p=1.000 (Stars is LESS homogeneous, not more)

---

## Interpretation

The vocabulary-compositional explanation for Stars' low AXM variance does not hold. Bridge density and e-stability concentration do not clamp Stars programs to similar dynamics. The mechanism must lie elsewhere:

**Possible alternatives (untested):**
1. **LINK-mediated regulation**: Stars' 7.4x LINK elevation (C1107) might actively regulate dynamics, forcing convergence through monitoring rather than vocabulary restriction
2. **CC trigger profile**: Stars' CLOSE_FLOW/FQ_FREQUENT dominance might channel programs through a narrower set of control pathways
3. **Paragraph-level constraint**: Stars may have structural properties at the paragraph level (PSC) that constrain folio-level dynamics
4. **Section-specific forbidden transitions**: Stars may have additional de facto forbidden transitions beyond the 17 universal ones (C109)

The REGIME_1 variance ratio (0.66) is suggestive of clamping in that REGIME specifically, but the R3 reversal (1.34) prevents a clean conclusion.

---

## Provenance

- Phase: 392 (STARS_RECIPE_CHARACTERIZATION), Tests S7-S10
- Script: `phases/STARS_RECIPE_CHARACTERIZATION/scripts/stars_recipe_characterization.py`
- Results: `phases/STARS_RECIPE_CHARACTERIZATION/results/stars_recipe_characterization.json`
- Related: C1048, C1104, C1106, C1107
