# Negative Control: f82r ↔ II.16.0 (Element Separation, Sevenfold Distillation)

**Test type:** Wrong-recipe control (expert-advisor reassessment)
**True recipe:** III.19.3 (lunaria maceration, 3-day sealed cucurbit)
**Wrong recipe:** II.16.0 (element separation, sevenfold distillation + silver-plate test)
**Prior verdict (generic agent):** COHERENT
**Expert verdict:** INCOHERENT — the prior COHERENT verdict is a false positive

---

## Why This Retest Exists

A generic cold-read agent produced a paragraph-by-paragraph narrative mapping f82r to II.16.0 and rated it COHERENT. This expert reassessment applies constraint-system knowledge and discriminative structural tests to determine whether that verdict survives scrutiny. The question is not "can a narrative be constructed?" (it always can), but "does the structural evidence discriminate II.16.0 from III.19.3?"

---

## Structural Prediction Table

| # | Prediction from II.16.0 | Expected | Actual (f82r) | Verdict |
|---|-------------------------|----------|---------------|---------|
| 1 | Counting anchor at x7 (septena distillacio) | 7-token identical or near-identical qok-class window (per C1965, C1969) | Max identical run = 2 tokens; no 7-token qok window in any 2-line span | **FAIL** |
| 2 | Silver-plate test (quality gate after 6th distillation) | chekar cluster or observation MIDDLE concentration at paragraph ~7 position (per C929, C1926) | 1 chekar total on folio, at line 1 of P1; 0 chekar in P6/P7/P8 | **FAIL** |
| 3 | Two thermal regimes: calcination (hot/dry, e-depth << 0.3) + distillation (e-depth > 0.8) | Bimodal e-depth with at least one paragraph in calcination range (0.0-0.3) | Lowest e-depth = P2 at 0.47 — well above calcination level | **FAIL** |
| 4 | Calcination signature: bare k-HEAD dominance, no cooling modulation | At least one paragraph where k >> e with zero or near-zero e-MOD | P2 has k=1, e=4 — e actually dominates k; inverse of calcination | **FAIL** |
| 5 | Separation structure: 4 distinct material streams processed differently | Sharp vocabulary breaks between paragraphs; distinct PREFIX profiles | PREFIX profile is qo-dominant across all major paragraphs; uniform | **FAIL** |
| 6 | Transfer distributed across all 7 distillation passes | t-HEAD spread across P3-P8 (6 rectification paragraphs) | t-HEAD concentrated 100% in P8 (9/9 folio total); P3-P7 have 0-1 each | **FAIL** |
| 7 | Dregs handling produces dar at each distillation pass | dar in P3, P4, P5, P6, P7 (each of 5 passes through rectification) | dar absent from P3 and P7; present in P1 (3), P6 (4) = front/back-loaded | **PARTIAL** |
| 8 | P9 zero-heat encodes "water of life" product declaration | Strong terminal/product marker | P9 has zero qo and zero k-HEAD — BUT this is the general paragraph-termination pattern (C1237), not recipe-specific | **INFLATED** |
| 9 | hh-marker in P8 = "extended vessel observation for silver-plate test" | hh appears at quality-gate position | hh does appear in P8 L28 (1 occurrence) — BUT C1929 places the confirmed match at III.19.3 where this maps to careful distillation monitoring, not silver testing | **CONTESTED** |
| 10 | Folio scale matches recipe complexity (2753 chars) | 275 tokens for multi-phase recipe | Scale plausible but non-discriminative (many recipes produce similar folio sizes) | INCONCLUSIVE |

**Score: 0 clean PASS, 1 PARTIAL, 1 INFLATED, 1 CONTESTED, 1 INCONCLUSIVE, 6 FAIL**

---

## Key Discriminative Tests

### 1. The Counting Anchor (x7): ABSENT

II.16.0's central operation is "septena distillacio" — seven distillations. This is a primary-operation repetition count, exactly the class of count that C1965 and C1969 demonstrate is recoverable on confirmed-match folios.

