# Phase 652: Block-Pure Paragraph Signatures

**Status:** COMPLETE
**Date:** 2026-04-26
**Constraint registered:** C1967 (Tier 2)

---

## Question

Phase 648 registered C1961: 46% of Currier B paragraphs are >70% block-pure (fire-side or vessel-side per the channel partition). Crazy-expert's recommended follow-up: classify the block-pure paragraphs by their dominant channel within the block, then test whether each channel-class shows operationally distinct signatures matching the predicted role of that channel.

Phase 652 runs the test, performs a case-study on an unexpected sub-finding, and registers a single narrow Tier 2 constraint capturing the genuinely novel result after expert audit.

---

## Method

### Test 1 (s1): Block-pure paragraph operational signatures

For each Currier B paragraph (n=477):
- Compute fire-side / vessel-side block fractions
- Filter to block-pure (>70% one block) → 222 paragraphs
- Classify by dominant channel within block
- Compute per-class signatures: HEAD atom distribution, mean e_depth (per F-B-007 thermal-intensity), section concentration, REGIME assignment

### Test 2 (s2): Vessel-pure paragraph case study

The Test 1 result revealed a striking 94/6 fire/vessel asymmetry — vessel-side prefixes rarely concentrate enough to dominate paragraphs. Crazy-expert hypothesized that the 13 vessel-pure paragraphs might be a distinct structural class — "vessel-state preamble" paragraphs that declare apparatus configuration before the operational body of the folio.

Test: examine each of the 13 paragraphs for folio-position (early/mid/late), token count, section, and dominant channel. If they cluster at folio-opening positions (par 0 or 1) at significantly above baseline rate, the preamble class is real.

---

## Findings

### Finding 1: Block-pure paragraphs are 94% fire-side

Channel-class counts in block-pure subset (n=222):

| Channel-class | Count | Block | % of block-pure |
|---|---|---|---|
| qo | 102 | Fire | 46% |
| ch | 82 | Fire | 37% |
| sh | 25 | Fire | 11% |
| ok | 5 | Vessel | 2% |
| ot | 5 | Vessel | 2% |
| ol | 3 | Vessel | <2% |
| or | 0 | Vessel | 0% |

**94% of block-pure paragraphs are fire-side.** Vessel-side prefixes (ok, ot, ol, or) rarely concentrate enough to dominate a paragraph at >70% block-purity. Independent confirmation of C1964 (vessel-side prefixes operate at token scale via rapid interleaving, not at paragraph scale).

### Finding 2: e_depth gradient (qo > ch > sh) — the registered finding

| Channel-class | Mean e_depth | Delta from baseline (0.636) |
|---|---|---|
| qo (heat application) | **0.679** | +0.043 |
| ch (active test) | 0.606 | -0.030 |
| sh (passive monitor) | **0.538** | -0.098 |

Monotonic across the three primary fire-side channels. e_depth measures per-token thermal-intensity precision (per F-B-007: k=raw, ke=degree-1, kee=degree-2 stabilized "balneum" signature). The paragraph-aggregated gradient maps to predicted operational roles:

- qo paragraphs (driving heat): highest thermal-precision commitment per token
- ch paragraphs (active testing): mid commitment
- sh paragraphs (passive monitoring): lowest commitment

This is **novel structural evidence**. F-B-007 established e_depth at the atom/MIDDLE level. Phase 652 cross-validates it at paragraph aggregation across operational channel classes. The gradient was not predicted by any registered constraint and is the genuinely new piece of information from this phase.

### Finding 3: Channel-class confirmation signatures (mostly tautological per audit)

Other per-channel signatures match registered channel readings but are partially tautological:

| Predictor | qo | ch | sh | Status |
|---|---|---|---|---|
| k-HEAD rate | 18.9% | 10.5% | 10.6% | Confirms C1300 (qo near-pure THERMAL) — independent |
| Top section | B=57% | S=75% | dispersed | Tautological with C909/C1404 (sections defined by operations) |
| Top regime | R1=63% | R3=66% | R3=56% | Tautological with C547 (qo→R1 enrichment) |

After expert-advisor's circularity audit, the genuinely independent confirmations are:
- e_depth gradient (Finding 2 — the registered finding)
- k-HEAD rate ordering (corroborates C1300)
- 94/6 fire/vessel asymmetry (Finding 1 — corroborates C1964)

