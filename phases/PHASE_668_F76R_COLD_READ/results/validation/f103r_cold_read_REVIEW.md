# f103r Cold Read — Error Review

**Reviewed against:** Expert positive control verdict (PARTIALLY COHERENT, 5/7), decode summary JSON, raw cold read TXT
**Expert downgrade reasons:** Ash regime absent, sa-prefix misplaced

---

## ERRORS

### E1. P5 mapped to "ash-fire step" but the predicted ash regime is structurally absent

The cold read maps P5 (e-depth 0.46) to the recipe's "put it on ashes and fire in the manner described in the preceding chapter" and P3-P4 as transitional to ash-fire. The expert found that the folio is **dominated by a single sustained balneum regime** in the latter half, with no distinct ash-fire thermal phase visible in the data. The cold read's two-phase thermal arc narrative (P1-P5 = "heat-dominated" vs P6-P12 = "cooling-dominated") overclaims the first half as encoding a distinct direct-fire mode.

**What the data actually shows:** P5 has the lowest e-depth (0.46) and P4 is second-lowest (0.48), but these are only modestly below the P1 baseline (0.49). The difference between "liquefaction heat" (P1, 0.49) and "ash-fire peak direct heat" (P5, 0.46) is 0.03 — a difference that does not support the strong claim that P5 encodes a categorically different heat regime. The cold read treats this tiny gradient as a major structural signal ("the lowest e-depth on the folio marks peak direct-fire work") when it is within noise range.

**Fix required:** Remove or substantially weaken the ash-regime interpretation for P3-P5. The e-depth dip is real but too small to support mapping to a distinct ash-fire processing step. Acknowledge that the folio's thermal profile is better described as: moderate initial phase (P1-P5, ~0.46-0.67) followed by sustained balneum regime (P6-P12, ~0.75-1.05), without a cleanly distinct "direct fire" intermediate step.

### E2. sa-prefix tokens are mislocated in the interpretive mapping

The cold read mentions `sain`/`saiin` tokens in P7 (L31: `soiin`), P11 (L51: `saiin`), and P2 (L7: `sain`, L10: `sarain`), glossing them as "scaffold: iterate, bind" and treating them as iteration infrastructure. The expert noted that sa-prefix tokens **concentrate in material-combination setup (P1-P2)** rather than in the multiplication phase (P7-P12) as the cold read's narrative would predict.

**What the data actually shows:** From the JSON, sa-prefix counts are: P1=2, P2=3, P3=1, P5=0, P6=0, P7=0, P8=0, P9=0, P10=0, P11=2, P12=0. The cold read is correct that sa appears in P2 and P11, but incorrectly implies sa appears in P7 — `soiin` on L31 has prefix `so`, not `sa`. The cold read does not explicitly claim P7 has sa-prefix tokens, but the P7 narrative mentions "iteration scaffolding" without noting that the actual scaffold prefix (sa) is absent from P7. The broader issue: the cold read does not flag that sa-prefix tokens are front-loaded (5 of 8 in P1-P3), which conflicts with mapping them to "multiplication" phases.

**Fix required:** Correct the implication that sa-prefix is an iteration marker for later phases. Note that sa concentrates in the combination/setup paragraphs (P1-P3), which is where the recipe describes mixing and combining — this is actually consistent with a "scaffold for combination" reading, but the cold read fails to make this point.

---

## OVERSTATEMENTS

### O1. "e-depth draws a distinctive two-phase arc" — overstated

The cross-paragraph patterns section claims a "distinctive two-phase arc" with "the most abrupt e-depth transition on the folio" between P5 (0.46) and P6 (0.92). The transition at P5-P6 IS genuinely sharp (+0.46 absolute change), but the cold read overstates the first phase as encoding "mixing and direct-fire work" when P1-P5 actually shows a rise (P1=0.49 to P2=0.67) followed by a decline (P3=0.63 to P5=0.46). This is not a flat "heat-dominated" phase — it has internal structure that the two-phase narrative glosses over.

