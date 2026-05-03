# Phase 677: Iteration Cardinality Generalization Test

**Status:** COMPLETE
**Started:** 2026-05-03
**Goal:** Test whether the f75r ×4/×9 cardinality match (per C1965) generalizes to other matched folios. If recipe correspondence is real, recipes with explicit numeric iteration counts in source should produce analogous cardinality markers in the matched folio.

## Pre-Registration

**Source-extracted predicted iteration counts** (locked from English recipe text BEFORE looking at folios):

| Folio | Recipe | Predicted N | Source phrase | Strength |
|-------|--------|-------------|----------------|----------|
| f75r | III.19 aqua vitae | 9 | "ond distillation through nine times" | strong (template, C1965) |
| f82r | III.19.1-5 multi-recipe | 9 | (same chapter as f75r) | strong |
| f79r | III.12 mercury sublim. | 3 | "a third time distill" | strong |
| f112r | III.11 red mercury tincture | 3 | "distill...three times" | strong |
| f103r | III.16 ferment multipl. | 8 | "all four or eight chambers" | weak |
| f84r | II.12 gold dissolution | 3 | "three natural days" | weak (duration) |

Excluded (no iteration count in source): f76r, f76v, f81v, f112v, f116r.

**Test:** Find clusters of N qok-class tokens (qo-prefix with k as first MIDDLE atom) in 1-2 line windows. Pass = max-cluster-size ≥ N, with folio-relative rarity ≤ 25%.

## Results

**Folio-relative rarity** (corpus baseline — % of all 82 B folios reaching max cluster ≥ N):
- N=3: **83%** — TRIVIAL, no discriminative power
- N=8: **15%** — moderate rarity
- N=9: **4%** — RARE (consistent with C1969)

**Per-folio:**

| Folio | Predicted N | Max observed | Verdict | Position | Recipe Position |
|-------|------------|--------------|---------|----------|-----------------|
| **f75r** | **9** | **9 (exact)** | **HIT** | L37-L38 (~84%) | late ("nine times") |
| **f103r** | **8** | **8 (exact)** | **HIT (NOVEL)** | L36-L37 (~67%) | middle/late ("four or eight chambers") |
| f82r | 9 | 7 | within ±2 | n/a | n/a (multi-recipe) |
| f79r | 3 | 7 | trivial pass | L3-L8 (~10-20%) | late — POSITION MISALIGNS |
| f112r | 3 | 4 | trivial pass | L9-L11 (~30%) | early — rough alignment |
| f84r | 3 | 6 | trivial pass | scattered | n/a (duration not iteration) |

**The clean novel finding: f103r ×8.**

Cluster at L36-L37 (out of 54 lines, ~67% through):
```
L36: okool chedy okeedy [qokeedy qokeey] shdy otey [qokeey]
L37: pchedy [qokeey qokeodair qokshy qokeedy qokeedy] chsky shey shalky
```

8 qok-class tokens in adjacent lines, in the rare 15% baseline band, position-aligned with the recipe's late "all four or eight chambers" passage.

