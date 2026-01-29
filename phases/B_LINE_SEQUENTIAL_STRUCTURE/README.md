# B_LINE_SEQUENTIAL_STRUCTURE

**Status:** COMPLETE | **Constraints:** C670-C681 | **Scope:** B

## Objective

Characterize **line-to-line sequential structure** in Currier B programs. C664-C669 established that class-level deployment proportions are stationary within folios. This phase asks: **what changes from line to line at the token level? Are lines sequentially coupled or independent draws? Do per-line parameters form predictable groups?**

## Key Finding

**Lines are contextually-coupled, individually-independent assessments.** Each folio configures a parameter context (REGIME + folio-specific conditions). Lines sample independently from that context. Adjacent lines are weakly more similar than random (+3.1%, p<0.001), but show no vocabulary memory, no trigger memory, and no lane memory beyond folio identity. 24/27 features show lag-1 prediction — but this captures folio-level configuration, not line-to-line state transfer.

| Dimension | Result |
|-----------|--------|
| Adjacent vocabulary coupling | None (0/79 folios significant) |
| Vocabulary introduction | Front-loaded (87.3% of folios) |
| Boundary grammar | Grammar-transparent (7.4% entropy reduction) |
| CC trigger memory | None (permutation p=1.0) |
| Lane balance memory | Folio-driven only (permutation p=1.0) |
| MIDDLE identity drift | Minimal (JSD=0.081, 4/135 biased) |
| Morphological parameterization | Significant evolution (PREFIX chi2 p=3.7e-9, suffix p=1.7e-7) |
| Line complexity | Declines late (unique tokens rho=-0.196, p<1e-21) |
| Discrete line types | None (best sil=0.0995) |
| Adjacent line similarity | Weak coupling (+3.1%, p<0.001) |
| Positional prediction | 11/27 features, 9 beyond REGIME |
| Sequential prediction (lag-1) | 24/27 features significant — folio-mediated |

## Interpretation

The control loop operates as a **stateless assessor within a stateful context**. The folio (program) configures operating parameters — REGIME, lane emphasis, morphological mode — and each line independently evaluates the system within those parameters. Late-program lines are shorter, simpler, and more bare-morphology, but this is positional convergence (approaching steady-state), not sequential state propagation.

There is no recipe. There is no phase sequence. There is a controller that starts with broad vocabulary, gradually simplifies its morphological mode, and maintains constant class proportions throughout. The "memory" between lines is the shared folio context, not information passed from line N to line N+1.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `line_sequential_coupling.py` | T1-T5: Vocabulary coupling, novelty, boundaries, CC/EN autocorrelation | `line_sequential_coupling.json` |
| `line_token_trajectory.py` | T6-T10: MIDDLE, PREFIX, suffix, articulator, complexity trajectories | `line_token_trajectory.json` |
| `line_profile_classification.py` | T11-T15: Feature vectors, clustering, sequencing, prediction | `line_profile_classification.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C670 | Adjacent-Line Vocabulary Coupling | No coupling (0/79 sig, Jaccard diff +0.014) |
| C671 | MIDDLE Novelty Shape | Front-loaded (87.3% FL, 0% BL) |
| C672 | Cross-Line Boundary Grammar | Grammar-transparent (H ratio 0.926, chi2 p=0.187) |
| C673 | CC Trigger Sequential Independence | No memory (perm p=1.0) |
| C674 | EN Lane Balance Autocorrelation | Folio-driven (raw rho=0.167, perm p=1.0) |
| C675 | MIDDLE Vocabulary Trajectory | Minimal drift (JSD=0.081, 4/135 biased) |
| C676 | Morphological Parameterization Trajectory | PREFIX/suffix shift (chi2 p<1e-7) |
| C677 | Line Complexity Trajectory | Lines shorten late (unique tok rho=-0.196) |
| C678 | Line Profile Classification | Continuous, no discrete types (sil=0.100) |
| C679 | Line Type Sequencing | Weak adjacent coupling (+3.1%, p<0.001) |
| C680 | Positional Feature Prediction | 11/27 correlated, 9 beyond REGIME |
| C681 | Sequential Coupling Verdict | 24/27 lag-1 sig — folio-mediated, not sequential |

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token -> 49 classes)
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json` (folio -> REGIME 1-4)
- `scripts/voynich.py` (canonical transcript library + Morphology)

## Cross-References

- C664-C669: Meso-temporal stationarity — class proportions flat within folios
- C506.b: 73% within-class MIDDLE heterogeneity — now shown to be line-independent (C670)
- C171: 94.2% class change line-to-line — class turnover without sequential memory
- C357: Lines as formal control blocks — confirmed grammar-transparent boundaries (C672)
- C389: Bigram determinism H=0.41 bits — boundary entropy only 7.4% lower (C672)
- C606: CC trigger predicts EN subfamily — intra-line only, no cross-line memory (C673)
- C608: No lane coherence — extended to continuous autocorrelation, folio-driven (C674)
