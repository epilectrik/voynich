# PHASE_765 — Is Currier B nearer to discrete-operation step notations?

**Status:** COMPLETE. Locked verdict: **NOT SUPPORTED**, stable across all variants. Registered as C2083 (Tier 2,
negative knowledge).
**Pre-registration:** `PRE_REGISTRATION.md`, locked at commit d9bb96f after a lean-expert audit (edits E1–E8).
**Scripts:** `scripts/step_compare.py` (17.3 min) and `scripts/sn765.py` (extraction); shared statistics come from
PHASE_764's `g764.py`.
**Results:** `results/step_compare.json`, `results/run_log.txt`.
**Corpora** (raw files in git-ignored `external/`):
- 11 knitting/crochet notation corpora (Project Gutenberg);
- 6 chess collections (pgnmentor);
- Apollo Guidance Computer assembly (Comanche055 + Luminary099; public domain);
- 15 needlework-prose corpora;
- 4 Latin procedural texts (Antidotarium Nicolai, Mesue, Rupescissa 1561, SISMEL Testamentum);
- 71 meaningful texts and 23 gibberish samples (Gaskell & Bowern);
- constrained non-notation: Naibbe ×5, Timm–Schinner ×5, Roget's Thesaurus.

## Question
Is B's low-level rule-boundedness profile nearer to discrete-operation step notations than to prose, improvised
gibberish and constrained non-notation? This tests the human's "discrete workshop operations" model of B.

The profile has three parts: P1 boundary coupling (normalised by word-initial entropy), P2 identical adjacent repeats,
and P3 near-repeats (observed/expected). Chunks are 197 within-line pairs, and every corpus, B included, is re-wrapped
to B's line lengths.

## Result
**Unit median distance to B** (lower is nearer; B's own chunks sit at 0.94 from B's profile; two random halves of B
are 0.22 apart):

| Unit | Distance | P1 coupling | P2 repeats | P3 near-repeats |
|---|---|---|---|---|
| **B** | — | 0.058 | −0.14 | +0.05 |
| **Gibberish (G)** | **1.31** (nearest) | 0.015 | −0.46 | +0.02 |
| Constrained non-notation (CN) | 1.58 | 0.001 | −0.41 | −0.03 |
| Chess (SN) | 1.71 | 0.005 | +0.79 | +0.43 |
| Latin procedural prose (PP-L) | 1.75 | 0.011 | −0.91 | −0.32 |
| Meaningful (M) | 2.02 | 0.021 | −1.38 | −0.42 |
| Needlework prose (PP) | 2.17 | 0.047 | −1.55 | −0.04 |
| **Knitting notation (SN)** | **3.00** | 0.131 | −1.90 | +0.33 |
| **AGC assembly (SN)** | **3.33** (farthest) | 0.061 | −2.21 | −1.24 |

- **No step-notation subgroup wins.**
  - Knitting and AGC lose to every class.
  - Chess beats M and PP (stability 1.0) but not PP-L (0.62), G (0.0) or CN (0.0).
- **Paired test:** in all 11 needlework books, the book's own prose is nearer to B than its notation (0/11 notation
  nearer).
- **The 10 corpora nearest to B:** 9 are gibberish samples; the tenth entry is B itself.
- **Mann–Whitney, SN vs the others (descriptive):** p = 0.998, i.e. step notations are, if anything, farther from B.
- **Variants:** all NOT SUPPORTED (V1 EVA; V2 +TTR; V3 chess lower-cased; V4 thresholds 0.25 and 0.35; V5 authorial
  lines; V6 digits collapsed; V7 Mahalanobis; V8a–c each statistic dropped).

## Reading
- **Modern step notations are more extreme than B, in characteristic directions.**
  - Knitting: strong boundary coupling, strong avoidance of identical repeats, many near-repeats (k2/p2 alternation).
  - AGC: strongly anti-repetitive, because opcode and operand alternate.
  - B is moderate on all three.
- **B's profile is closest to fluent improvised writing.** It is still more constrained than improvisation: 4× the
  coupling, and more repetition and near-repetition. The constrained generators come next.
- **On these statistics, B does not look like abbreviated, tabular operation notation.** The "discrete workshop
  operations" model loses this line of support, not the model itself.
- **What stays open:** procedures written as fluent word-like tokens (rather than abbreviations and counts), and any
  claim at line, paragraph or page level. Line-position dependence was excluded by design here; in PHASE_764 it was
  B's strongest descriptive difference from gibberish.
- **Not evidence of meaninglessness.** Nearest is not the same: B's own chunks are 0.94 from its profile, and gibberish
  is 1.31.

## Deviations
- **Roget's Thesaurus was also loaded as a needlework-prose corpus.** It sits in the same download folder, so it
  appeared in PP as well as in CN (implementation slip). Without it, the PP median distance is 2.19 instead of 2.17.
  No verdict-bearing comparison changes, since no step-notation subgroup beats G in either case.
- **AGC:** no source files were byte-identical across Comanche055 and Luminary099, so all 169 files entered the merged
  corpus.
- **B and the CN generators were joined within folio** (declared D2).
