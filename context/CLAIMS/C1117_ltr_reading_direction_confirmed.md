# C1117: LTR Reading Direction Confirmed

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** READING_DIRECTION_TEST (Phase 399)
**Extends:** C1024 (structural directionality), C391 (symmetric conditional entropy)
**Relates to:** C556 (execution syntax), C557 (daiin line-initial), C816 (canonical ordering), C1001 (PREFIX zones)

---

## Statement

Currier B reading direction is left-to-right (LTR), confirmed by a 7-test battery scoring LTR 5, RTL 0, NEUTRAL 2. The strongest structural evidence is MIDDLE-level MI forward bias (+0.070 bits, z=17.0 vs positional null, C1119). 75.2% of MIDDLE-level forbidden co-occurrences are bidirectional adjacency constraints (C1118), with 24.8% directional component aligned with LTR. All positional grammar (C556 execution syntax, C557 daiin initial, C816 canonical ordering, C1001 PREFIX zones) is coherent under LTR and incoherent under RTL. Boundary-inward reading hypothesis not supported (entropy profile non-monotonic from both boundaries).

---

## Evidence

### 7-Test Battery Results

| Test | Type | Verdict | Direction Vote |
|------|------|---------|----------------|
| T1: Forbidden Pair Landscape | DECISIVE | NEUTRAL_HIGH_OVERLAP | NEUTRAL (direction-invariant by construction) |
| T2: MI Asymmetry | DECISIVE | LTR_FORWARD_BIASED (z=17) | **LTR** |
| T3: PREFIX Positional Coherence | DECISIVE | LTR_MORE_COHERENT (7-0) | **LTR** |
| T4: Transition Spectral Properties | DIAGNOSTIC | WEAKLY_SENSITIVE | NEUTRAL |
| T5: Entropy Profile | DIAGNOSTIC | NO_CLEAR_PATTERN | NEUTRAL |
| T6: CC Positional Role | SUPPORTING | CC_BOUNDARY_LEFT | **LTR** |
| T7: Vocabulary Gradient | SUPPORTING | LTR_SPEC_TO_EXEC | **LTR** |

### Key Findings

**T2 (strongest structural evidence):** MIDDLE predicts physical-right neighbor better than physical-left (MI_fwd=0.312 vs MI_bwd=0.242, asymmetry=+0.070 bits, z=17.0). This is the only test providing direction-specific evidence without relying on interpretive labels. Confirms and extends C1024.

**T3 (strongest interpretive evidence):** Under LTR, preparation PREFIXes (so, tch, sa, pch, sh) cluster at line-initial and closure PREFIXes (ar, or, ot, ol) cluster at line-final (score 7/10). Under RTL, score = 0/10. This relies on Tier 3 Brunschwig labels — conditionally strong.

**T1 (structural discovery):** 75.2% of MIDDLE forbidden pairs are bidirectional (adjacency constraints). This cannot distinguish directions but explains C1034's symmetric forbidden model improvement (see C1118).

**T4 (confirmation):** Spectral gap LTR=0.896, RTL=0.899 (diff=0.003). Transition topology is direction-invariant, as expected for graph-theoretic properties.

**T5 (boundary-inward falsification):** Entropy profile shows "bathtub" (high at boundaries, low in middle), not U-shaped (boundary-inward prediction). Boundary-inward reading hypothesis not supported.

### External Motivation

The voynich-toolkit (external GitHub project) found character-level RTL with z=22.97 using bigram reversal statistics. This prompted the investigation. Phase 399 tests at the TOKEN SEQUENCE level, not the character level. Character-level writing direction (how symbols are drawn) and token-level reading direction are separate questions — LTR token reading is confirmed regardless of how individual characters were physically written.

---

## Interpretation

LTR reading direction is consistent with all existing positional grammar and the Brunschwig procedural framework. The system reads left-to-right at the token level within lines, with MIDDLE carrying the primary directional signal. The grammar's constraints are largely bidirectional (C391 symmetric entropy, C1118 symmetric forbidden pairs), but the execution layer carries a genuine LTR forward bias.

---

## Provenance

- Phase: 399 (READING_DIRECTION_TEST)
- Script: `phases/READING_DIRECTION_TEST/scripts/reading_direction_test.py`
- Results: `phases/READING_DIRECTION_TEST/results/reading_direction_results.json`
- Expert validation: 0 Tier 0-2 conflicts, confirmed Tier 2 for main finding
- Related: C391, C886, C1024, C1034, C556, C557, C816, C1001, C109, C783
