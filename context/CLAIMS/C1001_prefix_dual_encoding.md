# C1001: PREFIX Dual Encoding — Content and Positional Grammar

**Tier:** 2 | **Scope:** B | **Phase:** PP_INFORMATION_DECOMPOSITION | **Date:** 2026-02-11

## Statement

PREFIX operates as a dual-axis encoder: it simultaneously selects **content** (lane, instruction class, suffix compatibility) and **line position** (where in a line a token may appear). MIDDLE is the primary operator for suffix and regime prediction, but PREFIX matches or exceeds MIDDLE for positional information (PREFIX R²=0.069 vs MIDDLE R²=0.062, PREFIX position dominance=51.3%). Conditional MI decomposition shows PREFIX adds significant unique information on 3/4 target variables (suffix, regime, position; permutation p<0.001 each). PREFIX positional grammar is regime-invariant for major PREFIXes (7/7 top PREFIXes folio-consistent) and defines clear line zones: line-initial (po, dch, so, tch, sh), line-final (ar, al, or, BARE, ot), and central (qo, ch, ok).

## Evidence

### T1: Conditional MI Decomposition
- I(MIDDLE; SUFFIX) = 1.24 bits (45.4% of H) vs I(PREFIX; SUFFIX) = 0.33 bits (12.0%)
- I(MIDDLE; REGIME) = 0.11 bits (7.1%) vs I(PREFIX; REGIME) = 0.04 bits (2.3%)
- **I(PREFIX; POSITION) = 0.09 bits (10.1%) ≈ I(MIDDLE; POSITION) = 0.09 bits (9.6%)**
- PREFIX unique contribution significant on 3/4 targets (perm p<0.001)
- PREFIX-SUFFIX redundancy = 0.63 bits (PREFIX partially determines suffix)
- PREFIX-MIDDLE show mild synergy for REGIME (-0.009 bits)

### T2: PREFIX Positional Grammar (CONFIRMED)
- 20/32 PREFIXes show non-uniform positional profiles (KS p<0.001)
- KW across top 10 PREFIXes: H=626, p=5.8e-129, eta²=0.032
- 37/45 pairwise separations significant (p<0.001)
- Extreme positional specialists:
  - `po`: 86.0% line-initial (Q1 concentration 4.30x)
  - `dch`: 73.1% initial (3.65x), `so`: 70.7% initial (3.56x)
  - `ar`: 61.0% line-final (Q5 concentration 3.05x)
  - `al`: 50.9% final (2.54x), `or`: 48.0% final (2.40x)
- R² variance decomposition:
  - PREFIX alone: 0.069, MIDDLE alone: 0.062
  - Additive (PREFIX+MIDDLE): 0.118
  - Full PP (with interaction): 0.168 (+0.051 interaction)
  - PREFIX unique: 0.056, MIDDLE unique: 0.049

### T3: PREFIX Sequential Grammar (PARTIAL)
- PREFIX transitions structured: chi²=2644, Cramér's V=0.060
- 19 forbidden PREFIX sequences, 35 enriched
- Strongest enrichment: sh→qo (+20.5 sigma)
- Strongest avoidance: BARE→qo (-14.4 sigma), sh↔ch mutual (-8.5/-7.5)
- Cross-component MI: I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits (current MIDDLE predicts next PREFIX)
- PREFIX sequential MI = 0.124 bits (10.4% of MIDDLE's 1.195 bits)

### T4: Regime Positional Stability (MOSTLY STABLE)
- 8/24 testable PREFIXes regime-stable (max JSD < 0.15)
- All 7 major PREFIXes (qo, BARE, ch, sh, ok, ot, da) are regime-stable
- 7/10 top PREFIXes folio-consistent (std < 0.10)
- PREFIX main effect: H=557, p=3.5e-116
- REGIME main effect: H=0.27, p=0.97 (ZERO regime effect on position)

### T5: Integrated Verdict
- Score: 3.08/4.0 — DUAL_ENCODING
- 3/4 dimensions show significant structure

## Positional Zone Map

| Zone | PREFIXes | Mean Position |
|------|----------|---------------|
| LINE-INITIAL | po (0.11), dch (0.17), so (0.19), to (0.27), tch (0.28), pch (0.30), sa (0.36), lsh (0.38), sh (0.40) | 0.11-0.40 |
| CENTRAL | qo (0.49), ke (0.49), ta (0.50), ch (0.52), da (0.52), lk (0.54), ok (0.54) | 0.49-0.54 |
| LINE-FINAL | BARE (0.56), ot (0.59), ol (0.56), ka (0.57), ko (0.64), or (0.66), al (0.69), ar (0.74) | 0.56-0.74 |

## Implications

- **Extends C661**: PREFIX transforms behavior (JSD=0.425) AND encodes line position
- **Extends C662**: PREFIX role reclassification (75% class reduction) operates alongside positional control
- **Confirms C660**: QO-predicting MIDDLEs are qo-locked (central position zone)
- **New**: PP is genuinely two-component — MIDDLE selects role identity, PREFIX selects execution position within the line
- **New**: sh→qo sequential enrichment (+20.5σ) combined with sh=initial, qo=central reveals procedural line structure: sh opens, qo continues
- **New**: I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits — cross-component sequential dependency; MIDDLE content constrains what PREFIX follows

## Provenance

- `phases/PP_INFORMATION_DECOMPOSITION/results/t1_conditional_mi_decomposition.json`
- `phases/PP_INFORMATION_DECOMPOSITION/results/t2_prefix_positional_grammar.json`
- `phases/PP_INFORMATION_DECOMPOSITION/results/t3_prefix_sequential_grammar.json`
- `phases/PP_INFORMATION_DECOMPOSITION/results/t4_prefix_regime_positional_stability.json`
- `phases/PP_INFORMATION_DECOMPOSITION/results/t5_integrated_verdict.json`
