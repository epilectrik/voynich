# Phase 734 — M2-vs-5-gram Decomposition: C1025 rescoped, M1 is the fidelity frontier

**Status:** COMPLETE (2026-05-28)
**Resolves:** the C1025 scope-flag opened in PHASE_733 ("which of M2's metrics are 5-gram-floor?").
**Also tests:** C978's 6-state spectral gap (0.894) under the 5-gram null.

---

## Method

Reused the validated C1025 generative-sufficiency battery (GENERATIVE_SUFFICIENCY / Phase 348) — imported `load_data`/`compute_metrics`/`evaluate_tests` verbatim — and added a **character-5-gram as a 6th model** alongside M0-M4, run through the identical 15-test battery, 20 instantiations. M0-M4 reproduced C1025's published pass rates almost exactly (M0 10.9, M1 11.9, M2 12.0, M3 12.0, M4 9.1), confirming faithful reuse. Real B1 6-state spectral gap = 0.8938 (= C978's 0.894).

## Result: 5-gram passes 9.3/15

| Test | M0 | M1 | M2 | 5GRAM | reading |
|------|----|----|----|----|---------|
| A2 hapax, A4 type-count | pass | pass | pass | **FAIL** (0.0, 0.25) | 5-gram hallucinates novel tokens → wrong vocab distribution |
| B1 6-state spectral gap | fail | pass | pass | **FAIL** (0.10) | macro-eigenstructure — see below |
| B3 forbidden (==0 test) | fail | fail | pass | **FAIL** | idealization test — see below |
| B4, C2 | fail | fail | fail | fail | nobody passes (test-spec issues C1030/C1033) |
| B5 fwd-rev JSD | pass | pass | **fail** | pass | M2 breaks symmetry (C1034 asymmetry gap) |
| A1,A3,B2,C1,C3,D1,D2,D3 | pass | pass | pass | pass | marginal floor |

B1 raw gaps: M0 0.978 > 5gram 0.956 > M1 0.895 ≈ M2 0.888 ≈ M3 0.896 ≈ real 0.894.
B3 raw violations: M0 24.8, M1 28.4, **M2 0.0**, M3 22.2, **5gram 12.8, real 13**.

## Three findings

### 1. C1025 "80% sufficiency" is mostly marginal-floor → RESCOPE

10/15 tests are passed by M0 (i.i.d. token sampling) too — they measure marginal/distributional properties, not sequential structure. Of the 5 non-floor tests (B1, B3, B4, B5, C2):
- **B1** (6-state spectral gap): the ONE clean above-character-Markov *structural* earn. M1+ pass, M0 and 5-gram fail. = the macro-eigenstructure (C2061/C978).
- **B3**: idealization credit (see #2), not earned structure.
- **B4, C2**: nobody passes — documented test-spec issues (C1030/C1033).
- **B5**: M2 *fails* (the known asymmetry gap, C1034).

So M2's genuine above-character-Markov structural content reduces to **B1 (macro-eigenstructure)**. The "M2 is the sufficiency frontier" framing was partly an artifact of scoring an idealization test (B3) inside a fidelity battery. **M1 (pure class-Markov) is the corpus-fidelity frontier** — the macro-automaton topology lives in the class-Markov matrix itself and does not need forbidden suppression to emerge. This *strengthens* the macro-automaton story: hazard avoidance is a thin overlay (consistent with C622 0.12% safety-buffer rate, C997 sparse-critical-buffer regime, C1023 PREFIX-routing as sole load-bearing macro component), not load-bearing for the topology.

### 2. B3 is an idealization test, NOT a fidelity test → NEW constraint C2063

B3 tests `forbidden violations == 0`. The REAL corpus has 13 (the ~0.7% leakage, C1360 ~0.05% realized rate, C789 permeability). M2 produces 0 by hard bidirectional suppression → passes. The 5-gram produces 12.8 ≈ real's 13 → fails. **So M2 passes B3 by being LESS faithful to the real corpus than the 5-gram is.** B3 rewards over-idealization. This is the 4th C1025-battery test-spec correction (cf. C1030/C1033/C1034) and is of *inverse polarity* — those were too strict on the model; B3 is too lenient on the over-idealized model. Consistent with C2060 (forbidden pairs are real-but-Markov-reproducible-as-rare-events; the 5-gram reproduces the real rate).

### 3. C978's 6-state spectral gap survives the 5-gram null → ANNOTATE (lead with C2061)

B1 = C978's 0.894. The 5-gram fails it (gap 0.947-0.956 vs real 0.894). **Blocking control** (both experts demanded, given the 5-gram's over-separated gap could be a hallucination artifact): hallucination rate is only **1.6%**; under drop-unmapped the gap stays 0.954, under vocab-constrained regeneration 0.947 (pass rate 0.45 — borderline, 0.053 outside the 0.05 tolerance). So the failure is NOT primarily a hallucination artifact — the 5-gram genuinely nearly-but-not-quite reproduces the 6-state gap. This is **consistent with PHASE_733's raw-49 λ2 result** (5-gram reproduces ~60% of the macro-eigenstructure excess, survives at p=0.000).

**The 6-state B1 is borderline and projection-dependent (it runs through C976's constraint-laden merge).** The load-bearing C978 evidence is **C2061** (raw-49 λ2, merge-free, per-synth-own-shuffle p=0.000). The 6-state B1 corroborates but is not elevated above C2061.

## Dispositions

| Constraint | Action |
|---|---|
| **C1025** | RESCOPE (Tier 2 stays). Headline → "M2 sufficiency = marginal floor (10/15, M0 too) + B1 macro-eigenstructure (= C2061) as the single clean above-char-Markov earn; B3 credit is idealization (C2063); B4/C2/B5 are documented test-spec/asymmetry issues (C1030/C1033/C1034). M1 is the corpus-fidelity frontier; M2's edge over M1 is forbidden-idealization, not fidelity." |
| **C2063** (new, Tier 2) | B3 idealization-vs-faithfulness correction. |
| **C978** | ANNOTATE: 6-state spectral gap robust to 5-gram null; lead with C2061 (raw-49 λ2, merge-free, p=0.000); 6-state B1 corroborates (borderline, projection-dependent). Cross-ref C2061. |
| **C121/C124, Tier 0** | UNTOUCHED |

## Methodology notes

- A character-5-gram is **NOT strictly stronger than M0** (i.i.d. token sampling): it fails A2/A4 (hapax, type count) via novel-token hallucination where M0 passes by construction. "5-gram floor" ≠ "i.i.d.-token floor" — different nulls. For class-layer tests, a character generator leaks token-hallucination into the class projection; a class-layer or vocabulary-constrained generator is cleaner (PHASE_733 worked at the class layer for this reason).
- Metrics through the C976 merge (6-state projection) are projection-dependent; the merge-free raw-49 λ2 (C2061) is the load-bearing macro-structure metric.

## Scripts / results

- `scripts/_m2_vs_5gram.py` — 6-model battery (M0-M4 + 5gram); `results/m2_vs_5gram.json`
- `scripts/_b1_hallucination_control.py` — drop-unmapped + vocab-constrained B1 check; `results/b1_hallucination_control.json`

## Cross-reference

C1025 (rescoped), C978 (annotated), C2061 (load-bearing macro-eigenstructure), C2060 (forbidden-pairs-as-rare-events), C2062 (three-axis decomposition), C1030/C1033/C1034 (prior C1025-battery test-spec corrections), C622/C997/C1023 (hazard-as-thin-overlay), C2023 (PHASE_733 scalar-MI demotion).
