# C929: ch/sh Sensory Modality Discrimination

## Statement

The prefixes **ch** and **sh** encode distinct sensory interaction modes: ch = **active state testing** (discrete checkpoint, interact with material), sh = **passive process monitoring** (continuous observation, no contact). This distinction is supported by five independent structural signals: within-line position (+0.120 delta), suffix pairing (checkpoint suffixes 1.87x enriched with ch), and operational context (sh precedes heat adjustment, ch precedes close/input/iterate actions).

## Tier

2 — Empirical, multi-signal convergence

## Scope

B (morphology, prefix semantics)

## Evidence

### Test: ch vs sh Within-Line Position
- **ch mean position:** 0.515 (evenly distributed mid-to-late)
- **sh mean position:** 0.396 (front-loaded, 33% in first 20% of line)
- **Delta:** +0.120 (ch appears 12.0 percentage points later)
- For unique middles: delta widens to +0.156 (ch=0.610, sh=0.454)

### Test: Suffix Pairing
- ch + checkpoint suffixes (-aiin/-ain): **7.3%** vs sh 3.9% (1.87x)
- ch + -ar (close): **4.6%** vs sh 2.7% (1.67x)
- ch + -al (complete): **3.8%** vs sh 2.4% (1.59x)
- ch + -am (finalize): **1.2%** vs sh 0.5% (2.33x)
- ch + -s (next/boundary): **3.1%** vs sh 1.8% (1.70x)
- sh + -edy (thorough): sh **5.6%** vs ch 4.2% (0.74x)
- sh + bare (no suffix): sh **59.0%** vs ch 46.9% — sh more often unsuffixed

### Test: Operational Neighbor Context (strongest signal)
**sh is FOLLOWED BY:**
- heat: **18.3%** (vs ch 10.6%) — observe, then adjust heat
- sustained heat: **4.0%** (vs ch 1.6%) — monitor fire specifically

**ch is FOLLOWED BY:**
- close: **6.6%** (vs sh 4.3%) — test, then seal
- input: **4.2%** (vs sh 2.1%, 1.98x) — test, then add material
- iterate: **3.1%** (vs sh 1.5%, 2.01x) — test, then repeat
- check: **5.8%** (vs sh 3.8%) — test chains (multiple checks)

### Test: Regime Distribution
- ch/sh ratio highest in R2 (1.98x) — balneum marie requires opening sealed vessels to test
- Both peak in R3 overall — direct fire needs both monitoring and testing
- ch rate is always higher than sh (ch=14.5-18.7%, sh=6.5-11.7%)

## Brunschwig Alignment

| Brunschwig check | Mode | Voynich prefix | Rationale |
|---|---|---|---|
| Drip rate watching | Continuous visual | **sh** | Watch, then adjust heat |
| Fire intensity monitoring | Continuous visual | **sh** | Observe, feed back to heat |
| Color/clarity monitoring | Continuous visual | **sh** | Visual, no contact |
| Finger test | Discrete touch | **ch** | Test, then decide |
| Taste test | Discrete taste | **ch** | Test, then act |
| Thumbnail viscosity | Discrete touch | **ch** | Test, accept/reject |
| Cloudiness inspection | Discrete visual | **ch** | Inspect sample, pass/fail |

The ch/sh distinction maps to Brunschwig's fundamental procedural split between **continuous process monitoring** (watching the apparatus) and **discrete state testing** (sampling the product).

## Functional Model

```
sh + [MIDDLE] + suffix = "monitor [operation] [outcome]"
  → feeds into HEAT ADJUSTMENT decisions
  → front-loaded in instruction lines (position 0.396)
  → continuous, often bare (no explicit verification needed)

ch + [MIDDLE] + suffix = "test [operation] [checkpoint]"
  → feeds into CLOSE/INPUT/ITERATE decisions
  → mid-to-late in instruction lines (position 0.515)
  → discrete, checkpoint-suffixed (binary outcome gates next action)
```

## Prior Constraints

- C645: ch at 75.2% post-hazard frequency (confirming active verification role)
- C408-409: ch and sh as prefix sisters (shared derivational family)
- C412: ch in precision mode (discrete testing aligns with precision)
- C911: prefix-middle compatibility rules (both ch and sh combine with all kernel families)

## Falsification

Would be falsified if:
1. ch and sh show identical positional distributions (delta < 0.02)
2. Suffix pairing shows no discrimination (checkpoint ratio < 1.2x)
3. Operational neighbors are identical (same following-operation profile)
4. An alternative explanation accounts for all five signals simultaneously