C1965 established that on f75r, the recipe's "quatre vegades" (x4) and "ix vegades" (x9) appear as contiguous identical-token runs (4 consecutive qokedy on L13) and high-density qok-class windows (9+ tokens in a 2-line span at L37-L38). C1969 tested this at corpus scale: only 3/82 folios reach the 9-token 2-line window threshold, and all three are confirmed or strongly-supported matches to recipes with high iteration counts.

Searching f82r for any counting anchor:
- Longest identical token run: 2 (several qokeedy/qokaiin doubles scattered throughout)
- No 3-consecutive-identical run exists anywhere on the folio
- No 7-token qok-class window in any 2-line span
- No 4-token qok-class window that could encode "four elements" either

The recipe's primary mechanism — repeated distillation counted to seven — has **zero structural trace**. This is not a marginal absence; it is a structural impossibility for the match. If the scribe were encoding x7 distillation, C1965/C1969 predict a visible density signature.

For III.19.3 (the true recipe): the recipe specifies x3 ("3 parts" lunaria, "3 natural days"). Small counts (x3) are structurally indistinguishable from corpus noise per C1965's caveat: "Idiom does NOT generalize to small-count recipes." The absence of a counting anchor is EXPECTED for III.19.3, and DISQUALIFYING for II.16.0.

**Verdict: STRONG FAIL for II.16.0.**

### 2. Silver-Plate Test: ABSENT

II.16.0's most distinctive feature is an empirical quality test: "posa'n un gota o dues sobre una lamina de pur argent: e si lo negrifica..." Place drops on pure silver; if it blackens, distill again. This is a specific quality gate that should produce a structural signature per C929 (ch=active test) and C1926 (chekar tokens cluster in post-thermal vessel-monitoring contexts on confirmed-match folios).

f82r's observation MIDDLE inventory:
- ckh (heat-level check): 2 occurrences, both in P1 (lines 1 and 3)
- ecth (cooled-transfer watch): 1 occurrence, in P1 (line 4)
- Total observation MIDDLEs outside P1: **ZERO**

The generic agent claimed the P8 hh-marker (okchhy at L28) encodes the silver-plate test. But this interpretation has problems:

1. **hh is not chekar.** C1926 specifically identifies chekar (ch+ek+ar) as the quality-test signature. The hh-marker (doubled h = watch-watch) is an extended monitoring event (C1966 note), not a quality test. They encode different things.

2. **C1929 already assigns hh on f82r.** The confirmed match III.19.3 identifies f82r's careful monitoring as part of the balneum distillation step, not a silver-plate test. The hh appears in what C1929 maps to the final distillation through balneum — careful watching of the distillation process, not testing product on silver.

3. **Position is wrong.** The silver-plate test occurs after the SIXTH of seven distillations. If P6 encodes the "core sevenfold distillation," then the test should appear AFTER P6, not in P8 (which the generic agent simultaneously claims is the seventh distillation). You cannot simultaneously distill and test the product you're distilling.

4. **No chekar cluster at any position.** On confirmed-match folios (f75r, f76r, f84r), quality-gate moments produce localized observation MIDDLE clusters. f82r has all its observation MIDDLEs in P1 (initial setup) and none in the distillation-testing region.

**Verdict: STRONG FAIL for II.16.0.**

### 3. Two Thermal Regimes (Calcination vs Distillation): ABSENT

II.16.0 requires:
- **Calcination:** "preparacio del foch calcinant" — aggressive dry-heat processing of earth+fire elements. Calcination is the HOTTEST operation in alchemical practice, involving direct strong fire.
- **Distillation:** "septena distillacio" — gentle aquatic processing of water+air elements.

These are fundamentally different thermal regimes. Calcination should produce e-depth near zero (pure heat, no cooling modulation). Distillation should produce high e-depth (>0.8).

