# Negative Control: f112v vs III.19.3 (Fourth Water Constitution)

**Test type:** Wrong-recipe control
**True recipe:** III.1.0 (lunaria to quicksilver pipeline, long multi-step chapter)
**Wrong recipe:** III.19.3 (fourth water constitution, short 2-step maceration)

## Structural Prediction Table

| Prediction | Expected (III.19.3) | Actual (f112v) | Verdict |
|------------|---------------------|----------------|---------|
| Paragraph count | 2-3 max (seal, macerate, distill) | **15 paragraphs** | MISMATCH |
| Token count | ~30-60 (369-char recipe) | **415 tokens** | MISMATCH |
| dar count (material additions) | 1 (lunaria moisture only) | **11 total across 8 paragraphs** | MISMATCH |
| Thermal variation | Uniform gentle (ashes + balneum only) | Highly variable (e-depth 0.30 to 1.41) | MISMATCH |
| Counting anchors (x3) | 3-token repetition clusters | No 3-token identical runs found | MISMATCH |
| Observation density | ~2 quality moments | chekar in 4 paragraphs, ch-prefix heavy throughout | MISMATCH |
| Sealing events (ot-prefix) | 1 sealing step (wax + glass cover) | ot-prefix in 12/15 paragraphs | MISMATCH |
| Apparatus complexity (lk tokens) | Minimal (single cucurbit) | lk in P1, P6, P10, P12, P13 (5 paragraphs) | MISMATCH |
| fch (mercury marker) | Not expected (no mercury in recipe) | fch in P1 (L1: fcheol) | MISMATCH |

**Score: 0/9 predictions match.**

## Key Discriminative Tests

### 1. Scale Mismatch

III.19.3 is 369 characters of Catalan text encoding exactly 5 procedural steps:
1. Add 3 parts lunaria moisture to flesh
2. Seal cucurbit with glass cover and wax
3. Place on ashes for 3 days with sawdust fire
4. Add alembic and distill through balneum
5. Store distillate

This requires at most 2-3 paragraphs (C1959 establishes paragraph layout-order tracks recipe-phase order on matched folios). f112v has **15 paragraphs spanning 47 lines and 415 tokens** -- approximately 7-8x more structural complexity than the recipe could possibly fill.

For comparison, III.19.3 is the shortest sub-recipe in the III.19 capon water series. III.19.2 (third water) is 207 chars and would need about 1 paragraph. III.19.4 (fifth water) is 143 chars. The entire III.19 sub-recipe series (III.19.0 through III.19.8) totals about 5,736 chars -- and even THAT combined text would be a stretch for 15 paragraphs.

**Verdict: DECISIVE MISMATCH.** The recipe exhausts its content by paragraph 3 at the absolute latest.

### 2. Thermal Complexity

III.19.3 specifies exactly one thermal regime: "sobre cendres per .iii. dies naturalls ab foch de serradura composta" (on ashes for 3 natural days with composed sawdust fire), followed by distillation "per lo bany" (through balneum). This is uniformly gentle heat throughout -- no heat adjustments, no temperature changes, no fire management.

f112v's e-depth values tell a completely different story:

| Para | e-depth | Thermal character |
|------|---------|-------------------|
| P1 | 0.81 | Moderate gentle |
| P2 | 0.64 | Moderate |
| P3 | 0.74 | Moderate gentle |
| P4 | 0.91 | Gentle (balneum-range) |
| P5 | 0.93 | Gentle (balneum-range) |
| P6 | **1.41** | Very gentle / deep stabilization |
| P7 | 1.14 | Gentle |
| P8 | 0.90 | Moderate gentle |
| P9 | 0.60 | Moderate |
| P10 | 1.11 | Gentle |
| P11 | 0.67 | Moderate |
| P12 | 0.90 | Moderate gentle |
| P13 | **0.30** | Low e-depth / direct-fire territory |
| P14 | 0.58 | Moderate |
| P15 | 0.42 | Low / moderate |

The folio shows a dramatic thermal arc: moderate beginning (P1-P3), rising to very gentle heat (P4-P7, peaking at P6 e-depth 1.41), then collapsing back to low e-depth in P13 (0.30) and P15 (0.42). This is the signature of a multi-phase process with at least 2-3 distinct thermal regimes. III.19.3 has exactly one.

The qo-prefix (heat source management) distribution confirms this:
- P4: 14 qo tokens (31% of paragraph -- intense fire management)
- P5: 9 qo tokens
- P7: 8 qo tokens
- P1: 8 qo tokens
- P10: 5 qo tokens

A 3-day sawdust fire on ashes requires zero active fire management. The operator sets it and walks away. Yet f112v dedicates enormous attention to heat management across multiple paragraphs with varying intensity.

**Verdict: DECISIVE MISMATCH.** The folio encodes a thermally complex, multi-phase process. III.19.3 is thermally trivial.

### 3. Counting Anchors (x3)

III.19.3 specifies two instances of 3: ".iii. parts" (3 parts lunaria moisture) and ".iii. dies naturalls" (3 natural days). Per C1965, iteration counts can be encoded as repeated identical tokens in line-localized clusters.

