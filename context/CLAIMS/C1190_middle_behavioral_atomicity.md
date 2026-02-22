# C1190: MIDDLE Behavioral Atomicity

## Statement

Single characters are genuine behavioral atoms of Currier B MIDDLE composition. Multi-character MIDDLEs inherit behavioral profiles by additive composition of component single-character atoms. Statistical validation: r=0.754 (no-kernel variant), z=3.32, p<0.001 vs 1000 permutations. Zero of 1000 random atom-letter permutations matched or exceeded the real assignment.

**Scope note (Phase 422 refinement):** The original C1190 claimed additive composition across ALL morphological positions (PREFIX, MIDDLE, SUFFIX). Phase 422 (CROSSWORD_GLOSS_VALIDATION) tested this claim and found that additive composition is MIDDLE-specific. PREFIX compounds show emergent behavior (c, h, s, p degrade predictions), and SUFFIX position imposes a systematic grammatical shift (r=0.892). Atoms carry consistent behavioral IDENTITY across positions (15/18 CONSISTENT in cross-position test), but the COMPOSITIONAL RULE varies by position. See C1191 for the cross-position findings.

## Tier

2 — Empirical, statistically validated, no gloss dependency

## Scope

B (Currier B internal grammar)

## Evidence

### Test Design

1. Computed behavioral profiles for 210 MIDDLEs (≥5 tokens each) from raw Currier B token data (H-track, no labels, no uncertain tokens)
2. Behavioral features per MIDDLE (22 total): mean normalized line position, line-initial rate, line-final rate, paragraph-initial rate, paragraph-final rate, suffix rate, articulator rate, section distribution (5 sections: B, C, H, S, T), prefix co-occurrence profile (qo/ch/sh/da/sa/ok/ot/ol/other/none — 10 bins)
3. Split: 20 single-character atoms, 190 testable compounds (2+ chars, all component atoms present)
4. Prediction method: compound profile = mean of component atom profiles
5. Null model: 1000 random permutations of atom-to-letter identity

### Results (Three Variants)

| Variant | Purpose | Real r | Perm r | Z | p | Perms beating |
|---------|---------|--------|--------|---|---|---------------|
| A: All features | Full test | 0.7106 | 0.4776 | 5.04 | <0.001 | 0/1000 |
| **B: No kernel** | **Circularity-free** | **0.7543** | **0.6052** | **3.32** | **<0.001** | **0/1000** |
| C: Kernel only | Circularity measure | 0.5001 | 0.0084 | 4.12 | 0.002 | 2/1000 |

**Variant B is the primary result.** Kernel features were removed because kernel assignments may derive from character content (tautology risk). The result holds without kernel features.

### Top Predictive Features (No-Kernel Variant)

| Feature | R | Category |
|---------|---|----------|
| pfx_da (da-prefix rate) | 0.624 | Prefix co-occurrence |
| pfx_sa (sa-prefix rate) | 0.474 | Prefix co-occurrence |
| lf_rate (line-final rate) | 0.466 | Positional |
| art_rate (articulator rate) | 0.454 | Morphological |
| sfx_rate (suffix rate) | 0.451 | Morphological |
| pfx_qo (qo-prefix rate) | 0.442 | Prefix co-occurrence |
| sec_B (section B rate) | 0.434 | Distributional |
| pfx_ok (ok-prefix rate) | 0.380 | Prefix co-occurrence |
| mean_pos (line position) | 0.347 | Positional |

### Circularity Control

Variant C (kernel-only) tests whether the result is driven by a tautology: if kernel assignments derive from character content, then "k-containing MIDDLEs have K-kernel" would be trivially true. Variant C's r=0.500 is weaker than Variant B's r=0.754, confirming that the compositionality is primarily carried by non-kernel behavioral features (position, morphology, prefix co-occurrence, section distribution).

## Strengthens

