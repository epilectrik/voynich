# Negative Control: f75r <-> III.21.0 (De les vexells)

**Test type:** Wrong-recipe control
**True recipe:** III.19.0 (aqua vitae, reflux distillation)
**Wrong recipe:** III.21.0 (vessel specification -- descriptive chapter listing vessel nomenclature)

---

## Recipe Summary

III.21.0 is a *descriptive* chapter, not a procedural recipe. It states:
- All medicines require only one vessel form with 3 pieces (cover, alembic, cucurbit)
- The vessel takes different names depending on operation (distillatory, dissolutory, putrefactory, calcinatory, congelatory, sublimatory, etc.)
- Each medicine needs its own glass vessel
- You can do 2, 3, or 4 things at once with enough vessels

There are **zero procedural steps**. No heating. No material additions. No monitoring. No iteration. No quality checks. This is taxonomic description, not execution.

---

## f75r Structural Summary

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | qo-prefix |
|------|-------|--------|-----|---------|-------------|-----------|
| P1 | 1-5 | 46 | 2 | 0.63 | -- | 7 (15.2%) |
| P2 | 6 | 9 | 1 | 0.56 | 1 cth | 3 (33.3%) |
| P3 | 7-12 | 58 | 0 | 0.45 | 2 ckh, 1 cth | 17 (29.3%) |
| P4 | 13-16 | 39 | 0 | 0.44 | 1 ckh | 13 (33.3%) |
| P5 | 17-22 | 52 | 2 | 0.42 | -- | 10 (19.2%) |
| P6 | 23-26 | 31 | 3 | 0.48 | 1 ecth, 1 ckh | 9 (29.0%) |
| P7 | 27 | 11 | 2 | 0.18 | -- | 1 (9.1%) |
| P8 | 28-31 | 46 | 5 | 0.61 | 1 ecth, 1 ckh | 14 (30.4%) |
| P9 | 32-46 | 120 | 12 | 0.60 | 1 ckh | 34 (28.3%) |
| **TOTAL** | 1-46 | **412** | **27** | **0.51** | **12 obs** | **108 (26.2%)** |

---

## Structural Prediction Table

| # | Prediction | Expected (III.21.0) | Actual (f75r) | Verdict |
|---|-----------|---------------------|---------------|---------|
| 1 | Low/zero procedural content (no heating cycles) | Near-zero qo-prefix tokens | 108 qo-prefix tokens (26.2% of folio) -- MASSIVE sustained heating | **MISMATCH** |
| 2 | Flat e-depth (no thermal arc) | e-depth ~0 or uniform | e-depth arc: 0.63 -> 0.44 -> 0.42 -> 0.18 -> 0.61 -- clear thermal trajectory | **MISMATCH** |
| 3 | Low/zero dar count (no material handling) | 0-2 dar across folio | 27 dar tokens across 7 of 9 paragraphs -- heavy material introduction | **MISMATCH** |
| 4 | Low/zero observation MIDDLEs | 0 ckh/cth/ecth | 12 observation MIDDLEs (ckh x7, cth x2, ecth x2, chekar x4) -- active monitoring | **MISMATCH** |
| 5 | Dominant ok-prefix tokens (vessel management) | ok should dominate if vessel-focused | ok = 16 tokens (3.9%). qo (heat) = 108 (26.2%), sh (observe) = 64 (15.5%). ok is a minor channel. | **MISMATCH** |
| 6 | Short folio (specification chapters are brief) | <100 tokens, 1-2 paragraphs | 412 tokens, 9 paragraphs, 46 lines -- one of the longer B folios | **MISMATCH** |
| 7 | No counting anchors | No repeated identical token runs | L13: 4x identical qokedy (corpus-singular run); L37-38: 9+ qok-class tokens in 2-line window (corpus-singular) | **MISMATCH** |

**Score: 0/7 predictions match. ALL seven structural predictions fail.**

---

## Paragraph-Level Assessment

### P1 (Lines 1-5, 46 tokens)

**Recipe says:** "Son, for composing all medicines you need only one vessel form with 3 pieces: a cover, an alembic, and a cucurbit."

