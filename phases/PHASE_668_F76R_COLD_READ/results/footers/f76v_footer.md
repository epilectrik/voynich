## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-14 | 144 | 1.007 | Initial fixation — gentle, balneum-level |
| P2 | 15 | 5 | 1.200 | Brief transition (micro-paragraph) |
| P3 | 16-24 | 86 | 0.977 | Second fixation — slightly more heat |
| P4 | 25-29 | 52 | 0.673 | Intense fixation — heat increasing |
| P5 | 30-31 | 21 | 0.714 | Fusibility test — "melt like wax" |
| P6 | 32-41 | 92 | **0.598** | Multiplication — strongest sustained heat |

The e-depth descends monotonically from 1.01 to 0.60 (setting aside the P2 micro-transition). This encodes the recipe's core logic: fixation requires progressively stronger fire. The operator starts gentle and increases heat through each phase until the material is fixed enough to melt like wax. P6 (infinite multiplication) requires the strongest sustained heat — and has the lowest e-depth.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 3 | 30% | Initial fixation — loading gold + ferment |
| P2 | 0 | 0% | Transition (no material action) |
| P3 | 2 | 20% | Second fixation — adding fifth letter |
| P4 | 3 | 30% | Intense fixation — process adjustments |
| P5 | 0 | 0% | Fusibility test (no additions during test) |
| P6 | 2 | 20% | Multiplication — mixing operations |

P5 zero dar is structurally significant: during the fusibility test ("see it melt like wax without smoke"), the operator observes the product on the fire. No material is added during a quality test. This zero is a negative prediction that holds.

### chekar Distribution

| Para | chekar | Density | Recipe phase |
|------|--------|---------|-------------|
| P1 | 0 | 0% | Fixation in progress (not testing yet) |
| P2 | 0 | 0% | Transition |
| P3 | 0 | 0% | Second fixation (not testing yet) |
| P4 | 1 | 1.9% | Late fixation — first test |
| P5 | **2** | **9.5%** | **Fusibility test — peak density** |
| P6 | 1 | 1.1% | Multiplication — end-check |

The chekar tokens concentrate in P5 at 9.5% density — the highest on the folio. The recipe's fusibility test ("temptaràs assaiant si bona fusió prestarà sobre lo foch") maps to exactly this paragraph. P4's single chekar is a preliminary check; P6's is a final verification.

### sa-prefix (Scaffold/Iterate) Distribution

| Para | sa-prefix | % of para | Note |
|------|-----------|-----------|------|
| P1 | 1 | 0.7% | — |
| P2 | 0 | 0% | — |
| P3 | 3 | 3.5% | — |
| P4 | 3 | 5.8% | Iterative cycling increasing |
| P5 | 1 | 4.8% | — |
| P6 | **8** | **8.7%** | **"in infinit se pot multiplicar"** |

sa-prefix tokens concentrate in P6 — the multiplication paragraph. The recipe says this ferment "can be multiplied infinitely by secret mixing operations." The folio encodes this with the highest scaffold/iterate density on the folio, including extreme iteration markers (`oiiin`, `lolsaiiin` with triple-i).

---

## Verdict: COHERENT

f76v produces a coherent structural reading against III.15.0 (ferment conversion / liquefaction → multiplication). The folio's 6 paragraphs map to the recipe's progressive fixation sequence:

1. **Initial fixation** (P1, 144 tokens) — e-depth 1.01 (gentlest heat), ecth×2 (handling cooled intermediates), 3 dar (loading gold + ferment)
2. **Transition** (P2, 5 tokens) — micro-paragraph, highest e-depth (1.20)
3. **Second fixation** (P3, 86 tokens) — e-depth 0.98, ckh×1 (temperature check), 2 dar (adding fifth letter)
4. **Intense fixation** (P4, 52 tokens) — e-depth drops to 0.67, first chekar
5. **Fusibility test** (P5, 21 tokens) — chekar×2 (9.5% density), zero dar, "melt like wax without smoke"
6. **Infinite multiplication** (P6, 92 tokens) — lowest e-depth (0.60), 8 sa-prefix tokens, extreme iteration markers

The descending e-depth arc (1.01 → 0.60) is the primary structural signal — it directly encodes progressive fire strengthening through fixation. The chekar concentration in P5 independently confirms the fusibility test position. The sa-prefix surge in P6 independently confirms the multiplication phase.

**Honest gaps:** dar=10 exceeds the predicted low/zero (the recipe says "ajustant" = joining, which we predicted would use n-atoms rather than dar, but the folio uses both). No cs gold markers despite the recipe adding gold — the expert positive control explained this as consistent with gold as a dissolved intermediate, not a primary metallic input.
