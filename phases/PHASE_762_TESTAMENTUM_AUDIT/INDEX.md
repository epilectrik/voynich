# PHASE_762 — Testamentum audit

**Status:** Part B COMPLETE; Part A (triage) PROPOSED in `TRIAGE_TABLE.md`, awaiting human review before it is applied.
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit dd88045; lean-expert audit applied).
**Scripts:** `scripts/testamentum_audit.py` (5.4 min; a numpy re-implementation of `shared_628.residual_match`, verified to
give identical assignments and confident counts), `scripts/b3_three_level.py` (the pre-registered three-level B3).
**Results:** `results/testamentum_audit.json`, `results/b3_three_level.json`, `results/run_log.txt`.

## Sources as built
PL-PROC: 82 Testamentum chapters with a non-theoretical primary family (median 291 words), re-featurized from their
English text with PHASE_718's featurizer (parity) and also with the original PL features. THEO: 179 Theophilus chapters
merged within books into 120 units; many single chapters already exceed the PL median, so units remain longer (median
556 words) — a residual length mismatch (features are per-word rates). CODI: 19 segments (descriptive). Folio pool: 82
Currier B pages (REGIME_1: 32).

## Results (locked rules, α = 0.0167)
**B1 — does real chapter content match better than the same chapters with features scrambled?** Median over 200 random
16-chapter subsets of (real − column-permuted-null median) mean ratio, and the median rank p:
| Source | Median excess | Median p |
|---|---|---|
| PL-PROC (parity features) | −0.003 | 0.59 |
| PL-PROC (original features) | −0.023 | 0.77 |
| PL-PROC, REGIME_1 pool | −0.006 | 0.64 |
| Theophilus | −0.0001 | 0.50 |
| Theophilus, REGIME_1 pool | −0.006 | 0.70 |
| Codicillus (descriptive) | −0.019 | 0.95 |
**Verdict: NO CORRESPONDENCE.** No source — Testamentum, Theophilus or Codicillus — matches the Voynich pages better than
its own chapters with the features shuffled among them. The 8D match quality reflects the shape of the feature sets,
not which chapter goes with which page.

**B2 — do the two sides of a leaf land on adjacent chapters (automated, similarity-matched)?** 34 eligible leaves.
| Source | Leaf-mates adjacent (Δ = 1) | Similarity-matched null | p | Same chapter (Δ = 0) |
|---|---|---|---|---|
| PL-PROC (parity) | 2.9% (1/34) | 3.1% | 0.72 | 11.8% vs 12.8% (p 0.67) |
| PL-PROC (original) | 0% | 1.9% | 1.0 | 5.9% vs 10.1% |
| Theophilus | 2.9% | 0.9% | 0.28 | 20.6% vs 16.0% |
MDE80 ≈ 6 percentage points. **Verdict: NO EFFECT.** Automated matching does not put the two sides of a leaf onto
adjacent Testamentum chapters.
**How the claimed recto/verso pairs were found (B4):**
| Leaf | Recto | Verso | How |
|---|---|---|---|
| f66 | Ch24P (full-spectrum scan) | Ch26P (reverse-blind) | separate methods; Δ = 2; "fixation → inceration" is an interpretive relation |
| f103 | Ch16M (expanded matching) | Ch27P (reverse-blind) | different books; relation interpretive |
| f108 | Ch16P (Phase 628) | Ch10 + 11P (reverse-blind) | not adjacent in number; relation interpretive |
| f84 | Ch14P (Phase 628) | Ch15P (cs hard filter on the verso of f84r) | targeted search of the other side |
| f115 | Ch21P + 28P (blind + split) | Ch25P (recto/verso scan) | targeted search of the other side |
| f114 | Ch23P (recto/verso scan) | Ch31P (recto/verso scan) | both via targeted scan |
| f106 (tentative) | Ch17M (recto/verso scan) | Ch40M (fch hard filter) | targeted search |
None of the six is a pair of numerically adjacent chapters found by independent matching of both sides.

**B3 — does the part of the book predict the manuscript section of the matched page?** Bias-corrected Cramér's V against
each source's own permutation null (10,000):
| Source | V_bc | p |
|---|---|---|
| **PL-PROC, pre-registered 3-level partition (Practica / Mercuriorum / Furnis)** | **0.00** | **1.0** |
| PL-PROC, original features, 3-level | 0.00 | 1.0 |
| PL-PROC including Theorica-part procedural chapters (4 levels; implementation slip, reported) | 0.086 | 0.30 |
| Theophilus, Books I / II / III | 0.235 | 0.002 |
| Theophilus, top-5 attractor pages excluded | 0.196 | 0.050 |
Flagged secondary (partition taken from the matching itself): Mercuriorum ≤ 28 / ≥ 29 — in the JSON. **Verdict: NO
EFFECT.** The Testamentum's parts do not map onto manuscript sections under automated matching — while the same pipeline
does sort Theophilus's books by section (mostly Book III → Section B), which shows the pipeline *can* produce a
book → section pattern from a non-alchemical text.

**B5 — the permutation-test flaw.** C1887's procedure gives p < 0.01 for **100 of 100** sets of random Gaussian
"chapters" and **100 of 100** random Theophilus subsets (median p = 0). **FLAW CONFIRMED:** that test cannot distinguish
real correspondence from noise.

## Reading
1. The recipe-matching evidence does not survive a matched control. The 8D matcher's match quality carries no
   chapter-specific signal (B1), its headline significance test is uninformative by construction (B5), the recto/verso
   adjacency does not appear when matching is automated (B2), and the Mercuriorum → Section B / S mapping does not appear
   either (B3). Together with C2052 (Theophilus matches the same pages) and C2035 (matched chapter similarity does not
   predict page similarity), the chapter → folio assignments are not evidence that the manuscript encodes the *Testamentum*.
2. What survives is a set of text facts that were found while examining matched folios (the ×4 qokedy run unique to
   f75r, the double dar, the f76r monitoring gradient, the cs enrichment on the f84 leaf) and source-text facts (III.19
   is the only SISMEL Catalan sub-recipe mentioning both ×4 and ×9). The f75r ↔ III.19 coincidence remains the single
   specific link, but its pairing came from the generic matcher and the ×4 feature was noticed afterwards; it needs a
   prospective test, not more post-hoc analysis.
3. This audit does not show that the manuscript is *not* about alchemy or distillation. It shows that this matching
   method cannot tell. The content question is open and needs a design the method cannot fool: prospective predictions
   frozen before looking, or a discriminative feature set not derived from the Voynich side (PHASE_723's blocked Phase 4).
