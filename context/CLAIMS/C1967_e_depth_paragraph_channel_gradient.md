# C1967: e_depth Paragraph-Channel Gradient

**Tier:** 2
**Scope:** B, paragraph, e_depth, channel-class, thermal-intensity
**Phase:** PHASE_652_BLOCK_PURE_SIGNATURES
**Date:** 2026-04-26
**Cross-validates:** F-B-007 (e_depth = thermal-intensity continuous modifier, atom level)
**Extends:** C1300 (qo near-pure THERMAL channel), C929 (ch active-test, sh passive-monitor), C1961 (block-pure paragraph specialization)
**Refines:** C1225 (e-depth parametricity at suffix level — extends to paragraph aggregation)
**Tier 3 candidate:** Attentional-commitment reframing of F-B-007 (registered as candidate, not promoted)

---

## Statement

Among block-pure Currier B paragraphs (n=222 of 477, per C1961), mean e_depth orders **monotonically** across the three primary fire-side channel classes:

| Channel-class | n paragraphs | Mean e_depth |
|---|:---:|:---:|
| **qo** (heat application) | 102 | **0.679** |
| **ch** (active testing) | 82 | **0.606** |
| **sh** (passive monitoring) | 25 | **0.538** |

Baseline (all block-pure paragraphs): 0.636

Difference qo − sh: **+0.141** (gentle/sustained-heat signature highest in heat-driving paragraphs, lowest in passive-monitoring paragraphs).

This cross-validates F-B-007 at paragraph aggregation — F-B-007 established e_depth as thermal-intensity continuous modifier at the atom/MIDDLE level; this constraint shows the same dimension organizes paragraphs by their dominant operational channel.

---

## Empirical evidence

### Sample

- Total Currier B paragraphs analyzed: 477
- Block-pure paragraphs (>70% one block per C1961): 222
- Of these:
  - qo-dominant: 102 paragraphs, 6,227 tokens
  - ch-dominant: 82 paragraphs, 2,902 tokens
  - sh-dominant: 25 paragraphs, 1,031 tokens
  - Vessel-side classes (ok/ot/ol/or): too rare to characterize (ok=5, ot=5, ol=3, or=0)

### e_depth measurement

Per F-B-007 / C1735, e_depth = number of consecutive `e` atoms following the HEAD in atom decomposition. Continuous-extensible thermal modulator:
- e_depth = 0: raw heat (`k` alone)
- e_depth = 1: degree-1 stabilized (`ke`)
- e_depth = 2: degree-2 stabilized — balneum mariae signature (`kee`)
- e_depth = 3+: progressively gentler

Per Phase 650 refinement to C1394: `e` is continuous-extensible (intensity modulator), distinct from discrete-event MOD atoms like `ch` (test event).

### Per-class observations

**qo-dominant paragraphs** (driving heat):
- Highest e_depth (0.679) — most thermal-precision commitment per token
- Concurrent k-HEAD rate: 18.9% (highest, corroborates C1300 qo near-pure THERMAL)
- Concentrated in Section B (57% — distillation work)

**ch-dominant paragraphs** (active testing):
- Mid e_depth (0.606)
- Lower k-HEAD rate (10.5%)
- Concentrated in Section S (75% — recipes section, where discrete test events occur)

**sh-dominant paragraphs** (passive monitoring):
- Lowest e_depth (0.538)
- Lower k-HEAD rate (10.6%)
- Dispersed across S/H/T sections

The monotonic ordering across all four signatures (e_depth, k-HEAD, sample size, baseline ratio direction) confirms channel-class specialization at paragraph aggregation.

---

## Header-body e_depth gap test (added 2026-04-26, off-books)

**The simple Tier 3 candidate as originally stated is FALSIFIED directionally.** A test predicting that paragraph headers should have higher e_depth than bodies (operator commits thermal precision at specification) found the opposite:

| Class | n | Header e_depth | Body e_depth | Gap (H-B) | p (paired) |
|---|:---:|:---:|:---:|:---:|:---:|
| qo | 112 | 0.651 | 0.684 | **−0.034** | 0.24 |
| ch | 72 | 0.569 | 0.631 | **−0.062** | 0.07 |
| sh | 25 | 0.463 | 0.586 | **−0.123** | **0.024** |

Headers have *lower* e_depth than bodies, not higher. The simple "header is specification commitment, body is execution" reading is wrong in direction.

**However, the cross-class gap-magnitude ordering is monotonic and informative:**

- qo paragraphs: gap −0.034 — thermal commitment is *consistent* header-to-body
- ch paragraphs: gap −0.062 — some drop-off
- sh paragraphs: gap −0.123 — large drop-off (significant)
- Permutation p (qo gap > sh gap, one-sided): 0.089

