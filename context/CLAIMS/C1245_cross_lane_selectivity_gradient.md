# C1245: Cross-Lane Selectivity Gradient

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** EN_CROSS_LANE_PAIRING (Phase 444)
**Extends:** C1242 (cross-lane content prediction), C911 (PREFIX selectivity), C660 (selectivity spectrum)
**Relates to:** C576 (PREFIX gates MIDDLE subvocabulary), F-B-007 (extensible atom scaling)

---

## Statement

QO MIDDLEs span a 1.773-bit entropy range in their cross-lane CHSH partner selection (3.364 to 5.137 bits, marginal CHSH entropy = 5.241 bits). Rare QO MIDDLEs are highly selective (locked to 1-3 CHSH partners), common QO MIDDLEs are promiscuous (partner entropy near marginal). Selectivity correlates strongly with frequency (Spearman rho=0.665, p<0.0001).

| QO MIDDLE | N pairs | Partners | Entropy | Selectivity | Top partner |
|-----------|---------|----------|---------|-------------|-------------|
| ked (rare) | 26 | 14 | 3.364 | 1.56x | edy (31%) |
| te | 56 | 22 | 3.490 | 1.50x | edy (38%) |
| l | 241 | 40 | 3.692 | 1.42x | edy (31%) |
| ke | 260 | 56 | 4.420 | 1.19x | edy (25%) |
| k (common) | 1601 | 135 | 4.648 | 1.13x | edy (28%) |
| aiin (most promiscuous) | 210 | 61 | 5.137 | 1.02x | edy (12%) |

The selectivity gradient means: specialized operations require specific monitoring; generic operations accept any monitoring. This is a natural property of a control language — the common verbs are flexible, the rare verbs are precise.

Fisher exact with Bonferroni identifies 4 significantly enriched pairs (k-edy at 1.25x, k-ey at 1.27x, k-eck at 1.63x, l-ey at 1.96x) and 2 depleted (aiin-edy at 0.54x, k-ed at 0.58x). The MI signal (C1242: z=13.42) is diffuse — many small biases, not a few dominant pairings.

---

## E-depth cross-lane pattern

E-depth (e-atom count) shows matched intensity at the category level: multi-e QO tokens pair with multi-e CHSH tokens at 2.625x the expected rate (Fisher p<0.0001). The i-atom control is null (rho=0.009, p=0.49), confirming the e-depth signal is specific per C1205.

Within the e-containing subset (N=4235), the correlation inverts (rho=-0.262, p=3.9e-67): high-e QO pairs with low-e CHSH. Two-scale pattern: e-presence is matched, e-depth is complementary.

---

## Section/REGIME conditioning

Top enriched pairs show significant section and REGIME variation (4/6 significant after Bonferroni). k-edy concentrates in REGIME_1 (380/441 = 86%), l-ey is absent from HERBAL. This refines C821: line syntax topology is REGIME-invariant, but pair frequencies within the topology are domain-specific. Different procedures use different heat-measure combinations at different rates.

---

## Method

- 5,591 cross-lane pairs from 2,330 lines (Currier B, H-track)
- All pairs normalized to (QO_MIDDLE, CHSH_MIDDLE) regardless of direction
- Shannon entropy per QO MIDDLE (threshold: >= 20 pairs, N=36 qualifying)
- Fisher exact per cell with Bonferroni correction (166 cells with expected >= 5)
- Spearman correlation on e-depth/i-count/k-count across lanes

**Script:** `phases/EN_CROSS_LANE_PAIRING/scripts/cross_lane_pairing.py` (T1, T2, T3, T4, T5)
**Results:** `phases/EN_CROSS_LANE_PAIRING/results/cross_lane_pairing.json`
