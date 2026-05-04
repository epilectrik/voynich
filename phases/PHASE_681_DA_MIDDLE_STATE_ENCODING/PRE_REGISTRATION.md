# Phase 681 Pre-Registration

**Locked: 2026-05-04, before any f84r dar-token data inspection.**

## Hypothesis

**H1:** In f84r, da-prefix MIDDLE composition encodes material state, where state varies systematically by recipe stage.

This is a refinement of C897 ("Prefixed FL MIDDLEs as Line-Final State Markers" — operation→state mapping via terminal MIDDLEs) extended to da-prefix MIDDLE composition.

## Framework Compatibility (Verified)

- **No conflict with C171** (atom semantics stable) — hypothesis is dimensional/compositional, not interpretive
- **No conflict with C1394** (atom model) — no new atom glosses required
- **No conflict with C1976** (polyalphabetic cipher REJECTED) — atoms keep stable semantics; state encoded by composition
- **Refines C897** (FL terminal MIDDLE state markers) — extends to da-prefix MIDDLE composition
- **Refines C1925** (dar = material introduction, 5 patterns) — predicts which MIDDLEs appear when

## Forbidden Frame (Bright Line)

- ❌ Specific material identity ("MIDDLE = mercury")
- ❌ Direct semantic content recovery
- ✅ Operational state classes via composition
- ✅ State transitions encoded structurally

## Target Folio

**f84r** — matched to Pseudo-Lull II.12 "Gold dissolution (balneum + putrefaction)."

Reasons for selection:
- Highest dar count among matched folios (13 expected per Phase 678)
- Clearest stage progression in source: gold → dissolved → putrefied → fixed
- Coherent match per Phase 668 (5/9 coherent, Tier 2)
- 14 paragraphs allowing stage-position resolution

## Operational Definitions

**Stage proxy:** paragraph ordinal (1-14) within f84r. Justified by C1959 "paragraph layout-order tracks recipe-phase order on matched folios" (mean rho=+0.81).

**Stage bins (k=4):** quartile-binned paragraph ordinals matching the recipe's 4 conceptual stages (gold → dissolved → putrefied → fixed).

**MIDDLE atom set:** for each dar token, extract the MIDDLE component (between prefix `da` and final terminal). For `darchdy`, MIDDLE atoms = {r, c, h, d}. For `daldal`, MIDDLE atoms = {l, d}.

**Distance metric:** atom-Jaccard on MIDDLE atom sets. d(A, B) = 1 - |A ∩ B| / |A ∪ B|.

## Tests (Pre-Registered)

### PRIMARY: ARI clustering test (crazy-expert's killer)

1. For each of 13 f84r dar tokens, compute MIDDLE atom set
2. Hierarchical clustering on Jaccard distance, k=4 clusters
3. Compute ARI between cluster assignments and paragraph-quartile bins
4. Permutation null: shuffle dar token MIDDLEs across the 13 paragraph positions, recompute ARI (10k shuffles)
5. **Pass criterion: ARI > 0.30 AND permutation p < 0.01**

### SECONDARY: Mantel correlation

1. Pairwise paragraph-ordinal distance matrix (78 pairs from 13 tokens)
2. Pairwise MIDDLE atom-Jaccard distance matrix
3. Mantel correlation rho
4. Permutation null: row/column permutation of MIDDLE distance matrix (10k shuffles)
5. **Pass criterion: rho > 0.30 AND permutation p < 0.01**

### NULL CONTROLS

**N1: Within-folio token-shuffle null** — for both tests, shuffle MIDDLE assignments across the 13 dar positions in f84r, recompute test statistic. The primary permutation test above implements this.

**N2: Section B dar-pool null** — sample 13 random dar MIDDLEs from non-f84r Section B folios, recompute test statistic. Tests whether observed MIDDLE composition is f84r-specific or generic-Section-B-pool.

## Power Check (Pre-Registration Sanity)

With n=13 dar tokens (78 pairs):
- Mantel rho 0.30 detection power at α=0.01 with n=78 pairs: ~80% (rule of thumb)
- ARI of 0.30 with k=4 over n=13 is roughly 60% power
- **Test is underpowered for marginal effects** (rho < 0.40); only large effects detectable

## Confound Controls

**C1: Paragraph-1 confound (Phase 675 lesson):** Run analysis (a) including paragraph-1 dar tokens, (b) excluding paragraph-1 dar tokens, (c) partial-Mantel with paragraph-position as covariate. Report all three.

**C2: dar-token clustering vs MIDDLE distribution:** Per Phase 678, f76r had 7 dar concentrated in P1 (6 of 7). Check if f84r dar's are similarly concentrated; if yes, the test reduces to "do paragraph-1 dar's differ from later-paragraph dar's?" — adjust interpretation accordingly.

## Decision Tree

| Outcome | Verdict | Action |
|---------|---------|--------|
| Both PRIMARY (ARI>0.30 p<0.01) and SECONDARY (Mantel rho>0.30 p<0.01) pass | State-encoding supported | Tier 3 registration candidate |
| One passes, one fails | Ambiguous | NO REGISTRATION; document as suggestive |
| Both fail | State-encoding rejected | NO REGISTRATION; identification-vocabulary explanation per C1135 prevails |
| f84r dar count < 8 | Insufficient power | Abort test, document limit |

## Crazy-Expert's Bet (For Calibration)

> "Partial signal, leaning null. f84r will probably show weak clustering (rho 0.15-0.30, p ≈ 0.05-0.20) — interesting but not decisive."

If outcome matches this bet (partial), don't register. Use as calibration for whether bet was accurate.

## What Will NOT Happen

- No post-hoc adjustment of pass criteria
- No "paragraph-1 only" or "paragraph 5-9 only" subset analysis if full test fails
- No interpretation of specific MIDDLE content (e.g., "this MIDDLE means dissolved")
- No tier promotion above Tier 3 from f84r alone

## What Could Promote Beyond Tier 3 (Future)

Tier 2 requires:
1. f84r primary test passes
2. Cross-folio replication on ≥3 matched pairs (e.g., f81v, f76r, f116r each have ≥5 dar tokens)
3. Negative control fails (shuffled-stage assignment doesn't reproduce pattern)
4. Per-stage MIDDLE conservation (same stage → similar MIDDLE across folios)

These are NOT being tested in Phase 681. They are deferred to Phase 682+ if Phase 681 passes.
