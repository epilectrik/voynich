# Phase 558: SINGLE_FOLIO_EXECUTION_COHERENCE

## Verdict: FAIL

**FC3 triggered:** Random B-corpus tokens produce execution indistinguishable from f43v's real tokens. The supervisory mapping lacks folio specificity.

## What This Phase Tested

Can a single Voynich folio (f43v) function as a coherent supervisory control program over a shared thermal plant, with:
- Tokens emitting **weighted supervisory contributions** (not direct actuator commands)
- A **supervisor** aggregating token weights into admissible control envelopes
- **Paragraphs as concurrent subroutines** with constraint intersection
- An **explicit closure latch** (SUP_CLOSING) for line-level safety
- A **low-level controller** acting within supervisor-determined bounds

## Architecture

```
Token → weighted emission {domain, permission, guard, routing, scope}
  → Line supervisor (aggregation + position modulation + closure latch)
    → Paragraph arbitration (INTERSECTION or SCHEDULER model)
      → Actuator bounds [Q_lo, Q_hi]
        → Controller (P-control or MPC)
          → Thermal plant ODE
```

Two levels of indirection between tokens and plant actuation. All weight tables pre-registered from Tier 2 constraints.

## Results Summary

| Criterion | Result | Key Metric |
|-----------|--------|-----------|
| C1: Execution Coherence | **PASS** | 100% viability, 0 NaN, 0 contradictions |
| C2: Safety Coherence | FAIL | Spearman rho = 0.008 (no CLOSE gradient) |
| C3: Paragraph Differentiation | FAIL | Perm p = 0.887 (paragraphs not different) |
| C4: Token-Level Fit | FAIL | 1/6 directional tests pass |
| C5a: Token-shuffle degrades | **PASS** | Full viability 1.0 > shuffled 0.984 |
| C5b: Line-shuffle preserves | **PASS** | Line-local metrics preserved |
| C5c: Random-token degrades | FAIL | Random tokens perform equally well |

### Failure Conditions

| FC | Status | Description |
|----|--------|-------------|
| FC1 | clear | Plant never diverges |
| FC2 | clear | Token order matters (C5a pass) |
| **FC3** | **TRIGGERED** | Random tokens equal to real (folio specificity absent) |
| FC4 | clear | Line-shuffle doesn't destroy safety |

### Models and Controllers

| Configuration | Viability | Mean Q | Mean Error | Closure Rate |
|--------------|-----------|--------|-----------|-------------|
| INTERSECTION_P | 1.000 | 0.077 | 0.764 | 100% |
| INTERSECTION_MPC | 1.000 | 0.077 | 0.764 | 100% |
| SCHEDULER_P | 1.000 | 0.085 | 0.746 | 100% |
| SCHEDULER_MPC | 1.000 | 0.085 | 0.746 | 100% |

P-control and MPC produce identical results — supervisor bounds are so tight that controller choice is irrelevant. INTERSECTION and SCHEDULER differ slightly (SCHEDULER allows marginally more heating).

## Diagnosis

### Why FC3 triggered: the mapping is too homogeneous

The core problem is that the weighted supervisory emissions from f43v tokens are nearly identical to those from random B-corpus tokens. This happens because:

1. **CONTAIN dominates everything.** f43v's HEAD distribution is: e=60, headless=45, o=22, a=16, k=7, t=3. The dominant HEADs (e, headless, o) all map primarily to STABILIZE/CONTAIN/ARRANGE — non-thermal domains. Only 10 of 153 tokens (6.5%) have THERMAL-primary HEADs (k or t).

2. **The B-corpus average looks similar.** Because the weight tables are **general** (apply to any B folio), and the B corpus has similar HEAD/PREFIX distributions across folios, random B tokens produce similar aggregate supervisory profiles.

3. **The supervisor conversion formula crushes differences.** `Q_hi = THERMAL_weight × ALLOW_weight × Q_MAX` means that with THERMAL ~0.12 and ALLOW ~0.37, Q_hi ≈ 0.067 — barely 4.5% of Q_MAX. The plant can never approach T_target (max T = 0.55 vs target 1.05). At such low Q, all tokens — real or random — produce essentially the same behavior: gentle warming that never reaches operating temperature.

4. **Closure activates universally.** SUP_CLOSING latches at Q4 for every line, in every condition. It's never NOT triggered. This makes closure rate useless as a discriminator.

### What the failure means

The failure is NOT that folio-level supervisory control is wrong. The failure is that **the weight tables don't produce enough dynamic range to discriminate between real tokens and random tokens.** The mapping correctly identifies CONTAIN/STABILIZE as dominant for f43v, but it does so for ALL B-corpus tokens equally.