f82r's e-depth by paragraph:
```
P2: 0.47  <- generic agent calls this "calcining"
P1: 0.76, P3: 0.88, P4: 0.86, P5: 0.67, P6: 1.00, P7: 1.00, P8: 1.02, P9: 0.69
```

The generic agent claimed P2's e-depth of 0.47 "encodes calcining fire." This is wrong on multiple levels:

1. **0.47 is not calcination-level.** Per C1970 and the ke/ek system (C1225, C1226), balneum-level gentle heat produces e-depth around 0.6-0.8. Calcination — which involves NO cooling intervention whatsoever — should produce e-depth near 0.0-0.2. An e-depth of 0.47 means nearly half the thermal atoms involve cooling modulation. That is not calcination.

2. **P2's actual HEAD distribution exposes the claim.** P2 has k=1 and e=4. The e-HEAD OUTNUMBERS k-HEAD 4:1. In calcination, the k-HEAD (heat) should dominate overwhelmingly with minimal or zero e (cool/stabilize). P2's profile is the OPPOSITE of calcination — it is cooling-dominated with incidental heating.

3. **The "sharp transition" from P2 to P3 is modest.** The generic agent emphasized the 0.47→0.88 jump. But this is a 0.41 swing, not a regime change. Compare with actual thermal regime contrasts in confirmed matches: REGIME_1 vs REGIME_3 folios show e-depth differences of 0.3+ across entire folio populations (C1735). A single paragraph at 0.47 surrounded by paragraphs at 0.67-1.02 does not constitute a "bimodal distribution" — it is a brief dip in a monotonically rising arc.

4. **III.19.3 explains P2's dip better.** The true recipe involves sealing operations (glass cover + wax) before placing the cucurbit on ash fire. Sealing is vessel management, not thermal processing. P2 has the most diverse HEAD distribution on the folio (11 distinct HEADs vs 4-8 for other paragraphs), consistent with setup/preparation operations, not a focused thermal step.

**Verdict: STRONG FAIL. No calcination exists on this folio.**

### 4. P5's Double-okain: III.19.3 Diagnostic

C1929 specifically identifies a structural signature on f82r that maps to III.19.3:

> "P3 (5 tokens, L18) at material→maceration boundary contains 2x okain (vessel-intake). Ch22 says 'close the cucurbit with glass cover and wax.'"

Note: C1929's "P3" uses an older paragraph numbering; in the current cold-read file this maps to P5 lines 17-18.

The double okain (vessel: yield, iterate, bind — "seal the vessel for a processing cycle") appearing at L18:
```
L18:  okain  char  okain  qokeedy  lchy
```

Two vessel-seal operations flanking a checking token. II.16.0 has no specific sealing instruction. The recipe discusses distillation and the silver-plate test but never says "seal the vessel with a cover." III.19.3 explicitly says "tanca la cucúrbita ab coberta de vidre e cera" — close the cucurbit with glass cover and wax.

This is a positive diagnostic for III.19.3 that has no explanation under II.16.0.

### 5. P8's t-HEAD Concentration: III.19.3 Diagnostic

P8 has 9 t-HEAD tokens — transfer operations — concentrated in a single late paragraph. The generic agent interpreted this as "placing drops on silver plate + seventh distillation."

But the concentration pattern is wrong for II.16.0:
- Sevenfold distillation should distribute transfer operations across ALL seven passes, not concentrate them in one paragraph
- If P6 encodes "the core sevenfold process" (57 tokens), why does P6 have ZERO t-HEAD tokens? Distillation IS transfer.

For III.19.3: the recipe has a single final step — "destil·la-la per lo bany" (distill it through the balneum). After 3 days of maceration (encoded in the long P1 and P6), the product is distilled once. A single concentrated burst of transfer operations in a late paragraph maps perfectly to a single terminal distillation event.

**Verdict: t-HEAD concentration is a positive discriminator for III.19.3 against II.16.0.**

---

## Dissection of the Generic Agent's Narrative