The P5-to-P6 jump is genuinely the largest single-paragraph e-depth change on the folio and correctly identified as structurally significant. But characterizing P1-P5 collectively as "moderate to low" obscures that P2 (0.67) is already moderately elevated — consistent with balneum mariae, which the cold read correctly identifies for P2 but then implies the subsequent e-depth decline represents a shift to "direct fire." The more honest reading: P2 is already balneum-like, P3-P5 show declining thermal regulation (not necessarily "direct fire"), and P6 marks a return to intensive thermal regulation that persists through the end.

### O2. "Zero observation MIDDLEs" in P10-P12 called "observation fade-out" — slightly overstated

The cold read claims a clean "observation fade-out" where observation MIDDLEs (ckh/cth/ecth) are "present in P1-P8, then completely absent in P9-P12." This is factually correct per the JSON data. However, P10 still contains 6 ch-prefix and 10 sh-prefix tokens — the operator is still actively monitoring. The "fade-out" is specifically of the compound observation MIDDLEs (ckh/cth/ecth), not of monitoring activity in general. The cold read's phrasing "the operator stops actively monitoring specific parameters" is misleading when P10-P12 contain substantial ch/sh prefix activity.

**Fix:** Reframe as "specific compound monitoring diminishes" rather than implying the operator stops monitoring altogether.

### O3. P5 "fluidity test" interpretation — speculative

The cold read maps P5's transfer-watch (`chcthy`) to the recipe's "if you see it doesn't flow." This is a reasonable interpretive reach, but calling it "the fluidity test" as though confirmed is stronger than warranted. The chcthy token is a generic active transfer-watch (C929) that appears in many contexts. The cold read should note this as plausible alignment, not definitive identification.

### O4. P7 "quintessence separation" — overconfident mapping

The cold read maps P7 to "the separation of the fifth essences is revealed to you." This is one of the recipe's most philosophical/theoretical statements, and mapping it to a specific paragraph with zero material additions and passive observation is reasonable but speculative. The cold read treats this as if the token structure "encodes" quintessence separation, when what it actually shows is an autonomous processing phase with passive monitoring. The mapping to quintessence separation specifically (rather than any autonomous processing step) depends entirely on paragraph-to-recipe-step alignment, which is the very thing being tested.

### O5. Verdict should be PARTIALLY COHERENT, not COHERENT

The cold read concludes with "Verdict: COHERENT." The expert downgraded this to PARTIALLY COHERENT (5/7 criteria). The two failures — absent ash regime and misplaced sa-prefix — are not minor. The ash regime is a named step in the recipe ("put it on ashes and fire") that lacks clear structural encoding in the folio. This is a meaningful gap that should have been flagged in the original verdict.

---

## OMISSIONS

### M1. No acknowledgment that the folio's second half is a single sustained balneum regime

The cold read breaks P6-P12 into distinct operational phases (recovery distillation, autonomous processing, maximum distillation, autonomous separation, final restitution). But the e-depth data shows P6-P12 are all in the 0.75-1.05 range — a single sustained high-cooling regime. The recipe DOES describe distinct steps in this range (recovery, quintessence separation, restitution), but the folio's thermal profile does not differentiate them structurally. The cold read should acknowledge this limitation: the folio encodes a sustained balneum-like regime in paragraphs 6-12, and the paragraph-to-step mapping within this regime relies more on narrative alignment than on distinguishing structural signals.

### M2. No mention of the sa-prefix front-loading pattern

The cold read does not note that 5 of 8 sa-prefix tokens appear in P1-P3. This is a real distributional fact that should have been flagged, either as supporting the combination-setup reading or as a discrepancy with the "scaffold for multiplication" gloss.

### M3. chekar_count inconsistencies not flagged

The JSON shows chekar_count=1 for P1, P2, P3, and P11, and 0 elsewhere. The cold read mentions a quality check (`chekeey`) in P11 (correctly) but does not discuss the chekar tokens in P1-P3. These are `checkhy`/`chckhy` type tokens — the cold read discusses them as "heat-level checks" in the narrative but doesn't connect them to the chekar metric from the JSON. This is a minor bookkeeping gap, not a factual error.

