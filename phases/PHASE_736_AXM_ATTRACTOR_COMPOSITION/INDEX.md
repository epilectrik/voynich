# Phase 736 — AXM Attractor: self-transition is composition; the macro-slow-mode is distributed

**Status:** COMPLETE (2026-05-29)
**Question (the "elephant" from the strategic consult):** is the AXM attractor's 0.698 self-transition (C976; 32 classes, 67.7% of mass) above-composition, or a frequency artifact? And where does the above-Markov macro-eigenstructure (C2061 λ2) actually live?
**Method:** per-synth-own-shuffle 5-gram null on the scalar AXM self-transition rate + submatrix-λ2 localization + 2nd-eigenvector loading falsification + qo→ch/sh gate-zero. (This is the expert-designed pivot after the original ablation design was killed as foregone + mechanically rigged.)

---

## Outcome

The AXM self-transition rate (0.698) is **composition** — a 68%-mass block self-transitions ~68% of the time by construction, and the 5-gram reproduces it (p=0.655). That's a NON-FINDING (not a demotion of anything). The genuinely-new result: the above-Markov macro-eigenstructure (C2061's λ2) is a **distributed slow mode** spanning ~29 classes, NOT the attractor self-loop — which mechanistically grounds C1010's long-standing non-spectral-partition puzzle (ARI=0.059). Registered as C2065. Tier 0 untouched; corroborates C1403.

## Results

- **GATE-ZERO** (qo→ch/sh, must survive like C549): real excess +0.0452 vs synth +0.0243, z=+3.58, p=0.000. PASS — pipeline reproduces the C549 survival, so a null PRIMARY is interpretable.
- **PRIMARY** (AXM self-transition, per-synth-own-shuffle): real 0.7055, shuffle-composition 0.6951, real excess +0.0104; synth excess +0.0121±0.0043, z=−0.39, **p_emp=0.655**. The 5-gram fully reproduces it (synth excess slightly HIGHER than real). → composition, not designed cohesion.
- **SUBMATRIX λ2** (descriptive, real-data only): full-49 λ2=0.2359, AXM-block-only λ2=0.2224, non-AXM lanes λ2=0.2047 → slow-mixing comparable across attractor and lanes, not attractor-concentrated.
- **2nd-EIGENVECTOR LOADING** (falsification of "distributed"): AXM-block loading 0.642 vs class-fraction 0.65 (≈ proportional, not concentrated); participation ratio 28.8/49; top-5 share 0.299; top loaders mix AXM (22,21,2,8,41) and lane (7,23,9) classes. → SPREAD across ~29 classes, not block-boundary-aligned. "Distributed" SURVIVES.

## Interpretation

1. **The AXM self-transition is a mass artifact.** 68% mass → ~68% self-transition by composition; the +0.0104 residual is reproduced by the 5-gram (p=0.655). The attractor's *self-cohesion* is its size, not designed dwell. This is a NON-FINDING — it was never registered as above-Markov; C978's own text attributes the attractor to "operational mass." **Not a demotion of C976/C978.**
2. **The C2062 scalar-vs-eigenstructure pattern recurs at the block level:** the self-transition SCALAR is composition-floor; the above-Markov signal lives in the EIGENSTRUCTURE (C2061 λ2).
3. **The macro-slow-mode is distributed, not attractor-localized.** The 2nd eigenvector loads ≈ class-proportionally across ~29 classes spanning both blocks (falsification-tested: a concentrated within-AXM gradient would have collapsed the claim and predicted high spectral ARI; it came back spread). 
4. **This mechanistically grounds C1010** (6-state partition spectral-ARI=0.059, "not spectrally natural"): the role/depletion-defined partition can't be spectrally recovered *because the slow mode genuinely doesn't align with the blocks*. Resolves a standing puzzle.

## Dispositions

| Constraint | Action |
|---|---|
| **C2065** (NEW, Tier 2) | Macro-eigenstructure slow mode is distributed across ~29 classes (PR 28.8, loading class-proportional, not block-aligned), NOT the AXM self-loop; grounds C1010's non-spectral partition. |
| **C978** | ANNOTATE (scope-correction, NOT demotion): self-transition rate is composition/mass (5-gram p=0.655); spectral-gap measurement stands; "attractor cohesion/designed dwell" interpretation → "mass-dominant macro-state." |
| **C976, C2061, C1010, C1019** | UNTOUCHED — C2061's above-Markov λ2 stands (this localizes it); C976 partition is role/depletion-defined (C1010 already said not-spectral). |
| **C1403** | CORROBORATED — MONOSTATE is thematic dominance, not sequential convergence; the mass-attractor reading aligns. |
| **Tier 0** | UNTOUCHED — the frozen "closed-loop control programs / narrow viability regime" rests on C074/C079/C084/C109/C627/C121/C124/C1025/C1394, not the AXM self-transition rate. |

## Methodology / hygiene

- The PRIMARY is a NON-FINDING (mass-artifact confirmed), NOT a demotion — keep this distinction sharp so no future reader thinks C976 lost something.
- The naive AXM-block-λ2-vs-5gram comparison (0.222 vs 0.131) was computed but is EXCLUDED from all claims — it's the per-synth-own-shuffle-violating level that produced the PHASE_733 false positive. The "distributed" claim rests only on (a) the real-data submatrix localization and (b) the falsification-passed eigenvector loading.
- Gate-zero positive control (qo→ch/sh) makes the null PRIMARY interpretable (the pipeline can detect above-Markov structure when present).
- Scalar-vs-eigenstructure + self-transition-as-mass-artifact lessons appended to `feedback_chained_controls_scalar_vs_eigenstructure.md`.

## Scripts / results

- `scripts/_axm_composition_test.py` — primary (per-synth-own-shuffle) + submatrix-λ2 + gate-zero; `results/axm_composition_test.json`
- `scripts/_eigenvector_loading.py` — 2nd-eigenvector loading falsification; `results/eigenvector_loading.json`

## Cross-reference

C976/C978 (macro-automaton, scope-corrected), C2061 (above-Markov λ2, localized here), C1010 (non-spectral partition, grounded), C1019 (tensor-orthogonality), C2062 (scalar-vs-eigenstructure, recurs), C1403 (MONOSTATE thematic-dominance, corroborated), C549 (gate-zero).
