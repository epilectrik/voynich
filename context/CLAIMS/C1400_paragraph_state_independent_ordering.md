# C1400: Paragraph State-Independent Ordering

**Tier:** 2 (ESTABLISHED)
**Scope:** B, paragraph, ordering, thermal, state
**Phase:** PARAGRAPH_STATE_DEPENDENT_ORDERING (Phase 512)
**Extends:** C1399 (paragraph ordering null), C1398 (paragraph operational gradient), C845 (paragraph self-containment)
**Relates to:** C1260 (B-track thermal state tracking), C1288 (within-folio paragraph coherence), C1121 (folio-level domain determination), C1295 (termination memoryless)

---

## Statement

Terminal physical state (kernel balance, category profile, tail product type) does **NOT** predict the zone of the next paragraph. 0/8 tests positive after disambiguation. The apparent thermal continuity between consecutive paragraphs (raw rho=+0.230) is entirely explained by **folio-level shared thermal environment** — all paragraphs in a folio share similar thermal profiles because they operate under the same REGIME and section, not because heat carries over sequentially. Paragraph ordering within folios is driven by folio-level program theme, not by cross-paragraph physical state chains.

### Disambiguation Evidence

The raw consecutive-paragraph e_frac correlation (+0.230) was disambiguated between physical continuity and shared environment:

| Test | Result | Verdict |
|------|--------|---------|
| Adjacent vs non-adjacent | +0.230 vs +0.194 (p=0.690) | SHARED_ENVIRONMENT |
| Shuffle control (1000 perms) | Shuffled mean +0.240, p=0.565 | SHARED_ENVIRONMENT |
| Lag gradient | Flat (0.230/0.177/0.233) | SHARED_ENVIRONMENT |
| Folio-residualized | rho flips to **-0.161** (p=0.029) | Thermal alternation, not carryover |

The folio-residualized sign flip indicates weak within-folio thermal **anti-correlation**: consecutive paragraphs compensate rather than propagate thermal state. Consistent with cycling architecture (C1228, C1229).

---

## Key Findings

### State Prediction Tests (8 tests, 0/8 PASS after disambiguation)

| Test | Question | Result | Key Numbers |
|------|----------|--------|-------------|
| T1 | Terminal kernel → next zone? | FAIL | LR=0.380, baseline=0.685 |
| T2 | Terminal category → next zone? | FAIL | LR=0.457, baseline=0.685 |
| T3 | Cross-zone transitions state-driven? | FAIL | LR=0.296, baseline=0.407 |
| T4 | Different transitions from different thermal states? | FAIL | KW p=0.172 |
| T5 | Thermal continuity across boundaries? | FAIL (disambiguated) | Raw rho=+0.230, shuffle p=0.565 |
| T6 | Tail product → next zone? | FAIL | chi2=10.11, p=0.120 |
| T7 | Combined model beats zone-only? | FAIL | Combined=0.484, zone-only=0.566 |
| T8 | Within-section state prediction? | FAIL | Mean gain=-0.126 |

### Folio-Mode Baseline Dominance

The folio-mode baseline (predicting the folio's most common zone) achieves 68.5% accuracy, crushing all state-based models. Just knowing "this folio is mostly Zone 0" is the best available predictor. Adding terminal state features to any model degrades performance.

### Combined Picture (Phases 510-512)

| Finding | Constraint | Implication |
|---------|-----------|-------------|
| Continuous operational gradient | C1398 | Paragraphs vary by emphasis, not type |
| No fixed ordering | C1399 | No thermal-first/monitoring-last ramp |
| No state-dependent ordering | C1400 | Terminal state doesn't route next zone |
| Zone inertia (O/E=2.02) | C1399 | Folio theme drives clustering |
| Thermal anti-correlation | C1400 | Weak compensatory cycling within folio |

Paragraphs are independently composed subroutines within a folio's thematic envelope. The folio specifies WHAT operational concerns to address, HOW MUCH of each, and the thermal character of the environment. Individual paragraphs are then composed independently, without reference to what other paragraphs said or how the process is currently unfolding.

---

## Falsification Criteria

1. If a finer-grained state representation (token-level rather than line-level) predicts next zone, the feature resolution was too coarse
2. If cross-folio paragraph pairs show zero correlation while within-folio show +0.230, the shared-environment interpretation is confirmed (already confirmed by shuffle test)
3. If the thermal anti-correlation (rho=-0.161) replicates at higher significance with more data, it becomes a standalone constraint

---

## Method

- 184 consecutive paragraph pairs across 80 folios (from 264 Phase 510 paragraphs with 3+ body lines)
- Terminal features: kernel fractions (k/e/h), category profile, headless fraction, bare suffix, qo PREFIX fraction — computed from last 2 body lines
- Prediction models: logistic regression and random forest with 5-fold CV
- Disambiguation: adjacent vs non-adjacent, folio residualization, lag gradient, 1000-permutation shuffle
- Random seed 42

**Script:** `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/scripts/state_dependent_ordering.py`
**Disambiguation:** `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/scripts/thermal_disambiguation.py`
**Results:** `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/state_dependent_ordering.json`
**Disambiguation results:** `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/thermal_disambiguation.json`