**The f82r miss explained but post-hoc:** f82r encodes III.19.1-5 (waters 2-6 multi-recipe per Phase 668's C1937). The "ond distillation through nine times" is from III.19.0 main recipe (= f75r). Sub-recipes within a chapter don't necessarily inherit the parent iteration count. Note: this rescue is post-hoc and unfalsifiable — flagged as a methodological concern in expert review.

**N=3 cases are uninformative:**
- f79r/f112r/f84r all "hit" but at 83% corpus baseline
- f79r position MISALIGNS (cluster early, recipe says late)
- f112r position roughly aligns (cluster ~30%, recipe says early)
- f84r ("three natural days") is duration not iteration; skip

## Verdict

**Tier 3 observation: rare-cardinality clustering plausibly encodes iteration counts. Validated on f75r (template, already C1965) and f103r (novel, 1 case).**

The cleanest evidence is exactly **one novel anchor** (f103r ×8). Joint p(f75r=9 AND f103r=8 | random) = 0.04 × 0.15 = 0.6%, but that's only 2 cases and f75r was already known.

**Why Tier 3 not Tier 2** (per expert review):

1. **One novel hit** (f103r) is not enough to register a generalized "iteration cardinality is encoded" claim. C1969 required pre-registered matched-pair specificity across multiple anchors before promotion.
2. **N=3 cases provide no information** (corpus-trivial baseline 83%).
3. **f82r miss is a post-hoc rescue** — "multi-recipe sub-recipes don't share parent count" is unfalsifiable; any miss can be attributed this way. Test loses falsifiability.
4. **Crazy-expert specifically flagged:** "qualitative reading of f103r 8 chambers = 8 thermal tokens" is confirmation bias dressed up. Inadmissible for tier promotion (per `feedback_atom_gloss_word_salad.md`).
5. **Pre-registered pass criterion was ≥5/7 within ±1**, achieved 4/6 strict; but only 2 of those are non-trivial (rare-N). Failure by own pre-reg threshold.

## Constraint Update

### C1988 (Tier 3, observation): f103r encodes rare-cardinality cluster matching source iteration count

f103r matched to III.16 (ferment multiplication, "all four or eight chambers"). Pre-registered N=8 from source text. Observed exactly 8 qok-class tokens in 2-line window at L36-L37, in the rare 15% folio-relative baseline band. Position aligns with the recipe's late chamber-multiplication passage.

Joint with f75r (×9 template, C1965): 2 of 2 rare-N predictions hit exactly. Joint chance probability = 0.6%. Adds one novel anchor to the C1965/C1969 evidence base for "iteration cardinality is structurally encoded."

**Limitations:** Single novel case (f75r is template, not independent novelty). f82r ×9 miss is explainable but unfalsifiable post-hoc. N=3 cases (f79r, f112r, f84r) corpus-trivial. Qualitative cluster-reading inadmissible for tier promotion.

Promotion to Tier 2 requires a third pre-registered rare-N anchor landing on a novel folio. Currently registered as candidate evidence pending more cases.

**Tier:** 3 (Currier B, observation)

## Methodological Notes

- Pre-registration (Stage 1 source extraction before Stage 2 folio test) was clean for the procedure
- Pass criterion (≥5/7 within ±1) was missed by own threshold — this is honestly a partial result
- Discriminating evidence (rare-N) is 2/3 hits including 1 novel
- Both experts converged on Tier 3 single-anchor framing
- Crazy-expert correctly flagged confirmation-bias risk on qualitative readings
- The N=3 trivial-baseline lesson generalizes: rarity threshold determines whether a count-match is informative

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_extract_source_counts.py | Extract numeric mentions from English recipe text | ~5s |
| s2_test_cardinality.py | Find qok-class clusters at predicted N, compute folio-relative rarity | ~30s |

## Relationship to Existing Constraints

- **C1925** (dar = material introduction, 5 patterns): different cardinality channel; orthogonal.
- **C1965** (f75r encodes ×4 + ×9 reflux/iteration): C1988 adds f103r ×8 as second anchor.
- **C1969** (corpus-singular density signature for f75r ×9): C1988 confirms this generalizes to at least one additional rare-N case.
- **C1971-C1975** (matched-folio operational coherence): C1988 contributes a structural anchor consistent with these.
- **C1937** (f82r is multi-recipe III.19.1-5): explains the f82r miss but post-hoc rescue is methodologically uncomfortable.

## Suggested Follow-Up

- **More rare-N cases in future matched folios:** if new matches identified, pre-register their iteration counts and test. Target: third novel anchor for Tier 2 promotion.
- **Other cardinality channels:** test dar-material-introduction cardinality (per C1925) on matched folios with explicit ingredient counts (e.g., f76r "three elements + four elements"). This is orthogonal to the qok-class iteration channel.
- **Falsifiability fix for multi-recipe folios:** define rules for which sub-recipe a multi-recipe folio encodes BEFORE looking at folio data. Currently the multi-recipe rescue is post-hoc.
