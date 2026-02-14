# C1024: Structural Directionality — MIDDLE Carries Execution Asymmetry, PREFIX Is Symmetric Router

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** STRUCTURAL_DIRECTIONALITY (Phase 347)
**Depends on:** C391 (conditional entropy symmetry), C886 (transition probability directionality), C1023 (PREFIX load-bearing), C521 (kernel one-way valves)

---

## Finding

Forward-backward asymmetry decomposition reveals that execution directionality (C886) resides in the MIDDLE layer, not PREFIX. PREFIX routing is symmetric (consistent with C391's bidirectional constraint structure and C1023's macro-state routing role). MIDDLE carries 4x more directional asymmetry than PREFIX. FL tokens show the highest role-specific asymmetry (consistent with SOURCE-biased flow control). Verdict: WEAK_ASYMMETRY (1/5 pre-registered predictions confirmed).

---

## Results

| Test | Prediction | Result | Verdict |
|------|-----------|--------|---------|
| T1: Class-level bigram JSD | JSD > 0.001 | JSD = 0.089 | **PASS** |
| T2: PREFIX asymmetry > MIDDLE (1.5x) | PREFIX/MIDDLE >= 1.5x | Ratio = 0.25x (MIDDLE 4x higher) | FAIL |
| T3: CC highest role asymmetry | CC = #1 | FL = #1, CC = #4 | FAIL |
| T4: FL_HAZ > FL_SAFE | FL_HAZ more asymmetric | FL_SAFE 6.4x higher (small-sample artifact) | FAIL |
| T5: Shuffle collapses asymmetry <10% | Null/real < 0.10 | Null/real = 0.64 | FAIL |

---

## Key Findings

### MIDDLE is the directional executor

Component-level mutual information asymmetry (MI(comp→next class) - MI(comp→prev class)):

| Component | MI forward | MI backward | Asymmetry | |Asymmetry| |
|-----------|-----------|-------------|-----------|------------|
| PREFIX | 0.153 bits | 0.171 bits | -0.018 | 0.018 |
| MIDDLE | 0.312 bits | 0.242 bits | **+0.070** | **0.070** |
| SUFFIX | 0.103 bits | 0.085 bits | +0.018 | 0.018 |

MIDDLE predicts the next class 0.070 bits better than the previous class. PREFIX predicts the previous class 0.018 bits better than the next. This means:
- **MIDDLE is forward-biased** — knowing the current action tells you more about what comes next than what came before
- **PREFIX is weakly backward-biased** — knowing the current routing position tells you slightly more about what came before
- **SUFFIX is weakly forward-biased** — minimal directional contribution

### PREFIX is a symmetric router

PREFIX's near-zero asymmetry (0.018 bits, weakly backward-biased) is consistent with:
- C391: Constraint predictability is symmetric (H(X|past) = H(X|future))
- C1023: PREFIX creates macro-state topology (routing is positional, not directional)

PREFIX establishes WHERE in the state space a token operates; this is equally knowable from either temporal direction. MIDDLE specifies WHAT action to perform; this has inherent temporal direction (heat → monitor → cool).

### FL tokens are most directionally asymmetric

Role-specific mean per-class JSD (forward vs reverse transition distributions):

| Role | Mean JSD | Rank |
|------|---------|------|
| FL | 0.311 | 1 |
| AX | 0.211 | 2 |
| EN | 0.183 | 3 |
| CC | 0.102 | 4 |
| FQ | 0.071 | 5 |

FL tokens (flow control operators) show the highest directional asymmetry, consistent with their SOURCE-biased hazard profile (BCSC: FL initiates 4.5x more forbidden transitions than it receives). CC tokens are NOT the most asymmetric — they mark execution boundaries symmetrically from either direction.

### Finite-sample sparsity dominates raw JSD

T5 null control: within-line shuffled sequences retain 64% of the measured JSD. This means most of the raw JSD metric reflects sparsity noise from rare bigrams (many of the 49×49 = 2,401 possible bigrams have <5 observations). The genuine sequential contribution is 36% above the null floor, which is statistically significant (z > 13 relative to null std of 0.0023) but smaller than predicted.

---

## Resolution of C391/C886 Tension

The apparent tension between symmetric constraint entropy (C391) and directional transition probabilities (C886) is now resolved:

| Layer | Property | Source |
|-------|---------|--------|
| PREFIX (routing) | Symmetric | Creates bidirectional constraint structure |
| MIDDLE (execution) | Directional | Actions have temporal ordering |
| Combined | Symmetric entropy, directional probabilities | PREFIX symmetry governs aggregate predictability; MIDDLE directionality governs specific transitions |

The grammar's constraints (what transitions are legal) are symmetric because they're mediated by PREFIX routing. The grammar's execution (which transitions are used) is asymmetric because it's mediated by MIDDLE action ordering.

---

## Pre-Registered Prediction Scorecard

| Prediction | Expected | Actual | Match |
|-----------|---------|--------|-------|
| P1: Bigram JSD > 0.001 | PASS | PASS (0.089) | Yes |
| P2: PREFIX/MIDDLE >= 1.5x | PASS | FAIL (0.25x) | No — MIDDLE dominates 4x |
| P3: CC highest asymmetry | PASS | FAIL (FL is #1) | No — FL SOURCE bias |
| P4: FL_HAZ > FL_SAFE | PASS | FAIL (reversed) | No — small-sample artifact |
| P5: Null < 10% of real | PASS | FAIL (64%) | No — sparsity dominance |

1/5 predictions correct. Overall hierarchy prediction wrong (expected PREFIX-mediated, found MIDDLE-mediated). But the result is more informative than the prediction: it cleanly decomposes the C391/C886 tension by morphological layer.

---

## Data

- Script: `phases/STRUCTURAL_DIRECTIONALITY/scripts/structural_directionality.py`
- Results: `phases/STRUCTURAL_DIRECTIONALITY/results/structural_directionality.json`
- Tokens: 16,054 classified B tokens across 2,409 lines
- Transitions: 13,645 within-line bigrams