Scanning f112v for any 3-token identical runs: **None found.** The closest approach to token repetition is in P4 L16, which has 2 consecutive qokeey tokens (not 3), and P4 L18, which has 3 consecutive qo-prefixed tokens (qokeedy, qokeeey, qokeeody) -- but these are NOT identical tokens, they are distinct tokens with varying e-depth encoding different thermal settings. There is no 3-count cycle-counting signature anywhere on the folio.

**Verdict: MISMATCH.** No structural encoding of x3 found.

### 4. Material Additions (dar count)

III.19.3 has exactly 1 material addition: "Pren de la humiditat simpla de la dita lunaria, e de aquella mit .iii. parts sobre la substancia de la dit carn" (put 3 parts lunaria moisture on the flesh substance). After that, the recipe involves zero further material introductions -- it is pure maceration followed by distillation.

f112v has **11 dar tokens across 8 different paragraphs**:

| Para | dar count | Context |
|------|-----------|---------|
| P1 | 1 | L5: daiin |
| P2 | 1 | L10: dain |
| P3 | 2 | L12: daiin, L13: daiin |
| P4 | 1 | L17: daiin |
| P8 | 1 | L30: dalkedy |
| P13 | 1 | L38: dain |
| P14 | 2 | L40: daiin, daiin (two on same line) |
| P15 | 1 | L45: daldy |

11 material additions distributed across the full length of the folio, with multiple additions in the second half (P13-P15). This is categorically incompatible with a recipe that adds material once at the beginning and then never again. The pattern of dar tokens appearing in P8, P13, and P14 -- well past any point where III.19.3's content could still be operating -- is the single strongest falsification signal.

**Verdict: DECISIVE MISMATCH.** 11 material additions vs 1 expected.

### 5. Observation Density

III.19.3 has 2 quality-critical moments: (1) verifying the seal after "tapa la carabasa ab son cubertor de vidre ab cera communa" and (2) determining when distillation is complete ("distilla tota l'aygua per lo bany"). The recipe contains zero explicit monitoring language -- no color checks, no sensory tests, no drip watching.

f112v is saturated with monitoring:
- ch-prefix (active testing) appears in **all 15 paragraphs**, ranging from 2 to 14 tokens per paragraph
- sh-prefix (passive observation) appears in **14/15 paragraphs**
- chekar tokens (quality-check markers per C1926) appear in P2, P5, P12, P15

The total ch+sh token count is approximately 120-130 across the folio, constituting roughly 30% of all tokens. This is the signature of a process requiring continuous quality monitoring across many operational phases -- the exact opposite of a set-and-forget maceration.

Additionally, the observation MIDDLEs (compound monitoring tokens) are present:
- P3 L11: chcfhy (adjust.flag.watch.end) -- a flagged heat check
- P14 L40: chckhy (adjust.heat.watch.end) -- a heat-level check
- P15 L44a: chcthy (adjust.transfer.watch.end) -- a transfer watch

These are sophisticated, multi-step monitoring instructions. III.19.3 requires no such monitoring.

**Verdict: DECISIVE MISMATCH.** Continuous intensive monitoring vs near-zero monitoring expected.

### 6. Recipe Exhaustion

Mapping III.19.3 to paragraphs:
- **P1** (52 tokens): Could map to adding lunaria moisture to flesh and sealing. But P1 alone has 52 tokens, 8 qo heat-management tokens, and an fch token (mercury marker). III.19.3 has no mercury and no heat management at the material-addition stage.
- **P2** (28 tokens): Could loosely map to placing on ashes. But P2 has a chekar quality-check token and a dar material addition -- III.19.3 adds nothing at this stage.
- **P3** (35 tokens): Could map to distillation. But P3 has 2 dar tokens (material additions during distillation -- III.19.3 adds nothing) and 6 qo tokens (active fire management -- not needed for balneum distillation).

**III.19.3 is exhausted by P3 at latest.** Paragraphs 4 through 15 (330 tokens, or 80% of the folio) have no referent in the recipe.

Even if we stretch the interpretation -- perhaps P4-P7 encode "repeated distillation" (not mentioned in the recipe) or "quality checking" -- the continued dar tokens in P8, P13, and P14, the lk apparatus tokens in P6 and P10 and P12, and the dramatic thermal arc through P6 (e-depth 1.41) down to P13 (e-depth 0.30) describe operations that have no conceivable relationship to III.19.3.

**Verdict: DECISIVE MISMATCH.** Recipe content covers at most 3/15 paragraphs (20% of folio).

## Paragraph-Level Assessment

