# C1242: Cross-Lane Content Prediction

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** EN_LANE_CROSS_PREDICTION (Phase 443)
**Extends:** C544 (energy interleaving), C549 (interleaving significance), C577 (interleaving content-driven)
**Relates to:** C961 (WORK zone unordered within lane), C576 (QO/CHSH vocabulary bifurcation), C1200 (k/e state carryover)

---

## Statement

Adjacent cross-lane EN pairs show genuine MIDDLE co-occurrence (MI = 1.0632 bits, z_perm = 13.42, p < 0.001) but null within-lane sequential ordering (z_wl = 0.05). The specific QO MIDDLE predicts the specific CHSH MIDDLE (and vice versa) as a line-level co-occurrence property, not a sequential ordering effect. Kernel-atom routing at lane boundaries is massively significant (z = 49.12) with directional asymmetry: CHSH→QO routing (z = 13.12) is 2.2x stronger than QO→CHSH routing (z = 5.94). The cycle is strictly line-scoped — cross-line atom MI is null (z = 0.37).

---

## Evidence

### T1: Cross-Lane MIDDLE MI
- N pairs: 5,591 (QO→CHSH: 2,640 + CHSH→QO: 2,951)
- Observed MI: 1.0632 bits
- Chi²: 177,464.3, Cramér's V: 0.324
- Permutation shuffle: z = 13.42 → **GENUINE**
- Within-lane shuffle: z = 0.05 → **NULL** (ordering doesn't matter, only co-occurrence)

### T1a: Same-Lane Control
- QO→QO MI: z_perm = 10.46 (significant)
- CHSH→CHSH MI: z_perm = 8.42 (significant)
- Cross-lane MI is comparable to same-lane MI (~1.2x ratio)

### T3: Directional Asymmetry (MIDDLE-level)
- QO→CHSH: z_perm = 8.23
- CHSH→QO: z_perm = 10.09
- Both directions significant, nearly symmetric at MIDDLE level

### T4: Kernel State Routing at Lane Boundaries
- Overall: z = 49.12 (massive)
- CHSH→QO: z = 13.12
- QO→CHSH: z = 5.94
- **CHSH→QO 2.2x stronger** — monitoring result constrains next energy operation more than energy constrains monitoring
- Top handoffs: y→k 19.5% (CHSH→QO), k→e 20.7% (QO→CHSH)
- Carryover matrix consistent with C1208 predictions

### Cross-Line Test
- Cross-line atom MI: z = 0.37 (NULL)
- Cross-line MIDDLE MI: z = 2.98 (borderline, likely folio vocabulary clustering)
- Cross-line lane pattern matches independence exactly
- Within-line interleave rate: 0.516, cross-line: 0.500 (chance)
- **Cycle is strictly line-scoped** (confirms C1233 cross-line independence)

---

## Interpretation

The QO and CHSH lanes carry paired information within each line. The specific energy operation (QO MIDDLE) co-occurs with a specific monitoring operation (CHSH MIDDLE), but the sequential order between them doesn't matter — it's the pairing that's structured, not the sequence. This resolves the C961 tension: within-lane ordering IS null (C961 correct), but cross-lane content pairing is genuine. The 2.2x CHSH→QO asymmetry in kernel routing means monitoring results constrain subsequent energy operations more strongly than energy operations constrain monitoring — consistent with a feedback architecture where measurement drives action.

---

## Source

- `phases/EN_LANE_CROSS_PREDICTION/scripts/lane_cross_prediction.py`
- `phases/EN_LANE_CROSS_PREDICTION/results/lane_cross_prediction.json`
- Exploratory: `_tmp_crossline_en.py` (cross-line null test)