The problem is at the **Voynich-to-supervisor mapping interface**, not at the supervisor or plant level.

### What passed and what that means

- **C1 pass:** The architecture is well-formed. No divergence, no contradictions.
- **C5a pass:** Token ORDER within lines matters (shuffling degrades viability from 1.0 to 0.984). This confirms that the SPEC→WORK→CLOSE line structure is real — it's just too weak to differentiate folios.
- **C5b pass:** Line-shuffle preserves line-local metrics, consistent with C1429 (cross-line category independence).
- **D3 pass (only passing C4 test):** a-HEAD and r-terminal tokens have significantly higher INHIBIT weights than k/e-HEAD tokens (effect=0.252, p<10^-10). The hazard topology is correctly captured in the weight tables.

### What failed and why

- **C2 (safety gradient):** The Spearman rho between CLOSE weight and position is 0.008. There is no positional gradient in the weight tables because the same prefixes appear throughout lines. The gradient would need to come from positional PREFIX enrichment (C1426-C1428), but the weight tables don't weight by position — they only respond to what prefix IS, not where it IS.

- **C3 (paragraph differentiation):** The three paragraphs have nearly identical domain distributions (all CONTAIN-dominant, mean pairwise JSD = 0.011). The paragraph operational gradient (C1398) exists at the MIDDLE/HEAD level but gets averaged into similar supervisory profiles because CONTAIN/STABILIZE dominate for all three paragraphs.

- **C4 (directional fit):** 1/6 tests pass. The weight tables correctly capture hazard asymmetry (D3), but don't produce measurable gradients for THERMAL position (D1), CLOSE within-line (D2), guard blocking (D4), closure routing (D5), or paragraph-initial ALLOW (D6).

## Progression: Phases 555-558

| Phase | Approach | Verdict | Key Failure |
|-------|----------|---------|------------|
| 555 | Direct ODE match | FAIL | Wrong representational level |
| 556 | MPC + categories | FAIL | Wrong controller aggressiveness |
| 557 | Full supervisor FSM | FAIL | Aggregate mismatch |
| **558** | **Folio-level weighted supervisor** | **FAIL** | **Mapping too homogeneous** |

**Progress trajectory:** Each phase moved to the correct representational level (555→558: actuator → categories → FSM → weighted supervisor). Phase 558 got the architecture right (C1 pass) but the Voynich-to-supervisor interface doesn't produce enough specificity.

## What Would Fix This

The weight tables use **constraint-derived priors** that are intentionally general (apply to any B folio). To get folio specificity, the mapping would need to:

1. **Weight by context, not just morphology.** The same `ch` prefix might emit different supervisory weights depending on what HEAD it accompanies, what line position it's in, or what paragraph it's in. C1003 (pairwise sufficiency) supports this — slots interact.

2. **Use MIDDLE compound structure.** The current mapping only uses HEAD (first char of MIDDLE). But MIDDLEs like `edch`, `opcheodai`, `kchedy` have internal structure (C1393-C1395) that could carry more specific supervisory information.

3. **Build the mapping from data, not from priors.** Instead of pre-registering weight tables from constraint interpretation, train a lightweight model to predict supervisory categories from token features, validated against null baselines.

## Non-Circularity

| Component | Voynich Input |
|-----------|---------------|
| Plant ODE | NONE |
| Controllers | NONE |
| Supervisor logic | NONE |
| Weight tables | INDIRECT (Tier 2 constraints) |
| Token decomposition | ALL |
| Paragraph structure | ALL |
| Null baselines | NONE |

## Key Numbers

- Tokens decomposed: 153
- Paragraphs: 3 (verified from par_initial)
- HEAD distribution: e=60, headless=45, o=22, a=16, k=7, t=3
- Max temperature: 0.55 (target: 1.05)
- Mean Q: 0.077 (Q_MAX: 1.5) — 5.1% utilization
- Null viability range: 0.984-0.999
- Full viability: 1.000
- Execution time: 39.8s (444 runs)

## Files

| File | Description |
|------|-------------|
| `scripts/t1_folio_decomposition.py` | Token → weighted supervisory contributions |
| `scripts/t2_plant_execution.py` | Supervisor + controller + plant execution |
| `scripts/t3_coherence_scoring.py` | Score C1-C5 |
| `scripts/t4_synthesis.py` | Verdict |
| `results/t1_folio_decomposition.json` | Per-token weight vectors |
| `results/t2_plant_execution.json` | Execution traces |
| `results/t3_coherence_scoring.json` | Coherence scores |
| `results/t4_synthesis.json` | Final verdict |
