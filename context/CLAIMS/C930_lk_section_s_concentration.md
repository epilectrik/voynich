# C930: lk Prefix Section-S Concentration and Fire-Method Specificity

## Statement

The prefix **lk** is concentrated 81.7% in section S (stellar), with 1.77x enrichment over baseline — the strongest section concentration of any common prefix. lk completely avoids core kernel MIDDLEs (k, t, ke, iin = 0 occurrences) and exclusively selects observation/checkpoint MIDDLEs (aiin 4.7x, ain 4.5x, ch 4.2x, ech 9.3x). This profile identifies lk as a **fire-method monitoring operator** (MONITOR_DRIPS / REGULATE_FIRE) that is apparatus-specific to fire-based distillation, not balneum mariae.

## Tier

2 — Empirical, multi-signal convergence

## Scope

B (prefix semantics, section distribution, apparatus mapping)

## Evidence

### Test: Section Distribution

| Section | lk tokens | lk rate | Enrichment |
|---------|-----------|---------|------------|
| **S (stellar)** | **358** | **3.4%** | **1.77x** |
| C (cosmological) | 18 | 1.2% | 0.52x |
| B (biological) | 48 | 0.7% | 0.30x |
| T (text) | 4 | 0.6% | 0.26x |
| H (herbal) | 10 | 0.3% | 0.13x |

Top 6 folios by lk rate are ALL section S: f115v (7.8%), f111r (6.8%), f113r (6.2%), f107v (6.2%), f111v (4.6%), f113v (4.4%).

### Test: Positional Behavior

- LINE_INITIAL: **0.3%** of prefixed tokens (effectively zero)
- LINE_MID: 2.6%
- LINE_FINAL: 2.2%

lk never opens a procedure. It is a pure mid-execution operator.

### Test: MIDDLE Selectivity (strongest signal)

**SELECTED (observation/checkpoint MIDDLEs):**

| MIDDLE | lk count / total | Enrichment | Semantic class |
|--------|-----------------|------------|----------------|
| ech | 7 / 33 | 9.3x | test-observation |
| aiin | 51 / 477 | 4.7x | checkpoint |
| ain | 35 / 340 | 4.5x | checkpoint |
| ch | 33 / 349 | 4.2x | test/check |
| eed | 8 / 83 | 4.2x | extended observation |
| eeo | 12 / 129 | 4.1x | observation |
| ar | 30 / 422 | 3.1x | close-in |
| eey | 40 / 614 | 2.9x | extended observation |
| e | 53 / 838 | 2.8x | equilibration |

**COMPLETELY AVOIDED (core kernel operators, all = 0):**
- k (0/2068), t (0/562), iin (0/560), r (0/533), dy (0/481), ke (0/421), d (0/288), in (0/263), ck (0/185), ek (0/162)

This is a binary partition: lk operates on checkpoint/observation targets and never touches thermal execution machinery.

### Test: Differentiation from ch/sh

ch and sh share Jaccard similarity of 0.82 on top-10 MIDDLEs. lk shares only **0.18** with either. lk is structurally distinct from the ch/sh monitoring family — it operates on completely different objects.

### Test: Co-occurrence

lk co-occurs on the same line with **ke** (1.31x enriched) and **lch** (1.39x enriched) more than expected. Both are low-frequency, functionally specific prefixes.

## Brunschwig Alignment

| lk property | Brunschwig match |
|------------|------------------|
| WORK phase, mid-execution only | Mid-distillation operations |
| Never line-initial | Not a setup/preparation operation |
| Selects checkpoint MIDDLEs (aiin, ain) | Drip-counting checkpoints |
| Selects test MIDDLEs (ch, ech) | State verification during monitoring |
| Avoids thermal operators (k, t, ke) | Not heating — observing heat effects |
| 82% section S, near-zero in H/B | **Fire-method specific** |

### Apparatus Discrimination Hypothesis

lk's section distribution implies:
- **Section S = fire-method distillation** (requires drip monitoring, fire regulation)
- **Section B = water-bath (balneum mariae) distillation** (requires replenishment, finger test — different operations, not lk)
- **Section H = gentle/precision distillation** (lowest fire, balneum mariae — lk near-zero confirms)

In Brunschwig, fire methods (Degrees 2-3) require:
- MONITOR_DRIPS: Watch drop rate at spout (timing/quality cue)
- REGULATE_FIRE: Open/close air vents to control temperature

These operations do NOT apply to balneum mariae (Degree 1), which uses:
- MONITOR_TEMP: Finger test for water temperature
- REPLENISH: Refill water bath with warm water

lk encodes the fire-specific monitoring family. Its absence from B and H sections aligns with those sections using gentler, non-fire methods.

## Functional Model

```
lk + [checkpoint MIDDLE] + suffix = "monitor-fire-state [observation target] [control flow]"
  -> appears in MEDIAL/LATE line positions (during active distillation)
  -> concentrated in section S (fire-method folios)
  -> never initiates a procedure
  -> selects gate/checkpoint objects (aiin, ain, ch, ar)
  -> avoids execution objects (k, t, ke)
```

## Prior Constraints

- C929: ch/sh sensory modality discrimination (lk is structurally distinct from both)
- C494: REGIME_4 precision axis (section H = gentle+precise, confirms lk absence)
- C556: prefix phase mapping (lk = WORK phase)
- C371-374: prefix role taxonomy (lk = EN_KERNEL)

## Source

`phases/BRUNSCHWIG_APPARATUS_MAPPING/` (lk_deep_analysis.py, lk_apparatus_crossref.py)
Results: `results/section_prefix_apparatus.json`

## Falsification

Would be falsified if:
1. lk shows uniform section distribution (S share < 40%)
2. lk combines freely with core kernel MIDDLEs (k, t, ke ratio > 0.5x)
3. An alternative explanation accounts for the section concentration without apparatus specificity
4. Section S is shown to NOT correspond to fire-method distillation by independent evidence