- **C267.a** (218 sub-components reconstruct 97.8% of MIDDLEs): C1190 provides behavioral validation that sub-component reconstruction reflects genuine functional decomposition, not arbitrary string-matching.
- **C1003** (Pairwise Compositionality): Extends the "no three-way synergy" finding down one level. Pairwise composition at the TOKEN level is paralleled by additive composition at the MIDDLE level.
- **C1065** (Atom Bigram Ordering Grammar): Explains the functional basis for ordering grammar — atoms carry behavioral profiles, so arrangement affects compound behavioral inheritance.
- **C906** (Vowel Primitive Suffix Saturation): Single-char atoms' suffix-attracting profiles propagate to compounds, explaining saturation effects.
- **C1141** (Dark Pipeline Compounds Built from Bridge Atoms): Provides mechanism — bridge atoms serve as building blocks because their behavioral profiles compose additively.

## Reconciliation with C985 (Character-Level Features Insufficient)

C985 found that character-level features achieve only AUC=0.71 for predicting MIDDLE **compatibility** (which tokens can co-occur), vs AUC=0.93 for spectral embedding — a 22% structural gap. This correctly established that characters cannot predict the **execution layer** (compatibility, legal transitions).

C1190 shows that characters DO predict the **construction layer** (line position, suffix rate, prefix co-occurrence, section distribution) at r=0.754 with p<0.001.

These findings are **complementary, not contradictory**. They measure different layers of the three-layer architecture (Section 0.C of INTERPRETATION_SUMMARY):

| Layer | Characters predict? | Constraint |
|-------|-------------------|------------|
| **Construction** (how tokens are built, where they sit) | **YES** (C1190: r=0.754) | C1190 |
| **Compatibility** (which tokens co-occur) | **NO** (C985: 22% gap) | C985 |
| **Execution** (legal program paths) | **NO** (C109, C985) | C985 |

C522 (Construction-Execution Layer Independence) already established that these layers are statistically independent. C1190 and C985 are the empirical proof: characters carry construction information but not execution information.

**The Tier 0 falsification "Individual glyphs don't carry meaning" (CORE/falsifications.md) is untouched.** C1190 does not claim characters carry semantic meaning (C120). It claims they carry behavioral profiles — construction-layer mechanics, not content.

## Prior Constraints

- C267 (Tokens are COMPOSITIONAL: PREFIX+MIDDLE+SUFFIX)
- C267.a (218 sub-components reconstruct 97.8% of MIDDLEs)
- C510 (Positional Sub-Component Grammar: START/END/FREE classes)
- C521 (Kernel Primitive Directional Asymmetry)
- C522 (Construction-Execution Layer Independence — C1190 and C985 are the empirical proof)
- C985 (Character-Level Features Insufficient for Discrimination — compatible, different layer)
- C984 (Independent Binary Features Cannot Reproduce Structure — compatible, different layer)
- C1003 (TOKEN is Pairwise Composite)
- C1065 (Atom Bigram Ordering Grammar)
- C1070 (Atom Ordering Grammar Independent of Kernel Directional Bias)

## Falsification

Would be falsified if:
1. A different behavioral feature set yields non-significant permutation results (p > 0.05)
2. The compositionality is shown to be an artifact of MIDDLE length alone (longer MIDDLEs → averaged position → baseline averaging effect). Control: permutation test already addresses this — random atom assignments also average, but produce lower correlations.
3. Cross-validation (split compounds into two families, train on one, test on other) fails to replicate.

## Provenance

Phase: COMPOUND_DECOMPOSITION (original), CROSSWORD_GLOSS_VALIDATION (scope correction)
Scripts: `phases/COMPOUND_DECOMPOSITION/scripts/behavioral_prediction_v2.py`
Results: `phases/COMPOUND_DECOMPOSITION/results/behavioral_prediction_v2.json`
Scope correction: `phases/CROSSWORD_GLOSS_VALIDATION/scripts/crossword_validation.py`, `grammatical_role_test.py`
