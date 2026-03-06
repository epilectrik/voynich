# Phase 530: Cross-Line Hazard Continuity

**Date:** 2026-03-05
**Status:** COMPLETE
**Verdict:** CROSS_LINE_HAZARD_FOLIO_MEDIATED

---

## Research Question

C1429 established that consecutive lines are categorically independent (MI=0.032 bits for category, MI=0.003 bits for suffix mode). C1451 showed Mode B carries 100% of forbidden violations. C1463 showed lines create a monotonic hazard gradient: safe operations first, hazardous operations last. Does one line's closing hazard predict the next line's opening safety? Is there cross-line hazard memory, and does Mode B status create elevated coupling?

## Method

- 2,338 consecutive line pairs across 82 Currier B folios (2,420 lines total)
- Per-token hazard classification using C1448 HEAD x TERM frame hazard map (HIGH/LOW/ZERO/IMMUNE)
- Line-level hazard profiles computed as per-class fractions
- Quintile assignment (Q0-Q4) within each line for positional analysis
- Suffix mode classification using centroids from decoder_maps.json
- 500 within-folio shuffle permutations for all correlation tests
- Mutual information, Spearman correlation, Fisher exact test, Cramer's V

**Script:** `phases/CROSS_LINE_HAZARD/scripts/cross_line_hazard.py`
**Results:** `phases/CROSS_LINE_HAZARD/results/cross_line_hazard.json`

## Corpus Statistics

| Metric | Value |
|--------|-------|
| Total lines | 2,420 |
| Total folios | 82 |
| Consecutive pairs | 2,338 |
| Total tokens classified | 23,096 |
| HIGH tokens | 4,782 (20.7%) |
| LOW tokens | 10,558 (45.7%) |
| ZERO tokens | 4,656 (20.2%) |
| IMMUNE tokens | 3,100 (13.4%) |
| Suffix mode A lines | 1,182 |
| Suffix mode B lines | 1,224 |

## Results

### Test 1: Cross-Line Hazard MI

| Metric | Value |
|--------|-------|
| Dominant hazard MI | 0.0172 bits |
| C1429 category MI | 0.032 bits |
| Ratio to category | 0.54x |
| Raw MI p-value | 0.0005 |
| HIGH fraction rho | 0.238 |

Hazard frames carry LESS cross-line information than operational categories. The raw values are statistically significant but entirely folio-mediated (see shuffle control below).

### Test 2: Mode-Stratified Analysis

| Mode transition | N | HIGH rho | ZERO rho | MI (bits) |
|----------------|---|----------|----------|-----------|
| A->A | 590 | 0.162 | 0.090 | 0.017 |
| A->B | 552 | 0.214 | 0.227 | 0.017 |
| B->A | 539 | 0.263 | 0.181 | 0.058 |
| B->B | 631 | 0.228 | 0.224 | 0.016 |

Despite C1451 (Mode B carries 100% of forbidden violations), B->B pairs show NO elevated hazard coupling vs A->A. MI is essentially identical (0.016 vs 0.017). The B->A elevated MI (0.058) reflects Mode B's higher mean HIGH fraction (0.241 vs Mode A 0.147), not sequential structure.

### Test 3: Closure-to-Opening Bridge

| Metric | Value |
|--------|-------|
| Q4 HIGH -> Q0 HIGH rho | +0.059 (p=0.004) |
| Q4 HIGH -> Q0 ZERO rho | -0.019 (p=0.365, NS) |
| Q4 HIGH -> Q0 IMMUNE rho | -0.036 (p=0.080, NS) |
| Bridge Cramer's V | 0.042 |

The closure-to-opening bridge has near-zero predictive power. Q4 hazard does not predict Q0 safety composition.

### Test 4: HIGH Frame Carry-Over

| Line N ending | N pairs | Next Q0 ZERO% | Next Q0 IMMUNE% | Next Q0 HIGH% |
|--------------|---------|---------------|-----------------|---------------|
| HIGH token | 504 | 25.1% | 10.8% | 18.5% |
| Non-HIGH token | 1,834 | 26.2% | 11.9% | 16.0% |
| Cramer's V | -- | -- | -- | 0.030 |

After a HIGH-ending line, the next line's opening is essentially identical to baseline. No compensatory recovery, no hazard persistence. V=0.030 is negligible.

### Test 5: e->y Recovery After Hazard

| HIGH exposure of line N | N pairs | Q0 ZERO rate (N+1) | Q0 IMMUNE rate (N+1) |
|------------------------|---------|--------------------|--------------------|
| Above-median HIGH | 1,137 | 0.223 | 0.103 |
| Below-median HIGH | 1,201 | 0.271 | 0.133 |
| Ratio (above/below) | -- | **0.823x** | **0.775x** |
| Fisher p (ZERO) | -- | **0.0001** | -- |

