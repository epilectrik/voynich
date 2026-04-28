# Positive Control Assessment: f112r vs III.11.0

**Recipe:** III.11.0 — Red mercury tincture (cohobation cycle)
**Folio:** f112r — Section S, 394 tokens, 14 paragraphs, 45 lines
**Prior 8D match status:** NOT a confirmed or supported match. This is tested as a positive control (recipe plausibility probe).
**Assessment by:** Expert-advisor agent

---

## Prediction Scorecard

| # | Prediction | Verdict | Evidence | Weight |
|---|-----------|---------|----------|--------|
| 1 | Alternating e-depth (balneum high / ashes low / balneum high) | **PARTIAL** | Alternation exists but not cleanly aligned with balneum/ashes distinction | HIGH |
| 2 | x3 counting anchor (".iii. vegades") | **FAIL** | No 3-token identical runs found | HIGH |
| 3 | dar at earth-return positions ("metrAs l'aygua sobre la terra") | **PARTIAL** | dar concentrated in P2 and P5 but absent from expected cohobation return points | MEDIUM |
| 4 | Quality gate: observation MIDDLE at "don't let earth redden" | **WEAK PASS** | cth at P3 L13, P6 L25; ckh at P8 L28; ckhh at P10 L33 — distributed, not concentrated at a gate | MEDIUM |
| 5 | Final paragraphs = calcination (low e-depth, fire-intensive) | **FAIL** | P14 has e-depth 0.92 (highest on folio); P13 = 0.54 is low but not fire-dominant | HIGH |
| 6 | Iterative structure ("reitera") | **PASS** | Abundant aiin/saiin/sain throughout; iteration is pervasive | LOW |
| 7 | fch mercury markers | **NOT TESTED** | fch not in decode output vocabulary; no dark pipeline markers visible | MEDIUM |

**Summary: 1 PASS, 2 PARTIAL, 2 FAIL, 1 WEAK PASS, 1 NOT TESTED**

---

## Detailed Assessment

### Prediction 1: Alternating e-depth (cohobation signature)

The recipe's characteristic structure is cohobation: distill in balneum (gentle heat, high e-depth) then re-distill on ashes (direct fire, low e-depth), cycling repeatedly. The prediction is an alternating HIGH-LOW-HIGH pattern across paragraphs.

**Observed e-depth trajectory:**

| Para | e-depth | Expected Pattern | Match? |
|------|---------|-----------------|--------|
| P1 | 0.60 | Initial setup (moderate) | Neutral |
| P2 | 0.77 | Balneum x3 (HIGH) | YES |
| P3 | 0.88 | Ash distillation (LOW expected) | **NO** — highest yet |
| P4 | 0.70 | Balneum return (HIGH) | Moderate |
| P5 | 0.72 | Mixed operations | Neutral |
| P6 | 0.45 | Drop — possible ash fire | YES (low) |
| P7 | 0.67 | Short (3 tokens) | Neutral |
| P8 | 0.78 | Return to balneum? | YES (high) |
| P9 | 0.56 | Short (9 tokens) | Low |
| P10 | 0.67 | Mixed | Neutral |
| P11 | 0.46 | Low — ash/dry fire? | YES (low) |
| P12 | 0.95 | HIGH — strongest balneum | YES |
| P13 | 0.54 | Low | YES (low) |
| P14 | 0.92 | Final calcination (LOW expected) | **NO** — very high |

There IS oscillation in e-depth (the trajectory goes 0.60 -> 0.77 -> 0.88 -> 0.70 -> 0.72 -> 0.45 -> 0.67 -> 0.78 -> 0.56 -> 0.67 -> 0.46 -> 0.95 -> 0.54 -> 0.92), but it does not cleanly align with the recipe's predicted balneum/ashes alternation. The P6/P8/P11/P12 segment (0.45 -> 0.78 -> 0.46 -> 0.95) shows the sharpest oscillation, which is suggestive. However, two critical failures:

1. P3 (expected LOW for ash distillation) is 0.88 (high)
2. P14 (expected LOW for final calcination) is 0.92 (very high)

**Verdict: PARTIAL.** Oscillation present in the folio's e-depth trajectory, but the alignment with specific recipe phases is poor. Per C1967, e-depth tracks thermal intensity at paragraph level, and the overall range (0.45-0.95) is wide, which is consistent with a multi-mode recipe. But the prediction that specific paragraphs would be HIGH or LOW based on recipe phases fails at the critical endpoints.

### Prediction 2: x3 counting anchor

The recipe specifies ".iii. vegades" (3 times) for the initial balneum cycle. Per C1965, cycle-counting is encoded as line-localized clusters of identical tokens. On f75r, the x4 anchor was a 4-token qokedy run (corpus-singular). We should look for a 3-token identical run.