The prior COHERENT verdict succeeded by exploiting five interpretive moves that do not survive expert scrutiny:

### Move 1: Redefining "calcination" as e-depth 0.47
Real calcination (direct strong fire on stite/mineral material) would produce e-depth near zero. The agent lowered the bar to make P2 fit, but 0.47 means nearly half the thermal operations involve cooling — the opposite of calcination.

### Move 2: Treating hh as silver-plate test
The hh-marker encodes extended monitoring, not a quality test. C1926 identifies chekar (ch+ek+ar) as the quality-test token. The agent substituted a different structural feature because the right one (chekar) was absent from the relevant position.

### Move 3: Ignoring the absent counting anchor
The recipe's central mechanism — x7 distillation — received zero discussion against C1965/C1969's counting-anchor evidence. The generic agent did not know about these constraints. A 7-fold primary-operation count should be visible; it is not.

### Move 4: Treating P6's zero t-HEAD as "autonomous cycling"
If P6 encodes "the core sevenfold distillation," it should contain the distillation's transfer operations. Instead P6 has zero t-HEAD. The agent reframed this absence as "autonomous cycling" — but distillation without transfer is a contradiction. The operation of distillation IS the transfer of volatile material through the alembic.

### Move 5: Treating P9's zero-heat as recipe-specific
P9 has zero qo and zero k-HEAD, which the agent interpreted as the fire being extinguished after completing the recipe. But per C1237/C1240, paragraph-final lines across ALL of Currier B show -am termination markers and reduced thermal vocabulary. P9's profile is a generic paragraph-terminal pattern, not a recipe-specific "the fire is out" signal. This pattern would appear on any folio regardless of recipe content.

---

## Paragraph-Level Assessment

| Para | Tokens | Key Profile | Better fit | Rationale |
|------|--------|------------|------------|-----------|
| P1 | 72 | qo=28, k=23, e=23, dar=3, chekar=1, e-depth=0.76 | **III.19.3** | Massive sustained thermal operation with 3 material additions. For III.19.3: "3 parts" lunaria moisture + sustained ash-fire heating. For II.16.0: should be element separation, but no 4-element structure visible. |
| P2 | 17 | 11 distinct HEADs, e-depth=0.47, kam terminal, dar=1 | **III.19.3** | Diverse setup operations, NOT calcination (e > k). For III.19.3: sealing operations (glass cover + wax). For II.16.0: calcination requires e-depth << 0.3 and k >> e — neither holds. |
| P3 | 17 | qo=6, k=5, e-depth=0.88, dar=0, ol=3 | **III.19.3** | Vessel-loading + gentle heat. For III.19.3: sealed cucurbit goes onto ash bed. For II.16.0: generic distillation paragraph, non-discriminative. |
| P4 | 28 | qo=9, k=8, e-depth=0.86, dar=2, dam terminal | **Ambiguous** | Standard thermal processing. Both recipes could produce this. |
| P5 | 15 | ok=3, double-okain (L18), dal=1, e-depth=0.67 | **III.19.3** | Double vessel-seal matches C1929 exactly. II.16.0 has no sealing instruction. |
| P6 | 57 | qo=16, e=23, dar=4, e-depth=1.00, t-HEAD=0 | **III.19.3** | Large sustained-heat paragraph at balneum level. For III.19.3: 3-day maceration on ash fire. For II.16.0: should be "sevenfold distillation" but has ZERO transfer (t-HEAD=0), which is structurally incompatible with distillation. |
| P7 | 9 | e-depth=1.00, dar=0, pure cooling | **Ambiguous** | Brief monitoring paragraph. Non-discriminative. |
| P8 | 44 | qo=18, t=9, e-depth=1.02, hh=1 | **III.19.3** | Single concentrated distillation event (heavy transfer). For III.19.3: final balneum distillation after maceration. For II.16.0: claims silver-plate test but no chekar present, and transfer concentration contradicts distributed 7-fold distillation. |
| P9 | 16 | ch=5, e-depth=0.69, zero qo, zero k | **Ambiguous** | Generic paragraph-terminal verification. Non-discriminative (C1237). |