Both safe categories are DEPLETED, not enriched. The direction is OPPOSITE to what a compensatory recovery mechanism would produce. This is a folio-level composition effect: high-hazard folios have more HIGH tokens everywhere, mechanically reducing the fraction for ZERO and IMMUNE.

### Test 6: Within-Paragraph vs Cross-Paragraph

| Context | N | HIGH rho | ZERO rho | MI (bits) |
|---------|---|----------|----------|-----------|
| Within-paragraph | 2,026 | 0.233 | 0.156 | 0.018 |
| Cross-paragraph | 312 | 0.207 | 0.113 | 0.014 |
| Difference | -- | 0.027 | 0.043 | 0.004 |

Negligible difference. Paragraph boundaries do not modulate hazard correlation. Consistent with C1399 (paragraph ordering null).

### Test 7: Autocorrelation Lag Structure

| Lag | N pairs | Spearman rho | Parametric p | Permutation p |
|-----|---------|-------------|-------------|---------------|
| 1 | 2,322 | 0.233 | <0.0001 | 0.115 |
| 2 | 2,243 | 0.222 | <0.0001 | 0.248 |
| 3 | 2,164 | 0.217 | <0.0001 | 0.306 |
| 4 | 2,085 | 0.208 | <0.0001 | 0.535 |

All lags show flat rho (~0.22) that is entirely folio-mediated. No decay with increasing lag confirms no sequential structure -- pure shared environment.

### Shuffle Control

| Metric | Real | Shuffled mean | p-value |
|--------|------|---------------|---------|
| Dominant hazard MI | 0.0172 bits | 0.0145 bits | 0.212 |
| HIGH fraction rho | 0.238 | 0.216 | 0.098 |

Neither metric survives within-folio shuffling at alpha=0.05. All cross-line hazard correlation is folio-mediated.

## Constraints Produced

| # | Constraint | Tier | Key Evidence |
|---|-----------|------|-------------|
| **C1470** | Cross-line hazard correlation is folio-mediated | 2 | MI=0.0172 bits (0.54x category), shuffle p=0.212, lags 1-4 flat, B->B=A->A |
| **C1471** | No compensatory safe opening after hazardous closure | 2 | e->y DEPLETED 0.82x (Fisher p=0.0001), IMMUNE 0.78x, folio composition effect |

## Integration with Existing Framework

### Lines Extended

| Constraint | What Phase 530 Adds |
|------------|-------------------|
| C1429 (cross-line category independence) | Extended to hazard-frame resolution: MI=0.0172 bits (0.54x of category MI) |
| C1451 (Mode B exclusive forbidden carrier) | Mode B status creates NO cross-line coupling (B->B MI = A->A MI) |
| C1463 (line-level zone-hazard routing) | Confirmed as self-contained within each line; no cross-line safety architecture |
| C1457-C1462 (e->y safe pathway) | e->y is WITHIN-LINE only; does not function as cross-line recovery |
| C681 (sequential coupling is folio-mediated) | Extended to hazard frames at C1448 resolution |
| C1399/C1400 (paragraph ordering null) | Paragraph boundaries show no hazard modulation effect |

### Implications

1. **Safety is line-scoped:** Each line independently opens safe and closes hazardous (C1463) without needing information about previous lines. The e->y safe pathway (C1457) is a within-line architectural feature.

2. **Folio = hazard budget:** The moderate raw correlations (~rho 0.23) reflect folio-level thematic consistency. High-hazard folios produce high-hazard lines throughout. The hazard budget is set at folio level, not adjusted line-by-line.

3. **Mode B is not special for cross-line dynamics:** Despite carrying 100% of forbidden violations (C1451), Mode B creates no cross-line hazard coupling. This means the forbidden transition topology is a WITHIN-LINE grammar constraint, not a cross-line state variable.

4. **Process interpretation:** If the system represents thermal control, each line encodes a self-contained control cycle. The operator does not need to remember the previous cycle's hazard exposure -- the next cycle's safety margin is pre-determined by the folio's overall hazard budget (C458: hazard clamped CV=0.11, recovery free CV=0.82).

## Quality Notes

- All 7 pre-registered tests completed plus shuffle control
- Within-folio permutation provides strong null control (500 shuffles)
- Mode-stratified analysis leverages C1451 prediction for targeted test
- Autocorrelation lag structure distinguishes sequential from shared-environment correlation
- Fisher exact test for e->y recovery provides precise p-value
- Consistent with all prior cross-line independence findings (C670, C672, C674, C681, C1429)