**What the tokens say:** 7 qo-prefix (heat management), 9 sh-prefix (passive observation), 2 dar (material-add), 1 chekar (quality check). Mean e-depth 0.63 (elevated thermal engagement). Line 1 opens with kchedy (apparatus-level cooling-close), followed by okeey (vessel cool-cool-end), qokar (fire-respond), sh/ch interleaving. Line 4 has dackhy (material-add with heat-watch), lkamo (apparatus yield-final). Only 1 vessel token (`okeey` on L1) appears in 46 tokens.

**Forced mapping:** If this paragraph described "you need one vessel form," we would expect declarative specification vocabulary (ok-dominant, low heat, no material-add). Instead we see active thermal management, observation cycling, and material addition. The paragraph reads as an active distillation step, not a vessel description.

**Verdict: INCOHERENT** -- active procedural content cannot map to declarative vessel specification.

### P2 (Line 6, 9 tokens)

**Recipe says:** "...which has 3 pieces: a cover, an alembic, and a cucurbit."

**What the tokens say:** 3 qo-prefix (heat), 1 dar (material-add), 1 ok (vessel), 1 cth observation MIDDLE (transfer-watch). Opens pchedy, includes olky (vessel-load heat-end), dar (material introduction), qokain (sustained cyclic heating), qokeedy (gentle balneum fire).

**Forced mapping:** If listing 3 vessel parts, we expect ok/ot-dominant vocabulary, zero heat, zero material-add. Instead: 33% of tokens are heat management (qo), there is an active material addition (dar), and a transfer-watch observation (cth). A taxonomic list of vessel parts should be flat and non-procedural.

**Verdict: INCOHERENT** -- active heat + material handling + monitoring cannot map to a vessel part list.

### P3 (Lines 7-12, 58 tokens)

**Recipe says:** "It takes different names per operation: distillatory, dissolutory, putrefactory, calcinatory, mortificatory..."

**What the tokens say:** 17 qo-prefix (29.3%), 11 ch-prefix (active monitoring), 8 sh-prefix (passive observation). 3 observation MIDDLEs (ckh x2, cth x1). Dense qo/ch/sh interleaving across 6 lines. Multiple qokain (sustained cyclic heating). Line 9: qokchdy (adjust fire while watching). Line 10: chckhy (heat-level-check). e-depth 0.45 indicates sustained gentle heat -- characteristic of fermentation or balneum processing.

**Forced mapping:** This is the folio's most intensive heat-management paragraph. A catalogue of operation names (distillatory, dissolutory, putrefactory...) should produce classificatory vocabulary, not 29% qo-prefix thermal content with active fire-watching.

**Verdict: INCOHERENT** -- the single most heat-intensive paragraph on the folio. Cannot map to a vocabulary list.

### P4 (Lines 13-16, 39 tokens)

**Recipe says:** "...and always it is only one single form."

**What the tokens say:** Line 13 contains **4 consecutive identical qokedy tokens** -- corpus-singular in all of Currier B:

```
L13:  pchedy  keedy  qokedy  qokedy  qokedy  qokedy  qokain  olshedy
```

This is the x4 counting anchor (C1965). The paragraph also contains 6 instances of qokain (sustained cyclic heating), 3 scaffold tokens (sain, saiin), and zero material additions. III.21.0 mentions "2, 3, or 4 things at once" but that refers to parallel vessel operations (efficiency advice), not counted iterations of a single process. The 4x identical token run is structurally diagnostic of cycle-counting, which is meaningless for a descriptive vessel chapter.

**Verdict: INCOHERENT** -- counting shorthand for repeated distillation cycles has no semantic target in a vessel specification. The numbers do not correspond ("2, 3, or 4 at once" vs. "repeat this 4 times").

### P5 (Lines 17-22, 52 tokens)

**Recipe says:** (Recipe text essentially exhausted -- III.21.0 is approximately 250 words total.)

**What the tokens say:** 13 sh-prefix (25%, passive observation), 10 qo-prefix (heat), 5 ch-prefix (active monitoring). 2 dar (material-add). Line 17: dal (careful collect/placement), line 20: ydain (material-add). Line 21: am (yield-final, stage completion marker). Mean e-depth 0.42 (moderate thermal engagement). Zero observation MIDDLEs -- process running autonomously.

**Forced mapping:** The recipe has already ended. Even stretching III.21.0's content, a descriptive chapter about vessel naming cannot account for observation-heavy, thermal-management content spanning 6 lines with material additions and an autonomous-processing signature.