**Observed:** Zero consecutive identical token runs of length >= 3 anywhere on f112r. The closest is the doubled `oteedy oteedy` on Line 3 (length 2). The folio shows no counting idiom.

**Verdict: FAIL.** This is a clean failure. Per C1965, the cycle-counting idiom is detectable when it exists (f75r's x4 run has corpus rarity ~7). Either the recipe's x3 is not encoded this way on f112r, or f112r does not encode this recipe's iteration count. Note that C1965 itself established that small-count recipes (x3, x4 outside f75r) are often structurally indistinguishable from corpus noise — the absence is therefore not diagnostic by itself, but it does mean we lack positive evidence.

### Prediction 3: dar at earth-return positions

The recipe's cohobation cycle involves "metrAs l'aygua sobre la terra viscosa" — returning water to the earth residue after each distillation. This is a material-addition event that should produce dar tokens (C1925: dar encodes new material introduction).

**Observed dar distribution:**

| Para | dar count | Total tokens | dar rate |
|------|-----------|-------------|----------|
| P1 | 0 | 48 | 0% |
| P2 | 3 | 30 | 10% |
| P3 | 0 | 34 | 0% |
| P4 | 1 | 37 | 2.7% |
| P5 | 3 | 53 | 5.7% |
| P6-P14 | 0 | 188 | 0% |

dar is concentrated in P2 (3x), P4 (1x), and P5 (3x), then disappears entirely for the final 9 paragraphs. The recipe predicts dar at EACH cohobation return (earth-return after each balneum), which would distribute dar across multiple paragraph boundaries throughout the folio. Instead, dar is front-loaded in the first third.

There is a potential match: if P2-P5 collectively encode the "x3 balneum distillation with earth-return" phase (total dar = 7), this would be a reasonable concentration. But the recipe's later phase ("Distilla aquella liquor altra vegada per bany" — distill again in balneum) and the repeated reiteration should also produce dar for the earth-return steps, and the final 9 paragraphs show zero dar.

**Verdict: PARTIAL.** dar exists and is concentrated in a plausible region, but the absence from the final two-thirds of the folio contradicts the recipe's iterative earth-return structure. The recipe calls for repeated material addition throughout; f112r front-loads it.

### Prediction 4: Quality gate observation MIDDLEs

The recipe has a critical watchpoint: "guarda que la terra no's rubifich, car tantost cremaria la tinctura" (watch that the earth doesn't turn red, or the tincture burns). This should produce observation MIDDLEs (cth = watch the transfer, ckh = check the fire level) concentrated at a quality-gate paragraph.

**Observed observation MIDDLEs:**
- P3 L13: `chcthy` (cth = watch transfer) 
- P6 L25: `chcthy` (cth = watch transfer)
- P8 L28: `chckhy` (ckh = check fire level)
- P10 L33: `shckhhy` (ckhh = extended heat watch — the only hh on the folio)

These are distributed across four paragraphs rather than concentrated at a single gate. The `shckhhy` at P10 (with its unique double-h, the ONLY hh on the folio) is the strongest candidate for the "don't let the earth redden" warning — extended heat-watching is exactly what you'd do when the risk is overheating. But it appears at L33/P10, which is roughly 73% through the folio, whereas the recipe places this warning roughly 60% through its text. The positional alignment is in the right neighborhood.

**Verdict: WEAK PASS.** Observation MIDDLEs are present and the unique ckhh at P10 is a striking structural feature that aligns with the recipe's "extended watchfulness during dangerous phase." But they are distributed rather than gate-concentrated.

### Prediction 5: Final paragraphs = calcination

The recipe ends with "lavalo ab la distillacio et calcinacio en tro que sia be roig" (wash it by distillation and calcination until it's red as burning fire). Calcination requires direct, intense fire. This should produce LOW e-depth and HIGH k-HEAD concentration in the final paragraphs.

**Observed:**
- P13: e-depth 0.54, k-HEAD = 4/28 = 14.3%, ok PREFIX dominant (8/28)
- P14: e-depth **0.92**, k-HEAD = 4/39 = 10.3%, ok PREFIX dominant (8/39)

P14's e-depth of 0.92 is the second-highest on the entire folio. This is the exact opposite of what calcination predicts. Calcination should produce e-depth near zero (direct fire, no balneum dampening). The heavy e-enrichment in P14 suggests gentle/dampened heat operations, not calcination.

P13's e-depth of 0.54 is lower and could be compatible with a transition to more direct heat, but the ok-PREFIX dominance (vessel management) doesn't suggest fire-intensive calcination — it suggests apparatus management operations.

**Verdict: FAIL.** The final paragraph's e-depth profile directly contradicts the calcination prediction. This is a strong negative signal.

### Prediction 6: Iterative structure

The recipe says "reitera en tro que veies la terra comminuida" (repeat until the earth is depleted). We expect pervasive iteration markers.

**Observed:** aiin appears 11 times, saiin 6 times, sain 4 times, otaiin 4 times, okaiin 5 times. Iteration markers are pervasive across the entire folio.

**Verdict: PASS.** But this is LOW WEIGHT because iteration markers are pervasive across most Currier B folios (C1234: aiin is the standard bounded-loop control token). Nearly every folio shows abundant iteration vocabulary. This prediction has no discriminatory power.

### Prediction 7: fch mercury markers

C1939 established fch as a dark pipeline marker for mercury-related operations (infinite enrichment on 6/6 mercury-recipe folios in confirmed matches). For a mercury tincture recipe, we'd expect fch tokens.

**Observed:** No fch tokens visible in the decode. The decode format shows PREFIX + MIDDLE decomposition, and no tokens parse with an `fch` MIDDLE compound. Dark pipeline MIDDLEs are not annotated in the cold read output.

**Verdict: NOT TESTED.** The cold read format may not capture dark pipeline compounds at the resolution needed. However, the absence is not encouraging for a mercury recipe, given C1939's strong enrichment pattern.

---

## Cross-Paragraph Structural Assessment

### PREFIX profile

f112r is heavily ok-dominant (ok total ~56 tokens, highest PREFIX on the folio). Per C1962, ok encodes vessel/apparatus temperature management. The recipe is about apparatus-intensive operations (distilling over ashes, in balneum, calcination), so high ok is structurally compatible. However, ok dominance is common across Section S folios generally.

qo is the second major PREFIX (~50 tokens), consistent with a recipe involving sustained heating. ch is third (~40 tokens), consistent with active testing. The PREFIX profile is a general distillation signature, not specifically cohobation.

### Paragraph count

14 paragraphs for a recipe with roughly 8 distinct phases is higher than expected but not implausible. Per C1937, multi-step recipes may use more paragraphs than recipe phases. The short paragraphs (P6=11, P7=3, P9=9) could represent brief transitional operations (the recipe has several "set aside" and "separate again" instructions).

### Section S membership

f112r is in Section S (Stars), which per C1930 corresponds to Mercuriorum higher chapters (transmutation/multiplication). III.11.0 IS a Mercuriorum chapter. This is a structural prerequisite that passes.

---

## Verdict: PARTIALLY COHERENT

**Score: 1 PASS + 2 PARTIAL + 1 WEAK PASS + 2 FAIL + 1 NOT TESTED on 7 predictions**

The generic agent's PARTIALLY COHERENT assessment is confirmed. The assessment is:

**What works:**
- Section S membership is correct for a Mercuriorum recipe
- e-depth oscillation exists on the folio (consistent with multi-mode thermal processing)
- Observation MIDDLEs are present, with the unique ckhh being a plausible quality-gate marker
- The PREFIX profile is compatible with apparatus-intensive distillation
- Iteration is pervasive (low weight)

**What fails:**
- **No counting anchor** for the recipe's explicit ".iii. vegades" — absence is not diagnostic per C1965, but positive evidence is missing
- **Final paragraph e-depth directly contradicts calcination** (0.92 instead of near-zero) — this is the strongest negative signal
- **dar front-loading contradicts iterative earth-return** — the recipe predicts distributed dar, f112r concentrates it in P2-P5
- **e-depth alternation does not align with specific recipe phases** — P3 should be low (ash fire) but is the third-highest

**Assessment:** The folio and recipe share general structural compatibility (Section S, multi-mode thermal, apparatus-intensive) but diverge on specific phase-to-paragraph predictions. The P14 e-depth failure is particularly diagnostic: a genuine calcination endpoint should produce the lowest e-depth on the folio, not the second-highest. This suggests f112r either encodes a different recipe, or the paragraph mapping is substantially different from the recipe's textual ordering.

**Comparison to confirmed matches:** On f75r (CONFIRMED, C1970), the ke/ek density was 9.74 vs corpus baseline 4.68, the x4 counting anchor was corpus-singular, and dar distribution matched 4 material-introduction events with positional precision. f112r shows none of this level of specific alignment. The match is at the level of "compatible Section S distillation folio" rather than "this specific recipe encodes this specific folio."

**Expert-advisor concurrence with generic agent:** CONFIRMED PARTIALLY COHERENT. Not upgraded, not downgraded.