---

## APPROVED

### A1. dar distribution analysis is accurate and well-supported

The dar counts match the JSON precisely: P1=4, P2=5, P3=1, P4=0, P5=3, P6=3, P7=0, P8=1, P9=0, P10=0, P11=0, P12=1. Total 18 dar tokens. The 89% front-loading claim (16/18 in P1-P6) is correct. The interpretation that material additions concentrate in the first half while the second half is autonomous processing is well-supported by the data and aligns with the recipe.

### A2. P1 active monitoring concentration is genuine

P1 has 12 ch-prefix tokens — confirmed by the JSON. This is the highest ch-prefix density on the folio (12/49 = 24.5%). The cold read's interpretation that this reflects careful monitoring during initial combination is reasonable.

### A3. P2 as largest paragraph correctly identified

94 tokens across 8 lines, confirmed by JSON. The identification of this as the balneum mariae evaporation step is supported by the elevated e-depth (0.67) and the recipe's explicit mention of "evaporate in the balneum mariae."

### A4. P4 zero-dar sealed cycling correctly identified

P4 has 0 dar, 0.48 e-depth, and heavy iteration tokens (qokain/qokaiin). The cold read's identification of this as sealed cycling is consistent with the data.

### A5. P8 maximum e-depth correctly identified and interpreted

P8 e-depth = 1.02 (confirmed by JSON as 1.022). The cold read correctly identifies this as the peak cooling intervention paragraph and notes the 3 observation MIDDLEs on L38 (1 cth + 2 ckh per JSON).

### A6. P9 minimal paragraph correctly described

4 tokens, single line, pure observation — all confirmed by JSON and raw TXT.

### A7. Token dictionary is well-constructed

The token table correctly maps prefix domains and atom decompositions. Source citations distinguish PT-013, B Dict, and Compositional readings. Workshop readings are internally consistent with the atom system.

### A8. e-depth P5-to-P6 jump is the largest on the folio

P5=0.464 to P6=0.915 per JSON — a +0.451 jump. This IS the largest single-paragraph e-depth transition and is correctly identified as structurally significant. The issue (O1) is with the interpretation of the first half, not with the identification of this transition.

### A9. Cross-paragraph observation MIDDLE distribution is factually correct

The ckh/cth/ecth counts per paragraph all match the JSON. P1-P8 presence and P9-P12 absence is confirmed.

---

## OVERALL

**Grade: NEEDS REVISION — Two substantive issues require correction**

The cold read is well-structured, factually grounded in the token data, and produces a largely coherent paragraph-by-paragraph reading. The dar distribution, e-depth thermal arc (with caveats), and observation MIDDLE patterns are genuine structural signals that align with the recipe.

However, two issues identified by the expert positive control are real problems:

1. **The ash regime is overclaimed.** The folio does not show a distinct direct-fire thermal phase. The e-depth dip in P3-P5 (from 0.67 to 0.46) is real but modest, and mapping it to the recipe's explicit "put on ashes and fire" step is stronger than the data supports. The honest reading is that the folio transitions from moderate thermal regulation to sustained balneum without a clearly distinguishable intermediate fire regime.

2. **The sa-prefix distribution is not discussed.** sa-prefix tokens concentrate in setup (P1-P3), not in multiplication (P7-P12). This is a distributional fact that the cold read should have flagged. It doesn't invalidate the reading, but it means the "scaffold for iterative multiplication" narrative needs qualification.

**Recommended verdict revision:** Change from COHERENT to PARTIALLY COHERENT. The dar front-loading, e-depth two-phase structure (with the P5-P6 transition), and observation MIDDLE fade-out are genuine matches. The ash-fire step and sa-prefix distribution are gaps. 5 of 7 major criteria pass, consistent with the expert's assessment.
