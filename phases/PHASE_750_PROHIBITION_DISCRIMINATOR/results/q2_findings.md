# Q2 — Is C2076's "sealed/self-contained" REGIME-real or a corpus-average artifact?

**Verdict: SPLIT — and it kills the proposed sharpening while confirming the property is real.**
The two candidate seal-break metrics disagree, and the disagreement is the finding.

Method fidelity (cross-line FL): 561 cross-line pairs (C1227=707), 36.0% regression (C1227=36.4%),
26 LATE→EARLY (C1227=33) — same method, ~80% of C1227's paragraph set (par-segmentation diff);
proportions match, so the REGIME split is valid.

---

## Leg (a) — aii "unseal" MIDDLE by regime  [the DIRECT seal-break correlate]
Reproduces C1247 **exactly**:

| Regime | aii-folios | aii tokens |
|---|---|---|
| REGIME_1 (sealed/continuous) | **1/32** | 1 |
| REGIME_2 | 3/15 | 3 |
| REGIME_3 (open-cycle) | **14/20** | 23 |
| REGIME_4 | 3/15 | 5 |

→ **Strongly REGIME-stratified.** The explicit "unseal" vocabulary is an R3 (open-cycle) feature, ~absent in R1 (sealed). The sealed-vs-open-cycle distinction is REAL at the operation level.

## Leg (b) — cross-line LATE→EARLY full FL reset by regime  [crazy's proposed STRUCTURAL correlate]

| Regime | LATE→EARLY / pairs | rate |
|---|---|---|
| REGIME_1 | 19 / 415 | **4.58%** |
| REGIME_2 | 5 / 105 | 4.76% |
| REGIME_4 | 1 / 27 | 3.70% |
| REGIME_3 | 1 / 14 | 7.14% (underpowered — R3 lacks 6+ body-line paragraphs) |

→ **UNIFORM ~4–5%, NOT stratified.** The prediction "R1 ≈ 0 resets" is **falsified** — R1 carries the *most* full resets (19, more than any regime), at the same rate as R2/R4. R3 cannot be measured (14 pairs, 1 event). Full FL-resets are a **global cycle-boundary phenomenon** (consistent with C1227's own reading: "marks cycle boundaries within a continuous process"), **not** a regime-specific seal-break.

---

## Synthesis
- The sealed-vs-open-cycle distinction **is REGIME-real** — but it lives in the **unseal vocabulary** (aii, C1247: R1 sealed, R3 open-cycle), **NOT** in FL-reset structure (uniform).
- So C2076's "self-contained" is **not a corpus-average artifact** (the property is real and regime-differentiated via aii) — but the **structural** "no-full-reset" property is **global/uniform**, present in R1 at the normal ~4–5% rate. Full resets ≠ unsealing; they don't track closure.
- **Crazy's specific sharpening fails on its own metric:** you cannot stratify self-containment via cross-line resets. The right metric (aii) already exists and is already registered (C1247). The new structural test (resets) adds **no new stratification** — it's a NULL.

## C2070 discipline notes
- aii is partially **section-aligned**: 11/14 R3 aii-folios are Section S (pharma); R1 ≈ Bio. The R1-vs-R3 contrast co-varies with section — but C1247 (Tier 2) already stands as "the strongest single-MIDDLE REGIME discriminator," and aii is off the high-iteration axis (R3 is not the high-iteration regime), so it is not GMM-circular.
- FL state is terminal-suffix-based → adjacent to the `terminal_rate` GMM feature, but the cross-line *reset* is a dynamic, not the static rate (off-axis-ish). Reported as gradient, not crisp classes.

## Consequence for the plan
- **C2076 stands as-is (Tier 3).** Its "sealed" leg is real (via C1247), not a corpus average — so not disqualified — but Q2 provides **no new structural stratification** to harden it, and coder-independence still blocks B regardless (lean).
- **Do NOT invest in the FL-reset sharpening** (null) or in B's structural angle.
- The sealed-vs-open-cycle axis is **already maximally captured by C1247**. The real referent move remains **Q3** (the Catalan prohibition-ontology crib).
