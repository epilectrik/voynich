# C1023: Structural Necessity Ablation — PREFIX Routing Is Sole Load-Bearing Macro Component

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** STRUCTURAL_NECESSITY_ABLATION (Phase 346)
**Depends on:** C1010 (6-state automaton), C1015 (PREFIX MDL compression), C978 (spectral gap), C979 (REGIME modulation), C1007 (gatekeeper enrichment), C586 (FL split), C109 (forbidden transitions)

---

## Finding

Counterfactual ablation of 4 structural components (6 sub-tests) reveals a clear necessity hierarchy for the 6-state macro-automaton (C1010). **PREFIX→state content routing is the sole load-bearing component**, creating 78-81% of non-random transition structure. All other tested components (FL hazard/safe split, gatekeeper classes, within-state PREFIX routing, REGIME conditioning) are decorative at the macro level.

---

## Method

Shared ablation engine: each test modifies the token stream, then measures spectral gap, forbidden transition count, AXM dwell statistics, and exit entropy against baseline. Metric: **non-random structure** = 1 - spectral_gap. Baseline: 0.1062 (spectral gap 0.894).

---

## Results

| Test | Ablation | Key Metric | Value | Verdict |
|------|----------|-----------|-------|---------|
| T1 | Merge FL_HAZ + FL_SAFE → single FL | Spectral gap Δ | -0.34% | DECORATIVE |
| T2 | Gatekeeper exit destination JSD | Gatekeeper vs non-GK exits | JSD = 0.0014 | DECORATIVE |
| T3a | Shuffle PREFIX within macro-state | Structure loss | 0.0% | DECORATIVE |
| T3b | Shuffle PREFIX within position quintile + state reassignment | Structure loss | 77.8% | LOAD-BEARING |
| T3c | Shuffle PREFIX globally + state reassignment | Structure loss | 80.7% | LOAD-BEARING |
| T4 | Pool all 4 REGIMEs | Pooled vs per-REGIME spectral gap | 1.1% diff | DECORATIVE |

**Null controls:** T1 — 100 random state-pair merges (null mean=0.898, std=0.003, z=-2.39). T2 — 100 random 5-class pseudo-gatekeeper sets (null JSD mean=0.0024, std=0.0015, z=-0.70). T3 — 20 runs per variant for stability.

---

## Key Findings

### PREFIX routing is the dominant structural creator

T3b/T3c destroy 78-81% of non-random transition structure. The spectral gap INCREASES from 0.894 to 0.976-0.979 (chain becomes nearly random). PREFIX routing creates the ordered non-random transitions that define the macro-automaton's topology.

The difference between T3b (within-position, 77.8%) and T3c (global, 80.7%) is only 2.9pp — positional constraint contributes negligibly beyond content routing. The difference between T3a (within-state, 0.0%) and T3b (77.8%) is the entire effect — the PREFIX→state assignment is what matters.

### FL split is topologically negligible

Merging FL_HAZ and FL_SAFE changes spectral gap by only -0.34%. The z-score of -2.39 vs null state merges confirms the split carries statistically real information (not noise), but it is structurally negligible. The FL states contain only ~4.7% of tokens (C582), limiting topological impact.

### Gatekeepers are markers, not mechanisms

Gatekeeper classes {15,20,21,22,25} are enriched 1.58x at AXM exit boundaries (4.3% at exits vs 2.7% at interior). However, exit DESTINATIONS are indistinguishable: JSD = 0.0014 (BELOW the null mean of 0.0024). Whether a gatekeeper or non-gatekeeper is the last AXM token before exit, the chain exits to FQ at ~57%, CC at ~14%, FL_HAZ at ~17%, etc. identically. Gatekeepers mark exits but do not channel them.

### REGIME modulates weights, not topology

Per-REGIME spectral gaps range from 0.843 (REGIME_2) to 0.918 (REGIME_4), with the pooled value at 0.894. The 1.1% difference confirms C979: REGIME conditioning shifts transition probabilities but preserves the topological skeleton.

---

## Methodological Note

Initial implementation shuffled PREFIX without reassigning macro-state, producing tautologically invariant spectral gap (state is determined by class, which doesn't change when PREFIX changes). The fix: after shuffling PREFIX, sample each token's new state from P(state | new_prefix) built from the original data. This correctly tests whether PREFIX→state routing is causally necessary.

---

## Structural Hierarchy

```
LOAD-BEARING:  PREFIX→state content routing (78-81% of non-random structure)
DECORATIVE:    FL split (0.3%), Gatekeepers (JSD 0.001), Within-state routing (0%), REGIME (1.1%)
```

The macro-automaton's topology is created primarily by PREFIX class composition. MIDDLE determines the specific instruction; PREFIX determines which part of the state space the instruction operates in.

---

## Pre-Registered Prediction Scorecard

| Test | Predicted | Actual | Match |
|------|-----------|--------|-------|
| T1 | PARTIAL (5-15% drop) | DECORATIVE (0.3%) | No — more decorative |
| T2 | PARTIAL (uncertain) | DECORATIVE (JSD 0.001) | No — more decorative |
| T3a | MODERATE (10-25% drop) | DECORATIVE (0%) | No — tautological at this level |
| T3b | LOAD-BEARING (30-50% drop) | LOAD-BEARING (78% structure loss) | Yes |
| T3c | LOAD-BEARING (catastrophic) | LOAD-BEARING (81% structure loss) | Yes |
| T4 | DECORATIVE (<5%) | DECORATIVE (1.1%) | Yes |

3/6 verdict matches. Overall hierarchy prediction (PREFIX >> FL ≈ gatekeepers >> REGIME) confirmed. Mechanism was directionally wrong for PREFIX: structure loss manifests as spectral gap INCREASE (chain becomes random), not decrease.

---

## Data

- Script: `phases/STRUCTURAL_NECESSITY_ABLATION/scripts/structural_necessity_ablation.py`
- Results: `phases/STRUCTURAL_NECESSITY_ABLATION/results/structural_necessity_ablation.json`
- Tokens analyzed: 16,054 classified B tokens
- Baseline: spectral gap 0.894, 13 forbidden transitions, exit entropy 1.744 bits
