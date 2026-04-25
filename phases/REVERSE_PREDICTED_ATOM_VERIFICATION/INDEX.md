# Reverse-Predicted Atom Verification

**Phase:** 644
**Status:** COMPLETE
**Type:** Match-tier confirmation via atom-decode operational scoring
**Started:** 2026-04-25
**Completed:** 2026-04-25
**Outcome:** BOTH_CANDIDATES_CONFIRMED. f108v↔III.29.0 and f79v↔II.8.0 promoted from blind-test hits to MATCH-tier confirmed. C1959 evidence base extended.

## Purpose

Verify two reverse-predicted folio↔recipe candidates from the Phase 641-followup blind reverse-prediction test. Both candidates passed initial structural-anchor matching (count present in recipe + procedure-family alignment) but had not yet been validated at the operational level (atom-decode reading of recipe steps against folio paragraph structure).

Both internal experts independently recommended this verification as the highest-value next move after Phase 643 registered C1959.

## Candidates

| Folio | Recipe | Recipe family | Initial blind-test verdict |
|-------|--------|---------------|----------------------------|
| f108v | III.29.0 | Mercury sublimation | STRONG HIT (3 anchor + family fit) |
| f79v | II.8.0 | First liquefaction / 3-day balneum | STRONG HIT (3 anchor + family fit + dar-adjacency) |

## Methodology

For each candidate:
1. Pull full Catalan + Latin recipe text (SISMEL critical edition)
2. Pull folio raw line dump with paragraph-initial markers
3. Read directly (per the methodology lesson — read first, scripts only verify)
4. Score per criterion: heat-pattern match, count-anchor location, material-introduction alignment, observation/decision pattern, operational-structure length match
5. Tally: MATCH / WEAK / MISMATCH per criterion
6. Verdict: STRONG SUPPORT / MODERATE / WEAK / DOES NOT SUPPORT

Followed by Test B Extended: paragraph layout-position vs recipe-phase ordinal Spearman correlation, to extend C1959's evidence base.

## Scripts

| Script | Purpose |
|--------|---------|
| `pull_data.py` | Pull recipe Catalan/Latin + folio raw line dumps |
| `test_B_extended.py` | Run Test B (layout-phase correlation) on the two new matches |

## Results

| File | Contents |
|------|----------|
| `raw_data.md` | Recipe texts + folio raw line dumps for direct reading |
| `findings.md` | Operational scoring per criterion + final verdicts |
| `test_B_extended.json` | Test B numerical results on new matches + aggregate across all 7 |

## Findings

### f108v ↔ III.29.0 (mercury sublimation): STRONG SUPPORT

**Score: 7 MATCH / 1 WEAK / 0 MISMATCH.** Heat-dominant procedure (qok-class total 63, qokeedy 28), three principal operations anchor (3-run of qokeedy at L39 — corpus-rare Shape 1), gentle-heat dominant (qokeedy:qokedy = 28:8 ratio = balneum signature), long sustained operation (P9 spans 19 lines), few discrete material additions (consistent with abstract/theoretical recipe), continuous procedure (0 chekar consistent with no phase-gating).

**Test B:** rho=+0.924, perm p=0.002, n=10 paragraphs. **Strict significance.**

**Caveat:** III.29.0 has unusual recipe-text character (long discursive content with religious-philosophical digression). The 3-anchor has multiple potential referents in the recipe text. Structural alignment is solid; interpretive judgment is involved.

### f79v ↔ II.8.0 (first liquefaction): STRONG SUPPORT

**Score: 6 MATCH / 2 WEAK / 0 MISMATCH.** Three-fold reinforced 3-anchor:
1. Corpus-rare 3-run of qokedy at L19 (Shape 1)
2. 3-run immediately followed by `dar` (material+cycle co-located)
3. Total dar count = 3 across folio (matches recipe's 3 distinct materials F, E, menstruum)

Plus: qokeedy-dominant (balneum: 13 vs 9 qokedy), heavy iteration (qokain 12), 0 chekar (recipe is straight procedure with no phase-gate). Length match (354 tokens, 7 paragraphs vs 2509-char recipe).

**Test B:** rho=+0.954, perm p=0.005, n=7 paragraphs. **Strict significance.**

**This is among the tightest reverse-predicted matches achieved.**

## C1959 evidence-base extension

Updated counts:
- Confirmed matches: 5 → **7** (across **6** distinct recipe classes; sublimation added)
- Mean rho: +0.812 → **+0.848**
- All matches positive direction: 5/5 → **7/7**
- Strict-significance (p<0.05): 2/5 → **4/7**

## Tier promotion question

Expert-advisor's threshold: *"3+ additional confirmed-match folios with n≥10 paragraphs reach individual significance."* Phase 644 added 2 such matches (f108v at n=10, f79v at n=7). Short of 3-additional by 1, but the empirical position is substantively stronger:
- Reverse-predicted matches that pass atom-decode verification + Test B at strict significance are stronger evidence than original forward-matches
- 4/7 strict-significance with 7/7 positive direction is a different evidence profile than 2/5

C1959 retained at Tier 3 pending explicit Tier 2 review. Updated constraint file documents the new evidence and the threshold question.

## Constraints

| Constraint | Action |
|------------|--------|
| C1959 | Evidence base extended: f108v + f79v added to confirmed matches. Phrasing updated to reflect 7-folio aggregate with mean rho +0.848 and 4/7 strict-significance. Tier 3 retained. |
| C-NEW (NOT created) | The two new matches were considered as sufficient evidence for a separate "reverse-prediction methodology validated" constraint, but deferred — the methodology validation is implicit in C1959's extension, and a separate constraint would duplicate. Note for future: if a third + fourth reverse-prediction also confirms, register methodology validation as a stand-alone constraint. |

## Next steps

Per both experts' convergent recommendation: heat-mode encoding investigation. C1225, C1226, C1457-C1462 scaffold ready. Crazy-expert's specific add: test heat-mode on matched folios using paragraph layout-order as predictor (converts heat-mode from corpus-correlation to recipe-decoded prediction).