| Para | Tokens | dar | e-depth | III.19.3 mapping? | Assessment |
|------|--------|-----|---------|-------------------|------------|
| P1 | 52 | 1 | 0.81 | Stretch: material addition | WEAK -- fch mercury marker has no referent |
| P2 | 28 | 1 | 0.64 | Stretch: sealing + ashes | WEAK -- extra dar, chekar have no referent |
| P3 | 35 | 2 | 0.74 | Stretch: distillation | WEAK -- 2 dar during distillation impossible |
| P4 | 45 | 1 | 0.91 | NO REFERENT | Recipe exhausted |
| P5 | 42 | 0 | 0.93 | NO REFERENT | Recipe exhausted |
| P6 | 17 | 0 | 1.41 | NO REFERENT | Recipe exhausted |
| P7 | 28 | 0 | 1.14 | NO REFERENT | Recipe exhausted |
| P8 | 10 | 1 | 0.90 | NO REFERENT | dar with no material to add |
| P9 | 5 | 0 | 0.60 | NO REFERENT | Recipe exhausted |
| P10 | 28 | 0 | 1.11 | NO REFERENT | Recipe exhausted |
| P11 | 6 | 0 | 0.67 | NO REFERENT | Recipe exhausted |
| P12 | 10 | 0 | 0.90 | NO REFERENT | Recipe exhausted |
| P13 | 23 | 1 | 0.30 | NO REFERENT | dar + low e-depth = new phase; no recipe basis |
| P14 | 24 | 2 | 0.58 | NO REFERENT | 2 dar in a recipe with 1 total material addition |
| P15 | 62 | 1 | 0.42 | NO REFERENT | Longest paragraph; closing operations for long process |

Even the first 3 paragraphs do not map cleanly. P1 contains an fch token (mercury/volatile material marker per C1939), which has no referent in III.19.3 (the recipe involves lunaria moisture and capon flesh, not mercury). P3 has 2 dar tokens during what would be the distillation phase, but III.19.3 adds no material during distillation.

## Additional Falsification Evidence

### fch Mercury Marker
P1 L1 contains `fcheol` -- an fch-prefixed token. Per C1939, fch encodes mercury or mercury-water with infinite enrichment on mercury-recipe folios. III.19.3 involves lunaria moisture (a plant extract) and capon flesh, not mercury. The presence of fch in the opening paragraph is a specific positive indicator for the TRUE recipe (III.1.0), which is entirely about lunaria-to-quicksilver transformation and involves mercury throughout.

### Apparatus Tokens (lk)
lk-prefix tokens appear in P1, P6, P10, P12, and P13 (5 of 15 paragraphs). Per the constraint system, lk tokens encode apparatus/furnace management. III.19.3 uses a single cucurbit with alembic -- one apparatus configuration throughout. The distributed lk tokens across 5 paragraphs suggest apparatus changes or multiple apparatus configurations, consistent with III.1.0's multi-step process (grinding, dissolution, multiple distillation stages, putrefaction in different vessels).

### P15 Length and Complexity
P15 is the longest paragraph at 62 tokens spanning 6 lines, with diverse prefix usage (15 different prefixes), low e-depth (0.42), and a terminal observation MIDDLE (cth = adjust.transfer.watch). This is a substantial closing operation -- appropriate for concluding a long multi-phase process like III.1.0, not for the "guarda a part" (store aside) that ends III.19.3.

### Thermal Arc Matches III.1.0, Not III.19.3
The thermal trajectory -- moderate start, gentle middle peak, collapse to direct-fire in late paragraphs -- is consistent with III.1.0's structure: initial dissolution (moderate), element separation via balneum (gentle peak), then fortification steps where "paulatinament fortifica ton foch" (gradually strengthen your fire) until rubification. The P13 e-depth of 0.30 (direct-fire territory) corresponds to III.1.0's "veies vostre dit feu molt fort rubificar" (you see your fire strongly rubify). III.19.3 never approaches direct fire.

## Verdict: INCOHERENT

The previous general-purpose control rated this PARTIALLY COHERENT. Under expert scrutiny with domain-specific structural markers, the verdict is **INCOHERENT**. Every discriminative test fails decisively:

1. **Scale**: 15 paragraphs / 415 tokens for a 5-step, 369-character recipe (7-8x oversize)
2. **Thermal complexity**: Dramatic e-depth arc (0.30 to 1.41) vs uniformly gentle heat
3. **Counting anchors**: No x3 signature found; recipe specifies x3 twice
4. **Material additions**: 11 dar tokens in 8 paragraphs vs 1 expected
5. **Observation density**: ~30% monitoring tokens vs near-zero monitoring recipe
6. **Recipe exhaustion**: Content exhausted by P3; 80% of folio has no referent

Three additional falsification markers seal the verdict:
- fch mercury marker in P1 (no mercury in III.19.3; explicit mercury in III.1.0)
- Distributed lk apparatus tokens across 5 paragraphs (single apparatus in III.19.3; multiple in III.1.0)
- Thermal arc (gentle peak then direct-fire collapse) matches III.1.0's "fortifica ton foch" progression

**The cold read methodology has strong discriminative power.** The folio's structural fingerprint -- dar distribution, thermal arc, apparatus complexity, mercury markers, observation density, and paragraph count -- collectively and individually reject III.19.3 while pointing toward a long, thermally complex, multi-material, mercury-involving process. This is exactly what III.1.0 is.