The section and regime co-concentrations were excluded from the independence count because they're downstream of existing section-regime-channel coupling per C909, C1404, C547.

### Finding 4: Vessel-state preamble hypothesis FALSIFIED

Of the 13 vessel-pure paragraphs:
- Folio-opening (par 0 or 1): 5/13 = 38.5% (vs baseline 29.9%, expected ~3.9, observed 5)
- Middle of folio: 5/13 = 38.5%
- Late in folio (rel ≥ 0.7): 3/13 = 23.1%

**No significant positional clustering at folio openings.** The 5/13 at early position is within noise (expected count 3.9 under null; observed 5). The hypothesis of a "vessel-state preamble" structural class is not supported.

Section S over-representation (7/13 = 54%, vs S being 28% of folios) reflects recipes-section condensation patterns rather than a distinctive structural class.

The vessel-pure paragraphs are real (some are substantial 30-70 tokens) but not a positionally-distinct class — they're scattered instances of vessel-side concentration without shared structural function.

---

## Constraint registered

### C1967 (Tier 2): e_depth Paragraph-Channel Gradient

[Full text in `context/CLAIMS/C1967_e_depth_paragraph_channel_gradient.md`]

**Statement:** Among block-pure Currier B paragraphs, mean e_depth orders monotonically across the three primary fire-side channel classes: qo (0.679, n=102) > ch (0.606, n=82) > sh (0.538, n=25). Cross-validates F-B-007 (e_depth = thermal-intensity continuous modifier) at paragraph aggregation level. Suggests e_depth may index operator attentional commitment to thermal specification — heat-driving (qo) commits most precision; passive-monitoring (sh) commits least. Tier 3 attentional-commitment reframing is a candidate; the registered Tier 2 fact is the gradient itself.

---

## What's NOT registered

- **The 12/12 broad signature confirmation** — expert-advisor flagged that 6/12 are tautological with existing constraints (section concentrations, regime mappings). The remaining 6 are: e_depth gradient (registered), k-HEAD rate ordering (corroborates C1300), 94/6 fire/vessel asymmetry (corroborates C1964), 46.5% block-pure rate (descriptive). Of these, only e_depth is genuinely novel; others reinforce existing constraints without adding new information.

- **Vessel-state preamble structural class** — falsified by case study.

- **Tier 3 attentional-commitment reframing of e_depth** — flagged in C1967 as candidate but not registered. Awaits stronger validation (e.g., header vs body e_depth gap test crazy-expert proposed).

---

## Pending future work

1. **Header vs body e_depth gap test.** Per crazy-expert: if e_depth indexes attentional commitment, paragraph headers (specification, per C1287) should show *higher* e_depth than bodies, with the gap *largest* in qo-class paragraphs and *smallest* in sh-class. Direct test of the Tier 3 reframing.

2. **AXM-dwell prediction for qo-class paragraphs.** Per crazy-expert: the 1.8× k-HEAD rate gap (qo 18.9% vs ch/sh 10.5%) should predict folio-level AXM self-transition enrichment in qo-dominant paragraphs (per C1382/C1384 k-initial-AXM coupling). Testable.

3. **ch:sh 3.3:1 ratio investigation.** Active testing concentrates 3× more than passive monitoring at paragraph-purity scale. Crazy-expert's reading: passive monitoring is too distributed to dominate paragraphs; active testing concentrates because procedures have explicit checkpoints. Could be tested via paragraph-position distribution of ch vs sh tokens.

---

## Methodology lesson

Both expert reviews flagged the original "12/12 confirmed" framing as overstating. Multiple of the dimensions tested were tautological with existing constraints (sections defined by operations, regimes correlated with channels). The **independence audit** (per crazy-expert) and **circularity controls** (per expert-advisor) reduced the effective count to ~3-4 genuinely novel signatures, of which only the e_depth gradient was registerable as a new finding.

The case study on the 13 vessel-pure outliers was the right next test — it falsified the preamble hypothesis cleanly and prevented over-claiming.

Lesson: when a multi-dimensional test produces "all predictions confirmed," run circularity audit before registering. Confirmation across dimensions that are downstream of existing structural couplings is not multiple independent confirmations.

---

## Files

- `scripts/`
  - `s1_block_pure_signatures.py` — channel-class signature analysis
  - `s2_vessel_pure_case_study.py` — 13-paragraph positional case study
- `results/`
  - `block_pure_signatures.json`
  - `vessel_pure_case_study.json`