**Verdict: INCOHERENT** -- recipe text exhausted; no mapping target exists.

### P6 (Lines 23-26, 31 tokens)

**What the tokens say:** 9 qo-prefix (29%), 3 dar, ecth x1 (cooled-transfer-watch), ckh x1 (heat-level-check). Line 26: dain-ol-sheol-dain-ol pattern (material-add, vessel-state, observe-vessel, material-add, vessel-state) -- repeated material introduction with vessel-state checking. Paragraph ends with dar-ady.

**Verdict: INCOHERENT** -- no recipe content remaining; active material handling cannot be vessel description.

### P7 (Line 27, 11 tokens)

**What the tokens say:** Lowest e-depth on the folio (0.18 -- near-zero thermal content). 2 dar, 2 ot-prefix (transfer/output monitoring), 3 sh-prefix. Contains otar (vessel-seal), otedy (vessel-seal cool-end).

**Forced mapping:** This is the only paragraph directionally consistent with vessel-management focus (ot/ok presence, low thermal content). But it still has 2 material-add tokens and 3 observation tokens, and the recipe was already exhausted at P5. The e-depth of 0.18 encodes physical material transfer between vessels, not a description of what vessels look like.

**Verdict: AMBIGUOUS** at surface vocabulary level (vessel-adjacent words present), but still procedural, not descriptive. Recipe already exhausted.

### P8 (Lines 28-31, 46 tokens)

**What the tokens say:** 14 qo-prefix (30.4%), 5 dar (material-add), 8 ch-prefix (active testing), ecth x1 (cooled-transfer-watch), ckh x1 (heat-level-check), chekar x1 (quality check). e-depth 0.61 (high thermal engagement). L29: lolkaiin (vessel-load with double-iterate-bind -- extended iterative vessel operation). L30: 6 qo-prefix in 12 tokens (50% heat management).

**Forced mapping:** Completely unmappable. 30% heat management, 5 material additions, and observation MIDDLEs encode an active procedural step. Recipe is long exhausted.

**Verdict: INCOHERENT** -- dense procedural execution with no remaining recipe text to map.

### P9 (Lines 32-46, 120 tokens)

**What the tokens say:** The folio's largest paragraph by far: 120 tokens across 15 lines. 34 qo-prefix (28.3%), 16 sh-prefix, 14 ot-prefix, **12 dar** (10% of paragraph). chekar x1 (quality check), ckh x1 (heat-level check).

Critical sequences:
- L34: dar followed by oty-otar-otar-ol (material-add, then triple vessel-seal/seal/continue) -- sealing a vessel after material addition
- L35-36: double dar on same line, twice (two material additions in quick succession)
- **L37-38: 9+ qok-class tokens in a 2-line window** -- corpus-singular (C1969). The x9 counting anchor.
- L43: chekar (quality check), followed by oldy-qokain-chkar-otar-oldy
- L44: otam (vessel-seal yield-final -- terminal closure)

**Forced mapping:** This paragraph alone is longer than the entire III.21.0 recipe. It contains 12 material additions, a corpus-singular 9-cycle heat iteration window, quality checks, vessel-sealing sequences, and sustained thermal management. There is nothing in "you need one vessel with 3 pieces" that could generate 120 tokens of procedural execution.

**Verdict: INCOHERENT** -- 120-token procedural paragraph with 12 material additions is maximally incompatible with a descriptive vessel chapter.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |
|------|----|----|----|----|----|----|----|----|-----|
| e-depth | 0.63 | 0.56 | 0.45 | 0.44 | 0.42 | 0.48 | **0.18** | 0.61 | 0.60 |
| III.21.0 predicts | flat | flat | flat | flat | flat | flat | flat | flat | flat |

The e-depth draws a distinctive arc: moderate start, declining through P3-P5 (sustained gentle heat), crashing to 0.18 at P7 (physical transfer), then rebounding to 0.60-0.61 for P8-P9 (active balneum processing). A descriptive specification chapter predicts thermally flat content throughout. The folio contradicts this prediction at every paragraph.

### dar (material addition) distribution

| Para | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | Total |
|------|----|----|----|----|----|----|----|----|-----|-------|
| dar | 2 | 1 | 0 | 0 | 2 | 3 | 2 | 5 | 12 | **27** |
| III.21.0 predicts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |

27 material additions, heavily back-loaded (P8-P9 = 17/27 = 63%). A vessel specification chapter describes equipment; it does not call for adding, loading, or handling substances.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | chekar | Total |
|------|-----|-----|------|--------|-------|
| P1 | -- | -- | -- | 1 | 1 |
| P2 | -- | 1 | -- | -- | 1 |
| P3 | 2 | 1 | -- | 1 | 4 |
| P4 | 1 | -- | -- | -- | 1 |
| P5 | -- | -- | -- | -- | 0 |
| P6 | 1 | -- | 1 | -- | 2 |
| P7 | -- | -- | -- | -- | 0 |
| P8 | 1 | -- | 1 | 1 | 3 |
| P9 | 1 | -- | -- | 1 | 2 |
| **Total** | 6 | 2 | 2 | 4 | **14** |

A vessel specification chapter predicts zero observation MIDDLEs (there is nothing to observe). The folio has 14, distributed across paragraphs tracking the thermal arc -- they concentrate where heating is active (P3, P8) and are absent where thermal content is minimal (P5, P7).

---

## Summary of Structural Mismatches

| Feature | III.21.0 prediction | f75r reality | Compatible? |
|---------|---------------------|-------------|-------------|
| Paragraph count | 1-3 (short spec) | 9 | **No** |
| Token count | Low (<100) | 412 | **No** |
| Thermal arc | Flat / near-zero | Dramatic arc 0.18-0.63 | **No** |
| dar count | 0 | 27 | **No** |
| Counting anchors | 0 | 2 (x4 on L13, x9 on L37-38) | **No** |
| Observation MIDDLEs | 0 | 14 | **No** |
| Dominant prefix | ok (vessel) | qo (heat source, 26.2%) | **No** |
| Process type | Descriptive | Procedural (reflux distillation) | **No** |
| Recipe exhaustion | Should cover all paras | Exhausted by P5 at latest | **No** |

---

## Verdict: INCOHERENT

f75r cannot be coherently read against III.21.0 (vessel specification). **Every structural prediction fails (0/7).** The mismatches are not marginal -- they are categorical:

1. **Scale:** f75r (412 tokens, 9 paragraphs, 46 lines) is approximately 5-8x larger than a descriptive chapter could fill. The recipe is exhausted by P5, leaving 260 tokens (63% of the folio) with zero mapping target.

2. **Genre:** III.21.0 is taxonomic description (vessel names). f75r encodes active procedural execution (heating, material handling, monitoring, iteration counting). Per C171, f75r is an execution program. III.21.0 specifies no process to execute.

3. **Thermal content:** 26.2% of f75r tokens are qo-prefix (heat management) with a dramatic thermal arc. A vessel specification chapter predicts near-zero thermal content.

4. **Material handling:** 27 dar tokens (6.6% of folio) indicate extensive material introduction and handling. III.21.0 introduces zero materials.

5. **Counting anchors:** The 4x qokedy run (L13) and 9x qok-class window (L37-38) are corpus-singular features diagnostic of cycle-counting (C1965, C1969). III.21.0 mentions "2, 3, or 4 things at once" as efficiency advice about parallel operations, not as counted sequential iterations, and the numbers (4, 9) do not match (2, 3, 4).

6. **Observation MIDDLEs:** 14 active observation tokens are distributed across paragraphs tracking the thermal arc. A descriptive chapter has nothing to observe.

7. **Prefix distribution:** If the folio encoded a chapter about the vessel, we would expect vessel-management tokens (ok) to dominate. Instead, heat-source tokens (qo, 108/412 = 26.2%) dominate, while vessel tokens appear only 16 times (3.9%).

**Discriminative power confirmed.** The cold read methodology cleanly distinguishes between the wrong recipe (III.21.0: INCOHERENT at 0/7 predictions, 0/9 paragraphs mappable) and the true recipe (III.19.0: previously assessed as COHERENT with both counting anchors, thermal arc, material-addition pattern, and paragraph-phase correspondence all matching). The structural features -- thermal arc, dar distribution, counting anchors, observation MIDDLEs, folio scale -- provide sharp, quantitative discriminators that cannot be narratively forced to fit the wrong recipe.
