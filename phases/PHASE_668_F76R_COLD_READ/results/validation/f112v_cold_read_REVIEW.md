# f112v Cold Read — Error Check Review

**Reviewed by:** Expert-advisor agent
**Date:** 2026-04-27
**Cold read file:** `f112v_cold_read.md`
**Cross-checked against:** `f112v_decode_summary.json`, `f112v_cold_read.txt`

---

## ERRORS

### 1. P3 line attribution of second dar (FACTUAL ERROR)

The cold read states: "L12: Two `daiin` ('start a new cycle') — two material additions."

**Reality:** L12 has ONE `daiin` and L13 has ONE `daiin`. The raw decode is unambiguous:
- L12: `daiin, al, olkeedain, oteey, sheeol, qokeedy, qochaiin, oteey, qoty`
- L13: `dcheoty, oy, otchedy, chedy, daiin, chedal, chedy, qokaiin, otam`

The paragraph total of 2 dar is correct (JSON confirms dar_count=2). The error is attributing both to L12. The narrative then says "two material-handling events on L12 match a physical division operation" — this interpretive claim loses its force when the tokens are on different lines.

**Fix:** Change "Two `daiin` on L12" to "One `daiin` on L12 and one on L13 — two material additions across the paragraph."

---

## OVERSTATEMENTS

### 2. "~15-operation pipeline and the folio has 15 paragraphs — a near-exact structural correspondence" (MILD OVERSTATEMENT)

In the Verdict section, the cold read claims the recipe describes a "~15-operation pipeline." The recipe is continuous prose that can reasonably be parsed into anywhere from 10 to 20+ discrete steps depending on granularity choices. The ~15 count is the result of parsing it to match the folio, not an independent enumeration. Calling this "near-exact structural correspondence" overstates the precision.

**Fix:** Soften to: "The recipe describes a multi-phase pipeline whose major operations map naturally onto the folio's 15 paragraphs." Remove the claim of numerical exactness.

### 3. P6 e-depth "among the highest seen on any cold-read folio" (SLIGHTLY IMPRECISE)

The claim is directionally correct — 1.41 is very high. But without a systematic comparison across all cold-read folios, this is an unsourced superlative. The e-depth of 1.41 is genuinely remarkable and the claim is probably true, but it should be phrased as a folio-internal observation ("by far the highest on this folio") unless a cross-folio comparison is provided.

**Fix:** Keep "by far the highest on the folio" (which is factual). Remove "and among the highest seen on any cold-read folio" unless cross-folio data is cited.

---

## OMISSIONS

### 4. fch mercury marker in P1 NOT highlighted (SIGNIFICANT OMISSION)

The expert positive control specifically identified "fch mercury marker in P1 where recipe introduces lunaria/mercury" as a key supporting feature. The JSON confirms P1 has fch=1 in prefix_counts. The raw decode shows `fcheol` on L1.

The cold read mentions `fcheol` only in passing on L1 — as part of a general apparatus description — without identifying it as the fch mercury marker (C1939: fch encodes mercury/mercury-water, infinite enrichment on 6/6 mercury-recipe folios). For a recipe that explicitly starts with "take mercurial liquor (lunaria)," the fch marker appearing on the very first line is a strong structural alignment that the narrative should foreground.

**Fix:** Add to P1 narrative: "The first line also carries `fcheol` — an fch-prefix token. fch is a dark-pipeline MIDDLE that encodes mercury/mercury-water handling (C1939), appearing on all 6 confirmed mercury-recipe folios. Its presence on L1, where the recipe says 'take mercurial liquor (lunaria),' is a direct structural match."

### 5. No mention of chekar_count distribution (MINOR OMISSION)

The JSON shows chekar_count is 1 for P2, P5, P12, and P15 (total 4). The cold read discusses the P2 and P12 chekar instances but does not provide a consolidated chekar distribution table alongside the observation MIDDLE distribution table. This is a minor formatting omission — the observation MIDDLE table captures only ckh/cth/cfh, while chekar is a separate quality-check metric.

**Fix:** Either add a note that the folio has 4 chekar-class quality checks (P2, P5, P12, P15) or fold the chekar counts into the observation MIDDLE distribution table with a note about the distinction.

---

## APPROVED

### Prefix counts — all correct
Every prefix count cited in the narrative matches the JSON exactly. Spot-checked P1 (ok=9, qo=8, ot=5), P4 (qo=14, ch=9), P5 (ch=12, qo=9), P6 (ch=7, qo=4), P10 (ch=10, qo=5), P14 (ch=9), P15 (ch=14, none=15, ot=6, qo=4).

### e-depth values — all correct
All 15 paragraph e-depth values in the cold read match the JSON to ±0.01. The three-phase arc interpretation (balneum / transition-ash / reiteration) is structurally sound.

### dar counts — all correct at paragraph level
Total of 10 dar across the folio, with the two-cluster pattern (early P1-P4 = 5 dar, late P13-P15 = 4 dar, P8 = 1 apparatus dar) matching the JSON exactly.

### Token-level readings — spot-checked, consistent
Tokens cited in the narrative match the raw decode. Individual token glosses are consistent with the token dictionary and atom reference. No invented tokens or misattributed lines beyond the P3/L12 error noted above.

### Observation MIDDLE placement — correct
cfh in P3, ckh in P14, cth in P15 — all match JSON. The interpretive mapping (cfh = critical division point, ckh = heat-level verification before reiteration, cth = transfer-watch during final collection) is structurally grounded.

### Recipe text and cipher note — correct
Part III cipher correctly applied. The Catalan original and English translation are faithful. No cipher letters appear explicitly in III.1.0, correctly noted.

### Recipe-folio structural alignment — well-supported
The paragraph-by-paragraph mapping follows the recipe's process order without post-hoc rearrangement. The thermal arc (balneum peak at P5-P6, crash to material-handling at P13, low sustained heat at P15) is genuinely striking and not an artifact of selective reading.

### Token dictionary — complete and well-sourced
~40 tokens listed with prefix, atoms, compositional reading, workshop reading, and source. Sources correctly attributed to PT-013, B Dict, or Compositional.

---

## OVERALL

**Verdict: PASS with 1 factual error, 2 mild overstatements, 2 omissions.**

The cold read is well-constructed and the structural alignment between f112v and III.1.0 is genuinely strong. The e-depth arc and dar distribution are compelling folio-level patterns that do not depend on individual token glosses. The paragraph-by-paragraph narrative is detailed and mostly accurate.

**Required fixes (before publication):**
1. Correct the P3 L12 dar attribution (factual error)
2. Highlight the fch mercury marker in P1 (significant omission that strengthens the match)

**Recommended fixes (quality improvement):**
3. Soften the "15-step near-exact correspondence" claim
4. Remove or source the cross-folio e-depth superlative
5. Add chekar distribution to cross-paragraph patterns

The match quality for f112v ↔ III.1.0 remains COHERENT after review. No constraint violations detected. No tier discipline issues.
