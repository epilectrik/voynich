# PHASE_754 — Glyph-unit orthography gate (pre-registration)

**Locked:** 2026-09-27, before the analysis script was written or run.
**Origin:** STRATEGIC_REVIEW_2026-09-27 §3 #3; failure pattern "transliteration-unit artifact" (taxonomy v1.1).
**Claims under test:** C1440 (h 98.7% "transparent" terminal), C1209 (n 99.4% terminal), C1484 (terminal modifier
exclusivity: n preceded only by i; h preceded only by c), C1207 (atom clusters {c,h} r≈0.75 and {a,i,n,r} r≈0.8),
C521 (e→h = 0.00, the "one-way valve").

## Glyph tokenization (declared)
Applied left to right within each EVA token, longest match first:
1. Benched gallows `cth`, `ckh`, `cph`, `cfh` → one glyph each.
2. Benches `ch`, `sh` → one glyph each.
3. Minim groups: one or more `i` followed by one of `n`, `r`, `l`, `m` → one glyph named by its i-count and final
   (e.g. `in`, `iin`, `iiin`, `ir`, `iir`, `il`, `im`).
4. Every other character is its own glyph (`e` runs stay as separate `e` glyphs).
Data: H track, Currier B text tokens (`Transcript().currier_b()`), and Currier A for the cross-check.

## Part A — definitional audit
For each EVA letter: the share of its occurrences that sit inside a multi-letter glyph under the rules above
("context determinism"), and its top left/right neighbours.

## Part B — glyph-level restatements (descriptive, with a within-token shuffle reference where stated)
- B1 (C1440 → bench finality): share of bench and benched-gallows glyphs that are token-final, vs all other glyphs.
- B2 (C1209 → minim-group finality): share of minim-group glyphs that are token-final; share of bare `n` tokens.
- B3 (C521): within-token transitions `e` → bench / benched-gallows glyph, observed vs a within-token glyph-shuffle
  expectation (glyph multiset of each token preserved, order shuffled, 200 replicates).
- B4 (C1207): folio-level Pearson r between letter counts in EVA (reproduce the registered clusters), then the same
  folio-level correlations between the corresponding glyph units.
- B5 (C1484): the two exclusivity rules checked as spelling rules.

## Classification rule (locked)
- **IDENTITY** — the registered claim is implied by an EVA spelling convention: every letter the claim is about has
  context determinism ≥ 99% (it essentially never occurs outside the multi-letter glyph that forces the pattern).
  The claim is restated as a glyph-level fact and stops counting as an atom-level grammar fact.
- **PARTLY ORTHOGRAPHIC** — determinism between 90% and 99%: the claim is dominated by spelling; report the residual.
- **NOT ORTHOGRAPHIC** — determinism < 90%: the transliteration-unit objection does not apply.
Glyph-level restatements (B1–B4) are reported descriptively; they do not by themselves promote or demote anything.
