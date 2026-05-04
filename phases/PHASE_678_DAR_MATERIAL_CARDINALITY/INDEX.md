# Phase 678: dar (Material Introduction) Cardinality Test

**Status:** COMPLETE — pre-registered test FAILED; not registered per expert disagreement
**Started:** 2026-05-03
**Goal:** Test orthogonal cardinality channel (dar = material introduction per C1925) on matched folios. Tests whether Phase 677's cardinality-encoding finding (qok-class iteration) generalizes to dar-class material counts.

## Pre-Registration

**Tests (locked from source text BEFORE folio inspection):**

- **f76r** (II.16 element separation): Source says "three elements, which pertain to the white" + "for the red there are all four elements signified by o, p, q, r." Predict: paragraph dar counts include {3, 4} within ±1.
- **f112v** (III.1 lunaria): Source says "divide it into two parts, and one part you shall keep... from the second part you shall draw the elements." Predict: early paragraph has 2 dar tokens.

**Pass criterion:** f76r paragraph counts match {3, 4} within ±1; f112v early paragraph has 2 dar within ±1.

## Results — Pre-Registered Tests FAIL

**f76r paragraph dar counts: [6, 0, 0, 1].** Does not include {3, 4} or anything within ±1 of those values. **FAIL.**

**f112v paragraph dar counts: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].** Zero dar tokens in any paragraph. Cannot satisfy "early paragraph has 2 dar." **FAIL.**

## Post-Hoc Observations (Not Registered)

After the pre-registered test failed, manual inspection and corpus baseline computation revealed:

**Observation 1: Total-count match for f76r.** Sum of paragraph dar counts in f76r = 7. Recipe predicts 3 white + 4 red = 7 elements total. f76r is the ONLY folio in 82 with exactly 7 dar tokens (1.2% rarity baseline).

**Observation 2: Line-level cluster pattern.** Manual reading of f76r shows:
- L5-L7: 3 consecutive lines, each with exactly 1 dar (3-cluster)
- L16, L22, L25, L42: 4 dar tokens spread across the latter half of the folio (4-spread)

**Observation 3: f76r's giant P1 (357 tokens).** Recipe is contrastive ("for the white...3 elements; for the red...4 elements") describing two cases within one continuous procedure. f76r's encoding doesn't separate white-paragraph from red-paragraph — it puts both in P1.

## Expert Disagreement on Registration

**Expert-advisor recommended:** Register at Tier 3 with explicit caveats. Total-count is arithmetically implicit in the source ("3+4=7"); 1.2% baseline rarity is empirical, not p-hacked.

**Crazy-expert recommended:** Do NOT register. Three core objections:

1. **Pre-registration failure must be respected.** Test specified paragraph distribution; it failed. Switching to total-count framing post-hoc is the same failure mode flagged in Phase 675.
2. **Total-count framing is unfalsifiable in disguise.** Recipes contain many numbers (proportions, days, repetitions, parts). Any folio's dar total can be decomposed into "a + b = total" matching some pair of numbers in the recipe. No pre-registered selection rule was specified.
3. **Joint p ≈ 7×10⁻⁵ is wrong.** With multiple-comparison correction across 5 cases reporting best 3, corrected p ≈ 0.02, not 7×10⁻⁵.

Plus: the L5-L7 line-level cluster is exactly the "atom gloss word salad" trap (knew "3+4," scanned for clusters of 3 and 4, found them, no pre-registered cluster definition).

## Decision

**Per user instruction "register if they agree" — they don't agree.** Following crazy-expert's harsher discipline.

**Action:** Phase 678 documented as test-ran-pre-reg-failed. No constraint registered. Methodologically suggestive observations preserved as **Tier 4 hypothesis** for future blind testing.

The Tier 4 framing: dar-channel cardinality MAY encode material counts, but rigorous test requires pre-registered paragraph-distribution criteria on multiple held-out folios with explicit selection rules for which source-numbers to count and how to define cluster windows. Without that, the f76r=7 observation is a numerical curiosity, not evidence.

## What Survives From Phase 677/678

The Phase 677 cardinality finding (C1988: f103r ×8 qok-iteration) stands. Phase 678's negative result on the orthogonal dar-channel:
- Doesn't refute Phase 677's qok-channel finding (different channels)
- Bounds the cardinality-encoding claim to **NOT confirmed for dar-material** (or at least: the paragraph-distribution prediction fails)
- f112v's zero dar specifically suggests either (a) f112v match is weaker than tier suggests, or (b) dar marks additive material introduction not partitive division (per crazy-expert)

## Methodological Lessons

- **Pre-registration discipline:** When a pre-registered test fails, don't switch to a post-hoc framing that "saves" the result. Crazy-expert explicitly called this trap before the test ran (in Phase 675 review) and called it again here.
- **The "any sum matches" trap:** Total-count framing is unfalsifiable when source contains multiple numbers. Future cardinality tests must specify (a) which source-numbers count, (b) how cluster windows are defined, (c) what counts as a hit, BEFORE looking at folio data.
- **Manual inspection still useful:** The 3-cluster + 4-spread pattern at line level is suggestive even if methodologically vulnerable. Pre-register a cluster definition (e.g., "≥N dar in K-line window") in any future blind test.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_dar_cardinality.py | Pre-registered paragraph-distribution test + corpus rarity check | ~10s |

## Suggested Follow-up

If pursuing dar-channel cardinality:
1. Pre-register a strict cluster definition (e.g., "≥N dar in 2-line window")
2. Pre-register selection rule for which source-numbers count (e.g., "first explicit material count mentioned in matched chapter")
3. Run blind on 5+ matched folios with explicit material counts
4. Pass criterion: ≥3/5 hits within ±1 of pre-registered N
5. Per crazy-expert's bet: expected outcome is 1-2/5 (regression to baseline). If 3+/5, finding is real.

## Relationship to Existing Constraints

- **C1925** (dar = material introduction, 5 distribution patterns): SURVIVES; this phase did not test C1925's claims.
- **C1988** (f103r ×8 qok-iteration cardinality): UNCHANGED; this phase tested orthogonal channel.
- **C1971** (Phase 668 cold-read coherence): f112v's zero-dar count combined with predicted 2 material introductions raises mild concern about match strength — but f112v was already classified "Coherent 6/8" partial.
