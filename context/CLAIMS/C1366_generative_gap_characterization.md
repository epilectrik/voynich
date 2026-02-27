# C1366 — M2.1 Generative Gap Characterization

**Tier:** 2
**Scope:** B, folio, M2.1, design freedom, accent
**Phase:** 479 (GENERATIVE_GAP_CHARACTERIZATION)
**Depends on:** C1365, C1169, C1048, C458, C1016

## Constraint

M2.1 (21/21 at corpus level) erases per-folio variation by generating from corpus-wide statistics. Comparing 72 real folios against 100 M2.1 synthetic counterparts each (matched on line count and per-line lengths) across 31 analysable features reveals:

**The folio accent is concentrated in class distribution and sequential dynamics, not in positional structure or vocabulary composition.**

## Quantitative Summary

| Measure | Value |
|---------|-------|
| Folios tested | 72 |
| Synthetic per folio | 100 |
| Features analysed | 31 (excl. forbidden_violations sanity check) |
| Feature-folio pairs within \|z\| < 2 | 76.5% |
| Systematic gap features (mean\|z\| > 1.5) | 11 |
| Composite anomaly mean | 1.326 (std 0.508) |

## Systematic Gap Features (the accent)

Ranked by mean |z| across 72 folios:

| Rank | Feature | Mean\|z\| | Frac > 2 | Direction | Group |
|------|---------|-----------|----------|-----------|-------|
| 1 | axm_fraction | 2.140 | 0.46 | negative | Class dist |
| 2 | class_concentration | 2.032 | 0.35 | positive | Class dist |
| 3 | axm_self_transition | 2.026 | 0.44 | negative | Sequential |
| 4 | class_entropy | 1.931 | 0.43 | negative | Class dist |
| 5 | fq_fraction | 1.917 | 0.42 | positive | Class dist |
| 6 | mean_word_length | 1.912 | 0.46 | negative | Morphological |
| 7 | mean_run_length | 1.824 | 0.36 | negative | Sequential |
| 8 | e_fraction | 1.824 | 0.42 | positive | Kernel |
| 9 | bigram_entropy | 1.745 | 0.33 | negative | Sequential |
| 10 | suffix_rate | 1.589 | 0.35 | negative | Morphological |
| 11 | category_entropy | 1.535 | 0.26 | negative | Category |

**NOT in the accent** (mean|z| < 1.5): positional features (q0/q4 AXM fraction, gradient, opener entropy), dark/bridge fractions, exclusive B fraction, prefix count, bare token rate, closer rate, spectral gap, articulator rate.

## Section Structure

| Section | Mean Anomaly | n | Interpretation |
|---------|-------------|---|----------------|
| H (Herbal) | 1.047 | 22 | Closest to corpus average — generic |
| S (Stars) | 1.282 | 23 | Near average |
| C (Cosmo) | 1.297 | 5 | Near average |
| B (Bio) | 1.691 | 20 | Most distinctive — strongest accent |

BIO has the HIGHEST anomaly (p=0.9996 against the alternative of being lower). This does NOT contradict C1048 (BIO LOO R2=0.754 for internal predictability). BIO programs are internally coherent AND collectively distinctive — all BIO folios are similar to each other and different from the corpus average. Internal predictability + external distinctiveness = strong accent.

## Archetype Structure

| Archetype | Mean Anomaly | n |
|-----------|-------------|---|
| 1 (strong attractor) | 2.034 | 10 |
| 5 (active interchange) | 1.398 | 7 |
| 2 | 1.213 | 13 |
| 6 (default) | 1.210 | 30 |
| 3 | 1.111 | 7 |
| 4 | 1.103 | 5 |

Archetype 1 (strongest AXM attractor, C1016) has the largest generative gap — its extreme AXM dynamics are farthest from the corpus average.

## REGIME Structure

| REGIME | Mean Anomaly | n |
|--------|-------------|---|
| R4 | 1.077 | 18 |
| R3 | 1.344 | 15 |
| R1 | 1.420 | 31 |
| R2 | 1.494 | 8 |

## Key Tests

**T1 (feature normality):** 76.5% within |z| < 2. M2.1 captures most variation through sampling noise alone.

**T2 (systematic gaps):** 11 features exceed threshold. The accent is real and structured.

**T3 (C1048 BIO):** NOT confirmed as lower anomaly. BIO is the most anomalous section. C1048 coherence = internal predictability, not proximity to corpus average. REINTERPRETATION: C1048 coherence manifests as strong collective accent (all BIO folios deviate from corpus in the same direction).

**T4 (C458 asymmetry):** NOT confirmed in generative gap. Hazard mean|z|=1.359, recovery mean|z|=1.306, ratio=0.96. The hazard-clamped/recovery-free asymmetry operates at a resolution M2.1 cannot distinguish. Both hazard and recovery features show equal per-folio variation relative to M2.1.

**T5 (metadata correlation):** Anomaly vs AXM self-transition: rho=0.153, p=0.199 (not significant). The gap is not simply "extreme AXM folios are more anomalous."

## Most Anomalous Folios

Top 5 most anomalous: f77r (3.38), f82r (2.69), f83v (2.61), f77v (2.23), f82v (2.21) — ALL BIO section.
Top 5 least anomalous: f34v (0.71), f106r (0.67), f106v (0.65), f31r (0.62), f66v (0.62) — all HERBAL or STARS.

## Interpretation

The folio accent — the ~27% design freedom from C1169 — is primarily a **macro-automaton operating point** parameter. Each folio tunes how much AXM vs FQ it uses, how long AXM runs persist, and how concentrated its class distribution is. This is exactly what C1016's dynamical archetypes describe, now confirmed from the generative direction.

The accent is NOT about:
- Where in the line things happen (positional structure is universal — C1363)
- What vocabulary subset is used (dark/bridge fractions match corpus)
- Differential hazard vs recovery freedom (C458 asymmetry doesn't propagate to this resolution)

The accent IS about:
- How much the folio's macro-automaton orbits AXM (class distribution)
- How the transitions flow between macro states (sequential dynamics)
- Which kernel balance the program uses (e_fraction)
- Morphological texture (word length, suffix rate) — likely downstream of class distribution

## Provenance

Script: `phases/GENERATIVE_GAP_CHARACTERIZATION/scripts/generative_gap_characterization.py`
Results: `phases/GENERATIVE_GAP_CHARACTERIZATION/results/generative_gap_characterization.json`