**Score: 4 favor III.19.3, 3 ambiguous, 0 favor II.16.0**

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |
|----|----|----|----|----|----|----|----|----|
| 0.76 | 0.47 | 0.88 | 0.86 | 0.67 | 1.00 | 1.00 | 1.02 | 0.69 |

**Shape: Single-regime gentle arc with brief setup dip.** This is NOT bimodal. P2's dip to 0.47 is followed by monotonic climbing to a sustained balneum plateau (P6-P8). The generic agent called this "two regimes" but the dip-then-rise pattern is far more consistent with preparation→processing than with calcination→distillation. True bimodality would show at least one paragraph at e-depth < 0.2 (calcination) clearly separated from the distillation cluster.

### dar distribution

| P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |
|----|----|----|----|----|----|----|----|----|
| 3 | 1 | 0 | 2 | 1 | 4 | 0 | 1 | 1 |

For II.16.0: material operations should cluster at each of the 7 distillation passes ("the dregs of the water you shall place with the earth, which you shall do at each distillation"). We would expect dar in P3, P4, P5, P6, P7 — but P3 and P7 have zero. The pattern is front-loaded (P1=3) and concentrated in P6 (4), which is inconsistent with "at each distillation."

For III.19.3: the pattern matches — initial loading (P1=3 for "3 parts"), sealing materials (P2=1), and periodic fire-maintenance additions (P6=4 for sawdust/fuel additions over 3 days of sustained heating).

### Transfer intensity (t-HEAD)

| P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |
|----|----|----|----|----|----|----|----|----|
| 5 | 2 | 1 | 1 | 0 | 0 | 0 | **9** | 0 |

This is the single strongest structural discriminator. P8 contains ALL major transfer operations. For a recipe built around 7 sequential distillation passes (II.16.0), transfer must be distributed across the distillation paragraphs. For a recipe with a single terminal distillation (III.19.3: "distil-la per lo bany"), transfer should concentrate in one late paragraph.

f82r's transfer profile is diagnostic for III.19.3.

---

## Verdict: INCOHERENT

II.16.0 (element separation via sevenfold distillation with silver-plate test) is **structurally incoherent** with f82r. The prior COHERENT verdict was a false positive produced by narrative accommodation — fitting a story to the data by redefining structural features (calling 0.47 "calcination," calling hh "silver-plate test") and ignoring absent signatures (no x7 counting anchor, no chekar at test position, no transfer distribution across distillation passes).

**Six structural failures:**

1. **No counting anchor at x7** (C1965, C1969) — the recipe's central counted iteration is invisible
2. **No silver-plate quality gate** (C929, C1926) — zero chekar or observation MIDDLE cluster at the predicted position
3. **No calcination thermal regime** — minimum e-depth is 0.47, not the < 0.2 that real calcination requires; P2's HEAD profile is e-dominant (4:1 over k), the inverse of calcination
4. **No separation structure** — uniform qo-dominant PREFIX profiles across all major paragraphs
5. **P5's double-okain is a III.19.3 diagnostic** (C1929) — no sealing instruction exists in II.16.0
6. **P8's t-HEAD concentration contradicts distributed distillation** — all transfer in one paragraph vs the 7 distributed passes II.16.0 requires; P6 (the claimed "core distillation") has ZERO transfer

**Two positive III.19.3 discriminators:**
- P5 double-okain matches C1929's sealing identification
- P8 t-HEAD concentration matches III.19.3's single terminal balneum distillation

**Negative control: PASSED.** The cold read methodology, when informed by the constraint system, successfully discriminates the wrong recipe from the folio. The prior COHERENT verdict demonstrates that narrative-only cold reads without constraint-system grounding can produce false positives through interpretive accommodation.