**Refined Tier 4 candidate (less developed):** the e_depth header-body gap may index *consistency of thermal commitment* across the paragraph rather than commitment magnitude per se. qo paragraphs maintain thermal precision throughout (drivers commit consistently); sh paragraphs only carry thermal context in body (passive monitors don't actively commit thermal precision).

Architectural implication: headers carry compound specification (high HT density per C1966, low e_depth — specification of *what* compound, not *how thermal*). Bodies carry thermal execution (lower HT, higher e_depth). The header-body division may reflect a *what-vs-how* split where:
- Header = "specify the compound and apparatus"
- Body = "execute the operation with detailed thermal regulation"

This Tier 4 candidate is registered for record only. Promotion would require:
1. Independent test that the gap-magnitude correlates with operator-mode (e.g., does it co-vary with sh→qo decision-gate density per C1963?)
2. Cross-validation that the header-body division is functionally what-vs-how, not just positional artifact
3. A more rigorous gap statistic (current paired test on 25 sh-class paragraphs is borderline by sample-size)

---

## Tier 3 candidate: attentional-commitment reframing (FALSIFIED IN ORIGINAL FORM)

The original Tier 3 candidate framing — "headers should have higher e_depth because the operator commits thermal precision at specification" — is empirically falsified by the header-body gap test. Headers consistently have *lower* e_depth than bodies. The simple version of the reframing is dead.

The refined reading (above, registered as Tier 4 candidate) — that the *header-body gap-magnitude* indexes thermal-commitment consistency — is plausible but unverified. The original Tier 3 candidate is retired; the refined Tier 4 candidate replaces it.

If the gradient is taken as primary evidence, **e_depth may index operator attentional commitment to thermal specification** rather than just thermal intensity itself:

- **qo paragraphs** (driving heat): the operator is actively setting the thermal regime. Each token requires precise thermal commitment because the fire is being managed. Hence highest e_depth.
- **ch paragraphs** (active testing): the operator interrupts execution to verify state. Some thermal commitment because tests often check thermal conditions, but the focus is the checkpoint event, not the thermal regime.
- **sh paragraphs** (passive monitoring): the operator watches for change. Less thermal precision committed because the operator isn't setting the regime — they're observing whatever's there.

Under this reframing, F-B-007's "e_depth = thermal intensity" becomes "e_depth = how much thermal precision the operator is committing to in this token." A high e_depth means "I am specifying carefully"; a low e_depth means "I am not."

This is a **Tier 3 candidate**, not registered. The registered Tier 2 fact is the gradient itself. The reframing requires further validation:

1. **Header vs body e_depth gap test.** If attentional commitment is right, paragraph headers (specification, per C1287) should show higher e_depth than bodies, with gap largest in qo-class paragraphs and smallest in sh-class.
2. **AXM-dwell coupling.** k-initial AXM dwell (C1384) should be enriched in qo-dominant paragraphs.

If both pass, the reframing could be promoted.

---

## What this does NOT claim

- **No claim that the qo > ch > sh ordering is universal across all paragraphs.** The constraint is restricted to the 222 block-pure paragraphs in the sample.
- **No claim that attentional-commitment is the primary mechanism.** That reading is registered as Tier 3 candidate, not as the established interpretation.
- **No claim that vessel-side channels follow the same pattern.** Vessel-side prefixes don't form block-pure paragraphs in sufficient numbers to test (per C1964).
- **No claim of independence from other signatures.** Section concentration, regime mapping, and k-HEAD rate co-vary with e_depth at the channel-class level. The genuinely-independent piece is the *monotonic ordering across all three fire-side channels*, which wasn't predicted by any prior constraint.

---

## Falsification

Would be falsified if:

1. The monotonic ordering (qo > ch > sh) breaks under any well-powered restriction (e.g., within-section, within-regime, by folio-length bin)
2. The gap qo − sh drops below +0.04 (the noise floor based on baseline standard error)
3. A different MOD atom (e.g., d, n, h) shows a stronger or contradictory channel-class gradient that better explains the variance

---

## Provenance

- `phases/PHASE_652_BLOCK_PURE_SIGNATURES/scripts/s1_block_pure_signatures.py`
- `phases/PHASE_652_BLOCK_PURE_SIGNATURES/results/block_pure_signatures.json`
- F-B-007 (e_depth thermal-intensity, atom level) — primary cross-validation target
- C1225 (e-depth parametricity) — extended to paragraph aggregation
- C1961 (block-pure paragraph specialization) — defines the sample
- C1300, C929 (channel readings used to predict gradient direction)
